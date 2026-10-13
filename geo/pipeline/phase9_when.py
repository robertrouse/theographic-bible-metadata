"""Phase 9: feature-level when{} (start only, per the spec).

Two attestations are compared:
  - Pleiades: the earliest ancient attestation found in Phase 8, written like
    the gold standard: {"timespans": [{"start": {"in": "-750"}}]}
  - Theographic chronology: the earliest year among the feature's verses
    (Theographic placeIDs and Digital Manna verse refs) and the events located
    there. A place mentioned only in undated verses (e.g. the Numbers 33
    campsites) takes the year of the nearest dated verse in the same book,
    within NEIGHBOR_CHAPTERS chapters. Inside the Levant the year is labelled
    with its PeriodO period from the NEAEHL chronology
    (geo/pipeline/periodo_neaehl.json).
Pleiades, the standardized source, is used unless the Bible attests the place
more than PLEIADES_TOLERANCE years earlier (Pleiades' record of Bethlehem only
starts in 30 BC). Set PLEIADES_FIRST = True to always prefer Pleiades.
Dates in geo/decisions.json ("when") override both. Features with no date are
listed for manual dating.

Reads:  geo/working/phase-7-output.geojson, phase-8-index.json, dm-places-cache.json;
        json/places.json, json/verses.json, json/events.json; geo/pipeline/periodo_neaehl.json
Writes: geo/working/phase-9-output.geojson          complete LPF FeatureCollection
        geo/working/phase-9-needs-manual-when.csv
        geo/working/phase-9-review-pleiades-later.csv  where the biblical date replaced a much
                                                       later Pleiades start
        geo/working/phase-9-report.md

Usage: python3 geo/pipeline/phase9_when.py
"""
import collections
import csv
import json
import re
from datetime import date

WORK = 'geo/working'
LEVANT = {'lon': (32.0, 39.5), 'lat': (28.0, 36.5)}   # where the Holy Land chronology applies
PLEIADES_TOLERANCE = 300     # years the Bible must precede Pleiades by to win
PLEIADES_FIRST = False
NEIGHBOR_CHAPTERS = 2
ORDER = ['@id', 'properties', 'type', 'geometry', 'when', 'names', 'links']   # gold-standard member order


def in_levant(geom):
    if not (geom or {}).get('coordinates'):
        return False
    lon, lat = geom['coordinates']
    return LEVANT['lon'][0] <= lon <= LEVANT['lon'][1] and LEVANT['lat'][0] <= lat <= LEVANT['lat'][1]


def main():
    fc = json.load(open(f'{WORK}/phase-7-output.geojson'))
    index = {x['@id']: x for x in json.load(open(f'{WORK}/phase-8-index.json'))}
    dm = {e['id']: e for e in json.load(open(f'{WORK}/dm-places-cache.json'))['entries']}
    places = {p['fields']['placeID']: p['fields'] for p in json.load(open('json/places.json'))}
    rec_to_pid = {p['id']: p['fields']['placeID'] for p in json.load(open('json/places.json'))}
    verses = {}
    by_verse_id = {}
    by_osis = {}
    for v in json.load(open('json/verses.json')):
        f = v['fields']
        verses[v['id']] = f
        by_verse_id[int(f['verseID'])] = f
        by_osis[f['osisRef']] = int(f['verseID'])
    # nearest dated verse for undated ones: same book, within NEIGHBOR_CHAPTERS, preceding first
    dated_by_book = collections.defaultdict(list)
    for vid in sorted(by_verse_id):
        if by_verse_id[vid].get('yearNum') is not None:
            dated_by_book[vid // 1000000].append(vid)

    def neighbor_year(vid):
        book, chapter = vid // 1000000, vid // 1000 % 1000
        best = None
        for d in dated_by_book.get(book, []):
            gap = abs(d // 1000 % 1000 - chapter)
            if gap <= NEIGHBOR_CHAPTERS:
                key = (gap, d > vid, abs(d - vid))
                if best is None or key < best[0]:
                    best = (key, d)
        return (by_verse_id[best[1]]['yearNum'], by_verse_id[best[1]]['osisRef']) if best else None
    events_at = collections.defaultdict(list)
    for e in json.load(open('json/events.json')):
        f = e['fields']
        m = re.match(r'(-?\d+)', f.get('startDate') or '')
        if m:
            for loc in f.get('locations') or []:
                if loc in rec_to_pid:
                    events_at[rec_to_pid[loc]].append((int(m.group(1)), f['title']))
    periods = json.load(open('geo/pipeline/periodo_neaehl.json'))['periods']
    dec_when = json.load(open('geo/decisions.json')).get('when', {})
    dec_verses = json.load(open('geo/decisions.json')).get('verses', {})

    def period_of(year):
        return next((p for p in periods if p['start'] <= year < p['stop']), None)

    def earliest_mention(x):
        """(year, reference, how) from dated mentions; else from undated mentions' neighbours."""
        found, undated = [], []
        vids = {int(verses[v]['verseID']) for p in x['placeIDs'] for v in (places.get(p) or {}).get('verses') or []
                if v in verses}
        vids |= {vid for d in x['dm_ids'] for vid in dm[d].get('verses') or [] if vid in by_verse_id}
        vids |= {by_osis[o] for d in x['dm_ids'] for o in dec_verses.get(d, []) if o in by_osis}
        for vid in vids:
            f = by_verse_id[vid]
            (found if f.get('yearNum') is not None else undated).append(vid)
        found = [(by_verse_id[v]['yearNum'], by_verse_id[v]['osisRef'], 'mention') for v in found]
        found += [(y, f'event: {t}', 'mention') for p in x['placeIDs'] for y, t in events_at.get(p, [])]
        if found:
            return min(found)
        near = []
        for vid in undated:
            n = neighbor_year(vid)
            if n:
                near.append((n[0], f'{by_verse_id[vid]["osisRef"]}, dated by {n[1]}', 'neighbor'))
        return min(near) if near else None

    stats = collections.Counter()
    period_counts = collections.Counter()
    manual, later = [], []
    for feat in fc['features']:
        x = index[feat['@id']]
        pl = x.get('pleiades_start')
        bible = earliest_mention(x)
        override = dec_when.get(x['dm_ids'][0]) if x['dm_ids'] else None
        bible_wins = bible and (not pl or (not PLEIADES_FIRST and bible[0] < pl['year'] - PLEIADES_TOLERANCE))
        if pl and bible and bible_wins:
            later.append({'title': feat['properties']['title'], 'pleiades_start': pl['year'],
                          'pleiades_name': pl['name'], 'pleiades': pl['pleiades'],
                          'first_biblical_mention': bible[0], 'reference': bible[1],
                          'years_apart': pl['year'] - bible[0]})
        when = None
        if override or bible_wins:
            year = override['year'] if override else bible[0]
            when = {'timespans': [{'start': {'in': str(year)}}]}
            period = period_of(year) if in_levant(feat.get('geometry')) else None
            if period:
                when['periods'] = [{'name': period['name'], 'uri': period['uri']}]
                period_counts[period['name']] += 1
            if override:
                when['label'] = override['label']
                stats['decision'] += 1
            else:
                what = 'earliest mention in the biblical narrative' if bible[2] == 'mention' else \
                    'earliest mention in the biblical narrative, undated verse'
                when['label'] = f'{what} ({bible[1]}), Theographic chronology' + \
                    (f'; Pleiades attests it from {pl["year"]}' if pl else '')
                stats[('theographic' if bible[2] == 'mention' else 'theographic, neighbouring verse') +
                      (', with PeriodO period' if period else ', outside the Levant (no period)')] += 1
        elif pl:
            when = {'timespans': [{'start': {'in': str(pl['year'])}}]}
            stats['pleiades'] += 1
        else:
            stats['none'] += 1
            manual.append({'@id': feat['@id'], 'title': feat['properties']['title'],
                           'fclasses': ' '.join(feat['properties']['fclasses']),
                           'dm_ids': ' '.join(x['dm_ids']), 'placeIDs': ' '.join(map(str, x['placeIDs']))})
        if when:
            feat['when'] = when
        feat['type'] = 'Feature'

    fc['features'] = [{k: f[k] for k in ORDER if k in f} for f in fc['features']]
    fc = {'type': fc['type'], '@context': fc['@context'], 'features': fc['features']}
    json.dump(fc, open(f'{WORK}/phase-9-output.geojson', 'w'), indent=2, ensure_ascii=False)

    def write(name, rows, cols):
        with open(f'{WORK}/{name}', 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=cols + ['decision'])
            w.writeheader()
            w.writerows(rows)
    write('phase-9-needs-manual-when.csv', manual, ['@id', 'title', 'fclasses', 'dm_ids', 'placeIDs'])
    write('phase-9-review-pleiades-later.csv', sorted(later, key=lambda r: -r['years_apart']),
          ['title', 'pleiades_start', 'pleiades_name', 'pleiades', 'first_biblical_mention', 'reference', 'years_apart'])

    feats = {f['properties']['title']: f for f in fc['features']}
    checks = ['Antioch (of Syria)', 'Jerusalem', 'Mount Nebo', 'Bethlehem (of Judah)', 'Babel', 'Aphek of Sharon',
              'Reuben', 'Eden (garden)', 'Patmos']
    total = len(fc['features'])
    lines = [
        '# Phase 9 Report: when{}', '',
        f'**Generated:** {date.today().isoformat()}', '',
        '| Source of the feature start date | Features |', '|---|---|',
        f'| Pleiades (earliest ancient attestation) | {stats["pleiades"]} |',
        f'| Theographic chronology, with a PeriodO period | {stats["theographic, with PeriodO period"]} |',
        f'| Theographic chronology, outside the Levant (no period) | {stats["theographic, outside the Levant (no period)"]} |',
        f'| Theographic, dated from the nearest dated verse, with a PeriodO period | {stats["theographic, neighbouring verse, with PeriodO period"]} |',
        f'| Theographic, dated from the nearest dated verse, outside the Levant | {stats["theographic, neighbouring verse, outside the Levant (no period)"]} |',
        f'| geo/decisions.json | {stats["decision"]} |',
        f'| None: needs manual dating (`phase-9-needs-manual-when.csv`) | {stats["none"]} |',
        f'| **Total with when{{}}** | **{total - stats["none"]} of {total}** |', '',
        f'Biblical date used instead of a Pleiades start more than {PLEIADES_TOLERANCE} years later: {len(later)} '
        '(`phase-9-review-pleiades-later.csv`). '
        + ('PLEIADES_FIRST is on, so these keep Pleiades.' if PLEIADES_FIRST else
           'Set PLEIADES_FIRST = True to keep Pleiades for these.'), '',
        '## PeriodO periods assigned (NEAEHL, Holy Land)', '',
        '| Period | Features |', '|---|---|',
    ] + [f'| {p["name"]} | {period_counts[p["name"]]} |' for p in periods if period_counts[p['name']]] + [
        '', '## Spot checks', '', '| Feature | when |', '|---|---|',
    ] + [f'| {t} | `{json.dumps(feats[t].get("when"), ensure_ascii=False)}` |' for t in checks if t in feats]
    lines += ['', '## Needs manual dating', ''] + [f'- {m["title"]}' for m in manual]
    open(f'{WORK}/phase-9-report.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
