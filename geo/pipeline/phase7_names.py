"""Phase 7: add names[] to every feature.

Sources, in order (a later source's duplicate of an earlier name adds its
citation to that name rather than a new entry; duplicates compare letters only,
so "Beth-lehem" = "Bethlehem"):
  1. Digital Manna: name + names[] of every DM entry merged into the feature
  2. Theographic: displayTitle / kjvName / esvName / aliases of its placeIDs
  3. OpenBible: translation_name_counts of its OpenBible places
  4. Pleiades: names attested in antiquity (start <= 640, or undated in an
     ancient language), with Pleiades' lang and start/end

Filters (counted in the report): parenthetical qualifiers are stripped
("Antioch (Syria)" -> "Antioch"); generic single words ("Mount", "Tower"),
possessives ("Ashdod's") and gentilics ("Ashdothites", unless that is the
feature's own title) are dropped from every source. OpenBible names, which are
translation renderings of whole verse phrases, are also dropped when they start
lowercase ("city of Moab") or name a different feature ("Edom" under Teman).
Pleiades' -3300..2000 range means "date unknown" and is treated as undated.

Per-name when{}: the earliest and latest verse yearNum of the Theographic
placeIDs whose displayTitle/kjvName/esvName is that name (Airtable `aliases`
contribute names but not dates) (e.g. Azotus only in Acts). Pleiades names use
Pleiades' own start/end instead.

Reads:  geo/working/phase-6-output.geojson, phase-6-index.json, dm-places-cache.json,
        openbible-ancient.jsonl, pleiades-cache.json; json/places.json, json/verses.json
Writes: geo/working/phase-7-output.geojson, geo/working/phase-7-report.md

Usage: python3 geo/pipeline/phase7_names.py
"""
import collections
import json
import re
from datetime import date

WORK = 'geo/working'
LATEST_ANCIENT = 640
ANCIENT_LANGS = {'grc', 'la', 'akk', 'egy', 'hbo', 'arc', 'cop', 'hit', 'peo', 'phn', 'sux', 'elx',
                 'xur', 'cana', 'xmn', 'xmr', 'xlc', 'syc', 'uga'}


GENERIC = {'mount', 'mountain', 'mountains', 'river', 'city', 'field', 'tower', 'valley', 'sea', 'brook',
           'gate', 'hill', 'lower', 'upper', 'plain', 'desert', 'wilderness', 'land', 'house', 'rock',
           'well', 'pool', 'spring', 'stream', 'forest', 'region', 'district', 'island', 'east', 'west',
           'north', 'south', 'hedges', 'jewish', 'jews', 'lord', 'there', 'judgment', 'most holy'}
GENTILIC = re.compile(r"(ites?|ians?|eans?|ines|ites’)$|^Jews?$|^Jewish$", re.IGNORECASE)
POSSESSIVE = re.compile(r"['’]s?$")
UNKNOWN_SPAN = (-3300, 2000)    # Pleiades' whole-range default


def clean(name):
    return re.sub(r'\s*\([^)]*\)', '', name or '').strip()


def norm(name):
    return re.sub(r'[^a-z]', '', (name or '').lower())


def dated(n):
    return n.get('start') is not None and (n['start'], n.get('end')) != UNKNOWN_SPAN


def ancient(n):
    if n.get('nameType') not in ('geographic', 'ethnic'):
        return False
    if dated(n):
        return n['start'] <= LATEST_ANCIENT
    lang = (n.get('language') or '').split('-')[0]
    return lang in ANCIENT_LANGS


def timespan(start, end=None):
    span = {'start': {'in': str(start)}}
    if end is not None:
        span['end'] = {'in': str(end)}
    return {'timespans': [span]}


def main():
    fc = json.load(open(f'{WORK}/phase-6-output.geojson'))
    index = {x['@id']: x for x in json.load(open(f'{WORK}/phase-6-index.json'))}
    dm = {e['id']: e for e in json.load(open(f'{WORK}/dm-places-cache.json'))['entries']}
    ob = {}
    for line in open(f'{WORK}/openbible-ancient.jsonl'):
        rec = json.loads(line)
        ob[rec['id']] = rec
    pleiades = json.load(open(f'{WORK}/pleiades-cache.json'))
    places = {p['fields']['placeID']: p['fields'] for p in json.load(open('json/places.json'))}
    year = {v['id']: v['fields'].get('yearNum') for v in json.load(open('json/verses.json'))}

    def place_names(p, aliases=True):
        f = places[p]
        names = [f.get('displayTitle'), f.get('kjvName'), f.get('esvName')]
        if aliases:
            names += [a.strip() for a in (f.get('aliases') or '').split(',')]
        return [n for n in names if n and n.strip()]

    def place_years(p):
        ys = [year[v] for v in places[p].get('verses') or [] if year.get(v) is not None]
        return (min(ys), max(ys)) if ys else None

    # Every feature's own names, to spot OpenBible names that belong to another feature.
    owner = collections.defaultdict(set)
    for feat in fc['features']:
        x = index[feat['@id']]
        own = {norm(clean(feat['properties']['title']))}
        for d in x['dm_ids']:
            own |= {norm(clean(n)) for n in [dm[d]['name']] + (dm[d].get('names') or [])}
        for p in x['placeIDs']:
            if p in places:
                own |= {norm(clean(n)) for n in place_names(p)}
        for k in own:
            owner[k].add(feat['@id'])

    dropped = collections.Counter()
    stats = collections.Counter()
    pleiades_skipped = collections.Counter()
    for feat in fc['features']:
        x = index[feat['@id']]
        pids = [p for p in x['placeIDs'] if p in places]
        by_norm = collections.defaultdict(list)          # normalized name -> placeIDs
        for p in pids:
            for n in place_names(p, aliases=False):
                if p not in by_norm[norm(clean(n))]:
                    by_norm[norm(clean(n))].append(p)

        names, seen = [], {}

        def add(toponym, lang, label, cite_id, when=None):
            if label != 'Pleiades':
                toponym = clean(toponym)
                if toponym.lower() in GENERIC:
                    dropped[f'{label}: generic word'] += 1
                    return
                if POSSESSIVE.search(toponym):
                    dropped[f'{label}: possessive'] += 1
                    return
                if ' ' not in toponym and GENTILIC.search(toponym) and \
                        norm(toponym) != norm(clean(feat['properties']['title'])):
                    dropped[f'{label}: gentilic'] += 1
                    return
            if label == 'OpenBible':
                if toponym[:1].islower():
                    dropped['OpenBible: lowercase phrase'] += 1
                    return
                if owner.get(norm(toponym)) and feat['@id'] not in owner[norm(toponym)]:
                    dropped['OpenBible: names another feature'] += 1
                    return
            key = norm(toponym)
            if not key:
                return
            cite = {'label': label, '@id': cite_id}
            if key in seen:
                entry = seen[key]
                if cite not in entry['citations']:
                    entry['citations'].append(cite)
                if when and 'when' not in entry:
                    entry['when'] = when
                stats[f'duplicate from {label}'] += 1
                return
            entry = {'toponym': toponym, 'lang': lang, 'citations': [cite]}
            if when:
                entry['when'] = when
            names.append(entry)
            seen[key] = entry
            stats[f'name from {label}'] += 1

        def verse_when(toponym):
            toponym = clean(toponym)
            ranges = [place_years(p) for p in by_norm.get(norm(toponym), [])]
            ranges = [r for r in ranges if r]
            if not ranges:
                return None, []
            span = timespan(min(r[0] for r in ranges), max(r[1] for r in ranges))
            cites = [{'label': 'Theographic', '@id': f'https://theographic.netlify.app/place/{places[p]["slug"]}/'}
                     for p in by_norm[norm(toponym)]]
            return span, cites

        def add_with_verses(toponym, lang, label, cite_id):
            when, theo_cites = verse_when(toponym)
            add(toponym, lang, label, cite_id, when)
            entry = seen.get(norm(clean(toponym)))
            if entry and when:
                for c in theo_cites:
                    if c not in entry['citations']:
                        entry['citations'].append(c)

        for d in x['dm_ids']:
            e = dm[d]
            url = f'https://www.digitalmanna.org/encyclopedia/places/{e["slug"]}'
            for n in [e['name']] + (e.get('names') or []):
                add_with_verses(n, 'en', 'Digital Manna', url)
        for p in pids:
            url = f'https://theographic.netlify.app/place/{places[p]["slug"]}/'
            for n in place_names(p):
                add_with_verses(n, 'en', 'Theographic', url)
        for o in x['openbible']:
            counts = ob.get(o, {}).get('translation_name_counts', {})
            for n in sorted(counts, key=lambda k: -counts[k]):
                add_with_verses(n, 'en', 'OpenBible', f'https://www.openbible.info/geo/ancient/{o}')
        for pid in x['pleiades']:
            rec = pleiades.get(pid)
            if not rec:
                stats['pleiades id not retrievable'] += 1
                continue
            for n in rec.get('names') or []:
                if not n.get('romanized'):
                    continue
                if not ancient(n):
                    pleiades_skipped[n.get('language') or '(none)'] += 1
                    continue
                when = timespan(n['start'], n.get('end')) if dated(n) else None
                add(n['romanized'], n.get('language') or '', 'Pleiades',
                    f'https://pleiades.stoa.org/places/{pid}', when)

        feat['names'] = names
        stats['features'] += 1
        stats['names'] += len(names)
        stats['names with when'] += sum(1 for n in names if 'when' in n)
        if not names:
            stats['features without names'] += 1

    # keep LPF member order: @id, type, properties, geometry, names, links
    order = ['@id', 'type', 'properties', 'geometry', 'names', 'links']
    fc['features'] = [{k: f[k] for k in order if k in f} for f in fc['features']]
    json.dump(fc, open(f'{WORK}/phase-7-output.geojson', 'w'), indent=2, ensure_ascii=False)

    per = collections.Counter(min(len(f['names']), 10) for f in fc['features'])
    antioch = next((f for f in fc['features'] if f['properties']['title'] == 'Antioch (of Syria)'), None)
    lines = [
        '# Phase 7 Report: names[]', '',
        f'**Generated:** {date.today().isoformat()}', '',
        '| Metric | Count |', '|---|---|',
        f'| Features | {stats["features"]} |',
        f'| Features without names | {stats["features without names"]} |',
        f'| Names | {stats["names"]} |',
        f'| Names with their own when{{}} | {stats["names with when"]} |',
        f'| From Digital Manna | {stats["name from Digital Manna"]} |',
        f'| From Theographic (not already in DM) | {stats["name from Theographic"]} |',
        f'| From OpenBible (not already listed) | {stats["name from OpenBible"]} |',
        f'| From Pleiades (ancient attestations) | {stats["name from Pleiades"]} |',
        f'| Duplicates folded into an existing name as extra citations | '
        f'{sum(v for k, v in stats.items() if k.startswith("duplicate"))} |',
        f'| Pleiades IDs that could not be retrieved | {stats["pleiades id not retrievable"]} |', '',
        'Names dropped by filter: ' + ', '.join(f'{k} {v}' for k, v in dropped.most_common()), '',
        'Names per feature (10 = 10+): ' + ', '.join(f'{k}: {v}' for k, v in sorted(per.items())), '',
        'Pleiades names left out (modern, or undated in a non-ancient language), by language: '
        + ', '.join(f'{k} {v}' for k, v in pleiades_skipped.most_common()), '',
        '## Gold-standard check: Antioch (of Syria)', '', '```json',
        json.dumps(antioch['names'] if antioch else None, indent=1, ensure_ascii=False), '```',
    ]
    open(f'{WORK}/phase-7-report.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:22]))


if __name__ == '__main__':
    main()
