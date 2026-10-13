# Geospatial Data

Theographic's place data is available in two forms: coordinates on every place record, and GeoJSON files for mapping.

## Coordinates on place records

`json/places.json` and `CSV/Places.csv` include coordinates for 1,252 of the 1,274 places.

| Field | Description |
|---|---|
| `latitude`, `longitude` | Best available coordinates, chosen after comparing OpenBible.info and Recogito matches. **Use these by default.** |
| `openBibleLat`, `openBibleLong` | Coordinates from [OpenBible.info Bible Geocoding](https://www.openbible.info/geo/) |
| `recogitoLat`, `recogitoLon`, `recogitoUri` | Coordinates and gazetteer link (Pleiades, GeoNames, DARE) from [Recogito](https://recogito.pelagios.org/) |
| `precision` | How the coordinates relate to the place: `Precise`, `Center`, `Rough`, `Related-Within`, `Related-Surrounding`, or `Unlocated`. Set on 542 places. |
| `featureType`, `featureSubType` | Classification such as City, Region, Water / River |
| `rootID` | When set, the coordinates are inherited from another place record (for example, Achaia → Athens, Abarim → Mount Nebo) |

All coordinate fields are **strings** in decimal degrees (WGS 84). Convert them to numbers before mapping. Note that GeoJSON orders coordinates `[longitude, latitude]`.

## GeoJSON files

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
