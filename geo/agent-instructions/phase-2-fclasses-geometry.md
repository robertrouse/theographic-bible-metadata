# Phase 2 — fclasses + Geometry + Coordinates

**Purpose:** Fill 106 empty `fclasses` arrays, convert all string coordinates to numeric floats, capitalize `"point"` → `"Point"`, enforce the `certainty` field on every geometry record, and handle null-geometry records.

**Prerequisite:** Phase 1 complete and approved. Requires `geo/working/phase-1-crossref.json` and `geo/working/openbible-cache.json`.

---

## Inputs

- `geo/bible-places.geojson` (read-only)
- `geo/working/phase-1-crossref.json`
- `geo/working/openbible-cache.json`

## Outputs

| File | Description |
|---|---|
| `geo/working/phase-2-output.geojson` | All three repairs applied |
| `geo/working/phase-2-report.md` | Counts, flags, manual review list |

---

## fclasses Mapping Tables

> **Never use "A".** Use "L" for all countries, regions, and administrative areas.

### Primary: places.json featureType + featureSubType

```python
FEATURE_TYPE_MAP = {
    # Settlements
    ('City', None):      ['P'],
    ('City', 'River'):   ['P'],   # 1 anomalous record — featureType wins over subtype
    # Regions / countries
    ('Region', None):    ['L'],
    ('Region', 'Country'): ['L'],
    # Water features
    ('Water', None):     ['H'],   # generic water → H
    ('Water', 'River'):  ['H'],
    ('Water', 'Stream'): ['H'],
    ('Water', 'Wadi'):   ['H'],
    ('Water', 'Spring'): ['S'],   # man-made spring infrastructure → S
    ('Water', 'Well'):   ['S'],
    ('Water', 'Pool'):   ['S'],
    # Landforms
    ('Mountain', None):  ['T'],
    ('Valley', None):    ['T'],
    ('Island', None):    ['T'],
    # Sites and structures
    ('Landmark', None):       ['S'],
    ('Landmark', 'Gate'):     ['S'],
    ('Landmark', 'Tower'):    ['S'],
    ('Landmark', 'Garden'):   ['S'],
    ('Landmark', 'Cave'):     ['S'],
    ('Landmark', 'Well'):     ['S'],
    ('Landmark', 'Pool'):     ['S'],
    ('Landmark', 'Spring'):   ['H'],  # natural spring labeled as Landmark
    ('Landmark', 'Hall'):     ['S'],
    ('Landmark', 'Fortification'): ['S'],
    ('Landmark', 'Structure'): ['S'],
    # Roads
    ('Path', None):      ['R'],
}
```

### Fallback: OpenBible `otype` (for NO_MATCH records with no places.json entry)

```python
OPENBIBLE_OTYPE_MAP = {
    'settlement': ['P'], 'settlement and spring': ['P'],
    'body of water': ['H'], 'canal': ['H'], 'river': ['H'],
    'spring': ['H'], 'wadi': ['H'],
    'district in settlement': ['L'], 'people group': ['L'], 'region': ['L'],
    'road': ['R'],
    'altar': ['S'], 'campsite': ['S'], 'garden': ['S'], 'gate': ['S'],
    'hall': ['S'], 'mine': ['S'], 'pool': ['S'], 'room': ['S'],
    'stone heap': ['S'], 'structure': ['S'], 'tree': ['S'], 'well': ['S'],
    'special': ['S'],
    'cliff': ['T'], 'field': ['T'], 'ford': ['T'], 'forest': ['T'],
    'fortification': ['T'], 'hill': ['T'], 'island': ['T'], 'mountain': ['T'],
    'mountain pass': ['T'], 'mountain range': ['T'], 'mountain ridge': ['T'],
    'natural area': ['T'], 'promontory': ['T'], 'rock': ['T'], 'valley': ['T'],
}
```

---

## Certainty Rules

`geometry.certainty` **must be present on every geometry object.** If missing or blank → set to `"less-certain"`.

| Condition | Certainty |
|---|---|
| Geometry is null | `"less-certain"` (always) |
| OpenBible `best_path_score >= 500` | `"certain"` |
| OpenBible `best_path_score < 500` | `"less-certain"` |
| No OpenBible score + geometry exists + certainty already set | Preserve existing |
| No OpenBible score + geometry exists + certainty missing/blank | `"less-certain"` |

> **Note:** If Phase 1 found that `best_path_score` uses a different field name, substitute it below.

---

## Null geometry rules

| fclasses contains | Action |
|---|---|
| `"P"` or `"S"` | Add `{"type": "Point", "coordinates": null, "certainty": "less-certain"}` |
| `"L"`, `"T"`, `"H"`, or `"R"` | Leave geometry as `null` |
| Empty / unknown | Add Point stub + flag `NEEDS_MANUAL_FCLASS` |

---

## Step 1: Load data

```python
import json, re

with open('geo/bible-places.geojson') as f:
    geo = json.load(f)

with open('geo/working/phase-1-crossref.json') as f:
    crossref = json.load(f)

with open('geo/working/openbible-cache.json') as f:
    ob_cache = json.load(f)
```

---

## Step 2: Helper functions

```python
def derive_fclass(crossref_row, ob_cache):
    """
    Returns (fclass_list, source_label, flag_or_None).
    Only call for records with empty fclasses.
    """
    ft  = (crossref_row.get('feature_type') or '').strip()
    fst = (crossref_row.get('feature_sub_type') or '').strip() or None

    # Try exact (featureType, featureSubType) match
    if ft:
        key = (ft, fst)
        if key in FEATURE_TYPE_MAP:
            return FEATURE_TYPE_MAP[key], 'places.json', None
        # Try featureType alone (ignore subtype)
        key_bare = (ft, None)
        if key_bare in FEATURE_TYPE_MAP:
            return FEATURE_TYPE_MAP[key_bare], 'places.json_no_subtype', None

    # Fallback: OpenBible otype
    ob_id = crossref_row.get('ob_id')
    if ob_id and ob_cache.get(ob_id):
        otype = (ob_cache[ob_id].get('otype') or '').lower().strip()
        if otype in OPENBIBLE_OTYPE_MAP:
            return OPENBIBLE_OTYPE_MAP[otype], 'openbible_otype', None

    # Cannot determine
    return [], None, 'NEEDS_MANUAL_FCLASS'


def derive_certainty(crossref_row, ob_cache):
    """
    Returns (certainty_str, source_label).
    Null geometry always → less-certain.
    Otherwise uses OpenBible score, then preserves existing, then defaults.
    """
    if crossref_row.get('geometry_null'):
        return 'less-certain', 'null_geometry_rule'

    ob_id = crossref_row.get('ob_id')
    if ob_id and ob_cache.get(ob_id):
        score = ob_cache[ob_id].get('best_path_score')
        if score is not None:
            try:
                return ('certain' if int(score) >= 500 else 'less-certain',
                        f'openbible_score_{score}')
            except (ValueError, TypeError):
                pass

    existing = crossref_row.get('certainty_current')
    if existing:
        return existing, 'preserved'
    return 'less-certain', 'default_missing'


def fix_geometry(geom, new_certainty):
    """
    Fix an existing (non-null) geometry dict:
    - Capitalize type: 'point' → 'Point'
    - Convert string coordinates to floats
    - Set certainty (always)
    Returns updated dict.
    """
    g = dict(geom)

    # Capitalize type
    if g.get('type'):
        g['type'] = g['type'].capitalize()

    # Convert coordinates
    coords = g.get('coordinates')
    if coords is not None:
        g['coordinates'] = convert_coords(coords)

    g['certainty'] = new_certainty
    return g


def convert_coords(coords):
    """Recursively convert string coordinate values to floats."""
    if isinstance(coords, str):
        return float(coords)
    if isinstance(coords, (int, float)):
        return coords
    if isinstance(coords, list):
        return [convert_coords(c) for c in coords]
    return coords


def handle_null_geometry(new_fclasses, new_certainty):
    """
    Returns (geometry_dict_or_None, flag_str).
    P/S → Point stub; L/T/H/R → null; unknown → Point stub + flag.
    """
    if any(fc in ('P', 'S') for fc in new_fclasses):
        return {'type': 'Point', 'coordinates': None, 'certainty': 'less-certain'}, None
    elif new_fclasses:
        return None, None  # Leave null for L/T/H/R
    else:
        return {'type': 'Point', 'coordinates': None, 'certainty': 'less-certain'}, 'NEEDS_MANUAL_FCLASS'
```

---

## Step 3: Main processing loop

Three record groups handled differently:
- **78 records**: empty fclasses + null geometry → derive fclass, apply null-geom rule
- **14 records**: null geometry but fclasses already set → apply null-geom rule only
- **28 records**: empty fclasses + non-null geometry → derive fclass, convert coords

```python
output = []
change_log = []
manual_fclass_needed = []

for fc_obj in geo:
    feat = fc_obj['features'][0]
    geo_id = feat['@id']
    row = crossref[geo_id]

    current_fclasses = feat['properties'].get('fclasses', [])
    current_geom = feat.get('geometry')

    # ── fclasses ──────────────────────────────────────────────────────────
    if current_fclasses:
        # Already set — preserve; do not modify
        new_fclasses = current_fclasses
        fc_source = 'preserved'
        fc_flag = None
    else:
        new_fclasses, fc_source, fc_flag = derive_fclass(row, ob_cache)
        if fc_flag:
            manual_fclass_needed.append({
                'geo_id': geo_id,
                'title': feat['properties']['title'],
                'feature_type': row.get('feature_type', ''),
                'feature_sub_type': row.get('feature_sub_type', ''),
                'ob_id': row.get('ob_id', ''),
                'flag': fc_flag
            })

    # ── certainty ─────────────────────────────────────────────────────────
    new_certainty, cert_source = derive_certainty(row, ob_cache)

    # ── geometry ──────────────────────────────────────────────────────────
    if current_geom is None:
        new_geom, geom_flag = handle_null_geometry(new_fclasses, new_certainty)
    else:
        new_geom = fix_geometry(current_geom, new_certainty)
        geom_flag = None

    # ── assemble ──────────────────────────────────────────────────────────
    new_feat = dict(feat)
    new_feat['properties'] = dict(feat['properties'])
    new_feat['properties']['fclasses'] = new_fclasses
    new_feat['geometry'] = new_geom

    change_log.append({
        'geo_id': geo_id,
        'title': feat['properties']['title'],
        'fclasses_from': current_fclasses,
        'fclasses_to': new_fclasses,
        'fc_source': fc_source,
        'fc_flag': fc_flag,
        'certainty_from': (current_geom.get('certainty') if current_geom else 'null_geom'),
        'certainty_to': new_certainty,
        'cert_source': cert_source,
        'geom_flag': geom_flag
    })

    new_fc_obj = dict(fc_obj)
    new_fc_obj['features'] = [new_feat]
    output.append(new_fc_obj)

with open('geo/working/phase-2-output.geojson', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Processed {len(output)} records")
print(f"fclasses needing manual review: {len(manual_fclass_needed)}")
```

---

## Step 4: Write phase-2-report.md

Report must include:

- Total records processed: (must be 1,055)
- **fclasses:**
  - Filled from places.json featureType: N
  - Filled from OpenBible otype: N
  - Preserved (already set): N
  - Still empty — needs manual: list each record with title + featureType
- **Geometry:**
  - String coordinates converted to numeric: N (expect 963)
  - Type capitalized (`"point"` → `"Point"`): N (expect 963)
  - Certainty field set or updated: N
  - Certainty field added where missing: N
  - Null geometry → Point stub added (P/S): N (expect 92 total, covering all null-geom records)
  - Null geometry → left null (L/T/H/R): N
- Spot-check table: show before/after for Jerusalem, Bethlehem, Antioch (Syria), Athens, Abilene

---

## Verification

```python
with open('geo/working/phase-2-output.geojson') as f:
    out = json.load(f)

assert len(out) == 1055, f"Expected 1055, got {len(out)}"

# No string coordinates
string_coords = [
    fc['features'][0]['@id'] for fc in out
    if fc['features'][0].get('geometry')
    and fc['features'][0]['geometry'].get('coordinates') is not None
    and isinstance(fc['features'][0]['geometry']['coordinates'][0], str)
]
assert len(string_coords) == 0, f"String coordinates remain: {string_coords[:5]}"

# No lowercase 'point'
lower_point = [
    fc['features'][0]['@id'] for fc in out
    if fc['features'][0].get('geometry')
    and fc['features'][0]['geometry'].get('type') == 'point'
]
assert len(lower_point) == 0, f"Lowercase 'point' remains: {lower_point[:5]}"

# No geometry with missing certainty
missing_cert = [
    fc['features'][0]['@id'] for fc in out
    if fc['features'][0].get('geometry')
    and not fc['features'][0]['geometry'].get('certainty')
]
assert len(missing_cert) == 0, f"Geometry missing certainty: {missing_cert[:5]}"

empty_fc_remaining = [
    fc['features'][0]['@id'] for fc in out
    if not fc['features'][0]['properties'].get('fclasses')
]
print(f"Records still with empty fclasses: {len(empty_fc_remaining)}")
# Expect ≤2 (Sheol, Judah have no theographic link and may lack otype)

print("All verifications passed.")
```

---

## ✋ Stop here

Present `geo/working/phase-2-report.md` to the user, including the full list of any records that still need manual fclass assignment. Wait for explicit approval before proceeding to Phase 3.
