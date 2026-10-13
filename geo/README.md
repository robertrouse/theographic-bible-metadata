# geo/ — Bible Places in Linked Places Format

`bible-places.geojson` is one GeoJSON FeatureCollection of 1,030 biblical
places (every one with at least one verse reference) in [Linked Places Format (LPF)](https://github.com/LinkedPasts/linked-places-format),
validated against the World Historical Gazetteer LPF schema v1.2.2. It merges
[Digital Manna](https://www.digitalmanna.org), [Theographic](../json/places.json),
[OpenBible.info](https://github.com/openbibleinfo/Bible-Geocoding-Data),
[Pleiades](https://pleiades.stoa.org), Wikidata and
[PeriodO](https://perio.do). `example-output.json` is the gold-standard record
(Antioch of Syria) from the project spec.

## What each feature has

| Member | Content |
|---|---|
| `@id` | `https://bible.helloao.org/api/c/places/<Digital Manna slug>.json` (API not live yet) |
| `properties.title` | Unique. Biblia title from OpenBible, else the Digital Manna name |
| `properties.fclasses` | LPF classes H, L, P, R, S, T (never A; regions are L) |
| `geometry` | Point `[lon, lat]` with `certainty` from OpenBible's score (≥ 500 `certain`, else `less-certain`). Unknown locations are an empty GeometryCollection |
| `when` | Start only. The earliest ancient Pleiades attestation, or the earliest biblical mention (Theographic chronology) with its PeriodO period when the Bible is over 300 years earlier |
| `names` | Every name with citations: Digital Manna, Theographic, OpenBible, and Pleiades (ancient attestations with language). An alias carries its own `when` from the verses that use it, e.g. Azotus (Acts) under Ashdod |
| `relations` | Dated "part of" (`gvp:broaderPartitive`) and "near" (`gvp:tgn3000_related_to`) links to other features, with certainty and verse citations: cities in tribal territories (Joshua's allotment lists), sites in Jerusalem, NT cities in Roman regions (Digital Manna), territories in the kingdoms |
| `links` | `seeAlso` to Digital Manna, Theographic, OpenBible, Pleiades, Wikidata |

Kingdoms (United Kingdom of Israel, Northern Kingdom of Israel, Kingdom of
Judah) are features too: their `when` has a start and an end, their geometry is
a MultiPoint of their member territories, and each member carries a dated
"part of" relation.

One feature is one real place. Places the sources split by name (Accho and
Ptolemais, En-gedi and Hazazon-tamar) are merged, and the other names become
dated aliases.

## Rebuilding

Requirements: Python 3.8+, internet access, and an authenticated `gh` CLI with
read access to the private `digitalmanna/stewards_data` repo. Validation also
needs `pip install jsonschema`.

```bash
geo/pipeline/run_all.sh            # add --refresh to re-download sources
python3 geo/pipeline/phase10_validate.py
cp geo/working/phase-9b-output.geojson geo/bible-places.geojson
```

Everything is written to `geo/working/` (not committed). Nothing overwrites
`bible-places.geojson` until the copy step.

| Step | Script | Does |
|---|---|---|
| fetch | `fetch_sources.py` | Caches DM places, OpenBible, Wikidata→Pleiades, Pleiades dumps |
| 5 | `phase5_crosswalk.py` | Joins DM, Theographic, OpenBible, Tyndale, Pleiades, Wikidata IDs; writes review lists |
| 6 | `phase6_rebuild.py` | Applies `decisions.json`; builds features with title, fclasses, geometry, links |
| 8 | `phase8_pleiades.py` | Validates and expands Pleiades links; finds earliest ancient attestations |
| 7 | `phase7_names.py` | Builds `names[]` (runs after 8, since it uses the final Pleiades links) |
| 9 | `phase9_when.py` | Feature `when{}` from Pleiades, Theographic and PeriodO |
| 9b | `phase9b_relations.py` | "part of" / "near" relations; kingdom dates and geometry |
| 10 | `phase10_validate.py` | Structure, WHG LPF schema, and HTTP check of every link |

## Curated inputs (committed)

| File | Purpose |
|---|---|
| `decisions.json` | Human decisions: merges, keep-separates, orphan assignments, exclusions, Pleiades picks, titles, fclasses, coordinates, dates, anchor verses, kingdoms, Joshua allotment ranges, and curated part-of/near pairs. Each says who made it. Edit and re-run |
| `pipeline/periodo_neaehl.json` | Holy Land periods from PeriodO (Stern, *NEAEHL*, 1993) |
| `legacy/bible-places-2026-03.geojson` | The March 2026 file, read for old `@id`s, fclasses and coordinates |

## Review files

Each phase writes a report (`phase-N-report.md`) and CSVs with an empty
`decision` column for anything it would not decide on its own:
`phase-5-review-*.csv`, `phase-6-review-coordinates.csv`,
`phase-8-review-pleiades.csv`, `phase-9-review-pleiades-later.csv`,
`phase-10-broken-links.csv`. Open items are tracked in `NOTES.md`.

`agent-instructions/` holds the instructions for the original phases 1–4
(March 2026), kept for history; the pipeline above replaces them.
