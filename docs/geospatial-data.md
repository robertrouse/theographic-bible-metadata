# Geospatial Data

Theographic's place data is available in two forms: coordinates and place-to-place links on every place record, and GeoJSON files for mapping.

## Coordinates on place records

`json/places.json` and `CSV/Places.csv` include coordinates for 1,272 of the 1,298 place records.

| Field | Description |
|---|---|
| `latitude`, `longitude` | Best available coordinates, chosen after comparing OpenBible.info and Recogito matches. **Use these by default.** |
| `openBibleLat`, `openBibleLong` | Coordinates from [OpenBible.info Bible Geocoding](https://www.openbible.info/geo/) |
| `recogitoLat`, `recogitoLon`, `recogitoUri` | Coordinates and gazetteer link (Pleiades, GeoNames, DARE) from [Recogito](https://recogito.pelagios.org/) |
| `precision` | How the coordinates relate to the place: `Precise`, `Center`, `Rough`, `Related-Within`, `Related-Surrounding`, or `Unlocated`. Set on 542 places. |
| `featureType`, `featureSubType` | Classification such as City, Region, Water / River |
| `canonicalPlace` | Set when this record is another name for a place (Salem → Jerusalem); the canonical record lists its `otherNames`. 257 records point to 181 canonical places. |
| `partOf`, `near` | The places this place lies within (a city's tribal territory, a site's city, a territory's kingdom) or beside; reversed in `parts` and `nearby`. |
| `startYear`, `endYear` | The period of places that existed only for a time, such as the three kingdoms |

All coordinate fields are **strings** in decimal degrees (WGS 84). Convert them to numbers before mapping. Note that GeoJSON orders coordinates `[longitude, latitude]`.

## GeoJSON files

### `geo/bible-places.geojson`

Every biblical place as one [Linked Places Format](https://github.com/LinkedPasts/linked-places-format) FeatureCollection, validated against the World Historical Gazetteer LPF schema v1.2.2. It merges the place records above with Digital Manna, OpenBible.info, Pleiades, Wikidata and PeriodO, so it is the file to use for gazetteer work or for loading into the [World Historical Gazetteer](https://whgazetteer.org/).

- **1,030 places.** Records that are other names of one place are merged into a single feature; each name keeps its own citations and dates (Azotus under Ashdod, dated to Acts).
- **Every place is biblical:** each has at least one verse reference.
- **`geometry`:** a point with `certainty` (`certain` or `less-certain`, from OpenBible.info's confidence score) on 1,025 places; kingdoms are a MultiPoint of their territories; 5 unlocatable places have an empty GeometryCollection.
- **`when`:** each place's start, from the earliest ancient attestation in Pleiades or the earliest mention in the Theographic chronology, labelled with its [PeriodO](https://perio.do/) period in the Levant. Kingdoms also have an end.
- **`names`:** 2,921 names with citations, including ancient-language forms from Pleiades.
- **`relations`:** 387 dated "part of" and "near" links, cited to verses: cities in the tribal territories of Joshua 13–19, sites in Jerusalem, New Testament cities in Roman regions, territories in the United Kingdom of Israel, the Northern Kingdom and Judah.
- **`links`:** Digital Manna, Theographic, OpenBible.info, Pleiades (258 places) and Wikidata.

How it is built, the decisions behind it, and how to rebuild it: the [`geo-pipeline`](https://github.com/robertrouse/theographic-bible-metadata/tree/geo-pipeline/geo) branch.

### `geo/pauls_journeys_all.geojson`

A FeatureCollection of Paul's missionary journeys with 112 features: 44 `Point` stops and 68 `LineString` route segments.

| Property | Description |
|---|---|
| `Place Name` | Stop name (on points) |
| `Place ID` / `first`, `second`, `third`, `rome` | Verse references (OSIS) linking a stop to each journey: first, second, third, and the voyage to Rome |
| `route_id` | Route segment identifier (on lines) |
| `Source Link` | Source for the coordinates, typically a Digital Atlas of the Roman Empire (DARE) URL |
| `Notes` | Editorial notes |
| `anchor`, `offset` | Label placement hints for map rendering |

Routes follow the scholarship listed under *Places* in the [Data Source Bibliography](data-source-bibliography.md), including Wilson (2009) and Thompson & Wilson (2016) for Asia Minor.
