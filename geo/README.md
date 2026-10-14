# geo/ — Bible places for mapping

Two GeoJSON files, free to use under [CC BY-SA 4.0](../LICENSE). More detail in
[Geospatial Data](../docs/geospatial-data.md).

## `bible-places.geojson`

Every place mentioned in the Bible as one
[Linked Places Format](https://github.com/LinkedPasts/linked-places-format)
FeatureCollection: 1,030 places, valid against the World Historical Gazetteer
LPF schema v1.2.2, so it can be loaded into the
[World Historical Gazetteer](https://whgazetteer.org/) or any GeoJSON tool.
Every place has at least one verse reference.

| Member | Content |
|---|---|
| `@id` | `https://bible.helloao.org/api/c/places/<slug>.json` (API not live yet) |
| `properties.title` | Unique name, e.g. "Antioch (of Syria)" |
| `properties.fclasses` | LPF class: P settlement, L region, T landform, H water, S site, R route |
| `geometry` | Point `[lon, lat]` with `certainty` (`certain` / `less-certain`). Kingdoms are a MultiPoint of their territories; unknown locations are an empty GeometryCollection |
| `when` | When the place is first attested: the earliest ancient attestation in Pleiades, or the earliest mention in the biblical narrative (Theographic chronology) with its [PeriodO](https://perio.do/) period. Kingdoms also have an end |
| `names` | Every name of the place with citations, including ancient-language forms; a name used only in part of the Bible carries its own dates (Azotus under Ashdod, in Acts) |
| `relations` | Dated "part of" and "near" links to other places, cited to verses: cities in the tribal territories of Joshua 13–19, sites in Jerusalem, New Testament cities in Roman regions, territories in the United Kingdom of Israel, the Northern Kingdom and Judah |
| `links` | Digital Manna, Theographic, OpenBible.info, Pleiades, Wikidata |

Years are ISO 8601 astronomical years: `-1094` is 1095 BC.

## `pauls_journeys_all.geojson`

Paul's missionary journeys: 44 stops and 68 route segments, with verse
references for each journey. Fields are described in
[Geospatial Data](../docs/geospatial-data.md#geopauls_journeys_allgeojson).

## How `bible-places.geojson` is made

It is built from this repository's `json/` place data, Digital Manna,
OpenBible.info, Pleiades, Wikidata and PeriodO. The build scripts, the
editorial decisions behind the merges and dates, and the Airtable sync logs are
kept on the [`geo-pipeline`](https://github.com/robertrouse/theographic-bible-metadata/tree/geo-pipeline/geo)
branch.

Found an error? [Report a data correction](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=data-correction.yml).
