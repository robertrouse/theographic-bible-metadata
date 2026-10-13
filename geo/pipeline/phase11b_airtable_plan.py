"""Phase 11b: prepare retiring the Airtable rootID and duplicate_of fields.

  1. Archive every rootID and duplicate_of value to
     geo/airtable/archive-rootID-duplicate_of-2026-10-13.csv (committed), so
     nothing is lost when the fields are deleted.
  2. Records with duplicate_of but no canonicalPlace get canonicalPlace = the
     canonical record of what they duplicate (duplicate_of meant "another form
     of that place's name"; canonicalPlace now carries that) -- unless the two
     records are different places in bible-places.geojson (decisions.json kept
     them apart), in which case the old link is only archived.
  3. Records for the two Israel kingdoms, linked to their anchor verses
     (decisions.json "verses"), and the Judah (Southern) record retitled
     "Kingdom of Judah", matching the kingdoms in bible-places.geojson.
  4. After applying: delete rootID and duplicate_of in the Airtable UI (the API
     cannot delete fields).

Reads:  json/places.json (snapshot; rootID and duplicate_of are unchanged since),
        geo/airtable/phase-11-plan.json + phase-11-applied.json (live canonicalPlace),
        json/verses.json, geo/decisions.json
Writes: geo/airtable/phase-11b-plan.json / .md, the archive CSV

Usage: python3 geo/pipeline/phase11b_airtable_plan.py
"""
import csv
import json
import re
from datetime import date

ARCHIVE = 'geo/airtable/archive-rootID-duplicate_of-2026-10-13.csv'


def main():
    snap = json.load(open('json/places.json'))
    rec = {p['id']: p['fields'] for p in snap}
    p11 = json.load(open('geo/airtable/phase-11-plan.json'))
    applied = json.load(open('geo/airtable/phase-11-applied.json'))
    dec = json.load(open('geo/decisions.json'))
    verse_rec = {v['fields']['osisRef']: v['id'] for v in json.load(open('json/verses.json'))}
    feature_of = {p: x['@id'] for x in json.load(open('geo/working/phase-8-index.json')) for p in x['placeIDs']}

    canonical = {u['id']: u['after'][0] for u in applied['records_updated'] if u['field'] == 'canonicalPlace'}
    created = {c['dm_id']: c for c in applied['records_created']}

    # 1. archive
    rows = []
    for rid, f in rec.items():
        for field in ('rootID', 'duplicate_of'):
            for target in f.get(field) or []:
                t = rec.get(target, {})
                rows.append({'record': rid, 'placeID': f['placeID'], 'displayTitle': f.get('displayTitle'),
                             'field': field, 'linked_record': target, 'linked_placeID': t.get('placeID'),
                             'linked_displayTitle': t.get('displayTitle')})
    with open(ARCHIVE, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r['field'], r['placeID'])))

    # 2. duplicate_of -> canonicalPlace
    updates, kept_apart = [], []
    for rid, f in rec.items():
        dup = (f.get('duplicate_of') or [None])[0]
        if not dup or rid in canonical:
            continue
        target = canonical.get(dup, dup)          # follow to the place's canonical record
        if target == rid:
            continue
        mine, theirs = feature_of.get(f['placeID']), feature_of.get(rec[target]['placeID'])
        if mine and theirs and mine != theirs:
            kept_apart.append(f'#{f["placeID"]} {f.get("displayTitle")} (duplicate_of #{rec[dup]["placeID"]} '
                              f'{rec[dup].get("displayTitle")})')
            continue
        updates.append({'id': rid, 'placeID': f['placeID'], 'displayTitle': f.get('displayTitle'),
                        'field': 'canonicalPlace', 'before': None, 'after': [target],
                        'canonical_placeID': rec[target]['placeID'], 'canonical_title': rec[target].get('displayTitle')})

    # 3. kingdoms
    judah = created.get('places-1257')
    if judah:
        updates.append({'id': judah['id'], 'placeID': judah['placeID'], 'displayTitle': 'Judah (Southern)',
                        'field': 'displayTitle', 'before': 'Judah (Southern)', 'after': 'Kingdom of Judah'})
    next_id = max(max(f['placeID'] for f in rec.values()), max(c['placeID'] for c in applied['records_created'])) + 1
    creates = []
    for pol in dec['polities']:
        if pol['dm_id'] in created:
            continue
        refs = dec.get('verses', {}).get(pol['dm_id'], [])
        slug = re.sub(r'[^a-z0-9]+', '-', pol['label'].lower()).strip('-')
        creates.append({'dm_id': pol['dm_id'], 'feature': pol['label'], 'fields': {
            'placeID': next_id, 'placeLookup': f'{slug}_{next_id}', 'displayTitle': pol['label'],
            'kjvName': 'Israel', 'status': 'wip', 'featureType': 'Region',
            'comment': f'Kingdom, {pol["start"]} to {pol["end"]} ({pol["start_ref"]} to {pol["end_ref"]}); '
                       f'added from Digital Manna {pol["dm_id"]} (LPF sync {date.today().isoformat()})',
            'verses': [verse_rec[r] for r in refs if r in verse_rec]}})
        next_id += 1

    plan = {'base': p11['base'], 'table': p11['table'], 'create_fields': [],
            'update_records': updates,
            'update_batches': [[{'id': u['id'], 'fields': {u['field']: u['after']}} for u in updates[i:i + 10]]
                               for i in range(0, len(updates), 10)],
            'create_records': creates,
            'manual_after': ['Delete the rootID field in the Airtable UI',
                             'Delete the duplicate_of field in the Airtable UI'],
            'archive': ARCHIVE}
    json.dump(plan, open('geo/airtable/phase-11b-plan.json', 'w'), indent=1, ensure_ascii=False)

    n_root = sum(1 for r in rows if r['field'] == 'rootID')
    lines = ['# Phase 11b Plan: retire rootID and duplicate_of', '',
             f'Archive: `{ARCHIVE}`: {n_root} rootID links on '
             f'{len({r["record"] for r in rows if r["field"] == "rootID"})} records, '
             f'{len(rows) - n_root} duplicate_of links.', '',
             f'## 1. canonicalPlace from duplicate_of ({sum(1 for u in updates if u["field"] == "canonicalPlace")} records)', '',
             '| Record | → canonicalPlace |', '|---|---|'] + \
            [f'| #{u["placeID"]} {u["displayTitle"]} | #{u["canonical_placeID"]} {u["canonical_title"]} |'
             for u in updates if u['field'] == 'canonicalPlace'] + \
            ['', f'Not moved, because they are different places in bible-places.geojson '
                 f'({len(kept_apart)}; archived only): ' + '; '.join(kept_apart)] + \
            ['', '## 2. Kingdoms', ''] + \
            [f'- Retitle #{u["placeID"]} "{u["before"]}" → "{u["after"]}"' for u in updates if u['field'] == 'displayTitle'] + \
            [f'- Create #{c["fields"]["placeID"]} {c["fields"]["displayTitle"]} '
             f'({len(c["fields"]["verses"])} verse links)' for c in creates] + \
            ['', '## 3. Then, in the Airtable UI', '', '- Delete `rootID`', '- Delete `duplicate_of`']
    open('geo/airtable/phase-11b-plan.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
