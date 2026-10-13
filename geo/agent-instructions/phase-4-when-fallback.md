# Phase 4 — when{} Fallback + Final Output

**Purpose:** For all records still missing `when{}` after Phase 3, assign a `when{}` based on standard ANE/biblical archaeology periods — **not raw event dates.** Events are used only to determine *which* period a place belongs to; the period's canonical start year is what gets written. Records with no events and no Pleiades data are flagged for manual review and left without `when{}`. Produce the final geojson and await user approval before overwriting the source file.

**Prerequisite:** Phase 3 complete and approved.

---

## Inputs

- `geo/working/phase-3-output.geojson`
- `geo/working/phase-3-no-when.csv`
- `geo/working/phase-1-crossref.json`
- `json/events.json`

## Outputs

| File | Description |
|---|---|
| `geo/working/phase-4-final.geojson` | Complete final geojson |
| `geo/working/phase-4-needs-manual-when.csv` | Records with no events and no Pleiades data |
| `geo/working/phase-4-report.md` | Cross-phase summary |

---

## Period Mapping Table

Map the earliest event `startDate` for a place to the appropriate standard archaeological period, then use the **period's start year** (not the raw event date). This prevents false precision and keeps temporal assertions at period granularity.

```python
# (event_year_min_inclusive, event_year_max_exclusive, period_name, period_start_year_to_use)
# None means unbounded. First matching range wins.

PERIOD_TABLE = [
    (None,  -3300, 'Early Bronze Age',               -3300),
    (-3300, -2000, 'Early Bronze Age',               -3300),
    (-2000, -1550, 'Middle Bronze Age',              -2000),
    (-1550, -1200, 'Late Bronze Age',                -1550),
    (-1200, -1000, 'Iron Age I',                     -1200),
    (-1000,  -900, 'Iron Age IIA',                   -1000),
    ( -900,  -720, 'Iron Age IIB',                    -900),
    ( -720,  -539, 'Iron Age IIC/Neo-Babylonian',     -720),
    ( -539,  -332, 'Persian (Achaemenid)',             -539),
    ( -332,   -63, 'Hellenistic',                     -332),
    (  -63,   284, 'Early Roman',                      -63),
    (  284,  None, 'Late Roman/Byzantine',             284),
]

def map_year_to_period(event_year):
    """
    Given an event year (int), return (period_name, period_start_year).
    """
    for (lo, hi, name, period_start) in PERIOD_TABLE:
        lo_ok = (lo is None) or (event_year >= lo)
        hi_ok = (hi is None) or (event_year < hi)
        if lo_ok and hi_ok:
            return name, period_start
    return 'Early Bronze Age', -3300  # safety fallback
```

---

## Step 1: Load data

```python
import json, csv

with open('geo/working/phase-3-output.geojson') as f:
    geo = json.load(f)

with open('geo/working/phase-3-no-when.csv') as f:
    no_when_set = {row['geo_id'] for row in csv.DictReader(f)}

with open('geo/working/phase-1-crossref.json') as f:
    crossref = json.load(f)

with open('json/events.json') as f:
    events_raw = json.load(f)

# Index events by Airtable record ID
events_by_airtable_id = {}
for record in events_raw:
    rec_id = record.get('id')
    if rec_id:
        events_by_airtable_id[rec_id] = record.get('fields', record)
```

---

## Step 2: startDate parser

Events have two date formats — pure integer strings (`"-4003"`) and ISO date strings (`"0030-05-01"`). The parser must handle both.

```python
def parse_event_year(start_date_str):
    """
    Parse an event startDate string to integer year.
    Handles: '-4003' → -4003, '750' → 750, '0030-05-01' → 30
    Returns int or None.
    """
    if not start_date_str:
        return None
    sd = str(start_date_str).strip()
    try:
        # Negative integer string like '-4003'
        if sd.startswith('-'):
            parts = sd.split('-')
            # '-4003' → split gives ['', '4003'] → year = -4003
            return -int(parts[1])
        # Positive: could be '750' or '0030-05-01'
        year_part = sd.split('-')[0]
        return int(year_part)
    except (ValueError, TypeError, IndexError):
        return None
```

---

## Step 3: Period assignment from events

```python
def get_period_when(geo_id, crossref_row, events_by_airtable_id):
    """
    Returns (when_dict, assignment_note) or (None, reason_str).

    Finds the earliest event year for this place, maps it to a standard period,
    and returns a when{} using the PERIOD start year (not the event year).
    """
    events_here = crossref_row.get('events_here', [])
    if not events_here:
        return None, 'no_events_here'

    earliest_year = None
    for ev_id in events_here:
        ev = events_by_airtable_id.get(ev_id)
        if not ev:
            continue
        yr = parse_event_year(ev.get('startDate'))
        if yr is not None:
            if earliest_year is None or yr < earliest_year:
                earliest_year = yr

    if earliest_year is None:
        return None, 'events_found_but_no_parseable_date'

    period_name, period_start = map_year_to_period(earliest_year)

    when = {
        'timespans': [{'start': {'in': str(period_start)}}],
        'label': period_name,
        'certainty': 'less-certain'
    }
    note = (f"Earliest event year {earliest_year} → "
            f"period '{period_name}' (canonical start {period_start})")
    return when, note
```

---

## Step 4: Main processing loop

```python
output = []
needs_manual_when = []
assignment_log = []

for fc_obj in geo:
    feat = fc_obj['features'][0]
    geo_id = feat['@id']
    row = crossref[geo_id]

    new_feat = dict(feat)

    if feat.get('when'):
        # Already assigned in Phase 3 from Pleiades
        assignment_log.append({'geo_id': geo_id, 'action': 'already_has_when_pleiades'})

    elif geo_id not in no_when_set:
        # Shouldn't happen — log as unexpected
        assignment_log.append({'geo_id': geo_id, 'action': 'unexpected_skip'})

    else:
        when_obj, note = get_period_when(geo_id, row, events_by_airtable_id)

        if when_obj is not None:
            new_feat['when'] = when_obj
            assignment_log.append({
                'geo_id': geo_id,
                'title': feat['properties']['title'],
                'action': 'period_from_events',
                'note': note
            })
        else:
            # No events and no Pleiades — do NOT assign speculative when{}
            needs_manual_when.append({
                'geo_id': geo_id,
                'title': feat['properties']['title'],
                'fclasses': str(feat['properties'].get('fclasses', [])),
                'pleiades_id': row.get('pleiades_id', ''),
                'events_here_count': row.get('events_here_count', 0),
                'reason': note
            })
            assignment_log.append({
                'geo_id': geo_id,
                'title': feat['properties']['title'],
                'action': 'needs_manual',
                'note': note
            })

    new_fc_obj = dict(fc_obj)
    new_fc_obj['features'] = [new_feat]
    output.append(new_fc_obj)

with open('geo/working/phase-4-final.geojson', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

with open('geo/working/phase-4-needs-manual-when.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'geo_id', 'title', 'fclasses', 'pleiades_id', 'events_here_count', 'reason'
    ])
    writer.writeheader()
    writer.writerows(needs_manual_when)

with_when = sum(1 for fc in output if fc['features'][0].get('when'))
print(f"Records with when{{}}: {with_when} / {len(output)}")
print(f"Needs manual when{{}}: {len(needs_manual_when)}")
```

---

## Step 5: Write phase-4-report.md (cross-phase summary)

This report covers the entire process across all four phases.

### Summary by phase
| Phase | Task | Records changed |
|---|---|---|
| Phase 2 | fclasses filled | N |
| Phase 2 | Coordinates converted to numeric | N (expect 963) |
| Phase 2 | `"point"` → `"Point"` | N (expect 963) |
| Phase 2 | `certainty` field added/updated | N |
| Phase 2 | Point stubs added (null geometry P/S) | N (expect 92) |
| Phase 3 | `when{}` from Pleiades | N |
| Phase 4 | `when{}` from period inference | N |
| Phase 4 | No `when{}` assigned (manual review) | N |

### when{} coverage
- Total records with `when{}`: N / 1,055
- Source breakdown: Pleiades N | period-events N | none N
- Period distribution:

| Period | Count |
|---|---|
| Early Bronze Age | N |
| Middle Bronze Age | N |
| Late Bronze Age | N |
| Iron Age I | N |
| Iron Age IIA | N |
| Iron Age IIB | N |
| Iron Age IIC/Neo-Babylonian | N |
| Persian (Achaemenid) | N |
| Hellenistic | N |
| Early Roman | N |
| Late Roman/Byzantine | N |

### Outstanding items
- Records with empty fclasses after Phase 2: list (expect ≤2)
- Records needing manual `when{}`: see `phase-4-needs-manual-when.csv`
- Spot-check: show final fclasses, geometry type, certainty, and `when{}` for: Antioch (Syria), Jerusalem, Bethlehem, Babylon, Athens

---

## Verification

```python
with open('geo/working/phase-4-final.geojson') as f:
    out = json.load(f)

assert len(out) == 1055

# No string coordinates
string_coords = [
    fc['features'][0]['@id'] for fc in out
    if fc['features'][0].get('geometry')
    and fc['features'][0]['geometry'].get('coordinates') is not None
    and isinstance(fc['features'][0]['geometry']['coordinates'][0], str)
]
assert len(string_coords) == 0, f"String coords remain: {string_coords}"

# No lowercase 'point'
lower_point = [
    fc['features'][0]['@id'] for fc in out
    if fc['features'][0].get('geometry')
    and fc['features'][0]['geometry'].get('type') == 'point'
]
assert len(lower_point) == 0, f"Lowercase point remains: {lower_point}"

# No geometry missing certainty
missing_cert = [
    fc['features'][0]['@id'] for fc in out
    if fc['features'][0].get('geometry')
    and not fc['features'][0]['geometry'].get('certainty')
]
assert len(missing_cert) == 0, f"Missing certainty: {missing_cert}"

# No end at feature level
for fc in out:
    when = fc['features'][0].get('when', {})
    for ts in when.get('timespans', []):
        assert 'end' not in ts, \
            f"Feature-level end found: {fc['features'][0]['@id']}"

with_when = sum(1 for fc in out if fc['features'][0].get('when'))
without_when = sum(1 for fc in out if not fc['features'][0].get('when'))
print(f"with when{{}}: {with_when}")
print(f"without when{{}}: {without_when} (in needs-manual CSV)")
print("All assertions passed.")
```

---

## ✋ Stop here — deployment requires explicit approval

Present `geo/working/phase-4-report.md` to the user.

**Only overwrite `geo/bible-places.geojson` after the user explicitly approves the final output.**

When approved, deploy:

```bash
cp geo/working/phase-4-final.geojson geo/bible-places.geojson
git add geo/bible-places.geojson
git commit -m "LPF: fill fclasses, fix coordinates, add when{} (Pleiades + period inference)"
```
