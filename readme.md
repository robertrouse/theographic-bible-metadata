# Theographic Bible Metadata

Theographic is a [knowledge graph](https://www.youtube.com/watch?v=mmQl6VGvX-c) of the Bible, weaving data about people, places, and periods of time into the tapestry of God's story. This data enables smarter search algorithms, new apps, and exciting research potential. It's an open-source project to share information about the scriptures in our digital world.

#### Who It's For

- **Bible Students**: Find related information on any passage or subject without expensive software or endless searching.
- **Visual Storytellers:** Images representing data capture attention and spark curiosity. See examples at [Viz.Bible](https://viz.bible).
- **Developers:** Use the JSON files or the GraphQL API to power your Bible websites and mobile apps.
- **Machine Learning & AI Researchers**: Knowledge graphs provide critical context to train algorithms and interpret results.

## What's Inside

Every verse of the King James Version (1769) is linked to the people, places, events, and dictionary entries it mentions.

| Table | Records | |
|---|---|---|
| Books / Chapters / Verses | 66 / 1,189 / 31,102 | KJV text, authorship, and counts of people and places |
| People | 3,067 | Names, family relationships, groups, birth and death places and years |
| Places | 1,298 | Coordinates, feature types, gazetteer links, other names, part-of links |
| Events | 450 | Timeline with dates, durations, predecessors, participants, and locations |
| People groups | 23 | Tribes, apostles, and other groups |
| Easton's Bible Dictionary | 6,519 | Entries linked to people and places |

**Chronology:** The events timeline and people's birth and death years follow **Dr. Floyd Nolen Jones**, *[The Chronology of the Old Testament: A Return to the Basics](https://floydnolenjonesministries.com/chronology/)*. See [Chronology and Dates](docs/chronology-and-dates.md).

## Getting the Data

| Folder | Contents |
|---|---|
| [`json/`](json) | **Preferred source.** One file per table; link fields are arrays of record IDs. |
| [`CSV/`](CSV) | The same tables as CSV, plus `WordIndex.csv` (one row per KJV word). |
| [`geo/`](geo) | GeoJSON for mapping: every place as a [Linked Places](https://github.com/LinkedPasts/linked-places-format) gazetteer (`bible-places.geojson`) and Paul's journeys |
| [`neo4j/`](neo4j) | Cypher scripts that build a Neo4j graph from the JSON |
| [`api/`](api) | A GraphQL API over the JSON, live at `https://theographic-api.netlify.app/api/graphql` |

## Documentation

**[📚 Documentation home](docs/README.md)**: start here.

- [Data Formats and Downloads](docs/other-data-formats-csv-json-etc.md)
- [JSON Fields Documentation](docs/json-fields-documentation.md)
- [Chronology and Dates](docs/chronology-and-dates.md)
- [GraphQL API](docs/api-documentation.md)
- [Neo4j Graph Documentation](docs/neo4j-graph-documentation.md)
- [Geospatial Data](docs/geospatial-data.md)
- [Data Source Bibliography](docs/data-source-bibliography.md)

## Learn More
[✍ Contributing](docs/contributing.md) · [📰 Articles](https://viz.bible/posts/) · [🐞 Report a data issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=data-correction.yml)

## Contact

To get in touch, email [robert@viz.bible](mailto:robert@viz.bible) or find [@bibleviz](https://x.com/bibleviz) on X.

Sign up [here](http://eepurl.com/dzAtOj) for e-mail updates.

## License
This work is free to use and copy under a [Creative Commons Attribution-ShareAlike 4.0 International License](LICENSE). Please also credit the [original sources](docs/data-source-bibliography.md), several of which have their own licenses.
