# Data Formats and Downloads

All Theographic data is free to download from this GitHub repository under [CC BY-SA 4.0](../LICENSE). Airtable is where the data is edited. The JSON and CSV files are generated from it by [`etl/export_airtable.py`](../etl/export_airtable.py), and the other formats on this page are built from those files.

| Format | Location | Best for |
|---|---|---|
| **JSON** | [`json/`](../json) | The preferred source. Each file is an array of `{id, createdTime, fields}` records, and link fields are arrays of record IDs. See [JSON Fields Documentation](json-fields-documentation.md). |
| **CSV** | [`CSV/`](../CSV) | Spreadsheets and SQL databases. Same tables and field names as the JSON, but link fields hold comma-separated lookup values (e.g. `god_1324,jesus_905`, `Gen.1.1,Gen.1.2`) instead of record IDs. |
| **Word index** | [`CSV/WordIndex.csv`](../CSV/WordIndex.csv) | One row per KJV word (~790,000 rows) with book, chapter, verse, word position, punctuation, italics, syllables, and the person and place IDs and year (ISO 8601) tied to that word. It is not generated from Airtable and is updated by hand. |
| **GeoJSON** | [`geo/`](../geo) | Mapping. See [Geospatial Data](geospatial-data.md). |
| **Neo4j** | [`neo4j/import/`](../neo4j/import) | Graph queries. Cypher scripts build a Neo4j graph straight from the JSON on GitHub. See [Neo4j Graph Documentation](neo4j-graph-documentation.md). |
| **GraphQL API** | `https://theographic-api.netlify.app/api/graphql` | Live queries without downloading anything. See [API Documentation](api-documentation.md). |
| **Airtable** | [Theographic Bible Data (read-only view)](https://airtable.com/shrlkhIzIUzmx9whR) | Browsing, filtering, and one-off CSV exports with no code. See [View and Export Data with Airtable](view-and-export-data-with-airtable.md). |

## Tables

| Table | JSON | CSV | Records |
|---|---|---|---|
| Books | `books.json` | `Books.csv` | 66 |
| Chapters | `chapters.json` | `Chapters.csv` | 1,189 |
| Verses | `verses.json` | `Verses.csv` | 31,102 |
| People | `people.json` | `People.csv` | 3,067 |
| People groups | `peopleGroups.json` | `PeopleGroups.csv` | 23 |
| Places | `places.json` | `Places.csv` | 1,298 |
| Events | `events.json` | `Events.csv` | 450 |
| Easton's Bible Dictionary | `easton.json` | `Easton.csv` | 6,519 |

## Using the CSV files in a SQL database

The CSV files do not follow normalized database design: many-to-many links are stored as comma-separated lists in a single column. For relational use, split those columns into join tables (for example, `verse_people(osisRef, personLookup)`). Join on the human-readable keys: `osisRef` for books, chapters, and verses; `personLookup`, `placeLookup`, and `eventID` for the others.

## Freshness

The JSON and CSV files are refreshed from Airtable **monthly** by the [Airtable export workflow](https://github.com/robertrouse/theographic-bible-metadata/actions/workflows/airtable-export.yml), which opens a pull request whenever the data has changed. To regenerate them yourself with an Airtable token, run `python3 etl/export_airtable.py` from the repository root. The commit history of [`json/`](https://github.com/robertrouse/theographic-bible-metadata/commits/master/json) shows when the data was last refreshed. If you need something more recent than the latest export, [open an issue](https://github.com/robertrouse/theographic-bible-metadata/issues) or email [robert@viz.bible](mailto:robert@viz.bible).
