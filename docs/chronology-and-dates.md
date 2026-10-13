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
- [Corrections log](#corrections-log)

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

Every year field in Theographic uses **ISO 8601 astronomical year numbering**, which includes a year 0:

| Year | Stored as |
|---|---|
| 4004 BC | `-4003` |
| 1 BC | `0` |
| AD 1 | `1` |
| AD 30 | `30` (or `0030-…` in a calendar date) |

This applies to `events.startDate`, `events.sortKey`, `people.birthYear`, `people.deathYear`, `people.minYear`, `people.maxYear`, and `verses.yearNum`. Since October 2026, people and verse years can be compared directly with event dates.

### Converting

**ISO → BC/AD:** for a value ≤ 0, the BC year is `1 - value` (`-4003 → 4004 BC`, `0 → 1 BC`). A positive value is already an AD year.

**BC → ISO:** `1 - BC year` (`1571 BC → -1570`).

```python
def iso_to_label(year: int) -> str:
    return f"{1 - year} BC" if year <= 0 else f"AD {year}"

def bc_to_iso(bc_year: int) -> int:
    return 1 - bc_year
```

> **Data exported before October 2026** stored people's `birthYear`/`deathYear` and `verses.yearNum` as BC years with a minus sign (`-4004` = 4004 BC). If you have an older copy, add 1 to its negative values to convert.

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

| Field | Coverage | Notes |
|---|---|---|
| `birthYear` | 70 of 3,067 people | String in JSON/CSV; the GraphQL API returns an `Int` |
| `deathYear` | 61 of 3,067 people | |
| `minYear` / `maxYear` | All people | Working fields rolled up from the `yearNum` of the verses that mention the person, used to align people with the timeline. They are not birth or death dates. |

Birth and death years come from Jones, Appendix F. They are recorded only where his chronology fixes them: the patriarchs, Moses and Aaron, the judges' era, and the kings. For example, David has `birthYear: "-1084"` and `deathYear: "-1014"`, which are Jones's 1085 BC and 1015 BC. Every person's years equal the dates of their *Birth of…* and *Death of…* events.

**Kings' death years** that Appendix F does not list explicitly are set to the successor's accession year from Appendix F. Under the accession-year method Jones uses, a king's last year is his successor's accession year.

## Verse years (`yearNum`)

`verses.yearNum` assigns an approximate year to 28,024 of 31,102 verses (`Gen.1.1 → -4003`). It comes from the marginal dates in *Torrey's Treasury of Scripture Knowledge*, which follow **Ussher**, not Jones.

Because the source is Ussher, `yearNum` can differ from the events timeline. The largest difference is in the New Testament: `Acts.2.1` has `yearNum: 33` (Ussher's crucifixion year), but the Pentecost event is dated AD 30. Use `yearNum` for rough placement of passages, and use the events table when the timeline needs to follow Jones.

## Book dates (`yearWritten`)

`books.yearWritten` is a string year (for example, Romans → `"57"`). It is populated for 21 of the 66 books. It is an approximate composition date and not part of the Jones events timeline.

## Corrections log

**October 2026.** The data was checked against Jones, Appendix F, and converted to ISO 8601 throughout:

- **Events:** 21 dates corrected to Jones, for example *Death of Adam* (3074 BC), *Birth of Abraham* (1996 BC), and *Judgeship of Jair* (1192 BC; previously mistyped as `-1991`). One calendar date was zero-padded, and *Death of Solomon* and *Death of Jotham* were linked to their participants.
- **People:** birth and death years set to Jones and converted to ISO. The Divided Monarchy kings previously used a different chronology (Thiele). Values that were impossible or that Jones does not support were removed. Examples are a birth year copied from a child's, a birth year equal to the record ID, and a birth year equal to the death year.
- **Verses:** `yearNum` converted to ISO.

Found something that still doesn't match Jones? [Open a data correction issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=data-correction.yml).
