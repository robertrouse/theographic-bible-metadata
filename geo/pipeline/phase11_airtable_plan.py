"""Phase 11: plan the Airtable `places` changes that mirror one-place-many-names.

The plan only adds; it never overwrites an existing value or deletes a record:
  1. New field `canonicalPlace` (link to places, single record).
  2. On every alias record (a Theographic place merged into a feature whose
     canonical record is another place), set canonicalPlace to that record.
     The canonical record is the feature's record named like the feature, then
     the one with the most verses; decisions.json "airtable_canonical"
     (dm_id -> placeID) overrides.
  3. New records for places Digital Manna has and Theographic lacks
     (decisions.json "dm_needs_theographic_record"), with the next placeIDs,
     linked to the verses Digital Manna lists for them.

Reads:  geo/working/phase-8-index.json, geo/bible-places.geojson, geo/decisions.json,
        geo/working/dm-places-cache.json, json/places.json (the pre-change snapshot),
        json/verses.json
Writes: geo/airtable/phase-11-plan.json   machine-readable plan, applied in batches
        geo/airtable/phase-11-plan.md     the same, for review

Usage: python3 geo/pipeline/phase11_airtable_plan.py
"""
import json
import re
from datetime import date

BASE, TABLE = 'app5UK4s70d5PwupX', 'tblrUnh4Q79pmELgB'
SNAPSHOT_COMMIT = 'bc4c1f1'
FEATURE_TYPE = {'L': 'Region', 'P': 'City', 'T': 'Mountain', 'H': 'Water', 'S': 'Landmark', 'R': 'Path'}


def norm(name):
    return re.sub(r'[^a-z]', '', name.lower())


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def main():
    index = json.load(open('geo/working/phase-8-index.json'))
    feats = {f['@id']: f for f in json.load(open('geo/bible-places.geojson'))['features']}
    dec = json.load(open('geo/decisions.json'))
    dm = {e['id']: e for e in json.load(open('geo/working/dm-places-cache.json'))['entries']}
    places = {p['fields']['placeID']: p for p in json.load(open('json/places.json'))}
    verse_rec = {int(v['fields']['verseID']): v['id'] for v in json.load(open('json/verses.json'))}

    updates = []
    for x in index:
        pids = [p for p in x['placeIDs'] if p in places]
        if len(pids) < 2:
            continue
        title = norm(re.sub(r'\([^)]*\)', '', x['title']))
        pinned = dec.get('airtable_canonical', {}).get(x['dm_ids'][0] if x['dm_ids'] else '')
        canon = pinned if pinned in pids else max(pids, key=lambda p: (
            title in {norm(re.sub(r'\([^)]*\)', '', places[p]['fields'].get(k) or ''))
                      for k in ('displayTitle', 'kjvName', 'esvName')},
            places[p]['fields'].get('verseCount') or 0,
            -p))
        crec = places[canon]
        for p in pids:
            if p == canon:
                continue
            rec = places[p]
            updates.append({
                'id': rec['id'], 'placeID': p, 'displayTitle': rec['fields'].get('displayTitle'),
                'feature': x['title'], 'field': 'canonicalPlace',
                'before': rec['fields'].get('canonicalPlace'),          # field does not exist yet: None
                'after': [crec['id']],
                'canonical_placeID': canon, 'canonical_title': crec['fields'].get('displayTitle')})

    by_dm = {x['dm_ids'][0]: x for x in index if x['dm_ids']}
    next_id = max(places) + 1
    creates = []
    for d in dec['dm_needs_theographic_record']:
        x = by_dm[d]
        f = feats[x['@id']]
        coords = f['geometry'].get('coordinates')
        fields = {
            'placeID': next_id,
            'placeLookup': f'{slugify(dm[d]["name"])}_{next_id}',
            'displayTitle': f['properties']['title'],
            'kjvName': dm[d]['name'],
            'status': 'wip',
            'featureType': FEATURE_TYPE[f['properties']['fclasses'][0]],
            'comment': f'Added from Digital Manna {d} (LPF sync {date.today().isoformat()})',
        }
        if coords:
            fields['openBibleLong'], fields['openBibleLat'] = str(coords[0]), str(coords[1])
        verses = [verse_rec[v] for v in dm[d].get('verses') or [] if v in verse_rec]
        if verses:
            fields['verses'] = verses
        creates.append({'dm_id': d, 'feature': f['properties']['title'], 'fields': fields})
        next_id += 1

    plan = {
        'base': BASE, 'table': TABLE,
        'snapshot': {'commit': SNAPSHOT_COMMIT, 'file': 'json/places.json', 'tag': 'airtable-places-backup-2026-10-13'},
        'create_fields': [{'name': 'canonicalPlace', 'type': 'multipleRecordLinks',
                           'description': 'The record for the same real place when this record is one of its '
                                          'other names (Linked Places sync). Empty on canonical records.',
                           # the API rejects prefersSingleRecordLink on create; set it in the UI if wanted
                           'options': {'linkedTableId': TABLE}}],
        'update_records': updates,
        'update_batches': [[{'id': u['id'], 'fields': {'canonicalPlace': u['after']}} for u in updates[i:i + 10]]
                           for i in range(0, len(updates), 10)],
        'create_records': creates,
    }
    json.dump(plan, open('geo/airtable/phase-11-plan.json', 'w'), indent=1, ensure_ascii=False)

    lines = [
        '# Phase 11 Plan: Airtable `places`', '',
        f'Snapshot before any change: `json/places.json` at commit `{SNAPSHOT_COMMIT}` '
        f'(tag `{plan["snapshot"]["tag"]}`); no record was modified after that export.', '',
        '## 1. New field', '',
        '`canonicalPlace`: link to another `places` record. Set only on alias records, always to one record.', '',
        f'## 2. Set canonicalPlace on {len(updates)} alias records '
        f'({len({u["canonical_placeID"] for u in updates})} canonical places)', '',
        '| Alias record | → Canonical record | Feature |', '|---|---|---|',
    ] + [f'| #{u["placeID"]} {u["displayTitle"]} | #{u["canonical_placeID"]} {u["canonical_title"]} | {u["feature"]} |'
         for u in sorted(updates, key=lambda u: (u['feature'], u['placeID']))] + [
        '', f'## 3. Create {len(creates)} records', '',
        '| placeID | placeLookup | displayTitle | featureType | coordinates | verses | from |',
        '|---|---|---|---|---|---|---|',
    ] + [f'| {c["fields"]["placeID"]} | {c["fields"]["placeLookup"]} | {c["fields"]["displayTitle"]} | '
         f'{c["fields"]["featureType"]} | {c["fields"].get("openBibleLong", "")}, {c["fields"].get("openBibleLat", "")} | '
         f'{len(c["fields"].get("verses", []))} | {c["dm_id"]} |'
         for c in creates] + [
        '', '## Not changed', '',
        '- No existing field value is overwritten and no record is deleted.',
        '- Records excluded from the LPF file (possessives, "There", Azazel, people groups, Temple rooms) stay as they are.',
        '- Coordinates, names and verse links of existing records are not touched.',
    ]
    open('geo/airtable/phase-11-plan.md', 'w').write('\n'.join(lines) + '\n')
    print(f'{len(updates)} alias updates, {len(creates)} new records')


if __name__ == '__main__':
    main()
