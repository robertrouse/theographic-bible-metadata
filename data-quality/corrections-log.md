# Corrections log

A readable summary of what changed in the Theographic data, across every file: books, chapters, verses, people, people groups, places, events, definitions, and the GeoJSON in [`geo/`](../geo). Newest first.

Each month's notes are written from the [ledger](issues.yaml) entries fixed that month, plus any larger cleanups. Fixes are made in Airtable and reach `json/` and `CSV/` through the monthly [Airtable export](../.github/workflows/airtable-export.yml). Changes to `geo/` are made directly in this repository.

Found something that still looks wrong? [Open a data correction issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=data-correction.yml).

## November 2026

Fixed in Airtable on November 9, after that month's export. These changes reach `json/` and `CSV/` in the next export.

- **Events:** Eleven kings' start-to-start lags were one year too long (DQ-0048). Each lag had been entered as the "Nth year" in the text, but a lag is the number of years between the two start dates, and the start dates (which follow Jones) are N−1 years apart. Only the lag changed; start dates and predecessors are unchanged.
  - *Reign of Abijam* 18Y → 17Y, *Reign of Asa* 20Y → 19Y (after *Reign of Jeroboam I*)
  - *Reign of Joram* 18Y → 17Y (after *Reign of Jehoshaphat*)
  - *Reign of Ahaziah (Jehoahaz)* 12Y → 11Y, *Reign of Jehu* 12Y → 11Y (after *Reign of Joram*). Jehu's predecessor was changed from *Reign of Joash* to *Reign of Joram*, with a 12Y lag, earlier the same day (DQ-0006); the lag is now 11Y.
  - *Reign of Jehoahaz* 23Y → 22Y (after *Reign of Joash*)
  - *Reign of Jeroboam II* 15Y → 14Y (after *Reign of Amaziah*)
  - *Reign of Shallum* 39Y → 38Y, *Reign of Menahem* 39Y → 38Y, *Reign of Pekahiah* 50Y → 49Y, *Reign of Pekah* 52Y → 51Y (after *Reign of Uzziah*)

Exported in [#63](https://github.com/robertrouse/theographic-bible-metadata/pull/63).

- **Events:**
  - *Lifetime of Jacob* now lasts 147 years instead of 180, which was Isaac's age (DQ-0001).
  - *Lifetime of Abraham* now starts in 1996 BC (`-1995`), the same year as *Birth of Abraham* (DQ-0002).
  - *Death of Moses* is now 1451 BC (`-1450`), following Jones, Appendix I (DQ-0003).
  - *Death of Isaac* no longer lists itself as its predecessor. It now follows *Birth of Isaac*, with the same 180-year lag (DQ-0005).
  - Ten event titles were corrected, including *The Annunciation*, *The Transfiguration*, *Samson destroys Temple of Dagon*, and *Zacchaeus Converted and Parable of the Pounds* (DQ-0008, DQ-0022).
- **Places:** The three Mount of Olives records were merged into `mount_of_olives_861`. Its events and verses moved with it, and the duplicates `mount_of_olives_828` and `olivet_907` were removed. "Olivet" is now an alias, replacing an editor's note that had been stored as an alias (DQ-0011).
- **Verses:** Inline links in Zechariah 14:4, Luke 19:29, Luke 21:37 and Acts 1:12 now point at the merged Mount of Olives record.

## October 2026

The data was checked against Jones, Appendix F, and converted to ISO 8601 throughout:

- **Events:** 21 dates corrected to Jones, for example *Death of Adam* (3074 BC), *Birth of Abraham* (1996 BC), and *Judgeship of Jair* (1192 BC; previously mistyped as `-1991`). One calendar date was zero-padded, and *Death of Solomon* and *Death of Jotham* were linked to their participants.
- **People:** birth and death years set to Jones and converted to ISO. The Divided Monarchy kings previously used a different chronology (Thiele). Values that were impossible or that Jones does not support were removed. Examples are a birth year copied from a child's, a birth year equal to the record ID, and a birth year equal to the death year.
- **Verses:** `yearNum` converted to ISO.
