# Theographic Bible Metadata - Neo4j Graph Documentation

This documentation provides a reference for the structure, nodes, and relationships of the Neo4j graph database implementation of Theographic.

[Neo4j](https://neo4j.com/) is a graph database built for following connections through data, such as ancestry, social networks, and influence. Queries are written in [Cypher](https://neo4j.com/docs/cypher-manual/current/), which describes a pattern of nodes and relationships to match. In Theographic, one query can find everything connected to a passage (people, places, events) or trace a person's complete ancestry.

## Table of Contents
- [Environment & Setup](#environment--setup)
- [Import Instructions](#import-instructions)
- [Graph Data Model](#graph-data-model)
- [Example Queries](#example-queries)
- [Helpful Resources](#helpful-resources)

## Environment & Setup

The queries and schema documented here were created and tested on:
- **Neo4j Kernel**: 2025.10.1 (Enterprise Edition)
- **Cypher Language**: Cypher 5

For beginners looking to set up their Neo4j environment, please refer to the official [Neo4j GraphAcademy](https://graphacademy.neo4j.com/) or the [Neo4j Deployment Center](https://neo4j.com/deployment-center/) for installation guides (ex. Desktop, Docker, or AuraDB).

**Requirements:**
- The **APOC** plugin (`apoc.load.json` and `apoc.periodic.iterate` are used by every import script).
- Outbound internet access from the database server. The scripts load JSON directly from `https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/`, so imports always use the latest published data on the `master` branch. To import a local or pinned copy, edit the URL at the top of each script.

## Import Instructions

### Manual Import

*This guide is for manual import that involves running multiple individual files.
For automated import, see the [Automated Import](#automated-import) section below.*

To manually run the import scripts, **scripts must be executed in the following specific order.** While the order of files *within* a folder (e.g., which node type is imported first) does not matter, **the folder order is critical.**

1.  **Schema & Indexes**: Run `neo4j/import/index.cypher` first. This sets up constraints and indexes which significantly speed up the subsequent data import. **Crucially, this also creates Full-Text Indexes**, which enable advanced search capabilities across text fields like names, descriptions, and verse text.
2.  **Nodes**: Run all scripts in `neo4j/import/nodes/`. These create the entities (People, Places, Books, etc.) without connecting them yet.
3.  **Relationships**: Run all scripts in `neo4j/import/relationships/`. These scripts match existing nodes and create the edges (relationships) between them.

> **⚠️ Important Note**: Some of the import scripts may time out. Running with parallel: false (the default setting in the scripts) reduces the chance of failure, but occasional retries and minor troubleshooting may still be necessary. If an import fails, re-run the failed step; repeated runs are safe because the scripts use idempotent patterns (ex. MERGE) and will resume by filling in what's missing.

---

### Automated Import

As an alternative to manually running the Cypher scripts, you can use the provided Python script to automate the entire import process. The script is located at `neo4j/import/neo4j_import.py`.

#### Prerequisites

1. **Python 3.7+**: Ensure you have Python installed. You can verify by running:
   ```bash
   python --version
   ```

2. **Neo4j Python Driver**: Install the official Neo4j driver:
   ```bash
   pip install neo4j
   ```

3. **Running Neo4j Instance**: Make sure your Neo4j database is running and accessible.

#### Configuration

Before running the script, open `neo4j/import/neo4j_import.py` and update the connection settings at the top of the file:

```python
DB_PATH = "bolt://localhost:7687"  # Your Neo4j Bolt URI
DB_USER = "neo4j"                   # Your database username
DB_PASSWORD = "ChangeMyPassword"    # Your database password
```

- **DB_PATH**: The Bolt connection URI. For local installations, this is typically `bolt://localhost:7687`. For AuraDB or remote instances, use the connection string provided by your Neo4j service.
- **DB_USER**: Your Neo4j username (default is `neo4j`).
- **DB_PASSWORD**: Your Neo4j password. Replace `"ChangeMyPassword"` with your actual password.

#### Running the Script

Navigate to the `neo4j/import/` directory and run:

```bash
cd neo4j/import
python neo4j_import.py
```

The script will automatically:
1. Execute the `index.cypher` file to create constraints and indexes
2. Import all node files from the `nodes/` directory
3. Import all relationship files from the `relationships/` directory

> **Note**: The script runs all import operations in the correct order. If any statement fails, it will print an error message but continue with the remaining statements. You can safely re-run the script if needed.

---

## Graph Data Model

The import scripts turn the JSON tables into a connected graph. Below, each node label lists the properties and relationships the scripts in `neo4j/import/` actually create. Arrows (`->`) show relationship direction.

> **IDs:** `id` on every node except `Dictionary` is the 17-character Airtable record ID (e.g. `recRAcqtgn28zXm1a`). It matches `id` in the JSON files.
>
> **Years:** `Person.birthYear` and `deathYear` are imported as **strings**, and `Event.startDate` is a string year or date. All of them use ISO 8601 astronomical years following Jones (`"-4003"` = 4004 BC). Use `toInteger()` for numeric comparisons. See [Chronology and Dates](chronology-and-dates.md).

### Overview

```
(:Testament)-[:CONTAINS]->(:Division)-[:CONTAINS]->(:Book)-[:CONTAINS]->(:Chapter)-[:CONTAINS]->(:Verse)
(:Testament)-[:CONTAINS]->(:Book)

(:Verse)-[:MENTIONS]->(:Person)          (:Verse)-[:MENTIONS]->(:Place)
(:Verse)-[:DESCRIBES]->(:Event)          (:Person)-[:WROTE]->(:Chapter)

(:Person)-[:CHILD_OF]->(:Person)         (:Person)-[:PARENT_OF]->(:Person)
(:Person)-[:PARTNER_OF]->(:Person)       (:Person)-[:MEMBER_OF]->(:PeopleGroup)
(:Person)-[:BORN_IN]->(:Place)           (:Person)-[:DIED_IN]->(:Place)
(:Place)-[:PART_OF]->(:Place)            (:Place)-[:NEAR]->(:Place)
(:Place)-[:ALIAS_OF]->(:Place)
(:Person)-[:PARTICIPATED_IN]->(:Event)

(:Event)-[:OCCURRED_IN]->(:Place)
(:Event)-[:PRECEEDS]->(:Event)           (:Event)-[:FOLLOWS]->(:Event)

(:Dictionary)   // standalone; no relationships are imported yet
```

---

### Node: `Testament` and `Division`
Grouping nodes created from `books.testament` (e.g. "Old Testament") and `books.bookDiv` (e.g. "Pentateuch", "Pauline Epistles").

**Properties:** `title`

**Relationships:**
- `(:Testament)-[:CONTAINS]->(:Division)`
- `(:Testament)-[:CONTAINS]->(:Book)`
- `(:Division)-[:CONTAINS]->(:Book)`

---

### Node: `Book`
One of the 66 books of the Protestant canon.

| Property | Source field | Description |
| :--- | :--- | :--- |
| `id` | `id` | Airtable record ID |
| `title` | `bookName` | Full English name, e.g. "Genesis" |
| `osisRef` | `osisName` | OSIS abbreviation, e.g. "Gen" |
| `shortName` | `shortName` | Shortest abbreviation, e.g. "Ge" |
| `slug` | `slug` | URL-friendly slug |
| `bookOrder` | `bookOrder` | Canonical order (1–66) |

**Relationships:**
- `(:Testament)-[:CONTAINS]->(:Book)`
- `(:Division)-[:CONTAINS]->(:Book)`
- `(:Book)-[:CONTAINS]->(:Chapter)`

---

### Node: `Chapter`

| Property | Source field | Description |
| :--- | :--- | :--- |
| `id` | `id` | Airtable record ID |
| `osisRef` | `osisRef` | e.g. "Gen.1" |
| `chapterNum` | `chapterNum` | Chapter number |
| `slug` | `slug` | e.g. "gen_1" |

**Relationships:**
- `(:Book)-[:CONTAINS]->(:Chapter)`
- `(:Chapter)-[:CONTAINS]->(:Verse)`
- `(:Person)-[:WROTE]->(:Chapter)`

---

### Node: `Verse`

| Property | Source field | Description |
| :--- | :--- | :--- |
| `id` | `id` | Airtable record ID |
| `osisRef` | `osisRef` | e.g. "Gen.1.1" |
| `verseId` | `verseID` | Sortable ID `BBCCCVVV`, e.g. "01001001" |
| `verseNum` | `verseNum` | Verse number (string) |
| `verseText` | `verseText` | KJV text |
| `mdText` | `mdText` | KJV text with Markdown links to people and places |

**Relationships:**
- `(:Chapter)-[:CONTAINS]->(:Verse)`
- `(:Verse)-[:MENTIONS]->(:Person)`
- `(:Verse)-[:MENTIONS]->(:Place)`
- `(:Verse)-[:DESCRIBES]->(:Event)`

---

### Node: `Person`

| Property | Source field | Description |
| :--- | :--- | :--- |
| `id` | `id` | Airtable record ID |
| `personId` | `personID` | Integer ID; also the suffix of the slug |
| `name` | `name` | Primary KJV name |
| `title` | `displayTitle` | Disambiguated title, e.g. "Joseph (son of Jacob)" |
| `alsoCalled` | `alsoCalled` | Alternate names |
| `gender` | `gender` | "Male" or "Female" |
| `description` | `dictionaryText` | Easton's Bible Dictionary text |
| `birthYear` | `birthYear` | String, ISO 8601 year (Jones) |
| `deathYear` | `deathYear` | String, ISO 8601 year (Jones) |
| `slug` | `slug` | e.g. "moses_2108" |
| `status` | `status` | Record validation status |

**Relationships:**
- `(:Person)-[:CHILD_OF]->(:Person)` and the reverse `(:Person)-[:PARENT_OF]->(:Person)`, from `mother`, `father`, and `children`
- `(:Person)-[:PARTNER_OF]->(:Person)`, created in both directions
- `(:Person)-[:MEMBER_OF]->(:PeopleGroup)`
- `(:Person)-[:BORN_IN]->(:Place)`
- `(:Person)-[:DIED_IN]->(:Place)`
- `(:Person)-[:PARTICIPATED_IN]->(:Event)`
- `(:Person)-[:WROTE]->(:Chapter)`
- `(:Verse)-[:MENTIONS]->(:Person)`

---

### Node: `Place`

| Property | Source field | Description |
| :--- | :--- | :--- |
| `id` | `id` | Airtable record ID |
| `placeId` | `placeID` | Integer ID; also the suffix of the slug |
| `name` | `displayTitle` | Disambiguated display name |
| `latitude` | `latitude` | String; best available latitude |
| `longitude` | `longitude` | String; best available longitude |
| `precision` | `precision` | Geolocation precision note |
| `featureType` | `featureType` | e.g. "City", "Region", "Water" |
| `description` | `dictionaryText` | Easton's Bible Dictionary text |
| `comment` | `comment` | OpenBible.info comment |
| `slug` | `slug` | e.g. "jerusalem_636" |
| `startYear` | `startYear` | Integer, ISO 8601 year; set on places that existed for a period, such as kingdoms |
| `endYear` | `endYear` | Integer, ISO 8601 year |

**Relationships:**
- `(:Verse)-[:MENTIONS]->(:Place)`
- `(:Event)-[:OCCURRED_IN]->(:Place)`
- `(:Person)-[:BORN_IN]->(:Place)`
- `(:Person)-[:DIED_IN]->(:Place)`
- `(:Place)-[:ALIAS_OF]->(:Place)`, from `canonicalPlace`: this record is another name of that place (Salem → Jerusalem)
- `(:Place)-[:PART_OF]->(:Place)`, from `partOf`: a city in its tribal territory, a site in its city, a territory in its kingdom. A kingdom's `startYear` and `endYear` date the link.
- `(:Place)-[:NEAR]->(:Place)`, from `near` (Gethsemane → Jerusalem)

Example: every place in the Northern Kingdom, with the kingdom's dates.

```cypher
MATCH (p:Place)-[:PART_OF*1..2]->(k:Place {name: "Northern Kingdom of Israel"})
RETURN p.name, k.startYear, k.endYear
```

---

### Node: `Event`
An event on the Theographic timeline. Dates follow Dr. Floyd Nolen Jones; see [Chronology and Dates](chronology-and-dates.md).

| Property | Source field | Description |
| :--- | :--- | :--- |
| `id` | `id` | Airtable record ID |
| `eventID` | `eventID` | Integer ID |
| `title` | `title` | Event title |
| `startDate` | `startDate` | ISO 8601 astronomical year or date (string) |
| `duration` | `duration` | e.g. "7D", "40Y" |
| `sortKey` | `sortKey` | Float for chronological ordering |

**Relationships:**
- `(:Event)-[:PRECEEDS]->(:Event)` and `(:Event)-[:FOLLOWS]->(:Event)`, from `predecessor`. Both carry `lag` and `lagType` properties. *(The relationship type is spelled `PRECEEDS` in the import scripts.)*
- `(:Event)-[:OCCURRED_IN]->(:Place)`, built from both `events.places (from verses)` and `places.eventsHere`
- `(:Person)-[:PARTICIPATED_IN]->(:Event)`
- `(:Verse)-[:DESCRIBES]->(:Event)`

---

### Node: `PeopleGroup`

| Property | Source field | Description |
| :--- | :--- | :--- |
| `id` | `id` | Airtable record ID |
| `name` | `groupName` | e.g. "Apostles (The Eleven)" |

**Relationships:**
- `(:Person)-[:MEMBER_OF]->(:PeopleGroup)`

---

### Node: `Dictionary`
An entry from Easton's Bible Dictionary.

| Property | Source field | Description |
| :--- | :--- | :--- |
| `id` | `termID` | Position in the source XML, e.g. "a-p1.11". *(The import script overwrites the Airtable record ID with `termID`.)* |
| `term` | `termLabel` | Dictionary headword |
| `dictText` | `dictText` | Definition text |

**Relationships:** None are imported yet. To connect entries to people and places, use `easton.personLookup` / `easton.placeLookup` in the JSON, or `Person.description` / `Place.description` in the graph.

---

## Example Queries

This section demonstrates example cases of how to use the graph.

### 1. Ancestry & Family Trees
**Find the father and grandfather of King David:**
```cypher
MATCH (david:Person {name: "David"})-[:CHILD_OF]->(father)-[:CHILD_OF]->(grandfather)
RETURN father.name, grandfather.name
```

**Find the siblings of Moses:**
```cypher
MATCH (p1:Person)-[:CHILD_OF]->(parent)<-[:CHILD_OF]-(p2:Person)
WHERE p1.name = "Moses" AND p1 <> p2
RETURN DISTINCT p2.name AS Sibling
```

### 2. Geography & Events
**Find all events that happened in Jerusalem:**
```cypher
MATCH (e:Event)-[:OCCURRED_IN]->(p:Place {name: "Jerusalem"})
RETURN e.title, e.startDate
ORDER BY e.sortKey
```

**Find the place where Paul was born:**
```cypher
MATCH (paul:Person {name: "Paul"})-[:BORN_IN]->(p:Place)
RETURN paul.name, p.name, p.latitude, p.longitude;
```

### 3. Events/Timeline Analysis
**Find which events Moses was part of:**
```cypher
MATCH (p:Person {name: "Moses"})-[:PARTICIPATED_IN]->(e:Event)
RETURN e.title, e.startDate
ORDER BY e.sortKey ASC
LIMIT 10
```

**Find who participated in the event called "The Great Flood begins":**
```cypher
MATCH (e:Event {title: "The Great Flood begins"})<-[:PARTICIPATED_IN]-(p:Person)
RETURN p.name
```

### 4. Full-Text Search
If you ran the `index.cypher` file during setup, you have access to powerful full-text search capabilities. This allows you to do things like:
- **Phrase Search**: Find exact phrases like "River of Egypt".
- **Boolean Search**: Combine required/optional/excluded terms with Lucene operators like AND, OR, and NOT.
- **Proximity Search**: Find words that are near each other (e.g., "love" within 5 words of "hate").
- **Fielded Search**: Search specific properties (e.g., `title:Prophet`).
- **Range Search**: Find terms within a lexical range (e.g., `title:[king TO kinsman]`).
- **Weighted Search (Boosting)**: Boost the relevance of certain terms or fields (e.g., `title:king AND title:Israel^2`).

The results will be ranked by how well they match the query.

**Example 1: Boolean Search**

Find people associated with both the terms "Prophet" and "Judge".
```cypher
CALL db.index.fulltext.queryNodes("person_fulltext", "Prophet AND Judge") 
YIELD node, score 
RETURN node.name, node.title, score LIMIT 5;
```

**Returns:**
<!-- The weird <span></span> wrapper around the "." is to stop github from automatically making it into a hyperlink. -->
| node<span>.</span>name | node.title | score |
| :--- | :--- | :--- |
| Jesus | Jesus Christ | 2.17 |
| Samuel | Samuel | 1.74 |

**Example 2: Proximity Search**

Find verses where "love" and "hate" appear within 5 words of each other.
```cypher
CALL db.index.fulltext.queryNodes("verse_fulltext", "\"love hate\"~5") 
YIELD node, score 
RETURN node.osisRef, node.verseText, score LIMIT 3;
```

**Returns:**
| node.osisRef | node.verseText | score |
| :--- | :--- | :--- |
| Ps.97.10 | Ye that love the LORD, hate evil... | 2.38 |
| Prov.8.36 | ...all they that hate me love death. | 2.30 |
| Matt.5.43 | ...Thou shalt love thy neighbour, and hate thine enemy. | 2.30 |

**Example 3: Fielded Search**

Search only within the `title` property for "King".
```cypher
CALL db.index.fulltext.queryNodes("person_fulltext", "title:King") 
YIELD node, score 
RETURN node.name, node.title, score LIMIT 3;
```

**Returns:**
| node.name | node.title | score |
| :--- | :--- | :--- |
| Abimelech | Abimelech (King of Gerar) | 1.50 |
| Arioch | Arioch (king of Ellasar) | 1.50 |
| Jabin | Jabin (king of Hazor) | 1.50 |

**Example 4: Range Search**

Find people whose `title` contains a word between "king" and "kinsman" alphabetically.
```cypher
CALL db.index.fulltext.queryNodes("person_fulltext", "title:[king TO kinsman]")
YIELD node, score
RETURN node.title, score LIMIT 3;
```

For numeric ranges such as years, use an ordinary `WHERE` clause instead of the full-text index. People born between 1100 BC and 1000 BC (ISO `-1099` to `-999`):
```cypher
MATCH (p:Person)
WHERE p.birthYear IS NOT NULL
  AND toInteger(p.birthYear) >= -1099 AND toInteger(p.birthYear) <= -999
RETURN p.title, p.birthYear
ORDER BY toInteger(p.birthYear);
```

**Example 5: Weighted Search (Boosting)**

Find multiple figures called Joseph, but order them based on if their title contains "son of" or not.
```cypher
CALL db.index.fulltext.queryNodes(
  "person_fulltext",
  'name:joseph^3, title:"son of"^2'
)
YIELD node, score
RETURN node.name, node.title, score ORDER BY score DESC LIMIT 4;
```

**Returns:**
<!-- The weird <span></span> wrapper around the "." is to stop github from automatically making it into a hyperlink. -->

| node<span>.</span>name | node.title | score |
| :--- | :--- | :--- |
| Joseph | Joseph (son of Jacob) | 11.35 |
| Joseph | Joseph (son of Asaph) | 11.35 |
| Joseph | Joseph (son of Judah) | 11.35 |
| Joseph | Joseph | 7.86 |

## Helpful Resources

- [Neo4j GraphAcademy](https://graphacademy.neo4j.com/): free courses, including an introduction to Neo4j and Cypher
- [Cypher Cheat Sheet](https://neo4j.com/docs/cypher-manual/current/cheat-sheet/)
- [Full-text index query syntax](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/full-text-indexes/)
- [Neo4j Sandbox](https://neo4j.com/sandbox/): free, temporary hosted databases with example use cases
