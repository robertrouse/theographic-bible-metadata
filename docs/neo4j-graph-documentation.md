# Theographic Bible Metadata - Neo4j Graph Documentation

This documentation provides a reference for the structure, nodes, and relationships of the Neo4j graph database implementation of Theographic.

## Table of Contents
- [Environment & Setup](#environment--setup)
- [Import Instructions](#import-instructions)
- [Graph Data Model](#graph-data-model)
- [Example Queries](#example-queries)

## Environment & Setup

The queries and schema documented here were created and tested on:
- **Neo4j Kernel**: 2025.10.1 (Enterprise Edition)
- **Cypher Language**: Cypher 5

For beginners looking to set up their Neo4j environment, please refer to the official [Neo4j GraphAcademy](https://graphacademy.neo4j.com/) or the [Neo4j Download Center](https://neo4j.com/download-center/) for installation guides (ex. Desktop, Docker, or AuraDB).

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

The graph model transforms the flat JSON tables into a connected network of entities. Below is the documentation for each Node Label, its properties, and its relationships.

### Node: `Book`
Represents one of the 66 books of the Protestant canon.

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `title` | Full English name of the book |
| `shortName` | Standard abbreviation (e.g., "Gen") |
| `osisRef` | OSIS standard identifier (e.g., "Gen") |
| `slug` | URL-friendly slug |
| `bookOrder` | Canonical ordering (1-66) |

**Relationships:**
*Note: Arrows (`->`) indicate the direction of the relationship.*
- `(:Testament)-[:CONTAINS]->(:Book)`
- `(:Division)-[:CONTAINS]->(:Book)`
- `(:Book)-[:CONTAINS]->(:Chapter)`

---

### Node: `Person`
Represents a distinct individual mentioned in the Bible.

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `personId` | Integer ID for external mapping |
| `name` | Primary name of the person |
| `alsoCalled` | Alternative names or spellings |
| `title` | Title or role (e.g., "King of Israel") |
| `gender` | Gender of the person |
| `description` | Biographical text from Easton's Dictionary |
| `slug` | URL-friendly slug |

**Relationships:**
- `(:Person)-[:CHILD_OF]->(:Person)`
- `(:Person)-[:PARTNER_OF]->(:Person)`
- `(:Person)-[:BORN_IN]->(:Place)`
- `(:Person)-[:DIED_IN]->(:Place)`
- `(:Person)-[:BORN_IN]->(:Year)`
- `(:Person)-[:DIED_IN]->(:Year)`
- `(:Verse)-[:MENTIONS]->(:Person)`

---

### Node: `Place`
Represents a geographic location mentioned in the text.

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `placeId` | Integer ID for external mapping |
| `name` | Display name of the place |
| `latitude` | GPS Latitude |
| `longitude` | GPS Longitude |
| `featureType` | Type of location (e.g., "City", "Mountain") |
| `description` | Description from dictionary |
| `comment` | Editor's comments or notes |
| `precision` | Accuracy of the geolocation |

**Relationships:**
- `(:Event)-[:OCCURRED_IN]->(:Place)`
- `(:Person)-[:BORN_IN]->(:Place)`
- `(:Person)-[:DIED_IN]->(:Place)`
- `(:Verse)-[:MENTIONS]->(:Place)`

---

### Node: `Event`
Represents a specific event or narrative unit in the biblical timeline.

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `title` | Title of the event |
| `startDate` | Approximate start date |
| `duration` | Duration of the event |
| `sortKey` | Chronological sorting key |

**Relationships:**
- `(:Event)-[:PRECEEDS]->(:Event)`
- `(:Person)-[:PARTICIPATED_IN]->(:Event)`
- `(:Event)-[:OCCURRED_IN]->(:Place)`
- `(:Verse)-[:DESCRIBES]->(:Event)`

---

### Node: `Verse`
Represents a single verse of scripture.

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `osisRef` | Standard reference (e.g., "Gen.1.1") |
| `verseText` | The text of the verse |
| `verseNum` | Verse number |

**Relationships:**
- `(:Chapter)-[:CONTAINS]->(:Verse)`
- `(:Verse)-[:MENTIONS]->(:Person)`
- `(:Verse)-[:MENTIONS]->(:Place)`
- `(:Verse)-[:DESCRIBES]->(:Event)`

---

### Node: `Chapter`
Represents a chapter within a book.

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `chapterNum` | Chapter number |
| `osisRef` | Standard reference (e.g., "Gen.1") |

**Relationships:**
- `(:Book)-[:CONTAINS]->(:Chapter)`
- `(:Chapter)-[:CONTAINS]->(:Verse)`

---

### Node: `Year`
Represents a specific year in history.

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `year` | Numeric year (negative for BC) |
| `formattedYear` | Display string (e.g., "1000 BC") |

**Relationships:**
- `(:Person)-[:BORN_IN]->(:Year)`
- `(:Person)-[:DIED_IN]->(:Year)`

---

### Node: `PeopleGroup`
Represents a group of people (e.g., "Israelites", "Pharisees").

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `name` | Name of the group |

**Relationships:**
- `(:Person)-[:BELONGS_TO]->(:PeopleGroup)`

---

### Node: `Dictionary`
Represents an entry from Easton's Bible Dictionary.

**Properties:**
| Property | Description |
| :--- | :--- |
| `id` | Unique 14-char identifier |
| `term` | The dictionary term |
| `dictText` | The definition text |

**Relationships:**
- `(:Person)-[:DEFINED_BY]->(:Dictionary)`
- `(:Place)-[:DEFINED_BY]->(:Dictionary)`

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
- **Range Search**: Find values within a range (e.g., years `[1000 TO 1010]`).
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

Find years between 1000 BC and 1010 BC.
```cypher
CALL db.index.fulltext.queryNodes("year_fulltext", "[1000 TO 1010]") 
YIELD node, score 
RETURN node.formattedYear, score;
```

**Returns:**
| node.formattedYear | score |
| :--- | :--- |
| 1006 BC | 1.0 |
| 1001 BC | 1.0 |
| 1004 BC | 1.0 |

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