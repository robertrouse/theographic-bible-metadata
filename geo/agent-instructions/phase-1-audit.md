# Phase 1 — Audit + OpenBible Cache

**Purpose:** Build the cross-reference table linking geojson records to `places.json`, fetch and cache OpenBible data, and produce an audit report. **No changes to geojson in this phase.**

---

## Inputs

- `geo/bible-places.geojson`
- `json/places.json`
- `json/events.json`

## Outputs

| File | Description |
|---|---|
| `geo/working/phase-1-crossref.json` | Keyed by `@id`; includes placeID, featureType, ob_id, pleiades_id, flags |
| `geo/working/openbible-cache.json` | OpenBible responses keyed by 7-char OpenBible ID |
| `geo/working/phase-1-report.md` | Summary counts, flag list, OpenBible field inventory |

Create `geo/working/` if it doesn't exist.

---

## Step 1: Load and index source files

```python
import json, re, os

with open('geo/bible-places.geojson') as f:
    geo = json.load(f)

with open('json/places.json') as f:
    places_raw = json.load(f)

with open('json/events.json') as f:
    events_raw = json.load(f)

# Index places.json by numeric placeID
# Handle both Airtable-wrapped ({id, fields}) and plain JSON
places_by_id = {}
for record in places_raw:
    fields = record.get('fields', record)
    pid_raw = fields.get('placeID')
    if pid_raw is not None:
        try:
            places_by_id[int(pid_raw)] = fields
        except (ValueError, TypeError):
            pass

# Index events.json by Airtable record ID
events_by_airtable_id = {}
for record in events_raw:
    rec_id = record.get('id')
    if rec_id:
        events_by_airtable_id[rec_id] = record.get('fields', record)

os.makedirs('geo/working', exist_ok=True)
print(f"Loaded: {len(geo)} geojson records, {len(places_by_id)} places, {len(events_by_airtable_id)} events")
```

---

## Step 2: Build the cross-reference table

### Matching key

Extract the numeric placeID from the theographic.netlify.app link slug:

```
https://theographic.netlify.app/place/abel-beth-maachah_5  →  placeID = 5
```

Use regex `_(\d+)` — NOT `_(\d+)$`. The `$` anchor would break compound IDs like `_421, 1010` (Euphrates). Always take the **first** numeric match.

```python
def extract_place_id(feature):
    """Extract placeID integer from theographic link. Returns int or None."""
    for link in feature.get('links', []):
        ident = link.get('identifier', '')
        if 'theographic.netlify' in ident:
            m = re.search(r'_(\d+)', ident)
            if m:
                return int(m.group(1))
    return None

def get_link_by_domain(feature, domain_substr):
    """Return first link identifier containing the given domain substring."""
    for link in feature.get('links', []):
        if domain_substr in link.get('identifier', ''):
            return link['identifier']
    return None

crossref = {}

for fc_obj in geo:
    feat = fc_obj['features'][0]
    geo_id = feat['@id']

    pid = extract_place_id(feat)
    place_fields = places_by_id.get(pid, {}) if pid is not None else {}

    ob_link = get_link_by_domain(feat, 'openbible.info')
    ob_id = ob_link.rstrip('/').split('/')[-1] if ob_link else None

    pl_link = get_link_by_domain(feat, 'pleiades.stoa.org')
    pl_id = pl_link.rstrip('/').split('/places/')[-1] if pl_link else None

    current_fclasses = feat['properties'].get('fclasses', [])
    geom = feat.get('geometry')
    current_certainty = geom.get('certainty') if geom else None

    events_here = place_fields.get('eventsHere', []) or []

    flags = []
    if not place_fields:
        flags.append('NO_MATCH')
    if not current_fclasses:
        flags.append('EMPTY_FCLASSES')
    if geom is None:
        flags.append('NULL_GEOMETRY')
    elif not current_certainty:
        flags.append('MISSING_CERTAINTY')
    if not ob_id:
        flags.append('NO_OPENBIBLE')
    if not pl_id:
        flags.append('NO_PLEIADES')

    crossref[geo_id] = {
        'title': feat['properties']['title'],
        'place_id': pid,
        'matched': bool(place_fields),
        'feature_type': place_fields.get('featureType', ''),
        'feature_sub_type': place_fields.get('featureSubType', ''),
        'events_here': events_here,
        'events_here_count': len(events_here),
        'ob_id': ob_id,
        'pleiades_id': pl_id,
        'fclasses_current': current_fclasses,
        'geometry_null': geom is None,
        'certainty_current': current_certainty,
        'flags': flags
    }

with open('geo/working/phase-1-crossref.json', 'w') as f:
    json.dump(crossref, f, indent=2, ensure_ascii=False)

print(f"Cross-reference built: {len(crossref)} records")
```

### Known edge cases

| Title | Issue | Expected result |
|---|---|---|
| Euphrates | Theographic link slug is `_421, 1010` (comma-separated) | Regex `_(\d+)` takes `421` → matches placeID 421 |
| Mount Zalmon | Same compound ID pattern | First numeric match → matches |
| Sheol | No theographic link at all | `NO_MATCH` flag; fclass derived from OpenBible `otype` in Phase 2 |
| Judah | No theographic link | `NO_MATCH` flag |
| El-elohe-Israel | No theographic link | `NO_MATCH` flag |
| Remmon-methoar | No theographic link | `NO_MATCH` flag |

---

## Step 3: Fetch and cache OpenBible data

### Try bulk download first

Visit `https://www.openbible.info/geo/` and inspect the page for a downloadable dataset (TSV, CSV, or JSON). If a bulk file is available, download and parse it — this is much faster than per-record fetching.

```python
import urllib.request

# Inspect the page for download links before trying these patterns:
BULK_CANDIDATES = [
    'https://www.openbible.info/geo/data.tsv',
    'https://www.openbible.info/geo/ancient/data.tsv',
    'https://www.openbible.info/geo/ancient.tsv',
]
bulk_succeeded = False
for url in BULK_CANDIDATES:
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            content = r.read().decode('utf-8')
        print(f"Bulk download succeeded: {url}")
        # Parse the TSV/CSV here and build openbible_cache from it
        # Document column names found
        bulk_succeeded = True
        break
    except Exception as e:
        print(f"  {url} → {e}")
```

### Per-record fallback

```python
import time

def fetch_openbible(ob_id):
    """Try JSON endpoint(s) for a single OpenBible record."""
    for url in [
        f"https://www.openbible.info/geo/ancient/{ob_id}.json",
        f"https://www.openbible.info/geo/{ob_id}.json",
    ]:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'theographic-bible-metadata/1.0'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            continue
    return None

openbible_cache = {}

if not bulk_succeeded:
    all_ob_ids = sorted({row['ob_id'] for row in crossref.values() if row['ob_id']})
    print(f"Fetching {len(all_ob_ids)} OpenBible records individually...")
    for i, ob_id in enumerate(all_ob_ids):
        result = fetch_openbible(ob_id)
        openbible_cache[ob_id] = result
        if i % 100 == 0:
            print(f"  {i}/{len(all_ob_ids)}...")
        time.sleep(0.3)  # Be polite

with open('geo/working/openbible-cache.json', 'w') as f:
    json.dump(openbible_cache, f, indent=2, ensure_ascii=False)

fetched = sum(1 for v in openbible_cache.values() if v is not None)
print(f"OpenBible cache: {fetched}/{len(openbible_cache)} successful")
```

### Document actual field names (critical for Phase 2)

```python
# Inspect 5 sample records and print their keys
sample = [(k, v) for k, v in openbible_cache.items() if v][:5]
for ob_id, data in sample:
    print(f"\n{ob_id}: keys = {list(data.keys())}")
    print(f"  best_path_score = {data.get('best_path_score')}")
    print(f"  otype = {data.get('otype')}")
```

Report the actual field names in `phase-1-report.md`. Phase 2 depends on knowing whether the fields are `best_path_score` / `otype` or something else.

---

## Step 4: Write phase-1-report.md

Include all of the following:

### Counts
```
Total geojson records:           1,055 (expected)
Matched to places.json:          N / 1,055
NO_MATCH records:                N — list each with title and reason
Empty fclasses:                  N (expect 106)
Null geometry:                   N (expect 92)
Missing certainty field:         N
OpenBible link present:          N (expect 1,052)
OpenBible data fetched:          N / N_attempted
Pleiades link present:           N (expect 105)
```

### Three-way geometry/fclass split (important for Phase 2)
```
Empty fclasses AND null geometry:          N (expect 78)
Null geometry but fclasses already set:    N (expect 14) — list them
Empty fclasses but non-null geometry:      N (expect 28) — list them
```

### OpenBible field inventory
- Confirm `best_path_score` exists and its data type (expect integer)
- Confirm `otype` exists and list all unique values found
- If field names differ from expected, document actual names here

### Pleiades IDs
List all ~105 Pleiades IDs (needed for Phase 3).

### Flag summary
Show each flag combination and its record count.

---

## Verification

```python
assert len(crossref) == 1055, f"Expected 1055 records, got {len(crossref)}"

pleiades_count = sum(1 for r in crossref.values() if r['pleiades_id'])
print(f"Records with Pleiades link: {pleiades_count}")     # expect ~105

ob_count = sum(1 for r in crossref.values() if r['ob_id'])
print(f"Records with OpenBible link: {ob_count}")          # expect ~1052

empty_fc = sum(1 for r in crossref.values() if not r['fclasses_current'])
null_geom = sum(1 for r in crossref.values() if r['geometry_null'])
both = sum(1 for r in crossref.values() if not r['fclasses_current'] and r['geometry_null'])
print(f"Empty fclasses: {empty_fc}")     # expect 106
print(f"Null geometry: {null_geom}")     # expect 92
print(f"Both: {both}")                   # expect 78
```

---

## ✋ Stop here

Present `geo/working/phase-1-report.md` to the user and wait for explicit approval before proceeding to Phase 2.
