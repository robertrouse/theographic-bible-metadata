"""Export the Theographic Airtable base to json/ and CSV/.

Usage (from the repository root):
    AIRTABLE_TOKEN=pat... python3 etl/export_airtable.py
    AIRTABLE_TOKEN=pat... python3 etl/export_airtable.py --out /tmp/export   # write somewhere else

The token needs the data.records:read and schema.bases:read scopes on the base.

Output format
- json/<table>.json: a list of {id, createdTime, fields} records, fields in Airtable schema order, indent=4.
- CSV/<Table>.csv: UTF-8 with BOM, LF line endings. Cells are formatted the way Airtable's own CSV
  download formats them. Linked records are written as the linked records' primary field values
  joined by "," (a value containing a comma or quote is wrapped in quotes), and lookups and
  rollups that return lists are joined by ", ". Columns keep the order of the existing CSV file. Columns whose field no longer
  exists are dropped, and new Airtable fields are reported but not added (add them to the CSV
  header by hand to start exporting them).
- Records in both formats follow each table's "Grid view" order, so diffs between exports stay small.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_ID = 'app5UK4s70d5PwupX'
VIEW = 'Grid view'
CSV_NAMES = {
    'books': 'Books', 'chapters': 'Chapters', 'verses': 'Verses', 'places': 'Places',
    'people': 'People', 'peopleGroups': 'PeopleGroups', 'events': 'Events', 'easton': 'Easton',
}
LINK_TYPES = {'multipleRecordLinks'}
LIST_TYPES = {'multipleLookupValues', 'rollup'}

TOKEN = os.environ.get('AIRTABLE_TOKEN') or sys.exit('Set AIRTABLE_TOKEN.')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else ROOT


def get(path, params=None):
    url = 'https://api.airtable.com/v0/' + path
    if params:
        url += '?' + urllib.parse.urlencode(params, doseq=True)
    request = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + TOKEN})
    for _ in range(6):
        try:
            return json.loads(urllib.request.urlopen(request, timeout=120).read())
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limited: Airtable asks for a 30 s pause
                time.sleep(30)
                continue
            raise
    raise RuntimeError('Airtable kept rate-limiting the export')


def quote(value):
    """Quote one linked-record name the way Airtable's CSV download does."""
    if ',' in value or '"' in value:
        return '"' + value.replace('"', '""') + '"'
    return value


def fetch(table_id, **params):
    records, offset = [], None
    while True:
        page = {'pageSize': 100, 'view': VIEW, **params}
        if offset:
            page['offset'] = offset
        data = get(f'{BASE_ID}/{table_id}', page)
        records += data['records']
        offset = data.get('offset')
        time.sleep(0.21)  # stay under 5 requests/second
        if not offset:
            return records


def main():
    tables = get(f'meta/bases/{BASE_ID}/tables')['tables']
    raw, text = {}, {}
    for t in tables:
        raw[t['id']] = fetch(t['id'])
        text[t['id']] = {r['id']: r['fields'] for r in fetch(
            t['id'], cellFormat='string', timeZone='America/Chicago', userLocale='en-us')}
        print(f"fetched {t['name']}: {len(raw[t['id']])}", flush=True)

    # Primary field value of every record, for rendering linked records in CSV.
    primary = {}
    for t in tables:
        name = next(f['name'] for f in t['fields'] if f['id'] == t['primaryFieldId'])
        for r in raw[t['id']]:
            primary[r['id']] = text[t['id']][r['id']].get(name, '')

    os.makedirs(os.path.join(OUT, 'json'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'CSV'), exist_ok=True)
    for t in tables:
        fields = {f['name']: f for f in t['fields']}
        order = list(fields)
        records = raw[t['id']]

        for r in records:
            r['fields'] = {k: r['fields'][k] for k in order if k in r['fields']}
        with open(os.path.join(OUT, 'json', t['name'] + '.json'), 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=4)

        csv_name = CSV_NAMES.get(t['name'], t['name'][:1].upper() + t['name'][1:])
        csv_path = os.path.join(OUT, 'CSV', csv_name + '.csv')
        existing = os.path.join(ROOT, 'CSV', csv_name + '.csv')
        if os.path.exists(existing):
            with open(existing, encoding='utf-8-sig', newline='') as f:
                header = next(csv.reader(f))
            dropped = [h for h in header if h not in fields]
            header = [h for h in header if h in fields]
            unexported = [k for k in order if k not in header]
            if dropped:
                print(f'  {csv_name}.csv: dropped columns no longer in Airtable: {dropped}')
            if unexported:
                print(f'  {csv_name}.csv: Airtable fields not in CSV (not exported): {unexported}')
        else:
            header = order

        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow(header)
            for r in records:
                cells = text[t['id']][r['id']]
                row = []
                for h in header:
                    value = r['fields'].get(h)
                    if fields[h]['type'] in LINK_TYPES:
                        row.append(','.join(quote(primary.get(i, '')) for i in value or []))
                    elif (fields[h]['type'] in LIST_TYPES and isinstance(value, list)
                          and all(isinstance(v, str) for v in value)):
                        row.append(', '.join(value))
                    else:
                        row.append(cells.get(h, ''))
                w.writerow(row)
        print(f"wrote {t['name']}: json + {csv_name}.csv ({len(records)} records)")


if __name__ == '__main__':
    main()
