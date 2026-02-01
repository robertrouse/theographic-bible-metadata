CALL apoc.periodic.iterate(
  "WITH 'https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/events.json' AS url
   CALL apoc.load.json(url) YIELD value
   RETURN value",
  "MATCH (e:Event {id: value.id})
   WITH e, value

   FOREACH(verse IN value.fields.verses |
     MERGE (v:Verse {id: verse})
     MERGE (v)-[:DESCRIBES]->(e)
   )

   FOREACH(participant IN value.fields.participants |
     MERGE (p:Person {id: participant})
     MERGE (p)-[:PARTICIPATED_IN]->(e)
   )

   FOREACH(place IN value.fields.`places (from verses)` |
     MERGE (l:Place {id: place})
     MERGE (e)-[:OCCURRED_IN]->(l)
   )

   FOREACH(pre IN value.fields.predecessor |
     MERGE (pr:Event {id: pre})
     MERGE (pr)-[r:PRECEEDS]->(e)
     MERGE (e)-[rf:FOLLOWS]->(pr)
     SET r.lagType = value.fields.lagType,
         r.lag = value.fields.lag,
         rf.lagType = value.fields.lagType,
         rf.lag = value.fields.lag
   )",
  {batchSize: 1000, iterateList: true, parallel: false}
);