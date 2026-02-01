CALL apoc.periodic.iterate(
  "WITH 'https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/events.json' AS url
   CALL apoc.load.json(url) YIELD value
   RETURN value",
  "MERGE (e:Event {id: value.id})
   SET e.eventID = value.fields.eventID,
       e.title = value.fields.title,
       e.startDate = value.fields.startDate,
       e.duration = value.fields.duration,
       e.sortKey = value.fields.sortKey",
  {batchSize: 1000, iterateList: true, parallel: false}
);
