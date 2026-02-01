CALL apoc.periodic.iterate(
  "WITH 'https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/people.json' AS url
   CALL apoc.load.json(url) YIELD value
   RETURN value",
  "MERGE (p:Person {id: value.id})
   SET p.personId = value.fields.personID,
       p.name = value.fields.name,
       p.alsoCalled = value.fields.alsoCalled,
       p.title = value.fields.displayTitle,
       p.slug = value.fields.slug,
       p.gender = value.fields.gender,
       p.description = value.fields.dictionaryText,
       p.status = value.fields.status,
       p.birthYear = value.fields.birthYear,
       p.deathYear = value.fields.deathYear",
  {batchSize: 1000, iterateList: true, parallel: false}
);
