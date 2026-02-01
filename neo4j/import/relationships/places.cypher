CALL apoc.periodic.iterate(
  "WITH 'https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/places.json' AS url
   CALL apoc.load.json(url) YIELD value
   RETURN value",
  "MATCH (p:Place {id: value.id})
   WITH p, value

   FOREACH (verse IN value.fields.verses |
     MERGE (v:Verse {id: verse})
     MERGE (v)-[:MENTIONS]->(p)
   )

   FOREACH (event IN value.fields.eventsHere |
     MERGE (e:Event {id: event})
     MERGE (e)-[:OCCURRED_IN]->(p)
   )

   FOREACH (born IN value.fields.peopleBorn |
     MERGE (pb:Person {id: born})
     MERGE (pb)-[:BORN_IN]->(p)
   )

   FOREACH (died IN value.fields.peopleDied |
     MERGE (pd:Person {id: died})
     MERGE (pd)-[:DIED_IN]->(p)
   )",
  {batchSize: 1000, iterateList: true, parallel: false}
);
