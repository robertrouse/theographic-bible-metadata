# bible-places.geojson — Agent Instructions

## Goal

Complete `geo/bible-places.geojson` to full conformance with the [Linked Places Format (LPF) v1.1](https://github.com/LinkedPasts/linked-places-format). The source document governing field rules is the Theographic spec PDF ("Combine and reformat geo data sources").

## Reference Example

`geo/example-output.json` contains the fully-completed Antioch (Syria) record. Use it as your gold standard for output structure.

## Source Files

| File | Description |
|---|---|
| `geo/bible-places.geojson` | **Read-only** until Phase 6 is approved. 1,055 records. |
| `json/places.json` | 1,274 place records: featureType, featureSubType, placeID, eventsHere, kjvName, esvName, recogitoUri, dictText |
| `json/events.json` | 450 event records: startDate, duration, locations, eventsHere |
| `geo/example-output.json` | Target format reference |
| `geo/working/` | All intermediate outputs go here — never overwrite the source |

## Matching Key: Linking geojson ↔ places.json

Each geojson feature has a theographic link in `links[]`:
```
https://theographic.netlify.app/place/abel-beth-maachah_5
```
Extract the numeric ID at the end (`5`) — this is the `placeID` in `places.json`.

```python
import re
def get_place_id(feature):
    for link in feature.get('links', []):
        if 'theographic.netlify' in link['identifier']:
            m = re.search(r'_(\d+)$', link['identifier'].split('/place/')[-1])
            if m:
                return int(m.group(1))
    return None
```

~1,049 of 1,055 records match this way. The ~6 without theographic links will be flagged.

## External APIs

### OpenBible
- ID is in the existing link: `https://www.openbible.info/geo/ancient/{id}`
- Bulk data download available at: `https://www.openbible.info/geo/`
  - Look for a TSV/CSV/JSON bulk file. Preferred over per-record fetching.
- Key fields needed: `best_path_score`, `translation_name_counts`, `s7f5356` (Biblia title)

### Digital Manna
- URL pattern: `https://www.digitalmanna.org/encyclopedia/places/{slug}`
- Fetch the page and extract the `names` field from the JSON-LD or API response
- Agent should inspect the page structure to find the right extraction method

### Pleiades
- JSON endpoint: `https://pleiades.stoa.org/places/{id}/json`
- Extract: `names[]` (with `romanized`, `language`, `start`, `end` per name), `timePeriodsKeys`
- Be respectful: add a delay between requests (0.5s), cache results in `geo/working/pleiades-cache.json`

## fclasses Mapping (Authoritative)

> **"A" is never used.** Use "L" for all countries, regions, and administrative areas.

| LPF Code | Applies To | Notes |
|---|---|---|
| **H** | Rivers, lakes, seas, canals, springs, wadis | Pools and wells → S (man-made) |
| **L** | Regions, countries, provinces, people-group territories | Primary for large geographic areas |
| **P** | Cities, towns, villages, settlements | **Default for most Bible places** |
| **R** | Roads, routes | Paul's missionary routes, named roads |
| **S** | Altars, campsites, fortifications, gardens, gates, halls, mines, pools, rooms, stone heaps, structures, trees, wells | Temple, Jerusalem sites, etc. |
| **T** | Mountains, valleys, cliffs, fields, fords, forests, hills, islands, passes, ridges, rocks | Most natural landforms |

## Working File Conventions

Each phase writes to `geo/working/`:

```
geo/working/
  phase-1-audit.csv
  phase-1-no-pleiades.csv
  phase-1-duplicate-coords.csv
  phase-1-report.md
  openbible-cache.json         ← cached OpenBible data
  phase-2-output.geojson
  phase-2-report.md
  phase-3-output.geojson
  phase-3-duplicate-coords.csv
  phase-3-report.md
  pleiades-cache.json          ← cached Pleiades data
  phase-4-output.geojson
  phase-4-no-pleiades-when.csv
  phase-4-report.md
  phase-5-output.geojson
  phase-5-needs-manual-when.csv
  phase-5-report.md
  phase-6-final.geojson        ← final output for user approval
  phase-6-report.md
```

**Never overwrite `geo/bible-places.geojson`** until the user explicitly approves Phase 6 output.

## Verification (run after every phase)

```python
import json
data = json.load(open('geo/working/phase-N-output.geojson'))
print(f"Records: {len(data)}")  # Must be 1055

# Spot-check known places
titles = {fc['features'][0]['properties']['title']: fc for fc in data}
for name in ['Jerusalem', 'Bethlehem', 'Rome', 'Babylon']:
    print(f"{name}: {name in titles}")
```

## Phase Order

Run phases in sequence. Wait for user approval before starting the next phase.

1. **[Phase 1](phase-1-audit.md)** — Audit + OpenBible data collection
2. **[Phase 2](phase-2-fclasses-geometry.md)** — fclasses + geometry fixes
3. **[Phase 3](phase-3-names.md)** — names[] from DM, OpenBible, Pleiades
4. **[Phase 4](phase-4-when-pleiades.md)** — when{} from Pleiades
5. **[Phase 5](phase-5-when-events-fallback.md)** — when{} fallback (events + period)
6. **[Phase 6](phase-6-validation.md)** — URL validation + final merge
