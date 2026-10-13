# Contributing

This open source project is backed by individuals passionate about applying our best technology to the mission of making disciples. All contributions are coordinated through **[GitHub Issues](https://github.com/robertrouse/theographic-bible-metadata/issues)** in this repository.

| I want to… | Do this |
|---|---|
| Report a data error | [Open a data correction issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=data-correction.yml) |
| Report a problem with the docs, API, or import scripts | [Open a bug report](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=bug-report.yml) |
| Volunteer, or propose an idea or a new dataset | [Open an idea / volunteer issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=idea-or-volunteer.yml) |
| Find something to work on | Browse [open issues](https://github.com/robertrouse/theographic-bible-metadata/issues), especially those labeled [`help wanted`](https://github.com/robertrouse/theographic-bible-metadata/labels/help%20wanted) |

Questions that don't fit an issue can go to [robert@viz.bible](mailto:robert@viz.bible).

---

## Data corrections

Anyone who reads carefully can help validate and disambiguate the data. A good correction names:

1. **The record:** a lookup or reference such as `moses_2108`, `jerusalem_636`, `Gen.1.1`, or an event title.
2. **The field and its current value:** for example, `deathYear: -1452`.
3. **What it should be, with a source:** a verse, a work in the [bibliography](data-source-bibliography.md), or another citable reference.

Theographic's data is maintained in [Airtable](https://airtable.com/) and exported to this repository, so corrections are made there and appear in the next export. Pull requests that edit the JSON or CSV files directly are welcome as a way to propose a change, but they will be applied upstream by hand rather than merged.

Before reporting a date, please read [Chronology and Dates](chronology-and-dates.md). The timeline follows Dr. Floyd Nolen Jones, and two year conventions are in use, so a one-year difference may be expected.

## Code

Pull requests are welcome for the parts of this repository that are code:

- [`api/`](../api): the GraphQL API (run `npm test` before submitting)
- [`neo4j/import/`](../neo4j/import): the Neo4j import scripts
- [`docs/`](.): this documentation

For larger changes, open an issue first so the approach can be agreed before you write the code.

## Design and data visualization

Searching the scriptures should be as easy as searching Google or following link trails on Wikipedia, and interfaces should reflect the beauty of God's handiwork. Data visualization is an effective way to connect pieces of stories spread across the Bible and show them as a cohesive whole pointing to Jesus.

[Viz.Bible](https://viz.bible) shows some examples, but there are many more stories to be told. If you build something with Theographic data, whether in D3, Tableau, or the tool of your choice, share it in an [idea / volunteer issue](https://github.com/robertrouse/theographic-bible-metadata/issues/new?template=idea-or-volunteer.yml).
