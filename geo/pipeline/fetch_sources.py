"""Fetch and cache the external sources used by the LPF pipeline.

Writes to geo/working/ (never to source data):
  dm-places-cache.json        Digital Manna place entries (subset of fields)
  openbible-ancient.jsonl     OpenBible Bible-Geocoding-Data ancient places
  wikidata-pleiades.json      Wikidata QID -> Pleiades ID (P1584)

Digital Manna lives in the private repo digitalmanna/stewards_data and is
read with the authenticated `gh` CLI. Only the fields the pipeline needs are
cached; editorial fields such as admin_notes are dropped.

Usage (from repo root):
  python3 geo/pipeline/fetch_sources.py [--dm-dir DIR] [--refresh]

--dm-dir reads already-downloaded places-####.json files instead of calling gh.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

WORK = 'geo/working'
DM_REPO = 'digitalmanna/stewards_data'
DM_BRANCH = 'preview'
DM_PATH = 'encyclopedia/places/_entries'
OB_URL = 'https://raw.githubusercontent.com/openbibleinfo/Bible-Geocoding-Data/main/data/ancient.jsonl'
WD_SPARQL = 'https://query.wikidata.org/sparql'
DM_KEEP = ['id', 'slug', 'name', 'names', 'title', 'location', 'ids']


def gh(path, raw=False):
    cmd = ['gh', 'api', path]
    if raw:
        cmd += ['-H', 'Accept: application/vnd.github.raw']
    for attempt in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
    raise RuntimeError(f'gh api {path} failed: {r.stderr.strip()}')


def fetch_dm(dm_dir):
    commit = json.loads(gh(f'repos/{DM_REPO}/commits/{DM_BRANCH}'))['sha']
    if dm_dir:
        files = sorted(f for f in os.listdir(dm_dir) if f.endswith('.json'))
        entries = [json.load(open(os.path.join(dm_dir, f))) for f in files]
    else:
        parent = json.loads(gh(f'repos/{DM_REPO}/contents/{os.path.dirname(DM_PATH)}?ref={commit}'))
        tree_sha = next(x['sha'] for x in parent if x['name'] == os.path.basename(DM_PATH))
        tree = json.loads(gh(f'repos/{DM_REPO}/git/trees/{tree_sha}'))['tree']
        blobs = [x['sha'] for x in tree if x['path'].endswith('.json')]
        with ThreadPoolExecutor(max_workers=12) as pool:
            entries = list(pool.map(lambda s: json.loads(gh(f'repos/{DM_REPO}/git/blobs/{s}', raw=True)), blobs))
    entries = [{k: e.get(k) for k in DM_KEEP} for e in entries]
    entries.sort(key=lambda e: e['id'])
    return {'source': f'https://github.com/{DM_REPO}/tree/{commit}/{DM_PATH}',
            'commit': commit,
            'fetched': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'entries': entries}


def fetch_wikidata_pleiades(qids):
    out = {}
    qids = sorted(qids)
    for i in range(0, len(qids), 200):
        values = ' '.join(f'wd:{q}' for q in qids[i:i + 200])
        query = f'SELECT ?item ?pleiades WHERE {{ VALUES ?item {{ {values} }} ?item wdt:P1584 ?pleiades . }}'
        req = urllib.request.Request(
            WD_SPARQL + '?' + urllib.parse.urlencode({'query': query, 'format': 'json'}),
            headers={'User-Agent': 'theographic-bible-metadata LPF pipeline (github.com/robertrouse/theographic-bible-metadata)'})
        rows = json.load(urllib.request.urlopen(req, timeout=120))['results']['bindings']
        for r in rows:
            q = r['item']['value'].rsplit('/', 1)[1]
            out.setdefault(q, []).append(r['pleiades']['value'])
    return {q: sorted(set(v)) for q, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dm-dir')
    ap.add_argument('--refresh', action='store_true', help='re-download even if cached')
    args = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)

    dm_out = f'{WORK}/dm-places-cache.json'
    if args.refresh or not os.path.exists(dm_out):
        dm = fetch_dm(args.dm_dir)
        json.dump(dm, open(dm_out, 'w'), indent=1, ensure_ascii=False)
        print(f'DM: {len(dm["entries"])} entries @ {dm["commit"][:7]}')

    ob_out = f'{WORK}/openbible-ancient.jsonl'
    if args.refresh or not os.path.exists(ob_out):
        urllib.request.urlretrieve(OB_URL, ob_out)
        print(f'OpenBible: saved {ob_out}')

    wd_out = f'{WORK}/wikidata-pleiades.json'
    if args.refresh or not os.path.exists(wd_out):
        qids = set()
        for line in open(ob_out):
            q = json.loads(line).get('linked_data', {}).get('s7cc8b2', {}).get('id')
            if q:
                qids.add(q)
        wd = fetch_wikidata_pleiades(qids)
        json.dump({'fetched': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                   'queried': len(qids), 'pleiades_by_qid': wd}, open(wd_out, 'w'), indent=1)
        print(f'Wikidata: {len(wd)} of {len(qids)} QIDs have a Pleiades ID')


if __name__ == '__main__':
    sys.exit(main())
