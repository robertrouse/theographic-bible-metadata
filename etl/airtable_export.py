"""Export every table of the Theographic Airtable base to json/<table>.json.

Same output as scripts/airtable_etl.ipynb: a list of {id, createdTime, fields}
records per table, 4-space indented, ASCII-escaped. Read-only: it only GETs
from the Airtable API. The token comes from the environment, never the code.

Usage (from the repo root):
  AIRTABLE_TOKEN=pat... python3 etl/airtable_export.py [table ...]

With no table names, every table in the base is exported.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE_ID = 'app5UK4s70d5PwupX'
API = 'https://api.airtable.com/v0'
PAUSE = 0.22            # Airtable allows 5 requests per second per base


def get(url, token):
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                time.sleep(PAUSE)
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(30)
                continue
            raise SystemExit(f'GET {url} -> {e.code}: {e.read().decode()[:300]}')


def main():
    token = os.environ.get('AIRTABLE_TOKEN')
    if not token:
        raise SystemExit('Set AIRTABLE_TOKEN to a personal access token for the base.')
    wanted = set(sys.argv[1:])
    tables = get(f'{API}/meta/bases/{BASE_ID}/tables', token)['tables']
    for t in tables:
        if wanted and t['name'] not in wanted:
            continue
        records, offset = [], None
        while True:
            q = {'pageSize': 100, **({'offset': offset} if offset else {})}
            page = get(f'{API}/{BASE_ID}/{t["id"]}?{urllib.parse.urlencode(q)}', token)
            records += page['records']
            offset = page.get('offset')
            if not offset:
                break
        safe = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in t['name'])
        with open(f'json/{safe}.json', 'w') as f:
            json.dump(records, f, indent=4)
        print(f'{t["name"]}: {len(records)} records -> json/{safe}.json')


if __name__ == '__main__':
    main()
