# Corrections log

A readable summary of what changed in the Theographic data, across every file: books, chapters, verses, people, people groups, places, events, definitions, and the GeoJSON in [`geo/`](../geo). Newest first.

Each month's notes are written from the [ledger](issues.yaml) entries fixed that month, plus any larger cleanups. Fixes are made in Airtable and reach `json/` and `CSV/` through the monthly [Airtable export](../.github/workflows/airtable-export.yml). Changes to `geo/` are made directly in this repository.

Found something that still looks wrong? [Open a data correction issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=data-correction.yml).

## November 2026

Fixed in Airtable on November 24. These changes reach `json/` and `CSV/` in the next export. GeoJSON is unchanged (DQ-0072 remains on hold), so for now it still shows points for the 20 places cleared below.

- **Places:** 114 places that sat on points shared with unrelated places (for example, Simeon's towns plotted in Gilead and a dozen wilderness stations on one spot) now have their own coordinates (DQ-0109). Each was checked against OpenBible's candidates, Pleiades, the revised TIPNR, Easton and the verses' context.
  - 108 use their own OpenBible point, which also matches the GeoJSON.
  - Three now link to Pleiades and display its point, each a confident name match at the same site: *Jotbah* (`jotbah_655`, Pleiades 678201 Iotapata, at Yodfat), *Punon* (`punon_961`, 697726 Phaino, at Feinan, on the Num 33:42-43 route) and *Kamon* (`kamon_665`, 678218 Kamous, at Qamm).
  - Three use a different OpenBible identification that fits the verses better: *Adithaim* (`adithaim_26`, Khirbet Kheishum; it is listed with Socoh and Azekah in the Shephelah, Josh 15:36, and OpenBible's first choice is Hadid near Lod), *Etam* (`etam_415`, Tell Eton; the Simeonite town of 1 Chr 4:32, not Etam near Bethlehem) and *En-eglaim* (`eneglaim_386`, Ain Feshkha; Ezek 47:10 pairs it with En-gedi at the other end of the Dead Sea).
  - Displayed coordinates follow the formula (canonical place, else Pleiades, else OpenBible), so 22 alias records such as *Tolad*, *Bealoth* and *Seir* moved with them.
- **Places:** 20 regional names, peoples and lands, and unidentified wilderness stations now have no coordinates (DQ-0113): *Ai* (Jer 49:3), *Hamonah*, the *Valley of Hamon-gog*, *Immer*, *Casiphia*, *Sharon* (1 Chr 5:16), *Heres*, *Holon*, *Magog*, *Gog*, *Ophir*, *Uphaz*, *Hara*, *Mithkah*, *Tahath*, *Terah*, *Moseroth*, *Mount Shapher*, *Taberah* and *Waheb*. A point for a region, a people or an unidentified station implies an identification nobody has made, and most of the old points were placeholders shared with unrelated places. OpenBible links are kept. Three aliases still show their own stored points: *Valley of the Passengers*, *Moserah* and *Mount Heres*. *Mount Heres* (Judg 1:35) looks mislinked to *Heres* (Judg 8:13).
- **Places:** *Bethuel* (`bethuel_240`) is now the main record for the Simeonite town, at OpenBible's Khirbet ar-Ras point (31.327312, 34.87847). *Bethel* (`bethel_203`), *Bethul* (`bethul_241`) and *Chesil* (`chesil_289`) are linked to it as aliases. They are one town spelled three ways, Bethul (Josh 19:4), Bethuel (1 Chr 4:30) and Bethel (1 Sam 30:27), and the Greek of Josh 15:30 reads Chesil as Baithel (DQ-0109).
- **Places:** *Libnah*, the wilderness station (`libnah_729`, Num 33:20), now uses OpenBible's Wadi el-Beidha point (29.99321, 34.704), which matches the GeoJSON (DQ-0109).
- **Places:** *Riblah* on the northern border (`riblah_1002`, Num 34:11) now links to Pleiades 431124909 (Rablê, the modern village of Riblah south of Homs, near Hermel) and displays its point (34.432149, 36.549142). Its OpenBible fields are unchanged (DQ-0109).
- **Places:** *Dimonah* (`dimonah_336`, Josh 15:22) now uses OpenBible's second identification, Khirbet edh-Dheiba in the Negev (31.29606, 35.1562), which matches the GeoJSON. OpenBible's first pick points to Dibon in Moab, outside Judah, while Josh 15:21-22 lists Negev towns near Edom. Easton suggests Dimonah may be the Dibon of Neh 11:25 (DQ-0109).
- **Places:** *Laban* (`laban_710`, Deut 1:1) now uses OpenBible's first pick, the Wadi el-Beidha point it shares with *Libnah* (29.99321, 34.704). It stays a separate record, not an alias, because Easton calls Laban only "probably" the Libnah of Num 33:20 (Hazeroth, named with it, is in Sinai). The GeoJSON still has a point near Rafah until the next geo sync (DQ-0109).
- **Places:** *Chilmad* (`chilmad_292`, Ezek 27:23) now has no coordinates either (DQ-0113). OpenBible rates two candidates equally, Media and northern Syria, about 1,083 km apart, and Easton calls it "a place or country unknown". Its old point was a placeholder shared with Asshur.
- **Places:** *Hashmonah* (`hashmonah_531`, Num 33:29-30) now has no coordinates (DQ-0113). OpenBible's first pick, near Beersheba, does not fit the route or Easton's "not far from Mount Hor". The GeoJSON point is neither of OpenBible's top two picks, and the neighbouring stations (Mithkah, Terah, Tahath, Moseroth) were already cleared as unidentified.
- **Places:** *Enam* (`enam_384`, Josh 15:34) now uses OpenBible's pick in the Shephelah near Socoh (31.715, 34.969167), replacing a placeholder outside Judah. The GeoJSON point is 5 km away and will be reconciled at the next geo sync (DQ-0109).
- **Places:** *Zer* (`zer_1252`, Josh 19:35) now uses OpenBible's first pick by Hammath and Tiberias (32.799722, 35.459722). "Ziddim, Zer, and Hammath, Rakkath, and Chinnereth" cluster on the Sea of Galilee's west shore. The GeoJSON's point near Tyre does not fit and will be updated at the next geo sync (DQ-0109).
- **Places:** The aliases *Valley of the Passengers* (`valley_of_the_passengers_1227`) and *Moserah* (`moserah_823`) no longer show old placeholder points. Their stored coordinates were cleared, so like their main records (*Valley of Hamon-gog*, *Moseroth*) they have no coordinates (DQ-0113).
- **Places:** *Mount Heres* (`mount_heres_840`, Judg 1:35, near Aijalon) is no longer an alias of *Heres* (`heres_562`, Judg 8:13, east of the Jordan). They are different places. It now stands as its own record at its own point (31.75275, 34.97661) (DQ-0107).
- **Places:** 124 places had the wrong OpenBible id, often a neighbour's or namesake's, and now link to the article OpenBible gives for their verses, with that article's point (DQ-0108).
  - 11 now display in the right place: *Rimmon* (`rimmon_1004`, Josh 15:32, Zech 14:10) moves from Ain in Lebanon to the Negev of Judah, and its alias *En-rimmon* follows. *Ayyah* (`ayyah_125`, 1 Chr 7:28) moves from Gaza to the hills of Ephraim. *Mount Ephraim* (`mount_ephraim_833`, Jer 4:15) moves off Mount Ebal. *Gederah* (`gederah_452`, Josh 15:36) moves to OpenBible's Gederah in the Shephelah; its aliases *Gederothaim* and *Gederoth* follow. Also *Neah*, *Almon-diblathaim*, *Beth-diblathaim*, *Kerioth*, *Plain of Jordan*, *Jezreel* (2 Sam 4:4) and *Kir-hareseth*.
  - 8 alias records (*Greece*, *En-rimmon*, *Arabah*, *Ramoth*, *Arimathea*, *Geliloth*, *Hapharaim*, *Gederothaim*) have the right id and stored point. Each still displays its main record's point.
  - 105 more had the wrong id label. Most points moved under 5 km, but *Hormah* (`hormah_580`) moves 48 km to Tel Masos (its alias *Zephath* follows), *Mount Zemaraim* 23 km to Ras et-Tahuneh, *Nahaliel* 11 km and *Gibeath-haaraloth* 6 km.
  - On hold: *Baal-hamon*, because OpenBible's point for it is a generic Jerusalem point. *Shihor*, because one record covers both the Nile and the brook "before Egypt". *Merom*, because Easton's Lake Huleh fits the current point better. Also four aliases whose link is disputed: *Zalmon*, *Rumah*, *Kartah* and *Geba* (2 Sam 5:25). Twenty id-label rows already tracked under other ledger items, or only partly matched by OpenBible, were left for later.
- **Places:** *Baal-hamon* (`baal-hamon_141`, Song 8:11) no longer links to Mount Hermon's OpenBible id and no longer shows a point there. It now links to OpenBible's Baal-hamon (`a304bb7`) and, like *Chilmad* and *Hashmonah*, has no coordinates: the site is unknown (Easton), and OpenBible's only point for it is a generic Jerusalem placeholder (DQ-0108). The GeoJSON still has a point for it until the next geo sync (DQ-0072).
- **Not changed, by decision:** the *Red Sea* (`red_sea_986`) keeps its mid-sea point (27.0885, 34.7717). One record covers both the crossing verses near the Gulf of Suez and the Gulf of Aqaba verses (1 Kgs 9:26, Num 21:4), so a mid-sea point stands for the whole sea without picking a crossing site (DQ-0114).

Fixed in Airtable on November 20. These changes reach `json/` and `CSV/` in the next export. GeoJSON is unchanged (DQ-0072 remains on hold).

- **Places:** *On* (`on_908`) and its alias *Heliopolis* (`heliopolis_557`) had been given the OpenBible id for *City of Destruction* (`adca4b1`); *Destruction* (`destruction_301`) had On's id (`acd9137`) and Pleiades 727117 (Heliopolis). The OpenBible and Pleiades links now match the verses and OpenBible.info: On and Heliopolis have `acd9137` and Pleiades 727117 (Ain Shams); Destruction has `adca4b1` and no Pleiades (Isa 19:18 is only a 60% identification with Heliopolis). Displayed coordinates follow the formula (Pleiades else OpenBible). OpenBible lat/long were also updated from a stale point (30.108086, 31.33822) to OpenBible's current representative point (30.129444, 31.3075) (DQ-0084).

Fixed in Airtable on November 18 and 19. Exported in [#117](https://github.com/robertrouse/theographic-bible-metadata/pull/117) (`0fc17ce`).

- **People:** `simon_2750`, which had mixed Peter, Simon the Pharisee, and Judas Iscariot's father, was split (DQ-0080). New record `simon_2751` (*Simon the Pharisee*) is on the six Luke 7 verses that name him (7:36, 7:37, 7:39, 7:40, 7:43, 7:44). Peter (`peter_2745`) now has Mark 1:30, Luke 4:38 and Luke 5:3. `simon_2750`, retitled *Simon (father of Judas Iscariot)*, keeps the four John verses; John 6:71 and 13:26 now include "son of Simon" links. Acts 10:17's text link points at Simon the Tanner (`simon_2753`). `wife_of_simon_2943` is linked as Peter's partner; on November 19 Peter's own `partners` field was set to her as well, and Easton's Simon 4 `matchType`/`matchSlugs` were set to `person` / `simon_2751`.
- **People:** Moses (`moses_2108`) `deathYear` is now `-1450`, matching Death of Moses after the DQ-0003 event fix (DQ-0082).
- **People:** `Disambiguation (temp)` was cleared on all 1,707 People records (DQ-0010, option 1). The column was not a uniform shift, so it could not be realigned. `alexander_187` `displayTitle` changed from "Alexander (Son of Simon)" to "Alexander (family of Annas)". The DQ-0069 Azariah ledger check was retargeted from the cleared field to `alsoCalled`.

Fixed in Airtable on November 17. Exported in [#117](https://github.com/robertrouse/theographic-bible-metadata/pull/117) (`0fc17ce`).

- **Places:** The southern *Hazor* alias of *Kerioth-hezron* (`hazor_547`) and the *Hazor* of Josh 15:23 (`hazor_546`) no longer carry Recogito links to northern Tel Hazor (Pleiades 779967430). `recogitoUri`, `recogitoLat`, `recogitoLon` and `recogitoLabel` were cleared. The displayed coordinates are unchanged (DQ-0079). *Kerioth-hezron* itself stays at the shared "near Moladah" point (31.162327, 35.057114), precision Rough; Khirbet el-Qaryatein remains an unverified candidate.
- **Verses:** In Josh 15:25, the first "Hazor" in `mdText` and `richText` now links to *Hazor-hadattah* (`hazor-hadattah_550`). The closing "which is Hazor" still points at the Kerioth-hezron alias (`hazor_547`) (DQ-0079).

Fixed in Airtable on November 17. Exported in [#110](https://github.com/robertrouse/theographic-bible-metadata/pull/110) (`0243dac`).

- **Verses:** Person links in `mdText` no longer have a stray bracket. All 16,525 affected verses now read `[God](/person/god_1324)` instead of `[God]([/person/god_1324)`, 33,424 links in all, matching `richText` (DQ-0078, DQ-0013). The bracket was added by an export in January 2021 and was never an intended format. Place links and `richText` are unchanged. Punctuation inside some `mdText` link labels (for example `[Adam,](...)`) is still open (DQ-0026).
- **Places:** *Decapolis* (`decapolis_328`) now sits in the Decapolis region east of the Jordan, at the Pleiades point for the region (678116), instead of on Damascus, about 138 km to the north-northeast (DQ-0077). Precision stays `Related-Surrounding`. The point in `geo/bible-places.geojson` was not changed (DQ-0072).
- **Places:** *Rhodes* (`rhodes_1000`) and *Syracuse* (`syracuse_1121`) now link to Pleiades (590030 and 462503) and take its coordinates; Rhodes moved 0.15 km and Syracuse 1.04 km. *Melita* (Malta, `melita_761`) now links to Pleiades 462311; its coordinates are unchanged.

Fixed in Airtable and `geo/` on November 17. The patched `json/` and `CSV/` copies were replaced by the export in [#117](https://github.com/robertrouse/theographic-bible-metadata/pull/117) (`0fc17ce`).

- **Places:** New region *Country of the Gerasenes* (`country-of-the-gerasenes_1303`), the district east of the Sea of Galilee where Jesus healed the demoniac(s) (DQ-0076). KJV reads *Gadarenes* (Mark 5:1, Luke 8:26, 37) and *Gergesenes* (Matt 8:28); modern texts read *Gerasenes*. It is not the city of Gerasa or Gadara. Its point is a stand-in at the traditional site, Kursi (Pleiades 678093), with precision `Related-Surrounding`; the district's boundaries are unknown.
- **Verses:** Matt 8:28, Mark 5:1, Luke 8:26 and Luke 8:37 now link the place in `places`, `mdText` and `richText`. A stray period in Luke 8:26's `mdText` moved outside the Galilee link (DQ-0076).
- **Events:** *Gadarene Demoniacs* (event 387) now has a location (DQ-0076).
- **GeoJSON:** `geo/bible-places.geojson` adds the region (1,031 places), marked `less-certain` and part of the Decapolis (Mark 5:20) (DQ-0076).

Fixed in `geo/` on November 16 in [#104](https://github.com/robertrouse/theographic-bible-metadata/pull/104) (`c676d11`). No export needed.

- **GeoJSON:** Eleven stops in `geo/pauls_journeys_all.geojson` had properties shifted by a spreadsheet column error (DQ-0063). Only properties changed; coordinates and geometry are unchanged.
  - `Place ID` is now the Theographic `placeID` on *Seleucia* (1045), *Salamis* (1016), *Cenchreae* (281), *Troas* (1182), *Ptolemais* (959) and *Antipatris* (70). Three of these had held a verse reference, and three were empty.
  - `Source Link` on *Salamis* now points to Salamis (DARE 21562) instead of Paphos. *Rome* (DARE 1438) and *Samothrace* (DARE 22854) now have real links instead of `924` and `Acts.27.8`, so their "More" links work on the journeys map.
  - *Antipatris* no longer has the stray note `924`. *Three Taverns* now lists Acts 28:15 for the voyage to Rome instead of `924`. The two Antioch stops are now named *Antioch (Syria)* and *Antioch (Pisidia)*.
- **Docs:** [Geospatial Data](../docs/geospatial-data.md) now says `Place ID` is the Theographic `placeID`, not a verse reference.
- **viz.bible:** The Mapbox tileset `bibleviz.cjeuphot60b1v2qqjb1n4zd5y-2eo1m` and dataset `cjeuphot60b1v2qqjb1n4zd5y` behind the journeys map were republished to match.

Fixed in Airtable on November 16, after that day's export. Exported in [#110](https://github.com/robertrouse/theographic-bible-metadata/pull/110) (`0243dac`).

- **People:** Four people linked to another person's Easton's Bible Dictionary entry now link to their own, or to none (DQ-0075). Each person's Easton text (`dictText`) follows the link.
  - *Medan* (`medan_1978`) now links to Easton's *Medan* instead of *Dedan 2*, and *Manasseh* son of Hezekiah (`manasseh_1930`) to *Manasseh 2* instead of *Manasseh 1* (son of Joseph).
  - *Asahiah* (`asahiah_324`) no longer links to *Isaiah 1*, and *Nathan* son of Attai (`nathan_2155`, 1 Chr 2:36) no longer links to *Nathan 1* (the prophet). Easton has no separate entry for either.
  - *Noah*, daughter of Zelophehad (`noah_2211`), still links to Easton's *Noah*, whose last paragraph describes her.
  - Four pairs still share one entry because Easton describes both people in it: *Aram* (`aram_285`, `aram_286`), *Gaius* (`gaius_1269`, `gaius_1271`), *Heman* (`heman_1488`, `heman_1489`) and *James* (`james_718`, `james_719`).
- **Easton:** `matchSlugs` now agrees with the people links on *Dedan 2* (`dedan_999`), *James 1* (`james_717`), *Nathan 1* (`nathan_2153`) and *Manasseh 2* (`manasseh_1930`). Their `matchType` is now `person`; *Dedan 2* was `unmatched`, and the other three were `multi` (DQ-0075).
- **Places:** *Emmaus* (`emmaus_382`) and *Bethlehem* of Zebulun (`bethlehem_219`) no longer carry Recogito links to the wrong places: `recogitoUri`, `recogitoLat` and `recogitoLon` were cleared. They had pointed to a village named Emmaus in Russia (GeoNames 563481) and to Bethlehem in Judah (GeoNames 284315). The displayed coordinates are unchanged (DQ-0073).

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
- **Places:** Five places that had a latitude but no longitude now have complete coordinates, filled as a side effect of that formula (DQ-0016): *Azotus* (`azotus_132`) 31.755937, 34.658057; *Chios* (`chios_296`) 38.44484, 26.063302; *Clauda* (`clauda_280`) 34.84351, 24.091671; *Lasea* (`lasea_717`) 34.94083, 24.818266; *Phrygia* (`phrygia_946`) 37.76986723761415, 29.06450110237073. Exported in [#88](https://github.com/robertrouse/theographic-bible-metadata/pull/88) (`014222a`). Confirmed in master json and live Airtable on November 18.

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
