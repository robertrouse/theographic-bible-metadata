# Phase 3 — when{} from Pleiades

**Purpose:** For all records with a Pleiades link, fetch the Pleiades JSON, extract the earliest attested start year, and add a feature-level `when{}`. Produce a list of records still missing `when{}` for Phase 4.

**Prerequisite:** Phase 2 complete and approved. Input is `geo/working/phase-2-output.geojson`.

**Spec rule:** Feature-level `when` must contain only `start` — never `end`.

---

## Inputs

- `geo/working/phase-2-output.geojson`
- `geo/working/phase-1-crossref.json`

## Outputs

| File | Description |
|---|---|
| `geo/working/pleiades-cache.json` | Raw Pleiades JSON responses keyed by Pleiades ID |
| `geo/working/phase-3-output.geojson` | geojson with `when{}` added for Pleiades records |
| `geo/working/phase-3-no-when.csv` | Records still missing `when{}` after this phase |
| `geo/working/phase-3-report.md` | Summary counts, date distribution |

---

## Step 1: Load data

```python
import json, re

with open('geo/working/phase-2-output.geojson') as f:
    geo = json.load(f)

with open('geo/working/phase-1-crossref.json') as f:
    crossref = json.load(f)

def get_pleiades_id(feature):
    """Extract Pleiades numeric ID from links[]."""
    for link in feature.get('links', []):
        ident = link.get('identifier', '')
        if 'pleiades.stoa.org/places/' in ident:
            return ident.rstrip('/').split('/places/')[-1]
    return None
```

---

## Step 2: Fetch and cache Pleiades data

```python
import urllib.request, time

def fetch_pleiades(pleiades_id):
    """
    Fetch Pleiades place JSON.
    Returns parsed dict or None on failure.
    """
    url = f"https://pleiades.stoa.org/places/{pleiades_id}/json"
    try:
        req = urllib.request.Request(
            url,
            headers={
                'Accept': 'application/json',
                'User-Agent': 'theographic-bible-metadata/1.0'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print(f"  Failed: {pleiades_id} → {e}")
        return None

# Collect all unique Pleiades IDs from this batch
pleiades_ids = set()
for fc_obj in geo:
    feat = fc_obj['features'][0]
    pl_id = get_pleiades_id(feat)
    if pl_id:
        pleiades_ids.add(pl_id)

print(f"Fetching {len(pleiades_ids)} Pleiades records...")
pleiades_cache = {}

for i, pl_id in enumerate(sorted(pleiades_ids)):
    pleiades_cache[pl_id] = fetch_pleiades(pl_id)
    if i % 10 == 0:
        print(f"  {i}/{len(pleiades_ids)}")
    time.sleep(0.5)  # Respectful delay

with open('geo/working/pleiades-cache.json', 'w') as f:
    json.dump(pleiades_cache, f, indent=2, ensure_ascii=False)

fetched = sum(1 for v in pleiades_cache.values() if v)
print(f"Pleiades cache: {fetched}/{len(pleiades_ids)} successful")
```

---

## Step 3: Extract earliest start year

```python
def get_earliest_pleiades_year(pl_data):
    """
    Find the earliest start year from a Pleiades place record.
    Checks names[].start, names[].minDate, top-level minDate/start.
    Returns int year (negative = BC) or None.

    IMPORTANT: Use only integer fields. Do NOT interpret period-key strings
    like "archaic" or "hellenistic-republican" as years.
    """
    if not pl_data:
        return None

    earliest = None

    def update(val):
        nonlocal earliest
        if val is None:
            return
        try:
            yr = int(val)
            if earliest is None or yr < earliest:
                earliest = yr
        except (ValueError, TypeError):
            pass

    # Check names array
    for name_entry in pl_data.get('names', []):
        update(name_entry.get('start'))
        update(name_entry.get('minDate'))

    # Check locations array
    for loc in pl_data.get('locations', []):
        update(loc.get('start'))
        update(loc.get('minDate'))

    # Check top-level fields
    for field in ('minDate', 'start', 'begin'):
        update(pl_data.get(field))

    return earliest
```

---

## Step 4: Build feature-level when{}

```python
def build_feature_when(start_year):
    """
    Build LPF feature-level when object.
    Per spec: start only, never end at feature level.
    """
    return {
        "timespans": [{
            "start": {"in": str(start_year)}
        }]
    }
```

---

## Step 5: Process all records

```python
import csv

output = []
no_when_records = []
when_added_count = 0

for fc_obj in geo:
    feat = fc_obj['features'][0]
    geo_id = feat['@id']
    pl_id = get_pleiades_id(feat)

    new_feat = dict(feat)

    if pl_id and pleiades_cache.get(pl_id):
        start_yr = get_earliest_pleiades_year(pleiades_cache[pl_id])
        if start_yr is not None:
            new_feat['when'] = build_feature_when(start_yr)
            when_added_count += 1
        else:
            # Pleiades record exists but has no integer date data
            no_when_records.append({
                'geo_id': geo_id,
                'title': feat['properties']['title'],
                'pleiades_id': pl_id,
                'reason': 'pleiades_no_date_found'
            })
    elif pl_id:
        # Had a link but fetch failed
        no_when_records.append({
            'geo_id': geo_id,
            'title': feat['properties']['title'],
            'pleiades_id': pl_id,
            'reason': 'pleiades_fetch_failed'
        })
    else:
        # No Pleiades link
        no_when_records.append({
            'geo_id': geo_id,
            'title': feat['properties']['title'],
            'pleiades_id': '',
            'reason': 'no_pleiades_link'
        })

    new_fc_obj = dict(fc_obj)
    new_fc_obj['features'] = [new_feat]
    output.append(new_fc_obj)

with open('geo/working/phase-3-output.geojson', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

with open('geo/working/phase-3-no-when.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['geo_id', 'title', 'pleiades_id', 'reason'])
    writer.writeheader()
    writer.writerows(no_when_records)

print(f"when{{}} added from Pleiades: {when_added_count}")
print(f"Records still needing when{{}}: {len(no_when_records)}")
```

---

## Step 6: Write phase-3-report.md

Include:

- Records with Pleiades link: N (expect ~105)
- Pleiades records fetched successfully: N
- Pleiades records with no integer date data (stub records): N — list them
- `when{}` added from Pleiades: N
- Records still missing `when{}`: N (= 1,055 − N_added) — will be handled in Phase 4
- Date range of assigned start years: earliest to latest
- Distribution by period band (e.g. before −1000: N, −1000 to −500: N, etc.)
- Spot-check: show `when{}` for Antioch (Syria), Jerusalem, Athens

**Correct format example:**
```json
"when": {"timespans": [{"start": {"in": "-750"}}]}
```

**Not this** (no end at feature level):
```json
"when": {"timespans": [{"start": {"in": "-750"}, "end": {"in": "640"}}]}
```

---

## Verification

```python
with open('geo/working/phase-3-output.geojson') as f:
    out = json.load(f)

assert len(out) == 1055

with_when = sum(1 for fc in out if fc['features'][0].get('when'))
print(f"Records with when{{}}: {with_when}")   # expect ~100-105

# Confirm no end value at feature level
for fc in out:
    when = fc['features'][0].get('when', {})
    for ts in when.get('timespans', []):
        assert 'end' not in ts, \
            f"Feature-level end found: {fc['features'][0]['@id']}"

print("No feature-level 'end' values — confirmed.")
```

---

## ✋ Stop here

Present `geo/working/phase-3-report.md` and the distribution of assigned start years to the user. Wait for explicit approval before proceeding to Phase 4.
