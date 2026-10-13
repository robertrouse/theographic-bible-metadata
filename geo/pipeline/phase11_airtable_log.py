"""Phase 11: record Airtable writes in geo/airtable/phase-11-applied.json as they succeed.

  init                      start an empty log for the plan's base and table
  field <fieldId> <name>    a field was created
  batch <n>                 update batch n of the plan was applied
  created <n> <recordId>    create_records[n] of the plan was created as recordId

The rollback script reads this log. Usage: python3 geo/pipeline/phase11_airtable_log.py <command> ...
"""
import json
import sys
from datetime import datetime, timezone

PLAN = 'geo/airtable/phase-11-plan.json'
LOG = 'geo/airtable/phase-11-applied.json'


def main():
    plan = json.load(open(PLAN))
    cmd, args = sys.argv[1], sys.argv[2:]
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    if cmd == 'init':
        log = {'base': plan['base'], 'table': plan['table'], 'started': now,
               'fields_created': [], 'records_updated': [], 'records_created': []}
    else:
        log = json.load(open(LOG))
    if cmd == 'field':
        log['fields_created'].append({'id': args[0], 'name': args[1], 'at': now})
    elif cmd == 'batch':
        for r in plan['update_batches'][int(args[0])]:
            for field, value in r['fields'].items():
                log['records_updated'].append({'id': r['id'], 'field': field, 'before': None,
                                               'after': value, 'at': now})
    elif cmd == 'created':
        c = plan['create_records'][int(args[0])]
        log['records_created'].append({'id': args[1], 'placeID': c['fields']['placeID'],
                                       'placeLookup': c['fields']['placeLookup'], 'dm_id': c['dm_id'], 'at': now})
    json.dump(log, open(LOG, 'w'), indent=1)
    print(f'{cmd}: {len(log["fields_created"])} fields, {len(log["records_updated"])} updates, '
          f'{len(log["records_created"])} creates logged')


if __name__ == '__main__':
    main()
