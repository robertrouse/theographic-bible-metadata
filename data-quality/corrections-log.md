# Corrections log

A readable summary of what changed in the Theographic data, across every file: books, chapters, verses, people, people groups, places, events, definitions, and the GeoJSON in [`geo/`](../geo). Newest first.

Each month's notes are written from the [ledger](issues.yaml) entries fixed that month, plus any larger cleanups. Fixes are made in Airtable and reach `json/` and `CSV/` through the monthly [Airtable export](../.github/workflows/airtable-export.yml). Changes to `geo/` are made directly in this repository.

Found something that still looks wrong? [Open a data correction issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=data-correction.yml).

## November 2026

Fixed in Airtable on November 16, after that day's export. These changes reach `json/` and `CSV/` in the next export.

- **People:** Four people linked to another person's Easton's Bible Dictionary entry now link to their own, or to none (DQ-0075). Each person's Easton text (`dictText`) follows the link.
  - *Medan* (`medan_1978`) now links to Easton's *Medan* instead of *Dedan 2*, and *Manasseh* son of Hezekiah (`manasseh_1930`) to *Manasseh 2* instead of *Manasseh 1* (son of Joseph).
  - *Asahiah* (`asahiah_324`) no longer links to *Isaiah 1*, and *Nathan* son of Attai (`nathan_2155`, 1 Chr 2:36) no longer links to *Nathan 1* (the prophet). Easton has no separate entry for either.
  - *Noah*, daughter of Zelophehad (`noah_2211`), still links to Easton's *Noah*, whose last paragraph describes her.
  - Four pairs still share one entry because Easton describes both people in it: *Aram* (`aram_285`, `aram_286`), *Gaius* (`gaius_1269`, `gaius_1271`), *Heman* (`heman_1488`, `heman_1489`) and *James* (`james_718`, `james_719`).
- **Easton:** `matchSlugs` now agrees with the people links on *Dedan 2* (`dedan_999`), *James 1* (`james_717`), *Nathan 1* (`nathan_2153`) and *Manasseh 2* (`manasseh_1930`). Their `matchType` was not changed; *Dedan 2* is still marked `unmatched` (DQ-0075).

Fixed in Airtable on November 16. Exported in [#101](https://github.com/robertrouse/theographic-bible-metadata/pull/101) (`6dc5de5`).

- **Events:** Ten new events (eventIDs 502–511) cover exile-era episodes Jones's Appendix F does not list (DQ-0070). Gedaliah's appointment and murder are two events. *Ahasuerus honors Mordecai* now follows *Esther goes before the king*, so the Esther events stay in order. Dates follow Jones, except *Daniel in the lions' den*, which follows Ussher (538 BC). *Ezra reads the Law* is dated 536 BC, the same month as *The altar is rebuilt*.
- **Verses:** Ahasuerus is now tagged on ten verses in Esther 5, and Nehemiah on eighteen verses in Nehemiah 13, including first-person pronouns (DQ-0070).
- **Definitions:** Draft definitions were added for *Birth of Joshua* and the ten new events.

- **Events:** *Reign of Jehoash* (Israel) now counts 39 years from the start of *Reign of Joash*, matching its sole reign in 840 BC (DQ-0043).
  - *Reign of Amaziah* now follows *Reign of Jehoash* with a 1-year lag, the synchronism in 2 Kgs 14:1 (Amaziah began in Jehoash's second year). The start date is unchanged (839 BC) (DQ-0040).
  - *Reign of Omri* now counts 27 years from the start of *Reign of Asa*, matching the year the army made him king (929 BC). The start date and 12-year duration are unchanged (DQ-0044).
  - *Death of Tibni* now follows *Reign of Asa* with a 31-year lag, the synchronism in 1 Kgs 16:23 (Omri began to reign over all Israel in Asa's 31st year, 925 BC). Omri, Tirzah and 1 Kgs 16:23 were added to the event. The title, start date and 1-day duration are unchanged (DQ-0044).
- **Verses:** Jer 37:5, 37:7 and 37:11 now tag Pharaoh-hophra (`pharaoh_2336`) instead of Pharaoh of the Exodus (`pharaoh_2331`). Jones, Chart Five p. 201a, identifies this Pharaoh as Hophra and cites Jer 37:5–11 (DQ-0060). Jer 43:9 and Ezek 30:24 remain on `pharaoh_2331` for a separate pass.
  - Jer 46:2 now tags Pharaoh-nechoh (`pharaoh-nechoh_2337`); the inline "Pharaoh-necho" links in mdText and richText were updated in the same edit (DQ-0061).

Fixed in Airtable on November 15. Exported in [#94](https://github.com/robertrouse/theographic-bible-metadata/pull/94) (`7797ffb`).

- **Events:** *Judgeship of Eli* now follows *Oppression by Ammon and Philistia*, and the stray 28-year FS lag was cleared. The start date is unchanged (1162 BC). Predecessors are for ordering (DQ-0046). In the same pass, 55 other events that had no predecessor were given the previous event in sequence, with no lag. Only *Creation* now lacks a predecessor.
  - *Birth of Joshua* was added (1534 BC, eventID 501). *Lifetime of Joshua* now starts in that year and follows the birth. *Death of Joshua* (1424 BC) now follows *Birth of Joshua*, with the same 110-year lag.
- **People:** *Joshua* (`joshua_1727`) now has a birth year of 1534 BC (`-1533`).
- **Events:** *Death of Joshua* now has a predecessor for its 110-year lag (*Birth of Joshua*), and *Lifetime of Joshua* ends at the stored death year, 1424 BC (DQ-0047). Exported in `7797ffb`.

Fixed in Airtable on November 14. These changes reach `json/` and `CSV/` in the next export.

- **Events:** 40 new events fill the gap between the first deportation and Nehemiah's return to Persia (606–442 BC), dated to Jones, Appendix F (DQ-0054). Each has verses, participants, locations and predecessor/lag links.
  - Four framing spans: *Babylonian Captivity* (606–536 BC), *Return from Exile* (536–440 BC), *Reign of Darius (Ahasuerus)* and *Reign of Artaxerxes*. *Reign of Nebuchadnezzar* and *Construction of the Second Temple* are also new spans.
  - The three deportations, *Fall of Jerusalem* (586 BC), *Fall of Babylon* (539 BC), *Cyrus decrees the rebuilding of the Temple* and *Exiles return with Zerubbabel* (536 BC), and *Second Temple dedicated* (516 BC).
  - Esther (*Esther is made queen*, *Haman plots to destroy the Jews*, *Haman is hanged*, *The Jews defeat their enemies*), Ezra (*Ezra leads exiles to Jerusalem*, *Exiles put away their foreign wives*) and Nehemiah (from *Nehemiah mourns for Jerusalem* to *Nehemiah goes back to Artaxerxes*).
- **People:** *Azariah* (`azariah_545`), Daniel's companion, now lists his Babylonian name Abed-nego as an alias, like *Shadrach* (Hananiah) and *Meshach* (Mishael). His disambiguation note, which wrongly said Meshach, now reads "Azariah (Abed-nego)" (DQ-0069).
- **Places:** Coordinates now come from the place's canonical record first, then Pleiades (where it confidently matches), then OpenBible. The Recogito points are no longer used. *Iconium* now sits at the city (Pleiades 648647) instead of 37 km north of it, and *Paphos* at Nea Paphos (Pleiades 707586) instead of Palaepaphos. Nine more places were reviewed one by one, and 29 aliases now show their canonical place's point. New fields record each place's Pleiades and OpenBible links (DQ-0064).

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
