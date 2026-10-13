"""Phase 11: apply geo/airtable/phase-11-plan.json to Airtable, or roll it back.

Uses the Airtable REST API with a personal access token from the environment
(never stored in the repo). The token needs data.records:write, plus
schema.bases:write to create the canonicalPlace field; without that scope,
add the field in the Airtable UI first (Link to another record -> places,
single record) and the script will find it.

Every write is logged to geo/airtable/phase-11-applied.json as soon as it
succeeds, in the format phase11_airtable_rollback.py reads.

  AIRTABLE_TOKEN=pat... python3 geo/pipeline/phase11_airtable_apply.py --dry-run
  AIRTABLE_TOKEN=pat... python3 geo/pipeline/phase11_airtable_apply.py
  AIRTABLE_TOKEN=pat... python3 geo/pipeline/phase11_airtable_apply.py --rollback
  ... --plan geo/airtable/phase-11b-plan.json   (any of the above, for another plan)

Re-running the apply step skips writes the log already records, so an
interrupted run can be resumed.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

PLAN = 'geo/airtable/phase-11-plan.json'   # default; --plan picks another
LOG = ROLLBACK = None                      # set from the plan name: <plan>-applied.json, <plan>-rollback.json
API = 'https://api.airtable.com/v0'
PAUSE = 0.25          # Airtable allows 5 requests per second per base


def call(method, url, token, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                time.sleep(PAUSE)
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(30)
                continue
            raise SystemExit(f'{method} {url} -> {e.code}: {e.read().decode()[:300]}')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def save(log):
    json.dump(log, open(LOG, 'w'), indent=1)


def apply(plan, token, dry):
    base, table = plan['base'], plan['table']
    log = json.load(open(LOG)) if os.path.exists(LOG) else \
        {'base': base, 'table': table, 'started': now(), 'fields_created': [], 'records_updated': [], 'records_created': []}
    done_updates = {(u['id'], u['field']) for u in log['records_updated']}
    before = {(u['id'], u['field']): u.get('before') for u in plan['update_records'] if 'field' in u}
    done_creates = {c['placeID'] for c in log['records_created']}
    print(f'Plan: {len(plan["create_fields"])} field, {len(plan["update_records"])} updates, '
          f'{len(plan["create_records"])} new records. Already logged: {len(done_updates)} updates, '
          f'{len(done_creates)} creates.')
    if dry:
        return

    # 1. field
    schema = call('GET', f'{API}/meta/bases/{base}/tables', token)
    fields = {f['name']: f['id'] for t in schema['tables'] if t['id'] == table for f in t['fields']}
    for f in plan['create_fields']:
        if f['name'] in fields:
            print(f'Field {f["name"]} exists ({fields[f["name"]]})')
            continue
        res = call('POST', f'{API}/meta/bases/{base}/tables/{table}/fields', token, f)
        log['fields_created'].append({'id': res['id'], 'name': f['name'], 'at': now()})
        save(log)
        print(f'Created field {f["name"]} ({res["id"]})')

    # 2. alias links
    for n, batch in enumerate(plan['update_batches']):
        todo = [r for r in batch if any((r['id'], k) not in done_updates for k in r['fields'])]
        if not todo:
            continue
        call('PATCH', f'{API}/{base}/{table}', token, {'records': todo})
        for r in todo:
            for k, v in r['fields'].items():
                log['records_updated'].append({'id': r['id'], 'field': k, 'before': before.get((r['id'], k)),
                                               'after': v, 'at': now()})
        save(log)
        print(f'Update batch {n + 1}/{len(plan["update_batches"])}: {len(todo)} records')

    # 3. new records
    todo = [c for c in plan['create_records'] if c['fields']['placeID'] not in done_creates]
    for i in range(0, len(todo), 10):
        chunk = todo[i:i + 10]
        res = call('POST', f'{API}/{base}/{table}', token, {'records': [{'fields': c['fields']} for c in chunk]})
        for c, rec in zip(chunk, res['records']):
            log['records_created'].append({'id': rec['id'], 'placeID': c['fields']['placeID'],
                                           'placeLookup': c['fields']['placeLookup'], 'dm_id': c['dm_id'], 'at': now()})
        save(log)
        print(f'Created {len(chunk)} records')
    log['finished'] = now()
    save(log)
    print('Done. Change log:', LOG)


def rollback(token):
    subprocess.run([sys.executable, 'geo/pipeline/phase11_airtable_rollback.py', '--log', LOG, '--out', ROLLBACK],
                   check=True)
    rb = json.load(open(ROLLBACK))
    base, table = rb['base'], rb['table']
    for batch in rb['update_batches']:
        call('PATCH', f'{API}/{base}/{table}', token, {'records': batch})
    print(f'Restored {sum(len(b) for b in rb["update_batches"])} records')
    for batch in rb['delete_records']:
        q = '&'.join(f'records[]={r}' for r in batch)
        call('DELETE', f'{API}/{base}/{table}?{q}', token)
    print(f'Deleted {sum(len(b) for b in rb["delete_records"])} created records')
    for step in rb['manual']:
        print('Manual step:', step)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--rollback', action='store_true')
    ap.add_argument('--plan', default=PLAN)
    args = ap.parse_args()
    global LOG, ROLLBACK
    stem = args.plan[:-len('-plan.json')] if args.plan.endswith('-plan.json') else args.plan.rsplit('.', 1)[0]
    LOG, ROLLBACK = f'{stem}-applied.json', f'{stem}-rollback.json'
    token = os.environ.get('AIRTABLE_TOKEN')
    if not token and not args.dry_run:
        raise SystemExit('Set AIRTABLE_TOKEN to a personal access token for the base.')
    if args.rollback:
        rollback(token)
    else:
        apply(json.load(open(args.plan)), token, args.dry_run)


if __name__ == '__main__':
    main()
