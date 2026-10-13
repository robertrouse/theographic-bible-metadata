# geo/bible-places.geojson — Open Items

**Last updated:** 2026-03-05
**Current state:** Phase 4 complete (commit 9497ac2). 1,054 records.

---

## 1. when{} — 851 records need manual assignment

851 records have no `when{}` because they have neither a Pleiades link nor any associated events in `events.json`. They are listed in:

```
geo/working/phase-4-needs-manual-when.csv
```

Fields: `geo_id`, `title`, `fclasses`, `pleiades_id`, `events_here_count`, `reason`

Possible approaches:
- Add more events to `events.json` and re-run Phase 4 period inference
- Cross-reference against external gazetteers (Geonames, OpenBible, DARE)
- Manual assignment using PeriodO period URIs for scholarly attestation

---

## 2. Mount Nebo — suspect Pleiades ID

Mount Nebo has a 9-digit Pleiades ID (`563265622`) which is unusually large compared to the typical 5–7 digit range used by Pleiades. This produced a `when` start year of **1700 AD**, which is almost certainly a late attestation or data quality issue in the source geojson rather than a meaningful historical date.

**Action needed:** Verify the correct Pleiades ID for Mount Nebo (likely `687968` or similar) and update the record's `links[]` array, then re-run Phase 3 for that record.

---

## 3. names[] enrichment — deferred

The `names[]` array on each record has not been enriched. Potential sources:
- Theographic DM data (KJV names, alternate spellings)
- OpenBible place names
- Pleiades `names[]` array (already cached in `geo/working/pleiades-cache.json` for 102 records)

This was explicitly out of scope for the Phase 1–4 run and should be treated as a separate project phase.

---

## 4. URL validation — deferred

Links in `links[]` have not been validated. Some Pleiades IDs may be stale or incorrect (see item 2 above). This was explicitly out of scope for the Phase 1–4 run.
