"""Phase 6: rebuild the place features from the crosswalk and geo/decisions.json.

One LPF Feature per surviving Digital Manna entry (after merges and
exclusions), plus the Theographic places kept as their own features. This phase
sets @id, properties.title, properties.fclasses, geometry and links[].
names[] and when{} are added by later phases.

Reads:  geo/working/phase-5-crosswalk.json, geo/decisions.json,
        geo/working/openbible-ancient.jsonl,
        json/places.json, geo/bible-places.geojson (legacy, for @id and fclasses)
Writes: geo/working/phase-6-output.geojson   single FeatureCollection
        geo/working/phase-6-index.json       provenance per feature, for later phases
        geo/working/phase-6-id-map.csv       legacy @id -> new @id
        geo/working/phase-6-review-coordinates.csv  DM points OpenBible doesn't support
        geo/working/phase-6-report.md

Usage: python3 geo/pipeline/phase6_rebuild.py
"""
import collections
import csv
import json
import math
import re
from datetime import date

WORK = 'geo/working'
CONTEXT = 'https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld'
ID_BASE = 'https://bible.helloao.org/api/c/places/'
CERTAIN_SCORE = 500

# OpenBible type -> LPF fclass, from the spec table in the Notion project page.
OB_FCLASS = {
    'body of water': 'H', 'canal': 'H', 'river': 'H', 'spring': 'H', 'wadi': 'H',
    'district in settlement': 'L', 'people group': 'L', 'region': 'L',
    'settlement': 'P', 'settlement and spring': 'P',
    'road': 'R',
    'altar': 'S', 'campsite': 'S', 'garden': 'S', 'gate': 'S', 'hall': 'S', 'mine': 'S', 'pool': 'S',
    'room': 'S', 'special': 'S', 'stone heap': 'S', 'structure': 'S', 'tree': 'S', 'well': 'S',
    'cliff': 'T', 'field': 'T', 'ford': 'T', 'forest': 'T', 'fortification': 'S', 'hill': 'T',
    'island': 'T', 'mountain': 'T', 'mountain pass': 'T', 'mountain range': 'T', 'mountain ridge': 'T',
    'natural area': 'T', 'promontory': 'T', 'rock': 'T', 'valley': 'T',
}
# Theographic featureType -> fclass, used only when nothing else is known.
THEO_FCLASS = {'City': 'P', 'Region': 'L', 'Water': 'H', 'Mountain': 'T', 'Valley': 'T',
               'Island': 'T', 'Landmark': 'S', 'Road': 'R'}


def km(a, b):
    (lon1, lat1), (lon2, lat2) = a, b
    p = math.pi / 180
    h = (math.sin((lat2 - lat1) * p / 2) ** 2 +
         math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 12742 * math.asin(math.sqrt(h))


def norm(name):
    return re.sub(r'[^a-z]', '', (name or '').lower())


def dedup(seq):
    return list(dict.fromkeys(x for x in seq if x))


def ob_points(rec):
    """(score, [lon, lat]) for every OpenBible identification, best first."""
    pts = []
    for ident in rec.get('identifications') or []:
        for res in ident.get('resolutions') or []:
            if res.get('lonlat'):
                lon, lat = map(float, res['lonlat'].split(','))
                pts.append((res.get('best_path_score'), [lon, lat]))
    return pts


def main():
    ob_full = {}
    for line in open(f'{WORK}/openbible-ancient.jsonl'):
        rec = json.loads(line)
        ob_full[rec['id']] = rec
    cw = json.load(open(f'{WORK}/phase-5-crosswalk.json'))
    dec = json.load(open('geo/decisions.json'))
    places = {p['fields']['placeID']: p['fields'] for p in json.load(open('json/places.json'))}
    legacy = {f['@id']: f for fc in json.load(open('geo/bible-places.geojson')) for f in fc['features']}

    dm_rows = {r['dm_id']: r for r in cw['rows'] if r['kind'] == 'dm'}
    orphan_rows = {r['placeID']: r for r in cw['rows'] if r['kind'] == 'theographic-orphan'}

    absorbed_into = {a: m['canonical'] for m in dec['merges'] for a in m['absorb']}
    excluded_dm = {d['dm_id'] for d in dec['dm_exclude']}
    excluded_pid = {p for e in dec['theographic_exclude'] for p in e['placeIDs']}
    assign = {a['placeID']: a['dm_id'] for a in dec['theographic_assign']}
    pleiades_pick = {p['dm_id']: p for p in dec['pleiades']}

    # ---- group DM entries into features ------------------------------------
    members = collections.defaultdict(list)          # canonical dm_id -> [dm rows]
    for dm_id, r in dm_rows.items():
        if dm_id in excluded_dm:
            continue
        members[absorbed_into.get(dm_id, dm_id)].append(r)

    feats = []
    for canon, rows in members.items():
        rows.sort(key=lambda r: r['dm_id'] != canon)  # canonical first
        pids = [t['placeID'] for r in rows for t in r['theographic']
                if t['placeID'] not in excluded_pid and assign.get(t['placeID'], canon) == canon]
        pids += [p for p, d in assign.items() if d == canon and p not in pids]
        feats.append({'kind': 'dm', 'canonical': canon, 'rows': rows, 'placeIDs': pids})
    for nf in dec['theographic_new_feature']:
        feats.append({'kind': 'theographic', 'canonical': None, 'rows': [],
                      'placeIDs': [nf['placeID']], 'orphan': orphan_rows[nf['placeID']]})

    # ---- per-feature fields -------------------------------------------------
    ob_feature_count = collections.Counter()
    for f in feats:
        f['openbible'] = dedup(o['id'] for r in f['rows'] for o in r['openbible'])
        f['ob_records'] = {o['id']: o for r in f['rows'] for o in r['openbible']}
        f['verses'] = sum(places[p].get('verseCount') or 0 for p in f['placeIDs'] if p in places)
        for o in f['openbible']:
            ob_feature_count[o] += 1
    # A Biblia title names the OpenBible place; when features still share one,
    # it goes to the feature with the most verses and the others use their DM name.
    def names_of(f):
        return {norm(n) for r in f['rows'] for n in [r['dm_name']] + r['dm_names']} | \
               {norm(places[p].get(k)) for p in f['placeIDs'] if p in places for k in ('displayTitle', 'kjvName')}

    def owns_title(f, title):
        return norm(title.split('(')[0]) in names_of(f)

    ob_owner = {}
    by_ob = collections.defaultdict(list)
    for f in feats:
        for o in f['openbible']:
            by_ob[o].append(f)
    for o, fs in by_ob.items():
        bt = fs[0]['ob_records'][o]['biblia_title'] or ''
        best = max(fs, key=lambda f: (owns_title(f, bt), f['verses']))
        ob_owner[o] = id(best)

    out, index, idmap, moved, coord_review = [], [], [], [], []
    for f in feats:
        canon_row = f['rows'][0] if f['rows'] else None
        legacy_ids = dedup([i for r in f['rows'] for i in r['legacy_geojson_ids']] +
                           [i for p in f['placeIDs'] if p in orphan_rows for i in orphan_rows[p]['legacy_geojson_ids']])
        # @id follows the DM slug, as the legacy ids did; legacy ids map to it in phase-6-id-map.csv
        at_id = f'{ID_BASE}{canon_row["dm_slug"]}.json' if canon_row else legacy_ids[0]
        for i in legacy_ids:
            idmap.append({'legacy_id': i, 'new_id': at_id})

        # title
        title, title_src = None, None
        if f['canonical'] in dec['titles']:
            title, title_src = dec['titles'][f['canonical']], 'decision'
        else:
            for o in f['openbible']:
                bt = f['ob_records'][o]['biblia_title']
                if bt and ob_owner[o] == id(f):
                    title, title_src = bt, 'biblia'
                    break
        if not title:
            title = canon_row['dm_name'] if canon_row else legacy[at_id]['properties']['title']
            title_src = 'dm' if canon_row else 'legacy'

        # fclasses: legacy (already reviewed in Phase 2), else OpenBible types, else Theographic featureType
        fc = dec.get('fclasses', {}).get(f['canonical']) or \
            dedup(c for i in legacy_ids for c in legacy[i]['properties'].get('fclasses') or [])
        fc_src = 'decision' if f['canonical'] in dec.get('fclasses', {}) else 'legacy'
        if not fc:
            fc = dedup(OB_FCLASS.get(t) for o in f['openbible'] for t in f['ob_records'][o]['types'] or [])
            fc_src = 'openbible'
        if not fc:
            fc = dedup(THEO_FCLASS.get(places[p].get('featureType')) for p in f['placeIDs'] if p in places)
            fc_src = 'theographic'

        # geometry. Certainty comes from the OpenBible score of the identification
        # the point belongs to, so the point must be one OpenBible scored:
        #   decision override > DM point that matches any OpenBible identification
        #   > OpenBible's top identification > DM point (no OpenBible) > legacy point.
        geom, point, score = None, None, None
        dm_pt = [float(canon_row['lon']), float(canon_row['lat'])] \
            if canon_row and canon_row['lat'] is not None and canon_row['lon'] is not None else None
        pts = next((ob_points(ob_full[o]) for o in f['openbible'] if o in ob_full and ob_points(ob_full[o])), [])
        override = dec.get('coordinates', {}).get(f['canonical'])
        if override:
            point, coord_src = [override['lon'], override['lat']], 'decision'
            score = CERTAIN_SCORE if override.get('certainty') == 'certain' else None
        elif dm_pt and pts:
            near = next(((sc, p) for sc, p in pts if km(p, dm_pt) < 1), None)
            if near:
                point, score, coord_src = dm_pt, near[0], 'dm'
            else:
                point, score, coord_src = pts[0][1], pts[0][0], 'openbible (dm point not in openbible)'
                coord_review.append({'title': title, 'dm_id': f['canonical'], 'dm_lon': dm_pt[0], 'dm_lat': dm_pt[1],
                                     'openbible_lon': pts[0][1][0], 'openbible_lat': pts[0][1][1],
                                     'openbible_score': pts[0][0], 'km_apart': round(km(dm_pt, pts[0][1]), 1)})
        elif dm_pt:
            point, coord_src = dm_pt, 'dm'
        elif pts:
            point, score, coord_src = pts[0][1], pts[0][0], 'openbible'
        else:
            lg = next((legacy[i]['geometry'] for i in legacy_ids
                       if legacy[i].get('geometry') and legacy[i]['geometry'].get('coordinates')), None)
            if lg:
                point, coord_src = lg['coordinates'], 'legacy'
        if point:
            geom = {'type': 'Point', 'coordinates': [round(float(point[0]), 6), round(float(point[1]), 6)],
                    'certainty': 'certain' if score is not None and score >= CERTAIN_SCORE else 'less-certain'}
            for i in legacy_ids:
                lg = legacy[i].get('geometry') or {}
                if lg.get('coordinates'):
                    d = km(lg['coordinates'], geom['coordinates'])
                    if d > 1:
                        moved.append((title, i.rsplit('/', 1)[1], round(d, 1)))

        # Pleiades
        pl = collections.OrderedDict()
        for r in f['rows']:
            for p, s in r['pleiades'].items():
                pl.setdefault(p, set()).update(s)
        pick = pleiades_pick.get(f['canonical'])
        if pick:
            pl = {pick['id']: {'decision'}}
        wikidata = dedup(q for r in f['rows'] for q in r['wikidata'])

        links = []
        if canon_row:
            links.append(f'https://www.digitalmanna.org/encyclopedia/places/{canon_row["dm_slug"]}')
        links += [f'https://theographic.netlify.app/place/{places[p]["slug"]}/' for p in f['placeIDs'] if p in places]
        links += [f'https://www.openbible.info/geo/ancient/{o}' for o in f['openbible']]
        links += [f'https://pleiades.stoa.org/places/{p}' for p in pl]
        links += [f'https://www.wikidata.org/wiki/{q}' for q in wikidata]

        out.append({'@id': at_id, 'type': 'Feature',
                    'properties': {'title': title, 'fclasses': fc},
                    'geometry': geom,
                    'links': [{'type': 'seeAlso', 'identifier': u} for u in dedup(links)]})
        index.append({'@id': at_id, 'title': title, 'title_source': title_src, 'fclasses_source': fc_src,
                      'coordinates_source': coord_src if geom else None,
                      'dm_ids': [r['dm_id'] for r in f['rows']], 'placeIDs': f['placeIDs'],
                      'openbible': f['openbible'], 'pleiades': list(pl), 'wikidata': wikidata,
                      'tyndale': dedup(t for r in f['rows'] for t in r['tyndale']),
                      'legacy_ids': legacy_ids})

    # Title collisions: the feature whose own names match keeps it (then most
    # verses); the others fall back to their DM name.
    verses_by_id = {i['@id']: v for i, v in zip(index, [f['verses'] for f in feats])}
    names_by_id = {i['@id']: names_of(f) for i, f in zip(index, feats)}
    dm_name_by_id = {i['@id']: (f['rows'][0]['dm_name'] if f['rows'] else i['title']) for i, f in zip(index, feats)}
    by_title = collections.defaultdict(list)
    for x, i in zip(out, index):
        by_title[x['properties']['title']].append((x, i))
    for t, grp in by_title.items():
        if len(grp) < 2 or any(i['title_source'] == 'decision' for _, i in grp):
            continue
        grp.sort(key=lambda xi: (norm(t.split('(')[0]) in names_by_id[xi[0]['@id']], verses_by_id[xi[0]['@id']]), reverse=True)
        for x, i in grp[1:]:
            x['properties']['title'] = i['title'] = dm_name_by_id[x['@id']]
            i['title_source'] = 'dm (collision)'

    out.sort(key=lambda x: x['properties']['title'].lower())
    index.sort(key=lambda x: x['title'].lower())
    fc_out = {'type': 'FeatureCollection', '@context': CONTEXT, 'features': out}
    json.dump(fc_out, open(f'{WORK}/phase-6-output.geojson', 'w'), indent=2, ensure_ascii=False)
    json.dump(index, open(f'{WORK}/phase-6-index.json', 'w'), indent=1, ensure_ascii=False)
    with open(f'{WORK}/phase-6-id-map.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['legacy_id', 'new_id'])
        w.writeheader()
        w.writerows(sorted(idmap, key=lambda r: r['legacy_id']))

    with open(f'{WORK}/phase-6-review-coordinates.csv', 'w', newline='') as fh:
        cols = ['title', 'dm_id', 'km_apart', 'openbible_score', 'dm_lon', 'dm_lat', 'openbible_lon', 'openbible_lat']
        w = csv.DictWriter(fh, fieldnames=cols + ['decision'])
        w.writeheader()
        w.writerows(sorted(coord_review, key=lambda r: -r['km_apart']))

    # ---- checks + report ----------------------------------------------------
    C = collections.Counter
    titles = C(x['properties']['title'] for x in out)
    ids = C(x['@id'] for x in out)
    dup_titles = sorted(t for t, n in titles.items() if n > 1)
    dup_ids = sorted(i for i, n in ids.items() if n > 1)
    legacy_dropped = sorted(set(legacy) - {r['legacy_id'] for r in idmap})
    no_geom = [x['properties']['title'] for x in out if x['geometry'] is None]
    multi_fc = C(len(x['properties']['fclasses']) for x in out)
    placed = {p for x in index for p in x['placeIDs']}
    unplaced = sorted(set(places) - placed - excluded_pid)
    checks = [
        ('one FeatureCollection with @context', True),
        ('unique @id', not dup_ids),
        ('unique titles', not dup_titles),
        ('no fclass "A"', all('A' not in x['properties']['fclasses'] for x in out)),
        ('no repeated fclass codes', all(len(set(x['properties']['fclasses'])) == len(x['properties']['fclasses']) for x in out)),
        ('every feature has fclasses', all(x['properties']['fclasses'] for x in out)),
        ('no Point without coordinates', all(x['geometry'] is None or x['geometry'].get('coordinates') for x in out)),
        ('every Theographic place is placed or excluded', not unplaced),
        ('every legacy record maps to a feature', not legacy_dropped),
    ]
    lines = [
        '# Phase 6 Report: Rebuilt Features', '',
        f'**Generated:** {date.today().isoformat()}  ',
        '**Inputs:** phase-5-crosswalk.json, geo/decisions.json', '',
        '## Counts', '',
        '| Metric | Count |', '|---|---|',
        f'| Features | {len(out)} (was {len(legacy)}) |',
        f'| From DM entries | {sum(1 for f in feats if f["kind"] == "dm")} |',
        f'| Theographic-only features | {sum(1 for f in feats if f["kind"] == "theographic")} |',
        f'| DM entries merged away | {len(absorbed_into)} |',
        f'| DM entries excluded | {len(excluded_dm)} |',
        f'| Theographic places excluded | {len(excluded_pid)} |',
        f'| Features absorbing 2+ legacy records | {sum(1 for x in index if len(x["legacy_ids"]) > 1)} |',
        f'| New features (no legacy record) | {sum(1 for x in index if not x["legacy_ids"])} |',
        f'| With geometry | {len(out) - len(no_geom)} ({sum(1 for x in out if x["geometry"] and x["geometry"]["certainty"] == "certain")} certain) |',
        f'| Null geometry | {len(no_geom)} |',
        f'| Points moved > 1 km vs legacy | {len(moved)} |',
        f'| DM points not supported by OpenBible (OpenBible point used; see phase-6-review-coordinates.csv) | {len(coord_review)} |',
        f'| With Pleiades link | {sum(1 for x in index if x["pleiades"])} |',
        f'| With Wikidata link | {sum(1 for x in index if x["wikidata"])} |', '',
        f'Title sources: {dict(C(x["title_source"] for x in index))}  ',
        f'fclasses sources: {dict(C(x["fclasses_source"] for x in index))}  ',
        f'Coordinate sources: {dict(C(x["coordinates_source"] for x in index))}  ',
        f'fclasses per feature: {dict(sorted(multi_fc.items()))}', '',
        '## Checks', '',
    ] + [f'- {"✓" if ok else "✗"} {name}' for name, ok in checks]
    if dup_titles:
        lines += ['', '### Duplicate titles', ''] + [f'- {t}' for t in dup_titles]
    if dup_ids:
        lines += ['', '### Duplicate @id', ''] + [f'- {i}' for i in dup_ids]
    if unplaced:
        lines += ['', '### Theographic places not placed', ''] + [f'- #{p} {places[p]["displayTitle"]}' for p in unplaced]
    if legacy_dropped:
        lines += ['', '### Legacy records with no feature', ''] + [f'- {i}' for i in legacy_dropped]
    lines += ['', '## Null geometry', ''] + [f'- {t}' for t in sorted(no_geom)]
    lines += ['', '## Points moved more than 1 km (DM coordinates vs legacy)', '',
              '| Feature | Legacy record | km |', '|---|---|---|']
    lines += [f'| {t} | `{i}` | {d} |' for t, i, d in sorted(moved, key=lambda m: -m[2])]
    open(f'{WORK}/phase-6-report.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:40]))


if __name__ == '__main__':
    main()
