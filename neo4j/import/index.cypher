// Create id indexes for all node types to optimize import performance
CREATE INDEX book_id IF NOT EXISTS FOR (b:Book) ON (b.id);
CREATE INDEX chapter_id IF NOT EXISTS FOR (c:Chapter) ON (c.id);
CREATE INDEX verse_id IF NOT EXISTS FOR (v:Verse) ON (v.id);
CREATE INDEX person_id IF NOT EXISTS FOR (p:Person) ON (p.id);
CREATE INDEX place_id IF NOT EXISTS FOR (p:Place) ON (p.id);
CREATE INDEX event_id IF NOT EXISTS FOR (e:Event) ON (e.id);
CREATE INDEX peopleGroup_id IF NOT EXISTS FOR (g:PeopleGroup) ON (g.id);
CREATE INDEX dictionary_id IF NOT EXISTS FOR (d:Dictionary) ON (d.id);

// Create fulltext indexes for all node types to optimize search performance
CREATE FULLTEXT INDEX book_fulltext IF NOT EXISTS 
FOR (n:Book) ON EACH [n.title, n.shortName, n.osisRef];

CREATE FULLTEXT INDEX person_fulltext IF NOT EXISTS 
FOR (n:Person) ON EACH [n.name, n.alsoCalled, n.title, n.description];

CREATE FULLTEXT INDEX place_fulltext IF NOT EXISTS 
FOR (n:Place) ON EACH [n.name, n.description, n.comment];

CREATE FULLTEXT INDEX event_fulltext IF NOT EXISTS 
FOR (n:Event) ON EACH [n.title];

CREATE FULLTEXT INDEX dictionary_fulltext IF NOT EXISTS 
FOR (n:Dictionary) ON EACH [n.term, n.dictText];

CREATE FULLTEXT INDEX peopleGroup_fulltext IF NOT EXISTS 
FOR (n:PeopleGroup) ON EACH [n.name];

CREATE FULLTEXT INDEX verse_fulltext IF NOT EXISTS 
FOR (n:Verse) ON EACH [n.verseText, n.osisRef];

CREATE FULLTEXT INDEX chapter_fulltext IF NOT EXISTS 
FOR (n:Chapter) ON EACH [n.osisRef];
