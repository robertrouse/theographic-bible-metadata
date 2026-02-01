CALL apoc.periodic.iterate(
  "WITH 'https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/easton.json' AS url
   CALL apoc.load.json(url) YIELD value
   RETURN value",
  "MERGE (d:Dictionary {id: value.id})
   SET d.id = value.fields.termID,
       d.term = value.fields.termLabel,
       d.dictText = value.fields.dictText",
  {batchSize: 1000, iterateList: true, parallel: false}
);
