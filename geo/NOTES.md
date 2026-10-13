# geo/bible-places.geojson — Open Items

**Last updated:** 2026-10-13
**State:** LPF pipeline phases 5–10 complete (`geo/pipeline/`). 1,030 features,
all valid against the WHG LPF schema v1.2.2, all with `names[]` and `when{}`.

## 1. Airtable (Phase 11, next)

Conform the Airtable `places` table to the one-place-many-names model in
`decisions.json`: link each alias record to its canonical place, add the
Digital Manna ID, and add records for places DM has and Theographic lacks
(tribal territories, the kingdoms, Misgab, Parbar, and others listed under
`dm_needs_theographic_record`). Draft the changes and approve them before any
write.

## 2. Digital Manna corrections to make upstream

- Bethlehem entries `places-0278` and `places-1090` have lost their
  Theographic IDs (#218, #220 and #219); Tahtim-hodshi (#662) is filed under
  Kadesh-barnea instead of `places-1279`. The pipeline fixes these through
  `decisions.json`.
- 35 DM coordinates are not any OpenBible identification and some are clearly
  off (Kidron 44 km, Gilgal 57 km, Seba on Addis Ababa). The pipeline uses
  OpenBible's point for them: `working/phase-6-review-coordinates.csv`.
- One DM entry stores two Theographic IDs in one string (`"421, 1010"`).
- 34 DM pages linked from the file are not live on digitalmanna.org yet (new
  entries such as the tribal territories, and renamed slugs such as
  `appii-forum`): `working/phase-10-broken-links.csv`. Every other link
  resolves (4,086 of 4,120). digitalmanna.org answers HEAD with 404, so link
  checkers must use GET.

## 3. Review lists with open candidates

- `working/phase-8-review-pleiades.csv`: 92 Pleiades candidates not applied,
  11 applied matches with borderline names. Accept with `pleiades_add`, refuse
  with `pleiades_reject` in `decisions.json`.
- `working/phase-9-review-pleiades-later.csv`: 94 places whose biblical date
  replaced a Pleiades start over 300 years later. Set `PLEIADES_FIRST = True`
  in `phase9_when.py` to prefer Pleiades instead.
- `working/phase-5-review-shared-coordinates.csv`: 83 groups of places sharing
  one point by coincidence, likely placeholder coordinates.

## 4. Known approximations

- Places mentioned only in undated verses take the nearest dated verse's
  year (labelled). The Numbers 33 campsites all get -1451 from Numbers 32,
  late for the early stations.
- Dates follow Theographic's chronology (early Exodus); PeriodO labels follow
  from those years.
- Five places have no known location (Biziothiah, Edrei of Naphtali, Judah,
  Nebaioth, Nod) and carry an empty GeometryCollection.
- `certainty` is never `uncertain`; the spec left that tier undefined.

## 5. Not done yet

- `@id` URLs point to bible.helloao.org endpoints that do not exist yet (on hold).
- Original-script names (Hebrew/Greek forms in DM's CMS cache) are not in `names[]`.
