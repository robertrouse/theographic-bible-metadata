## Description
Theographic is a [knowledge graph](https://www.youtube.com/watch?v=mmQl6VGvX-c) of the Bible, weaving data about people, places, and periods of time into the tapestry of God's story. This data enables smarter search algorithms, new apps, and exciting research potential. It's an open-source project to share information about the scriptures in our digital world.


#### Who It's For

- **Bible Students**: Find related information on any passage or subject without expensive software or endless searching.
- **Visual Storytellers:** Images representing data capture attention and spark curiosity. See examples at [Viz.Bible](https://viz.bible)
- **Developers:** Use a GraphQL API to power your Bible websites and mobile apps.
- **Machine Learning & AI Researchers**: Knowledge graphs provide critical context to train algorithms and interpret results.

## Usage
Complete data documentation, including API information, can be found [here](docs/README.md). 

For specific details on using the Neo4j graph database, see the [Neo4j Graph Documentation](docs/neo4j-graph-documentation.md).

If your database is capable of importing nested JSON objects, the files in the json folder of this repo are the preferred source. The CSV files do not follow typical database table design, but can be imported and used in traditional SQL databases. Depending on your situation, you may prefer to transform array-based fields to relational "lookup" tables to simplify join logic.

## Learn More
[✍Contributing](docs/contributing.md)

[📰Articles](https://theographic.notion.site/Articles-41ac2e70f3d742a0921f9dec95fdfe99?pvs=25)

## Contact

To get in touch, email [robert@viz.bible](mailto:robert@viz.bible) or [@bibleviz](https://twitter.com/bibleviz) on Twitter. 

Sign up [here](http://eepurl.com/dzAtOj) for e-mail updates.

## License
This work is free to use and copy under a Creative Commons Attribution Share-Alike 4.0 License.
