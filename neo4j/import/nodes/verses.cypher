CALL apoc.periodic.iterate(
  "WITH 'https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/verses.json' AS url
   CALL apoc.load.json(url) YIELD value
   RETURN value",
  "MERGE (v:Verse {id: value.id})
   SET v.osisRef = value.fields.osisRef,
       v.verseNum = value.fields.verseNum,
       v.verseId = value.fields.verseID,
       v.verseText = value.fields.verseText,
       v.mdText = value.fields.mdText",
  {batchSize: 5000, iterateList: true, parallel: false}
);