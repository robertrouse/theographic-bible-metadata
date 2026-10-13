# Airtable sync (Phase 11)

Mirrors the one-place-many-names model of `geo/bible-places.geojson` into the
Airtable `places` table (base `app5UK4s70d5PwupX`). The sync only adds: a
`canonicalPlace` link on records that are another name of a place, and new
records for places Digital Manna has and Theographic lacks.

| File | Purpose |
|---|---|
| `phase-11-plan.md` / `.json` | The change set (built by `geo/pipeline/phase11_airtable_plan.py`) |
| `phase-11-applied.json` | Log of every write as applied: record, field, before, after |
| `phase-11-rollback.json` | Reverse operations (built by `geo/pipeline/phase11_airtable_rollback.py`) |

## Applying

The token needs `data.records:write`, and `schema.bases:write` to create the
`canonicalPlace` field. Without that scope, first add the field in the Airtable
UI: name `canonicalPlace`, type *Link to another record* → `places`. The API
cannot create the field as single-link; every value the sync writes is one
record, and *Allow linking to multiple records* can be turned off in the UI.

```bash
AIRTABLE_TOKEN=pat... python3 geo/pipeline/phase11_airtable_apply.py --dry-run
AIRTABLE_TOKEN=pat... python3 geo/pipeline/phase11_airtable_apply.py
```

Each write is logged as soon as it succeeds; re-running resumes where it stopped.

## Rolling back

```bash
AIRTABLE_TOKEN=pat... python3 geo/pipeline/phase11_airtable_apply.py --rollback
```

This builds `phase-11-rollback.json` from the log, restores every changed
field to its logged value and deletes the records the sync created. Then
delete the `canonicalPlace` field in the Airtable UI; the API cannot delete
fields. Airtable also created the reverse side of the link, "From field:
canonicalPlace" (on each canonical record, the list of its other-name
records); delete it too, under whatever name it has by then.

Full snapshot of the table before any change: `json/places.json` at git tag
`airtable-places-backup-2026-10-13` (commit `bc4c1f1`). No record had been
modified in Airtable after that export.
