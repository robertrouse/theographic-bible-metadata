"""Phase 5: build the place crosswalk and the review lists.

One crosswalk row per Digital Manna (DM) place entry, the planned spine for
LPF features, plus one row per Theographic place that no DM entry claims.
Each row joins Theographic placeIDs, OpenBible, Tyndale, Easton's, Pleiades
and Wikidata IDs, and the records in the legacy (March 2026) bible-places.geojson that
would collapse into it.

Reads:  geo/working/{dm-places-cache.json, openbible-ancient.jsonl, wikidata-pleiades.json}
        json/places.json, geo/legacy/bible-places-2026-03.geojson
Writes: geo/working/phase-5-crosswalk.json
        geo/working/phase-5-review-*.csv   (each has an empty `decision` column)
        geo/working/phase-5-report.md

Run fetch_sources.py first. Usage: python3 geo/pipeline/phase5_crosswalk.py
"""
import collections
import csv
import difflib
import json
import re
from datetime import date

WORK = 'geo/working'
CERTAIN_SCORE = 500


def norm(name):
    return re.sub(r'[^a-z]', '', (name or '').lower())


def link_ids(feature, host):
    return [l['identifier'] for l in feature.get('links', []) if host in l['identifier']]


def theo_ids_from_url(url):
    # slug_ID, and two malformed links carry "slug_421, 1010"
    return [int(x) for x in re.findall(r'\d+', url.rsplit('_', 1)[1])]


def dm_theo_ids(entry):
    # DM stores IDs as strings, and one entry has "421, 1010" in a single string
    return [int(x) for t in entry['ids'].get('theographic') or [] for x in re.findall(r'\d+', t)]


def load():
    dm = json.load(open(f'{WORK}/dm-places-cache.json'))
    ob = {}
    for line in open(f'{WORK}/openbible-ancient.jsonl'):
        rec = json.loads(line)
        ob[rec['id']] = rec
    wd = json.load(open(f'{WORK}/wikidata-pleiades.json'))['pleiades_by_qid']
    places = json.load(open('json/places.json'))
    geo = [f for fc in json.load(open('geo/legacy/bible-places-2026-03.geojson')) for f in fc['features']]
    return dm, ob, wd, places, geo


def ob_summary(rec, wd):
    ld = rec.get('linked_data', {})
    idents = rec.get('identifications') or []
    res = (idents[0].get('resolutions') or [{}])[0] if idents else {}
    qid = ld.get('s7cc8b2', {}).get('id')
    return {
        'id': rec['id'],
        'friendly_id': rec.get('friendly_id'),
        'biblia_title': ld.get('s7f5356', {}).get('name'),
        'types': rec.get('types'),
        'best_path_score': res.get('best_path_score'),
        'lonlat': res.get('lonlat'),
        'identification_count': len(idents),
        'pleiades': ld.get('s2428ed', {}).get('id'),
        'wikidata': qid,
        'wikidata_pleiades': wd.get(qid, []) if qid else [],
        'translation_names': sorted(rec.get('translation_name_counts', {}),
                                    key=lambda n: -rec['translation_name_counts'][n]),
    }


def theo_summary(f, by_rec):
    return {
        'placeID': f['placeID'],
        'slug': f.get('slug'),
        'displayTitle': f.get('displayTitle'),
        'kjvName': f.get('kjvName'),
        'esvName': f.get('esvName'),
        'aliases': f.get('aliases'),
        'featureType': f.get('featureType'),
        'featureSubType': f.get('featureSubType'),
        'lat': f.get('latitude'),
        'lon': f.get('longitude'),
        'verseCount': f.get('verseCount', 0),
        'rootID': [by_rec[r]['placeID'] for r in f.get('rootID') or [] if r in by_rec],
        'duplicate_of': [by_rec[r]['placeID'] for r in f.get('duplicate_of') or [] if r in by_rec],
    }


def write_csv(name, rows, fields):
    path = f'{WORK}/phase-5-review-{name}.csv'
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields + ['decision'], extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: ('; '.join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
    return path


def main():
    dm, ob, wd, places, geo = load()
    by_rec = {p['id']: p['fields'] for p in places}
    by_pid = {p['fields']['placeID']: p['fields'] for p in places}
    entries = dm['entries']

    # Current geojson records, keyed by their DM slug and Theographic IDs.
    geo_by_dmslug = collections.defaultdict(list)
    geo_by_pid = collections.defaultdict(list)
    geo_ob_by_pid = collections.defaultdict(set)
    geo_pleiades = collections.defaultdict(set)
    geo_fclasses = {f['@id']: f['properties'].get('fclasses') or [] for f in geo}
    for f in geo:
        for u in link_ids(f, 'digitalmanna'):
            geo_by_dmslug[u.rsplit('/', 1)[1]].append(f['@id'])
        obs = [u.rsplit('/', 1)[1] for u in link_ids(f, 'openbible')]
        for u in link_ids(f, 'theographic'):
            for pid in theo_ids_from_url(u):
                geo_by_pid[pid].append(f['@id'])
                geo_ob_by_pid[pid].update(obs)
        for u in link_ids(f, 'pleiades'):
            geo_pleiades[f['@id']].add(u.rstrip('/').rsplit('/', 1)[1])

    dm_by_pid = {}
    dm_by_ob = collections.defaultdict(list)
    dm_by_name = collections.defaultdict(set)
    for e in entries:
        for t in dm_theo_ids(e):
            dm_by_pid[t] = e['id']
        for o in e['ids'].get('openbible') or []:
            dm_by_ob[o].append(e['id'])
        for n in [e['name']] + (e.get('names') or []):
            dm_by_name[norm(n)].add(e['id'])

    rows = []
    for e in entries:
        pids = dm_theo_ids(e)
        theo = [theo_summary(by_pid[p], by_rec) for p in pids if p in by_pid]
        obs = [ob_summary(ob[o], wd) for o in e['ids'].get('openbible') or [] if o in ob]
        legacy = sorted({i for i in geo_by_dmslug.get(e['slug'], [])} |
                        {i for p in pids for i in geo_by_pid.get(p, [])})
        pleiades = collections.defaultdict(set)
        for i in legacy:
            for p in geo_pleiades.get(i, []):
                pleiades[p].add('geojson')
        for o in obs:
            if o['pleiades']:
                pleiades[o['pleiades']].add('openbible')
            for p in o['wikidata_pleiades']:
                pleiades[p].add('wikidata')
        loc = e.get('location') or {}
        rows.append({
            'kind': 'dm',
            'dm_id': e['id'],
            'dm_slug': e['slug'],
            'dm_name': e['name'],
            'dm_names': e.get('names') or [],
            'dm_title': e.get('title'),
            'lat': loc.get('lat'),
            'lon': loc.get('lon'),
            'theographic': theo,
            'theographic_missing': [p for p in pids if p not in by_pid],
            'openbible': obs,
            'openbible_missing': [o for o in e['ids'].get('openbible') or [] if o not in ob],
            'tyndale': e['ids'].get('tyndale') or [],
            'eastons': e['ids'].get('eastons') or [],
            'wikidata': sorted({o['wikidata'] for o in obs if o['wikidata']}),
            'pleiades': {p: sorted(s) for p, s in sorted(pleiades.items())},
            'legacy_geojson_ids': legacy,
            'legacy_fclasses': sorted({c for i in legacy for c in geo_fclasses.get(i, [])}),
        })

    # Theographic places no DM entry claims, with suggested homes.
    orphans = []
    for pid, f in sorted(by_pid.items()):
        if pid in dm_by_pid:
            continue
        t = theo_summary(f, by_rec)
        sugg = []
        for d in t['duplicate_of']:
            if d in dm_by_pid:
                sugg.append(f'duplicate_of #{d} -> {dm_by_pid[d]}')
        for o in sorted(geo_ob_by_pid.get(pid, [])):
            for d in dm_by_ob.get(o, []):
                sugg.append(f'openbible {o} -> {d}')
        for n in {t['displayTitle'], t['kjvName'], t['esvName']}:
            for d in sorted(dm_by_name.get(norm(n), [])):
                sugg.append(f'name "{n}" -> {d}')
        for r in t['rootID']:
            if r in dm_by_pid:
                sugg.append(f'rootID #{r} (coords only?) -> {dm_by_pid[r]}')
        orphans.append({**t, 'kind': 'theographic-orphan',
                        'legacy_geojson_ids': sorted(set(geo_by_pid.get(pid, []))),
                        'suggestions': list(dict.fromkeys(sugg))})
    rows.extend(orphans)

    # ---- review lists ------------------------------------------------------
    dm_rows = [r for r in rows if r['kind'] == 'dm']
    by_dm = {r['dm_id']: r for r in dm_rows}

    theo_name_index = collections.defaultdict(set)
    for pid, f in by_pid.items():
        for n in (f.get('displayTitle'), f.get('kjvName'), f.get('esvName')):
            theo_name_index[norm(n)].add(pid)
    dm_no_theo = []
    for r in dm_rows:
        if r['theographic']:
            continue
        cands = sorted({p for n in [r['dm_name']] + r['dm_names'] for p in theo_name_index.get(norm(n), [])})
        dm_no_theo.append({'dm_id': r['dm_id'], 'dm_name': r['dm_name'], 'dm_names': r['dm_names'],
                           'openbible': [o['id'] for o in r['openbible']],
                           'candidate_theographic': [f'#{p} {by_pid[p]["displayTitle"]} '
                                                     f'(in {dm_by_pid.get(p, "no DM")})' for p in cands],
                           'legacy_geojson_ids': r['legacy_geojson_ids']})

    rootid_conflicts = []
    for r in dm_rows:
        if len(r['theographic']) < 2:
            continue
        roots = {t['placeID']: (t['rootID'] or [t['placeID']])[0] for t in r['theographic']}
        if len(set(roots.values())) > 1:
            rootid_conflicts.append({
                'dm_id': r['dm_id'], 'dm_name': r['dm_name'],
                'theographic': [f"#{t['placeID']} {t['displayTitle']} root=#{roots[t['placeID']]}"
                                f" {by_pid[roots[t['placeID']]]['displayTitle']}" for t in r['theographic']],
                'distinct_roots': len(set(roots.values()))})

    coord_groups = collections.defaultdict(list)
    for r in dm_rows:
        if r['lat'] is not None and r['lon'] is not None:
            coord_groups[(round(float(r['lat']), 5), round(float(r['lon']), 5))].append(r)
    shared = []
    for (lat, lon), grp in sorted(coord_groups.items(), key=lambda kv: -len(kv[1])):
        if len(grp) < 2:
            continue
        obsets = [{o['id'] for o in g['openbible']} for g in grp]
        pids = {t['placeID'] for g in grp for t in g['theographic']}
        if set.intersection(*obsets):
            relation = 'same openbible id'
        elif any(set(t['rootID']) & pids for g in grp for t in g['theographic']):
            relation = 'airtable rootID (borrowed coordinates)'
        else:
            relation = 'coincident only'
        shared.append({'lat': lat, 'lon': lon, 'count': len(grp), 'relation': relation,
                       'dm_entries': [f"{g['dm_id']} {g['dm_name']} {g['legacy_fclasses']}" for g in grp],
                       'openbible_ids': sorted(set().union(*obsets))})

    def proposed_title(r):
        # A Biblia title belongs to the OpenBible place; when several DM entries
        # share that place, it would mislabel the aliases (metheg-ammah -> "Gath").
        for o in r['openbible']:
            if o['biblia_title'] and len(dm_by_ob[o['id']]) == 1:
                return o['biblia_title'], 'biblia'
        return r['dm_name'], 'dm'
    titles = collections.defaultdict(list)
    for r in dm_rows:
        t, src = proposed_title(r)
        r['proposed_title'], r['proposed_title_source'] = t, src
        titles[t].append(r)
    title_collisions = [{'title': t, 'count': len(g),
                         'dm_entries': [f"{x['dm_id']} {x['dm_name']}" for x in g],
                         'dm_titles': [x['dm_title'] for x in g]}
                        for t, g in sorted(titles.items()) if len(g) > 1]

    pleiades_conflicts = [{'dm_id': r['dm_id'], 'dm_name': r['dm_name'],
                           'pleiades': [f'{p} ({",".join(s)})' for p, s in r['pleiades'].items()]}
                          for r in dm_rows if len(r['pleiades']) > 1]

    def suggest_alias(grp):
        classes = [set(g['legacy_fclasses']) for g in grp]
        if all(not (a & b) for i, a in enumerate(classes) for b in classes[i + 1:] if a and b):
            return 'keep separate: different feature classes'
        names = [norm(g['dm_name']) for g in grp]
        sim = min(difflib.SequenceMatcher(None, a, b).ratio() for i, a in enumerate(names) for b in names[i + 1:])
        if sim >= 0.7:
            return 'merge: spelling variants'
        return 'review'
    ob_shared = []
    for o, ds in sorted(dm_by_ob.items()):
        if len(ds) < 2:
            continue
        grp = [by_dm[d] for d in ds]
        rec = ob.get(o, {})
        ob_shared.append({
            'openbible': o,
            'biblia_title': rec.get('linked_data', {}).get('s7f5356', {}).get('name'),
            'count': len(grp),
            'suggestion': suggest_alias(grp),
            'dm_entries': [f"{g['dm_id']} {g['dm_name']} {g['legacy_fclasses']} "
                           f"theo={[t['placeID'] for t in g['theographic']]} "
                           f"verses={sum(t['verseCount'] or 0 for t in g['theographic'])}" for g in grp]})

    geo_ids_mapped = {i for r in rows for i in r['legacy_geojson_ids']}
    geo_unmapped = [f for f in geo if f['@id'] not in geo_ids_mapped]

    # ---- write --------------------------------------------------------------
    json.dump({'generated': date.today().isoformat(),
               'dm_commit': dm['commit'],
               'rows': rows}, open(f'{WORK}/phase-5-crosswalk.json', 'w'), indent=1, ensure_ascii=False)
    write_csv('theographic-orphans', orphans,
              ['placeID', 'displayTitle', 'kjvName', 'featureType', 'verseCount', 'duplicate_of', 'rootID',
               'legacy_geojson_ids', 'suggestions'])
    write_csv('dm-without-theographic', dm_no_theo,
              ['dm_id', 'dm_name', 'dm_names', 'openbible', 'candidate_theographic', 'legacy_geojson_ids'])
    write_csv('rootid-conflicts', rootid_conflicts, ['dm_id', 'dm_name', 'distinct_roots', 'theographic'])
    write_csv('shared-coordinates', shared, ['lat', 'lon', 'count', 'relation', 'dm_entries', 'openbible_ids'])
    write_csv('shared-openbible', ob_shared, ['openbible', 'biblia_title', 'count', 'suggestion', 'dm_entries'])
    write_csv('title-collisions', title_collisions, ['title', 'count', 'dm_entries', 'dm_titles'])
    write_csv('pleiades-conflicts', pleiades_conflicts, ['dm_id', 'dm_name', 'pleiades'])

    # ---- report -------------------------------------------------------------
    multi = [r for r in dm_rows if len(r['theographic']) > 1]
    collapse = [r for r in dm_rows if len(r['legacy_geojson_ids']) > 1]
    pl_src = collections.Counter(s for r in dm_rows for srcs in r['pleiades'].values() for s in srcs)
    with_pl = sum(1 for r in dm_rows if r['pleiades'])
    scores = [o['best_path_score'] for r in dm_rows for o in r['openbible'][:1] if o['best_path_score'] is not None]
    orphan_dm_sugg = sum(1 for o in orphans if any('->' in s and 'rootID' not in s for s in o['suggestions']))
    lines = [
        '# Phase 5 Report: Place Crosswalk', '',
        f'**Generated:** {date.today().isoformat()}  ',
        f'**Digital Manna commit:** `{dm["commit"][:7]}` ({len(entries)} place entries)', '',
        '## Spine', '',
        '| Metric | Count |', '|---|---|',
        f'| DM entries (planned LPF features) | {len(dm_rows)} |',
        f'| Theographic places (json/places.json) | {len(by_pid)} |',
        f'| Theographic places claimed by a DM entry | {len(dm_by_pid)} |',
        f'| DM entries merging 2+ Theographic places | {len(multi)} |',
        f'| Theographic places no DM entry claims | {len(orphans)} ({orphan_dm_sugg} with a suggested DM home) |',
        f'| DM entries with no Theographic place | {len(dm_no_theo)} |',
        f'| Current geojson records | {len(geo)} |',
        f'| Current geojson records mapped to a row | {len(geo) - len(geo_unmapped)} |',
        f'| DM entries absorbing 2+ current geojson records | {len(collapse)} |', '',
        '## Cross-IDs on DM entries', '',
        '| ID | DM entries with it |', '|---|---|',
        f'| OpenBible | {sum(1 for r in dm_rows if r["openbible"])} |',
        f'| Biblia title (via OpenBible) | {sum(1 for r in dm_rows if r["proposed_title_source"] == "biblia")} |',
        f'| Tyndale | {sum(1 for r in dm_rows if r["tyndale"])} |',
        f'| Wikidata (via OpenBible) | {sum(1 for r in dm_rows if r["wikidata"])} |',
        f'| Pleiades (any source) | {with_pl} |',
        f'| Coordinates | {sum(1 for r in dm_rows if r["lat"] is not None)} |',
        f'| OpenBible score >= {CERTAIN_SCORE} (certain) | {sum(1 for s in scores if s >= CERTAIN_SCORE)} of {len(scores)} |', '',
        f'Pleiades ID sources (an ID can have several): geojson {pl_src["geojson"]}, '
        f'openbible {pl_src["openbible"]}, wikidata {pl_src["wikidata"]}.', '',
        '## Review lists (fill in the `decision` column)', '',
        '| File | Rows | What to decide |', '|---|---|---|',
        f'| `phase-5-review-theographic-orphans.csv` | {len(orphans)} | Which DM entry each belongs to, or new feature, or drop (e.g. possessives with 0 verses) |',
        f'| `phase-5-review-dm-without-theographic.csv` | {len(dm_no_theo)} | Link to a Theographic place, or new Theographic record (tribal territories, kingdoms) |',
        f'| `phase-5-review-shared-openbible.csv` | {len(ob_shared)} | Merge into one feature with dated aliases, or keep separate. '
        f'Suggestions: {dict(collections.Counter(x["suggestion"] for x in ob_shared))} |',
        f'| `phase-5-review-rootid-conflicts.csv` | {len(rootid_conflicts)} | Accept the DM merge, or split |',
        f'| `phase-5-review-shared-coordinates.csv` | {len(shared)} | Same place (merge) or just borrowed coordinates (keep separate). '
        f'By relation: {dict(collections.Counter(x["relation"] for x in shared))} |',
        f'| `phase-5-review-title-collisions.csv` | {len(title_collisions)} | Unique title for each |',
        f'| `phase-5-review-pleiades-conflicts.csv` | {len(pleiades_conflicts)} | Which Pleiades ID is right |', '',
        '## Current geojson records not mapped to any row', '',
    ]
    lines += [f'- {f["properties"]["title"]}: `{f["@id"]}`' for f in geo_unmapped] or ['- none']
    lines += ['', '## DM entries absorbing 2+ current geojson records', '']
    lines += [f'- {r["dm_id"]} {r["dm_name"]}: ' + ', '.join(f'`{i.rsplit("/", 1)[1]}`' for i in r['legacy_geojson_ids'])
              for r in collapse] or ['- none']
    open(f'{WORK}/phase-5-report.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
