"""Phase 11 rollback: turn the Airtable change log into the reverse operations.

Every write made while applying geo/airtable/phase-11-plan.json is recorded in
geo/airtable/phase-11-applied.json:
  {"fields_created":  [{"id", "name"}],
   "records_updated": [{"id", "field", "before", "after"}],
   "records_created": [{"id", "placeID", "placeLookup"}]}

This script writes geo/airtable/phase-11-rollback.json:
  update_batches   records to set back to their "before" value, 10 per batch
                   (the Airtable API's limit); empty becomes null, which clears the field
  delete_records   records the sync created, 10 per batch
  manual           steps the API cannot do: deleting a field must be done in
                   the Airtable UI (field menu > Delete field)

Apply the batches with the Airtable update/delete records calls, then follow
the manual steps. As a last resort, the full pre-change table is json/places.json
at git tag airtable-places-backup-2026-10-13 (commit bc4c1f1).

Usage: python3 geo/pipeline/phase11_airtable_rollback.py [--log <applied.json> --out <rollback.json>]
"""
import argparse
import json


def batches(items, n=10):
    return [items[i:i + n] for i in range(0, len(items), n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--log', default='geo/airtable/phase-11-applied.json')
    ap.add_argument('--out', default='geo/airtable/phase-11-rollback.json')
    args = ap.parse_args()
    log = json.load(open(args.log))
    restore = {}
    for u in log.get('records_updated', []):
        # the first logged "before" for a field is the original value
        # an empty "before" is restored as null, which clears any field type
        restore.setdefault(u['id'], {}).setdefault(u['field'], u['before'] if u['before'] not in ([], '') else None)
    updates = [{'id': rid, 'fields': fields} for rid, fields in restore.items()]
    created = [r['id'] for r in log.get('records_created', [])]
    out = {
        'base': log['base'], 'table': log['table'],
        'update_batches': batches(updates),
        'delete_records': batches(created),
        # Airtable adds the reverse side of a self-link ("From field: <name>") on its own
        'manual': [f'Delete fields "{f["name"]}" ({f["id"]}) and its reverse "From field: {f["name"]}" '
                   f'(or whatever it was renamed to) in the Airtable UI' for f in log.get('fields_created', [])],
        'snapshot': 'json/places.json at git tag airtable-places-backup-2026-10-13',
    }
    json.dump(out, open(args.out, 'w'), indent=1)
    print(f'{len(updates)} records to restore in {len(out["update_batches"])} batches; '
          f'{len(created)} records to delete; {len(out["manual"])} manual steps')


if __name__ == '__main__':
    main()
