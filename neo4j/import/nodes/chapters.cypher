WITH "https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/json/chapters.json" AS url
CALL apoc.load.json(url) YIELD value
MERGE (c:Chapter {id: value.id})
SET c.osisRef = value.fields.osisRef,
    c.chapterNum = value.fields.chapterNum,
    c.slug = value.fields.slug;