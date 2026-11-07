# Data-quality ledger

[`issues.yaml`](issues.yaml) records every known problem in the Theographic data in one place, whoever found it. Sources include:

- a careful reader;
- a project built on the data (such as a timeline poster);
- an automated consistency rule;
- a [data correction issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=data-correction.yml) on GitHub.

The data itself is still corrected in Airtable and published by the monthly [Airtable export](../.github/workflows/airtable-export.yml). This folder is outside `json/` and `CSV/`, so the export never overwrites it.

## How it fits with the rest of the repository

| Piece | Role |
|---|---|
| GitHub data correction issues | Where the public reports problems. Each report is copied into the ledger, and the entry's `github` field holds the issue number. |
| `data-quality/issues.yaml` | One entry per problem, with its status, evidence, and a check that can confirm the fix |
| Airtable | Where fixes are made |
| Monthly export pull request | Brings the fix into `json/` and `CSV/` |
| [Corrections log](../docs/chronology-and-dates.md#corrections-log) | Readable summary of what changed, written from the entries fixed that month |

Because the ledger is versioned with the data, a project pinned to a commit can read the list of known issues as of that commit.

## Entry lifecycle

1. **Add.** Copy the last entry and give the new one the next `DQ-####` id (ids are never reused).
   - Identify each record by its Airtable record id (`rec…`), which stays the same between exports, plus a readable key.
   - Record the commit you saw the problem at in `found.sha`.
2. **Research.** Use `status: needs-research` when the right value is not yet known, for example when two records disagree and either could be wrong.
3. **Fix in Airtable.** The change reaches this repository in the next export.
4. **Confirm.** When every assertion in `checks` passes on the exported JSON, set `status: fixed` and fill in `fixed.date` and `fixed.sha`. Entries with no checks (missing records, research items) are confirmed by hand.
5. **Close.** Close the linked GitHub issue, if there is one. Use `status: wontfix`, with a note, for reports that turn out to be intended, such as a one-year difference caused by the two year conventions explained in [Chronology and Dates](../docs/chronology-and-dates.md).

## Checks

Each check names a record, a field in the exported JSON, and one condition that is true once the problem is fixed. The condition is one of `equals`, `not_equals`, `contains`, `not_contains`, `matches` or `not_matches`. For example:

```yaml
checks:
  - { record: recTkocSMI0NxpIrw, field: duration, equals: "147Y" }
```

When an entry was found by a general rule, the `rule` field names it (for example `lifetime-matches-birth-death` or `predecessor-acyclic`). A future checker can then run those rules after each export and report only problems not already in the ledger.
