# geo/ — Bible Places Geospatial Data

This folder contains `bible-places.geojson` — 1,055 biblical place records being conformed to [Linked Places Format (LPF) v1.1](https://github.com/LinkedPasts/linked-places-format).

---

## What the process does

Adds three missing elements to every record:

| Field | Status before | Goal |
|---|---|---|
| `fclasses[]` | 106 records empty | All filled from featureType/OpenBible data |
| `geometry.certainty` | Missing on some records | Present on every geometry object |
| `geometry.coordinates` | Stored as strings | Converted to numeric `[lon, lat]` |
| `geometry.type` | Lowercase `"point"` | Capitalized `"Point"` |
| `when{}` | Missing on all records | Added from Pleiades or standard period inference |

> **Out of scope for now:** `names[]`, URL validation.

---

## Prerequisites

- Python 3.8+
- Internet access (for fetching OpenBible and Pleiades data)
- Source files present: `json/places.json`, `json/events.json`
- A Claude agent (or other capable LLM) to execute each phase

---

## How to run

Hand the appropriate instruction file from `geo/agent-instructions/` to a Claude agent and ask it to execute the phase. **Review the output report before proceeding to the next phase.**

### Phase order

| Phase | Instruction file | What it does |
|---|---|---|
| 1 | `phase-1-audit.md` | Build cross-reference table; fetch and cache OpenBible data |
| 2 | `phase-2-fclasses-geometry.md` | Fix `fclasses`, `certainty`, coordinate format, null geometry |
| 3 | `phase-3-when-pleiades.md` | Add `when{}` from Pleiades attestation dates (~105 records) |
| 4 | `phase-4-when-fallback.md` | Add `when{}` via ANE period inference for remaining records; produce final geojson |

### Running a phase

Example prompt to give an agent:

> Read `geo/agent-instructions/phase-1-audit.md` and execute all steps. Work from the repo root. When done, present the report and wait for approval before proceeding.

---

## Review workflow

Each phase:
1. Writes intermediate output to `geo/working/` (never overwrites source files)
2. Writes a markdown report (e.g. `geo/working/phase-1-report.md`)
3. **Pauses for your review** before the next phase begins

Read the report. If results look correct, tell the agent to proceed to the next phase. If something looks wrong, investigate before continuing.

---

## Intermediate files

All working files appear in `geo/working/`:

```
geo/working/
  phase-1-crossref.json           # geojson ↔ places.json cross-reference
  openbible-cache.json            # Cached OpenBible API responses
  phase-1-report.md

  phase-2-output.geojson
  phase-2-report.md

  pleiades-cache.json             # Cached Pleiades JSON responses
  phase-3-output.geojson
  phase-3-no-when.csv             # Records still missing when{} after Phase 3
  phase-3-report.md

  phase-4-final.geojson           # ← Final output for approval
  phase-4-needs-manual-when.csv   # Records with no events/Pleiades — need manual when{}
  phase-4-report.md               # ← Cross-phase summary
```

---

## Finalizing

After reviewing and approving `geo/working/phase-4-report.md`, tell the agent to deploy:

```bash
cp geo/working/phase-4-final.geojson geo/bible-places.geojson
git add geo/bible-places.geojson
git commit -m "LPF: fill fclasses, fix coordinates, add when{} (Pleiades + period inference)"
```

**Do not run this step until you have explicitly approved the Phase 4 output.**

---

## Reference files

| File | Purpose |
|---|---|
| `geo/bible-places.geojson` | Source data (read-only until Phase 4 approval) |
| `geo/example-output.json` | Gold standard completed record (Antioch of Syria) |
| `geo/certainty-check.json` | Records with empty fclasses or null geometry |
| `geo/agent-instructions/README.md` | Technical reference for agents (matching key, API notes) |
| `json/places.json` | Place records with featureType, placeID, eventsHere |
| `json/events.json` | Events with startDate for when{} period inference |
