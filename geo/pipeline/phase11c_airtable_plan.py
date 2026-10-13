"""Phase 11c: fill the Airtable partOf / near / startYear / endYear fields.

Mirrors the relations in geo/bible-places.geojson onto the Airtable `places`
table. Each feature is represented by its canonical record (aliases reach it
through canonicalPlace); a feature's "part of" parents go into partOf and its
"near" places into near. Kingdom records get startYear / endYear, which date
every partOf link pointing at them.

The fields are new and empty, so every "before" is empty and the rollback
clears them again.

Reads:  geo/bible-places.geojson, geo/working/phase-8-index.json, geo/decisions.json,
        json/places.json, geo/airtable/phase-11-applied.json, phase-11b-applied.json
Writes: geo/airtable/phase-11c-plan.json / .md

Usage: python3 geo/pipeline/phase11c_airtable_plan.py
"""
import collections
import json

PART_OF, NEAR = 'gvp:broaderPartitive', 'gvp:tgn3000_related_to'


def main():
    feats = {f['@id']: f for f in json.load(open('geo/bible-places.geojson'))['features']}
    index = {x['@id']: x for x in json.load(open('geo/working/phase-8-index.json'))}
    dec = json.load(open('geo/decisions.json'))
    snap = {p['fields']['placeID']: p for p in json.load(open('json/places.json'))}
    logs = [json.load(open(f'geo/airtable/{n}-applied.json')) for n in ('phase-11', 'phase-11b')]
    aliases = {u['id'] for log in logs for u in log['records_updated'] if u['field'] == 'canonicalPlace'}
    created = {c['dm_id']: c for log in logs for c in log['records_created']}
    titles = {rid: p['fields'].get('displayTitle') for p in snap.values() for rid in [p['id']]}
    titles.update({c['id']: feats[i]['properties']['title'] for i in feats for d in index[i]['dm_ids']
                   for c in [created.get(d)] if c})

    def record(fid):
        """The Airtable record that stands for a feature."""
        x = index[fid]
        recs = [snap[p]['id'] for p in x['placeIDs'] if p in snap]
        canon = [r for r in recs if r not in aliases]
        if canon:
            return canon[0]
        if recs:
            return recs[0]
        return next((created[d]['id'] for d in x['dm_ids'] if d in created), None)

    links = collections.defaultdict(lambda: {'partOf': [], 'near': []})
    missing = []
    for fid, f in feats.items():
        for r in f.get('relations') or []:
            child, parent = record(fid), record(r['relationTo'])
            if not child or not parent:
                missing.append(f'{f["properties"]["title"]} -> {feats[r["relationTo"]]["properties"]["title"]}')
                continue
            field = 'partOf' if r['relationType'] == PART_OF else 'near'
            if parent not in links[child][field]:
                links[child][field].append(parent)

    updates = []
    for rid, fields in links.items():
        for field, value in fields.items():
            if value:
                updates.append({'id': rid, 'displayTitle': titles.get(rid), 'field': field, 'before': [],
                                'after': value, 'after_titles': [titles.get(v) for v in value]})
    for pol in dec['polities']:
        fid = next((i for i, x in index.items() if pol['dm_id'] in x['dm_ids']), None)
        rid = record(fid) if fid else None
        for field, year in (('startYear', pol['start']), ('endYear', pol['end'])):
            updates.append({'id': rid, 'displayTitle': pol['label'], 'field': field, 'before': None, 'after': year})

    by_rec = collections.defaultdict(dict)
    for u in updates:
        by_rec[u['id']][u['field']] = u['after']
    recs = list(by_rec.items())
    plan = {'base': logs[0]['base'], 'table': logs[0]['table'], 'create_fields': [], 'create_records': [],
            'update_records': updates,
            'update_batches': [[{'id': rid, 'fields': f} for rid, f in recs[i:i + 10]] for i in range(0, len(recs), 10)]}
    json.dump(plan, open('geo/airtable/phase-11c-plan.json', 'w'), indent=1, ensure_ascii=False)

    n = collections.Counter(u['field'] for u in updates)
    links_n = collections.Counter()
    for u in updates:
        if u['field'] in ('partOf', 'near'):
            links_n[u['field']] += len(u['after'])
    lines = ['# Phase 11c Plan: partOf / near / startYear / endYear', '',
             f'{len(recs)} records updated in {len(plan["update_batches"])} batches: '
             f'partOf on {n["partOf"]} records ({links_n["partOf"]} links), '
             f'near on {n["near"]} records ({links_n["near"]} links), years on {n["startYear"]} kingdoms.', '',
             'Relations without an Airtable record on either side: ' + ('; '.join(missing) or 'none'), '',
             '## Kingdoms', ''] + \
            [f'- {u["displayTitle"]}: {u["field"]} = {u["after"]}' for u in updates if u['field'] in ('startYear', 'endYear')] + \
            ['', '## partOf / near', '', '| Record | Field | Links to |', '|---|---|---|'] + \
            [f'| {u["displayTitle"]} | {u["field"]} | {", ".join(map(str, u["after_titles"]))} |'
             for u in sorted(updates, key=lambda u: (u['displayTitle'] or '', u['field'])) if u['field'] in ('partOf', 'near')]
    open('geo/airtable/phase-11c-plan.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:8]))


if __name__ == '__main__':
    main()
