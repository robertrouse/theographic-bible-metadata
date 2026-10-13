# Chronology and Dates

This page explains where Theographic's dates come from and how to read every date-bearing field in the dataset. Read it before you build a timeline, sort records by year, or compare a person's dates with event dates.

## Table of Contents
- [Source: Dr. Floyd Nolen Jones](#source-dr-floyd-nolen-jones)
- [Anchor dates](#anchor-dates)
- [Year numbering conventions](#year-numbering-conventions)
- [Events timeline fields](#events-timeline-fields)
- [People dates](#people-dates)
- [Verse years (`yearNum`)](#verse-years-yearnum)
- [Book dates (`yearWritten`)](#book-dates-yearwritten)
- [Known chronology issues](#known-chronology-issues)

## Source: Dr. Floyd Nolen Jones

The timeline in Theographic's **events** table and the birth and death years in the **people** table follow the chronology of **Dr. Floyd Nolen Jones** (Th.D., Ph.D.):

> Jones, Floyd Nolen. *The Chronology of the Old Testament: A Return to the Basics.* Green Forest, AR: Master Books. First edition 1993; Master Books edition 2004 (LCCN 2004106969); 23rd edition 2026 (ISBN 978-1-61458-210-6, digital).

- Free PDF from the author's ministry: [The Chronology of the Old Testament (PDF)](https://floydnolenjonesministries.com/wp-content/uploads/2026/07/floydnolenjonesministries_com_files_131144963.pdf)
- Jones's chronology charts and related studies: [floydnolenjonesministries.com/chronology](https://floydnolenjonesministries.com/chronology/)

Jones builds on Archbishop James Ussher's *Annals of the World* (1650–54) and works only from the biblical text (Authorized/King James Version). For most of the Old Testament he agrees with Ussher to within a year. Where the two differ, Theographic's events and people follow Jones.

**New Testament.** Gospel events use the same framework: Jesus's birth around 4 BC and the crucifixion in AD 30, both as Jones gives them. Event dates in the **Book of Acts** come from timelines provided by **Todd Atwood, ThM**, and use the same AD 30 crucifixion anchor. If you want Jones's own treatment of Acts, see his *Acts Chronology* on the chronology page linked above.

## Anchor dates

Use the dates below to check whether a record follows Jones. Each one appears in Jones's text and matches the `events` table.

| Event | Jones | `events.startDate` (ISO) |
|---|---|---|
| Creation | 4004 BC | `-4003` |
| The Flood begins | 2348 BC | `-2347` |
| Birth of Isaac | 1896 BC | `-1895` |
| Exodus from Egypt | 1491 BC | `-1490` |
| Construction of Solomon's Temple begins | 1012 BC | `-1011` |
| Death of Solomon | 975 BC | `-974` |
| Crucifixion and Burial | AD 30 | `0030-04-04` |

## Year numbering conventions

> ⚠️ **Not every field uses the same convention.** Events use ISO 8601 astronomical years. People birth and death years and verse years use the historian's BC year with a minus sign. For the same year, the two values differ by 1.

| Convention | Used by | 4004 BC is stored as | 1 BC is stored as | AD 30 is stored as |
|---|---|---|---|---|
| **ISO 8601 astronomical** (year 0 exists) | `events.startDate`, `events.sortKey` | `-4003` | `0` | `30` / `0030-…` |
| **Negated BC year** (no year 0) | `people.birthYear`, `people.deathYear`, `people.minYear`, `people.maxYear`, `verses.yearNum` | `-4004` | `-1` | `30` |

### Converting

**ISO astronomical → BC/AD.** For a value ≤ 0, BC year = `1 - value`; for example, `-4003 → 4004 BC` and `0 → 1 BC`. A positive value is already an AD year.

**Negated BC → BC/AD.** For a negative value, BC year = `-value`; for example, `-1571 → 1571 BC`. A positive value is already an AD year.

**Negated BC → ISO astronomical** (to put people dates on the same axis as events): if the value is negative, add 1. For example, Moses's `birthYear` of `-1571` becomes `-1570` on the events axis.

```python
def negated_bc_to_iso(year: int) -> int:
    return year + 1 if year < 0 else year

def iso_to_label(year: int) -> str:
    return f"{1 - year} BC" if year <= 0 else f"AD {year}"
```

## Events timeline fields

The **events** table (`json/events.json`, `CSV/Events.csv`) holds 450 events: 247 in the Old Testament and 203 in the New, including 81 from Acts. Every event has a `startDate`.

| Field | Format | Notes |
|---|---|---|
| `startDate` | string | One of two forms: an ISO astronomical **year** (`"-4003"`, `"-974"`, `"9"`) or an ISO **calendar date** `YYYY-MM-DD` (`"0030-04-04"`). Calendar dates are used where the text supports a specific day, mostly in the Passion Week and Acts. |
| `duration` | string | A number followed by a unit: `D` days, `W` weeks, `M` months, `Y` years. Examples: `"7D"`, `"40Y"`. |
| `predecessor` | array of record IDs | The event this one follows. Together with `lag` and `lagType`, these fields define the dependency chain the dates were calculated from. |
| `lag` | string | Time between the predecessor and this event, in the same format as `duration` (for example, `"130Y"`). |
| `lagType` | string | `FS` (finish-to-start): this event starts `lag` after the predecessor **finishes**. `SS` (start-to-start): it starts `lag` after the predecessor **starts**. |
| `partOf` | array of record IDs | Parent event, for events nested inside a larger narrative such as a lifetime or a journey. |
| `rangeFlag` | boolean | `true` when the year is an approximation rather than a fixed date. Six events currently carry this flag, including the Tower of Babel. |
| `sortKey` | float | Chronological sort key: the start year plus a verse-order fraction, so events in the same year sort in canonical order. In Airtable it is calculated as `INT(year) + INT(verseSort)/100000000`. |
| `verseSort` | string | `verseID` of the event's first verse (`BBCCCVVV`). |

**Computing an end date:** add `duration` to `startDate`. Durations given in years or months are approximate by nature, so treat the computed end date as a timeline position, not an exact date.

## People dates

| Field | Coverage | Convention |
|---|---|---|
| `birthYear` | 75 of 3,067 people | Negated BC year (string in JSON/CSV; the GraphQL API returns an `Int`) |
| `deathYear` | 64 of 3,067 people | Negated BC year |
| `minYear` / `maxYear` | All people | Negated BC year. These are working fields that bound the span of a person's verses, used to align people with the events timeline. They are not birth or death dates. |

Birth and death years exist mainly for the patriarchs, judges, kings, and other people whose dates can be calculated from the text using Jones. For example, David has `birthYear: "-1085"` and `deathYear: "-1015"`, which are Jones's 1085 BC and 1015 BC.

## Verse years (`yearNum`)

`verses.yearNum` assigns an approximate year to 28,024 of 31,102 verses. It comes from the marginal dates in *Torrey's Treasury of Scripture Knowledge*, which follow **Ussher**, not Jones. It uses the negated-BC convention (`Gen.1.1 → -4004`).

Because the source is Ussher, `yearNum` can differ from the events timeline. The largest difference is in the New Testament: `Acts.2.1` has `yearNum: 33` (Ussher's crucifixion year), but the Pentecost event is dated AD 30. Use `yearNum` for rough placement of passages, and use the events table when the timeline needs to follow Jones.

## Book dates (`yearWritten`)

`books.yearWritten` is a string year (for example, Romans → `"57"`). It is populated for 21 of the 66 books. It is an approximate composition date and not part of the Jones events timeline.

## Known chronology issues

The issues below were found while reviewing the October 2026 data export. Corrections belong in the Airtable source. Please [open an issue](https://github.com/robertrouse/theographic-bible-metadata/issues) if you find more.

| Record | Issue |
|---|---|
| Event *Birth of Abraham* | `startDate` is `-1996` (1997 BC). Jones gives 1996 BC, which is `-1995` in ISO. |
| Person `abraham_58` | `birthYear` is `-1997`. Jones gives 1996 BC, which is `-1996` in the negated-BC convention. |
| Person `moses_2108` | `deathYear` is `-1452`. Jones gives 1451 BC (Moses was born in 1571 BC and died at 120), which is `-1451`. |
| Person `seth_2504` | `deathYear` is `-2692`; it appears to be a transposition of `-2962`. Seth was born in 3874 BC and lived 912 years, so he died in 2962 BC. |
| Event *Feast of Tabernacles* | `startDate` is `"0029-10-9"`. It should be zero-padded: `"0029-10-09"`. |
| People ↔ events | Some *Birth of…* and *Death of…* events link to a person whose `birthYear`/`deathYear` differs by more than the 1-year convention offset. Examples are the kings Saul, Abijam, Asa, and Jehoshaphat. Check `participants` before relying on those links. |
