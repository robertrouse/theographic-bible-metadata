WITH "https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/books.json" AS url
CALL apoc.load.json(url) YIELD value
MATCH (b:Book {id: value.id})
WITH b, value

FOREACH(chapter IN value.fields.chapters |
  MERGE (c:Chapter {id: chapter})
  MERGE (b)-[:CONTAINS]->(c)
);
