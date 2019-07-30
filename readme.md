## Description
Theographic is a [knowledge graph](https://www.youtube.com/watch?v=mmQl6VGvX-c) of the Bible, weaving data about people, places, and periods of time into the tapestry of God's story. This data enables smarter search algorithms, new apps, and exciting research potential. It's an open-source project to share information about the scriptures in our digital world.


#### Who It's For

- **Bible Students**: Find related information on any passage or subject without expensive software or endless searching.
- **Visual Storytellers:** Images representing data capture attention and spark curiosity. See examples at [Viz.Bible](https://viz.bible)
- **Developers:** Use a GraphQL API to power your Bible websites and mobile apps.
- **Machine Learning & AI Researchers**: Knowledge graphs provide critical context to train algorithms and interpret results.


## Usage
Complete data documentation, including API information, can be found [here](https://www.notion.so/theographic/Documentation-c7ebad9463b9477694fa428dfa8a76b0). 

If your database is capable of importing nested JSON objects, the files in the json folder of this repo are the preferred source. The CSV files do not follow typical database table design, but can be imported and used in traditional SQL databases. Depending on your situation, you may prefer to transform array-based fields to relational "lookup" tables to simplify join logic.


## License
This work is free to use and copy under a Creative Commons Attribution Share-Alike 4.0 License.
