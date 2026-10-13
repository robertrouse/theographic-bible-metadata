"""Phase 10: validate the final LPF FeatureCollection.

1. Structure: one FeatureCollection with @context; unique @id and titles;
   valid Point geometry; fclasses from the spec (never "A"); certainty values;
   feature-level when{} has a start and no end.
2. Schema: every Feature against the World Historical Gazetteer LPF schema
   (schema_lpf_v1.2.2.json from WorldHistoricalGazetteer/website), when the
   jsonschema package is installed (pip install jsonschema).
3. Links: every distinct URL in links[], name citations and PeriodO periods is
   requested (HEAD, then GET if HEAD fails), a few at a time per host. Results are
   cached in geo/working/link-check.json; --recheck ignores the cache.
   The @id URLs on bible.helloao.org are not checked: that API is on hold.

Reads:  geo/working/phase-9-output.geojson
Writes: geo/working/schema_lpf_v1.2.2.json (downloaded once), link-check.json,
        phase-10-broken-links.csv, phase-10-report.md

Usage: python3 geo/pipeline/phase10_validate.py [--recheck] [--no-links]
"""
import argparse
import collections
import csv
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

WORK = 'geo/working'
SCHEMA_URL = ('https://raw.githubusercontent.com/WorldHistoricalGazetteer/website/main/'
              'datasets/static/validate/schema_lpf_v1.2.2.json')
UA = {'User-Agent': 'theographic-bible-metadata LPF link check (github.com/robertrouse/theographic-bible-metadata)'}
FCLASSES = {'H', 'L', 'P', 'R', 'S', 'T'}
CERTAINTY = {'certain', 'less-certain', 'uncertain'}
PER_HOST = 4


def structure_errors(fc):
    errs = []
    if fc.get('type') != 'FeatureCollection':
        errs.append('top level is not a FeatureCollection')
    if not fc.get('@context'):
        errs.append('missing @context')
    ids = collections.Counter(f.get('@id') for f in fc['features'])
    titles = collections.Counter(f['properties'].get('title') for f in fc['features'])
    errs += [f'duplicate @id {i}' for i, n in ids.items() if n > 1]
    errs += [f'duplicate title {t}' for t, n in titles.items() if n > 1]
    for f in fc['features']:
        t = f['properties'].get('title')
        fcl = f['properties'].get('fclasses') or []
        if not fcl or set(fcl) - FCLASSES or len(set(fcl)) != len(fcl):
            errs.append(f'{t}: bad fclasses {fcl}')
        g = f.get('geometry')
        if g is not None:
            c = g.get('coordinates')
            if g.get('type') == 'GeometryCollection' and g.get('geometries') == []:
                pass    # location unknown
            elif g.get('type') != 'Point' or not (isinstance(c, list) and len(c) == 2 and
                                                  all(isinstance(v, (int, float)) for v in c)):
                errs.append(f'{t}: bad geometry {g}')
            elif not (-180 <= c[0] <= 180 and -90 <= c[1] <= 90):
                errs.append(f'{t}: coordinates out of range {c}')
            if g.get('certainty') not in CERTAINTY:
                errs.append(f'{t}: bad certainty {g.get("certainty")}')
        w = f.get('when')
        if not w or not w.get('timespans') or 'start' not in w['timespans'][0]:
            errs.append(f'{t}: feature when{{}} has no start')
        elif any('end' in s for s in w['timespans']):
            errs.append(f'{t}: feature when{{}} has an end')
        if not f.get('names'):
            errs.append(f'{t}: no names')
        for n in f.get('names') or []:
            if not n.get('citations'):
                errs.append(f'{t}: name {n.get("toponym")} has no citation')
    return errs


def schema_errors(fc):
    try:
        import jsonschema
    except ImportError:
        return None, 'jsonschema not installed (pip install jsonschema); schema check skipped'
    path = f'{WORK}/schema_lpf_v1.2.2.json'
    if not os.path.exists(path):
        urllib.request.urlretrieve(SCHEMA_URL, path)
    validator = jsonschema.Draft7Validator(json.load(open(path)))
    errs = []
    for f in fc['features']:
        for e in validator.iter_errors(f):
            errs.append(f'{f["properties"]["title"]}: {"/".join(map(str, e.path))} {e.message}')
    return errs, None


def collect_urls(fc):
    urls = collections.defaultdict(set)          # url -> where it is used
    for f in fc['features']:
        t = f['properties']['title']
        for l in f.get('links') or []:
            urls[l['identifier']].add(t)
        for n in f.get('names') or []:
            for c in n.get('citations') or []:
                if c.get('@id'):
                    urls[c['@id']].add(t)
        for p in (f.get('when') or {}).get('periods') or []:
            urls[p['uri']].add(t)
    return urls


def check(url, gates):
    host = urllib.parse.urlparse(url).netloc
    with gates[host]:
        for attempt in range(3):
            for method in ('HEAD', 'GET'):
                try:
                    req = urllib.request.Request(url, method=method, headers=UA)
                    with urllib.request.urlopen(req, timeout=30) as r:
                        return {'status': r.status, 'final': r.url}
                except urllib.error.HTTPError as e:
                    if method == 'HEAD':    # some servers (digitalmanna.org) refuse HEAD but serve GET
                        continue
                    if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                        time.sleep(5 * (attempt + 1))
                        break
                    return {'status': e.code, 'final': url}
                except Exception as e:
                    if attempt < 2:
                        time.sleep(3)
                        break
                    return {'status': None, 'error': str(e)[:120]}
    return {'status': None, 'error': 'gave up'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--recheck', action='store_true')
    ap.add_argument('--no-links', action='store_true')
    args = ap.parse_args()
    fc = json.load(open(f'{WORK}/phase-9-output.geojson'))

    struct = structure_errors(fc)
    schema, schema_note = schema_errors(fc)

    link_rows, by_host = [], collections.Counter()
    host_ok = collections.Counter()
    urls = collect_urls(fc)
    if not args.no_links:
        cache_path = f'{WORK}/link-check.json'
        cache = {} if args.recheck or not os.path.exists(cache_path) else json.load(open(cache_path))
        todo = [u for u in urls if u not in cache]
        gates = collections.defaultdict(lambda: threading.Semaphore(PER_HOST))
        with ThreadPoolExecutor(max_workers=24) as pool:
            for u, res in zip(todo, pool.map(lambda u: check(u, gates), todo)):
                cache[u] = res
        json.dump(cache, open(cache_path, 'w'), indent=1)
        for u, used in urls.items():
            host = urllib.parse.urlparse(u).netloc
            by_host[host] += 1
            res = cache[u]
            if res.get('status') and 200 <= res['status'] < 400:
                host_ok[host] += 1
            else:
                link_rows.append({'url': u, 'status': res.get('status'), 'error': res.get('error', ''),
                                  'used_by': '; '.join(sorted(used)[:5])})
        with open(f'{WORK}/phase-10-broken-links.csv', 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=['url', 'status', 'error', 'used_by'])
            w.writeheader()
            w.writerows(sorted(link_rows, key=lambda r: r['url']))

    feats = fc['features']
    lines = [
        '# Phase 10 Report: Validation', '',
        f'**Generated:** {date.today().isoformat()}  ',
        '**File:** geo/working/phase-9-output.geojson', '',
        '## Summary', '',
        '| Check | Result |', '|---|---|',
        f'| Features | {len(feats)} |',
        f'| Structure (collection, unique ids/titles, geometry, fclasses, certainty, when, names) | '
        f'{"✓ pass" if not struct else f"✗ {len(struct)} problems"} |',
        f'| WHG LPF schema v1.2.2 | ' + (schema_note if schema is None else
                                         ("✓ all features valid" if not schema else f"✗ {len(schema)} errors")) + ' |',
        f'| Links checked | ' + ('skipped' if args.no_links else
                                 f'{len(urls)} distinct URLs, {len(urls) - len(link_rows)} OK, {len(link_rows)} failed') + ' |',
        f'| @id URLs (bible.helloao.org) | not checked: the API is on hold |', '',
        '## Coverage', '',
        '| Field | Features |', '|---|---|',
        f'| geometry with coordinates | {sum(1 for f in feats if f["geometry"].get("coordinates"))} |',
        f'| geometry certain | {sum(1 for f in feats if f["geometry"]["certainty"] == "certain")} |',
        f'| when{{}} | {sum(1 for f in feats if f.get("when"))} |',
        f'| names[] | {sum(1 for f in feats if f.get("names"))} ({sum(len(f["names"]) for f in feats)} names) |',
        f'| Pleiades link | {sum(1 for f in feats if any("pleiades.stoa.org" in l["identifier"] for l in f["links"]))} |',
        f'| Wikidata link | {sum(1 for f in feats if any("wikidata.org" in l["identifier"] for l in f["links"]))} |',
    ]
    if not args.no_links:
        lines += ['', '## Links by host', '', '| Host | URLs | OK |', '|---|---|---|']
        lines += [f'| {h} | {n} | {host_ok[h]} |' for h, n in by_host.most_common()]
        if link_rows:
            lines += ['', 'Failed links are listed in `phase-10-broken-links.csv`.']
    if struct:
        lines += ['', '## Structure problems', ''] + [f'- {e}' for e in struct[:200]]
    if schema:
        lines += ['', '## Schema errors', ''] + [f'- {e}' for e in schema[:200]]
    open(f'{WORK}/phase-10-report.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
