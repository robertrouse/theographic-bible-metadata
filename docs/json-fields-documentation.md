# Theographic Bible Metadata - JSON Fields Documentation
This documentation provides a comprehensive reference for the structure and fields of JSON files within the Theographic Bible Metadata dataset.

## Table of Contents
- [Dataset Overview](#dataset-overview)
- [Standard JSON Entity Structure](#standard-json-entity-structure)
- [Books](#books)
- [Chapters](#chapters)
- [Easton](#easton)
- [Events](#events)
- [People](#people-38-fields)
- [PeopleGroups](#peoplegroups-7-fields)
- [Periods](#periods-9-fields)
- [Places](#places-40-fields)
- [Verses](#verses-17-fields)

## Dataset Overview
The JSON files are located in the `json/` directory of the root repository. These files were generated through a Python ETL script from Airtable, where the original data was inputted and continues to be updated. Because of this Airtable origin, you may encounter peculiarities in data structure and field name inconsistencies. Throughout this documentation, JSON files are referred to as "tables" since they directly represent tabular data exported from Airtable.

## Standard JSON Entity Structure
All Theographic JSON entities have three root fields:
- `id` - A 14-character alphanumeric case-sensitive unique record identifier (e.g., `recRAcqtgn28zXm1a`)
- `createdTime` - An ISO 8601/RFC 3339 formatted timestamp (e.g., `2018-06-01T13:12:45.000Z`)
- `fields` - A nested object containing entity-specific data

This documentation focuses exclusively on the fields within the `fields` object. Each section below corresponds to a specific JSON file and details its field names, data types, and relationships with other JSON files. Additionally, each section includes a sample JSON entity from real data to illustrate the structure in practice. Note that sample entities may not contain all possible fields, and some long text values or arrays have been truncated for conciseness.

## Books
This table contains high-level metadata for each of the 66 books in the Protestant Bible canon. It includes various naming conventions (e.g. `osisName`, `bookName`, `shortName`), canonical divisions (`testament`, `bookDiv`), and structural information like chapter and verse counts. It also serves as a sort of central hub, linking to the chapters, verses, writers, people, and places associated with each book.

### Fields Reference (16 Fields)

| Field | Type | Status | Description |
|-------|------|--------|-------------|
| `osisName` | string | Validated | Abbreviation matching the Open Scriptural Information Standard. |
| `bookName` | string | Validated | Full name of the book |
| `chapterCount` | integer | Validated | Total chapters |
| `bookDiv` | string | Validated | High-level divisions of the Bible |
| `shortName` | string | Validated | Shortest abbreviation, useful for small labels |
| `bookOrder` | integer | Validated | Order of books in the traditional Protestant canon, excluding Apocrypha. |
| `verses` | array | Validated | An array of record IDs linking to all verses contained within this book. |
| `yearWritten` | array | Incomplete | Approximate year written, if known. **Currently in unusable format as of 2026/01/05, but undergoing a fix.** It references an entry in the `periods` table - a table that was removed. In the future, it will be updated with an integer value of the isoYear for that period. |
| `placeWritten` | array | Incomplete | An array of record IDs linking to the 'places' table, representing the location where the book was written. |
| `verseCount` | integer | Validated | An integer representing the total number of verses in the book. |
| `chapters` | array | Validated | An array of record IDs linking to all chapters contained within this book. |
| `writers` | array | Validated | An array of record IDs linking to the 'people' table, representing the traditional writers of the book. |
| `testament` | string | Validated | Old or New Testament identifier |
| `slug` | string | Validated | Lowercase, url-friendly version of Osis Name |
| `peopleCount` | integer | Validated | Number of people mentioned by name within the book |
| `placeCount` | integer | Validated | Number of places mentioned by name within the book |


### Relationships
- `verses` → References field `id` of `verses` table records
- `placeWritten` → References field `id` of `places` table
- `chapters` → References field `id` of `chapters` table records
- `writers` → References subfield `personLookup` of field `fields` of `people` table records

### Example
```json
{
  "id": "recyvIyxRMFob6SoM",
  "createdTime": "2018-05-13T17:19:17.000Z",
  "fields": {
    "osisName": "Rom",
    "bookName": "Romans",
    "chapterCount": 16,
    "bookDiv": "Pauline Epistles",
    "shortName": "Ro",
    "bookOrder": 45,
    "verses": [
      "recld8Sxx8yDn1Ik8"
    ],
    "yearWritten": [
      "recvOFi9OkrgM1IAO"
    ],
    "placeWritten": [
      "recpmPd6JhbqhqA0Q"
    ],
    "verseCount": 433,
    "chapters": [
      "recMCMGLnVg4olx48"
    ],
    "writers": [
      "paul_2479"
    ],
    "testament": "New Testament",
    "slug": "rom",
    "peopleCount": 238,
    "placeCount": 13
  }
}
```
## Chapters
This table defines every chapter in the Bible. Each record links to its parent `book` and lists all the `verses` it contains. It also identifies the traditional `writer` of the chapter and provides counts of the distinct people and places mentioned within it.

### Fields Reference (10 Fields)

| Field | Type | Status | Description |
|-------|------|--------|-------------|
| `osisRef` | string | Validated | Unique identifier using book.chapter |
| `book` | array | Validated | An array containing the record ID of the book this chapter belongs to. |
| `chapterNum` | integer | Validated | |
| `writer` | array | Validated | An array of record IDs linking to the 'people' table, representing the traditional writer(s) of this chapter. |
| `verses` | array | Validated | An array of record IDs linking to all verses contained within this chapter. |
| `slug` | string | Validated | Lowercase, url-friendly version of Osis Ref |
| `peopleCount` | integer | Validated | Number of people mentioned by name within the chapter |
| `placesCount` | integer | Validated | Number of places mentioned by name within the chapter |
| `modified` | string | Unknown | Last modified date and time |
| `writer count`| integer | Validated | Total number of writers for the chapter |

### Relationships
- `book` → References field `id` of `books` table records
- `writer` → References field `id` of `people` table records
- `verses` → References field `id` of `verses` table records

### Example
```json
{
  "id": "recViIBdFQyyJQtzE",
  "createdTime": "2018-06-01T13:12:45.000Z",
  "fields": {
    "osisRef": "Gen.1",
    "book": [
      "recIFusdNl6d8dj3L"
    ],
    "chapterNum": 1,
    "writer": [
      "recjNRR60PAuFtjha"
    ],
    "verses": [
      "rec7mkRLwey2ntUG9"
    ],
    "slug": "gen_1",
    "peopleCount": 26,
    "placesCount": 0,
    "modified": "2019-08-08T01:43:21.000Z",
    "writer count": 1
  }
}
```
## Easton
This table contains parsed entries from the 1897 Easton's Bible Dictionary. Each record represents a single dictionary term, providing its label, definition text (`dictText`), and metadata extracted from the source XML at http://www.ccel.org/ccel/easton/ebd2.xml. Crucially, it links dictionary entries to corresponding records in the `people` and `places` tables, enriching the dataset with historical and theological context.

### Fields Reference (12 Fields)

| Field | Type | Status | Description |
|-------|------|--------|-------------|
| `dictLookup` | string | Validated | Unique string for a dictionary entry, split out by sub-paragraphs |
| `termID` | string | Unknown | This field preserves the term’s original position in the source XML, making theographic’s extraction process transparent and allowing easy entry to trace back to its source context. It records the `id` attribute of the `<term>` tag in the source XML, and it indicates the location of the term within the original document's structure. For example, `a-p1.11` signifies that the term is in the "a" section, and that, within that section, it is associated with the paragraph block indexed as "p1", and that within that block, it is the 11th tagged element. |
| `termLabel` | string | Validated | The title of the dictionary term being defined. |
| `def_id` | string | Unknown | The id attribute of the <def> tag in the source XML. This ID directly corresponds to the termID and points to the definition block for that specific term. For example, if the termID is "a-p1.11", the corresponding def_id will be "a-p1.12". |
| `has_list` | string | Unknown | A boolean field ("True" or "False") that indicates whether the definition text contains a numbered or itemized list. This is derived from the structure of the source XML, though not explicitly shown in the provided snippet. |
| `itemNum` | integer | Validated | Indicates the item number for definitions that are part of a list (e.g., 1, 2, 3). This occurs when multiple definitions exist for the same word and they are itemized. Defaults to 0 for entries that are not itemized. |
| `matchType` | string | Temporary | Used to validate scripts which automatically match entities. |
| `matchSlugs` | string | Temporary | Used to check automatically matched slugs of entities in other tables |
| `dictText` | string | Validated | The full definition text for the term. This field may contain Markdown-style links and newline characters for paragraph breaks. |
| `personLookup` | array | Populated | An array of record IDs that link to corresponding entries in the 'people' JSON. Each ID represents a person mentioned in the dictText. |
| `placeLookup` | array | Populated | An array of record IDs that link to corresponding entries in the 'places' JSON. Each ID represents a place mentioned in the dictText. |
| `index` | integer | Validated | Unique identifier |

### Relationships
- `personLookup` → References field `id` of `people` table records
- `placeLookup` → References field `id` of `places` table records

### Example
```json
{
  "id": "recwNJZnKaFjnRShm",
  "createdTime": "2019-07-08T22:44:33.000Z",
  "fields": {
    "dictLookup": "Joseph 4",
    "termID": "j-p441.3",
    "termLabel": "Joseph",
    "def_id": "j-p441.4",
    "has_list": "True",
    "itemNum": 4,
    "matchType": "person",
    "matchSlugs": "joseph_1715",
    "dictText": "The foster-father of our Lord ([Matt. 1:16](/matt#Matt.1.16); [Luke 3:23](/luke#Luke.3.23)). He lived at Nazareth in Galilee ([Luke 2:4](/luke#Luke.2.4)). He is called a “just man.” He was by trade a carpenter ([Matt. 13:55](/matt#Matt.13.55)). He is last mentioned in connection with the journey to Jerusalem, when Jesus was twelve years old. It is probable that he died before Jesus entered on his public ministry. This is concluded from the fact that Mary only was present at the marriage feast in Cana of Galilee. His name does not appear in connection with the scenes of the crucifixion along with that of Mary (q.v.), [John 19:25](/john#John.19.25).",
    "personLookup": [
      "recz2xTRGz9XZD6dT"
    ],
    "index": 3595
  }
}
```

## Events
This table chronicles the timeline of Biblical events. Each record details a specific event with a `title`, chronological data (e.g. `startDate`), and its relationship to other events (`predecessor`, `partOf`). It connects each event to its `participants` (people), `locations` (places), and the narrative `verses` that describe it.

### Fields Reference (19 Fields)

| Field | Type | Status | Description |
|-------|------|--------|-------------|
| `title` | string | Incomplete | Unique title for an event |
| `startDate` | string | Incomplete | ISO formatted date to identify calendar dates where known |
| `duration` | string | Incomplete | Event length in days, years, etc. for use in end date calculations |
| `participants` | array | Incomplete | An array of record IDs linking to the 'people' table, representing the participants in the event. |
| `locations` | array | Incomplete | An array of record IDs linking to the 'places' table, representing the location(s) where the event occurred. |
| `verses` | array | Incomplete | An array of record IDs linking to the 'verses' table, representing the scriptural basis for the event. |
| `predecessor` | array | Incomplete | An array containing the record ID of the immediately preceding event in the timeline. |
| `lag` | string | Unknown | The time elapsed between the predecessor event and the current event. |
| `partOf` | array | Unknown | An array containing the record ID of a parent event, indicating this event is a sub-component of a larger narrative arc. |
| `notes` | string | Unknown | A field for additional commentary or explanatory notes about the event. |
| `verseSort` | string | Unknown | The `verseID` of the first verse in the `verses` field of this event. |
| `groups` | array | Unknown | An array of record IDs linking to the 'peopleGroups' table, representing groups involved in the event. |
| `modified` | string | Unknown | Last modified date and time |
| `sortKey` | float | Incomplete | Uses a combination of year and verseSort to sort all events chronolgically. The calculation formula, originated in airtable, is `INT(IF(LEFT(startDate,1)='-',LEFT(startDate,5),LEFT(startDate,4))) + INT(verseSort)/100000000`|
| `places (from verses)` | array | Unknown | An array of record IDs linking to the 'places' table, derived automatically from the associated verses. |
| `rangeFlag` | boolean | Unknown | If rangeFlag is true, it means that the year is an approximation and not an exact date. |
| `people (from verses)` | array | Unknown | An array of record IDs linking to the 'people' table, derived automatically from the associated verses. |
| `lagType` | string | Unknown | The type of predecessor relationship - either Start-to-Start (SS) or Finish-to-Start (FS). For example, for an event with lag of 130Y, lagType `FS` means that the event started 130 years after the predecessor event finished, whereas lagType `SS` means that the event started 130 years after the predecessor event started.|
| `eventID` | integer | Unknown | Unique identifier |

### Relationships
- `participants` → References field `id` of `people` table records
- `locations` → References field `id` of `places` table records
- `verses` → References field `id` of `verses` table records
- `predecessor` → References field `id` of `events` table records
- `partOf` → References field `id` of `events` table records
- `places (from verses)` → References field `id` of `places` table records
- `people (from verses)` → References field `id` of `people` table records

### Example
```json
{
  "id": "recy4o2BxavybTuX6",
  "createdTime": "2020-08-27T01:17:11.000Z",
  "fields": {
    "title": "Tower of Babel",
    "startDate": "-2245",
    "duration": "1D",
    "locations": [
      "recO7At5WvGRe0Xsu"
    ],
    "verses": [
      "recLJMCOtNOhHq9Rq"
    ],
    "verseSort": "01011001",
    "modified": "2020-11-25T15:12:15.000Z",
    "sortKey": -2244.98988999,
    "places (from verses)": [
      "rechl3VIoaKFb2C9f"
    ],
    "rangeFlag": true,
    "people (from verses)": [
      "reccZB8SVU5bEMcgo"
    ],
    "eventID": 53
  }
}
```
## People (38 Fields)
This table provides a comprehensive catalog of every individual mentioned by name in the Bible. Records include identifying information (e.g. `name`, `gender`), biographical details (e.g. `birthYear`, `deathYear`), and extensive relational data, linking to family members (`father`, `mother`, `siblings`), associated `events`, and all `verses` where the person is mentioned.

### Fields Reference (38 Fields)

| Field | Type | Status | Description |
|-------|------|--------|-------------|
| `personLookup` | string | Validated | Unique identifier using name and ID number |
| `personID` | integer | Validated | Unique numerical identifier, helping to distinguish people with the same name. |
| `name` | string | Validated | Primary name used in the text of the KJV |
| `surname` | string | Validated | Surname, if known. |
| `isProperName` | boolean | Validated | Identifies those with proper names vs. descriptive names like "Wife of..." or "Son of..." |
| `gender` | string | Validated | Male or Female |
| `birthYear` | array | Populated | An array of record IDs linking to the 'events' table (specifically year records), representing the person's birth year. |
| `deathYear` | array | Populated | An array of record IDs linking to the 'events' table (specifically year records), representing the person's death year. |
| `memberOf` | array | Validated | An array of record IDs linking to the 'peopleGroups' table, indicating the groups (tribes, families, etc.) the person belongs to. |
| `birthPlace` | array | Validated | An array of record IDs linking to the 'places' table, representing the person's birthplace. |
| `deathPlace` | array | Validated | An array of record IDs linking to the 'places' table, representing the person's place of death. |
| `dictionaryLink` | string | Unknown | A URL to its Easton's Bible Dictionary entry at https://www.biblestudytools.com/dictionaries/eastons-bible-dictionary. |
| `dictionaryText` | string | Unknown | The text content from its Easton's Bible Dictionary entry. |
| `events` | string | Incomplete | Title of events in which the person participated. Complete for the book of Acts |
| `verseCount` | integer | Validated | Counts verses where the person is mentioned by name |
| `verses` | array | Validated | An array of record IDs linking to the 'verses' table, representing every verse where this person is explicitly mentioned. |
| `siblings` | array | Validated | An array of record IDs linking to the 'people' table, representing the person's full siblings. |
| `halfSiblingsSameMother` | array | Validated | An array of record IDs linking to the 'people' table, representing the person's maternal half-siblings. |
| `halfSiblingsSameFather` | array | Validated | An array of record IDs linking to the 'people' table, representing the person's paternal half-siblings. |
| `chaptersWritten` | array | Validated | An array of record IDs linking to the 'chapters' table, representing chapters attributed to this person. |
| `mother` | array | Validated | An array containing the record ID of the person's mother in the 'people' table. |
| `father` | array | Validated | An array containing the record ID of the person's father in the 'people' table. |
| `children` | array | Validated | An array of record IDs linking to the 'people' table, representing the person's children. |
| `minYear` | integer | Temporary | Temporary to help align birth year to passage/events timeline |
| `maxYear` | integer | Temporary | Temporary to help align birth year to passage/events timeline |
| `displayTitle` | string | Populated | Disambiguated name suitable for page titles and search results |
| `status` | string | Temporary | The validation status of the individual person record |
| `alphaGroup` | string | Validated | Used for alphabetical indexing |
| `slug` | string | Validated | Lowercase, url-friendly version of personLookup |
| `partners` | array | Unknown | An array of record IDs linking to the 'people' table, representing the person's spouse(s) or partner(s). |
| `alsoCalled` | string | Populated | Alternate spellings or other known names for the same person. |
| `ambiguous` | boolean | Temporary | Identifies display titles which have not been edited for disambiguation. |
| `Disambiguation (temp)` | string | Temporary | Mechanical Turk entries used to aid in disambiguation |
| `eastons` | array | Incomplete | An array of record IDs linking to the 'easton' table, representing relevant dictionary entries. |
| `Easton's Count` | integer | Unknown | 1 if it exists as an entry in Easton's Bible Dictionary; 0 otherwise.|
| `dictText` | array | Incomplete | Markdown-formatted text from relevant sub-section in Easton's dictionary. |
| `modified` | string | Unknown | Last modified date and time |
| `timeline` | array | Unknown | An array of record IDs linking to the 'events' table, representing events associated with this person. |

### Relationships
- `birthYear` → References field `id` of `events` table
- `deathYear` → References field `id` of `events` table
- `memberOf` → References field `id` of `peopleGroups` table records
- `birthPlace` → References field `id` of `places` table records
- `deathPlace` → References field `id` of `places` table records
- `verses` → References field `id` of `verses` table records
- `siblings` → References field `id` of `people` table records
- `halfSiblingsSameMother` → References field `id` of `people` table records
- `halfSiblingsSameFather` → References field `id` of `people` table records
- `chaptersWritten` → References field `id` of `people` table records
- `mother` → References field `id` of `people` table records
- `father` → References field `id` of `people` table records
- `children` → References field `id` of `people` table records
- `partners` → References field `id` of `people` table records
- `eastons` → References field `id` of `easton` table records
- `timeline` → References field `id` of `events` table records

### Example
```json
{
  "id": "recsU2ZSdzBvDqzgI",
  "createdTime": "2018-03-19T00:26:39.000Z",
  "fields": {
    "personLookup": "israel_682",
    "personID": 682,
    "name": "Israel",
    "isProperName": true,
    "gender": "Male",
    "birthYear": [
      "recz75OtTAGsJtzXb"
    ],
    "deathYear": [
      "recI6wOLkJOEWZhcL"
    ],
    "memberOf": [
      "rechHR2dYztVvgNWa"
    ],
    "deathPlace": [
      "recfrXyxhuYOczKTm"
    ],
    "dictionaryLink": "https://www.biblestudytools.com/dictionaries/eastons-bible-dictionary/israel.html",
    "dictionaryText": " the name conferred on Jacob after the great prayer-struggle at Peniel (  Genesis 32:28  ), because \"as a prince he had power with God and prevailed.\" (See  JACOB  .) This is the common name given to Jacob's descendants.",
    "verseCount": 1009,
    "verses": [
      "recF0awhZCSb06TMf"
    ],
    "siblings": [
      "recUQWSZuOecG4z1Q"
    ],
    "mother": [
      "recZb9e7YIG9qh2qX"
    ],
    "father": [
      "recqIoG1fkaNWJ1y0"
    ],
    "children": [
      "recDggWlQNbxJLalN"
    ],
    "minYear": -1853,
    "maxYear": 96,
    "displayTitle": "Jacob (Israel)",
    "status": "publish",
    "alphaGroup": "I",
    "slug": "israel_682",
    "partners": [
      "recdaqUcGEFXwM0Ml"
    ],
    "alsoCalled": "Israel",
    "eastons": [
      "recPxmjv7HmVeGVSD"
    ],
    "Easton's Count": 1,
    "dictText": [
      "One who follows on another’s heels; supplanter, ([Gen. 25:26](/gen#Gen.25.26); [27:36](/gen#Gen.27.36); [Hos. 12:2-4](/hos#Hos.12.2)), the second born of the twin sons of Isaac by Rebekah. He was born probably at Lahai-roi, when his father was fifty-nine and Abraham one hundred and fifty-nine years old."
    ],
    "modified": "2020-09-07T01:31:05.000Z",
    "timeline": [
      "recAyNphNXcFdeBdv"
    ]
  }
}
```

## PeopleGroups (7 Fields)
This table defines collective groups of people, such as tribes, nations, or families. Each record has a `groupName` and contains an array of `members` who belong to that group. It also links to `verses` where the group is mentioned and `events` in which they participated.

### Fields Reference (7 Fields)

| Field | Type | Status | Description |
|-------|------|--------|-------------|
| `groupName` | string | Validated | Unique name |
| `members` | array | Validated | An array of record IDs linking to the 'people' table, representing the individual members of this group. |
| `verses` | array | Incomplete | An array of record IDs linking to the 'verses' table, representing verses where this group is mentioned. |
| `modified` | string | Unknown | Last modified date and time |
| `events` | string | Incomplete | Events in which this group participated. |
| `events_dev` | array | Unknown | An array of record IDs linking to the 'events' table, representing events involving this group. |
| `partOf` | array | Unknown | An array containing the record ID of a parent group in the 'peopleGroups' table. |

### Relationships
- `members` → References field `id` of `people` table records
- `verses` → References field `id` of `verses` table records
- `events_dev` → References field `id` of `events` table records
- `partOf` → References field `id` of `peopleGroups` table records

### Example
```json
{
  "id": "recb9l9ttaZlODOFV",
  "createdTime": "2018-08-20T16:34:00.000Z",
  "fields": {
    "groupName": "Apostles (The Eleven)",
    "members": [
      "recX9MMADoVI2CSP1"
    ],
    "events": "The Holy Spirit is promised, Jesus ascends to Heaven, Matthias replaces Judas",
    "modified": "2025-08-21T23:23:51.000Z",
    "events_dev": [
      "recvfB75N6vrQwhWW"
    ]
  }
}
```

## Places (40 Fields)
This table catalogs all geographic locations mentioned in the Bible. Each record includes identifying names (e.g. `kjvName`, `displayTitle`), geographic coordinates (e.g. `latitude`, `longitude`), and feature classifications (e.g. `featureType`, `featureSubType`). It also links to all `verses` mentioning the location, `events` that occurred there, and people associated with it.

### Fields Reference (40 Fields)

| Field | Type | Status | Description |
|-------|------|--------|-------------|
| `placeLookup` | string | Validated | Unique identifier using name and ID number |
| `openBibleLat` | string | Populated | Latitude from OpenBible.info |
| `openBibleLong` | string | Populated | Longitude from OpenBible.info |
| `kjvName` | string | Validated | Place name in the King James Version |
| `esvName` | string | Validated | Place Name in the English Standard Version (from OpenBible.info/geo) |
| `comment` | string | Incomplete | Comments from OpenBible.info/geo |
| `precision` | string | Incomplete | Relative accuracy of lat/long assignment |
| `featureType` | string | Incomplete | Delineates, region, city, water, etc. Complete for the book of Acts |
| `rootID` | array | Temporary | An array containing the record ID of another place record from which coordinates are inherited. |
| `aliases` | string | Populated | Alternate names for the same coordinate |
| `dictionaryLink` | string | Unknown | A URL to its Easton's Bible Dictionary entry at https://www.biblestudytools.com/dictionaries/eastons-bible-dictionary. |
| `dictionaryText` | string | Unknown | The text content from its Easton's Bible Dictionary entry. |
| `verseCount` | integer | Validated | Counts how many verses mention this place by name |
| `placeID` | integer | Validated | Unique numerical identifier, useful to separate places which share the same name |
| `recogitoUri` | string | Populated | Links to an associated place in other historical databases |
| `recogitoLat` | string | Populated | Latitude from Recogito matches |
| `recogitoLon` | string | Populated | Longitude from Recogito matches |
| `peopleBorn` | array | Validated | An array of record IDs linking to the 'people' table, representing individuals born at this location. |
| `peopleDied` | array | Validated | An array of record IDs linking to the 'people' table, representing individuals who died at this location. |
| `booksWritten` | array | Incomplete | An array of record IDs linking to the 'books' table, representing books written at this location. |
| `verses` | array | Validated | An array of record IDs linking to the 'verses' table, representing verses where this place is mentioned. |
| `recogitoStatus` | string | Populated | Verification of inks to other historical databases |
| `recogitoType` | string | Populated | Geographic type from Recogito matches |
| `recogitoComments` | string | Populated | Notes on place assignments from Recogito |
| `recogitoLabel` | string | Populated | Title from Recogito matches |
| `recogitoUID` | string | Populated | Unique ID for importing Recogito records |
| `hasBeenHere` | string | Incomplete | A string containing a comma-separated list of `personLookup` identifiers for people who have visited this location. |
| `latitude` | string | Populated | Best available latitude, depending on Recogito and OpenBible validation |
| `longitude` | string | Populated | Best available longitude, depending on Recogito and OpenBible validation |
| `status` | string | Temporary | The validation status of the individual place record |
| `displayTitle` | string | Populated | Disambiguated name suitable for page titles and search results |
| `alphaGroup` | string | Validated | Used for alphabetical indexing |
| `slug` | string | Validated | Lowercase, url-friendly version of placeLookup |
| `duplicate_of` | array | Temporary | An array containing the record ID of the primary place record that this record duplicates. |
| `ambiguous` | boolean | Temporary | Identifies display titles which have not been edited for disambiguation. |
| `eastons` | array | Incomplete | An array of record IDs linking to the 'easton' table, representing relevant dictionary entries. |
| `dictText` | array | Incomplete | Markdown-formatted text from relevant sub-section in Easton's dictionary. |
| `modified` | string | Unknown | Last modified date and time |
| `eventsHere` | array | Incomplete | An array of record IDs linking to the 'events' table, representing events that occurred at this location.nts that occurred at this location. |
| `featureSubType` | string | Unknown | A more specific classification of the featureType, such as "River" for the "Water" type. |

### Relationships
- `peopleBorn` → References field `id` of `people` table records
- `peopleDied` → References field `id` of `people` table records
- `booksWritten` → References field `id` of `books` table records
- `verses` → References field `id` of `verses` table records
- `hasBeenHere` → References subfield `personLookup` of field `fields` of `people` table records
- `duplicate_of` → References field `id` of `places` table records
- `eastons` → References field `id` of `easton` table records
- `eventsHere` → References field `id` of `events` table records

### Example
```json
{
  "placeLookup": "egypt_362",
  "openBibleLat": "30.108086",
  "openBibleLong": "31.338220",
  "kjvName": "Egypt",
  "esvName": "Egypt",
  "comment": "region",
  "featureType": "Region",
  "verseCount": 564,
  "placeID": 362,
  "recogitoUri": "http://sws.geonames.org/357994",
  "recogitoLat": "26.4902014068366",
  "recogitoLon": "29.88079617",
  "verses": [
    "recX74cRHwDmYb1sK",
    "recPMnvB1cd7AQgro",
  ],
  "recogitoStatus": "VERIFIED",
  "recogitoLabel": "Egypt",
  "recogitoUID": "2f0169bb-b510-4688-8fca-9ea9ea19ed0d",
  "latitude": "26.4902014068366",
  "longitude": "29.88079617",
  "status": "publish",
  "displayTitle": "Egypt",
  "alphaGroup": "E",
  "slug": "egypt_362",
  "eastons": [
    "recaI03cdUrqCbVQE"
  ],
  "dictText": [
    "The land of the Nile and the pyramids, the oldest kingdom of which we have any record, holds a place of great significance in Scripture."
  ],
  "modified": "2021-05-06T20:48:10.000Z",
  "featureSubType": "Country",
  "rootID": [
    "recK0feE032FY9Hxi"
  ],
  "peopleDied": [
    "recPXtuWYdjyghv7R",
    "recsU2ZSdzBvDqzgI",
    "rechuDYJoK32gmrME"
  ],
  "precision": "Related-Surrounding",
  "recogitoType": "administrative-region",
  "hasBeenHere": "benjamin_463, moses_2108",
  "eventsHere": [
    "recbqTND1uSdqNjOx",
    "recwCFb0NhrYMkl8t",
  ],
  "dictionaryLink": "https://www.biblestudytools.com/dictionaries/eastons-bible-dictionary/egypt.html",
  "dictionaryText": " the land of the Nile and the pyramids, the oldest kingdom of which we have any record, holds a place of great significance in Scripture.",
  "recogitoComments": "Use this as a label but not the modern borders",
  "peopleBorn": [
    "recv0dAY2ULzJ687g",
    "rechuDYJoK32gmrME",
    "recvZksoA0NmFrYZ7",
    "recjNRR60PAuFtjha"
  ]
}
```

## Verses (17 Fields)
This table contains the full text of every verse in the King James Version (`verseText`). Each verse is a fundamental unit of the dataset, identified by its `osisRef` (an ID using Open Scriptural Information Standard) and linked to its `book` and `chapter`. It also contains the core relational data, linking to the specific `people`, `places`, `peopleGroups`, and `event` referenced in its text.

### Fields Reference (17 Fields)

| Field | Type | Status | Description |
|-------|------|--------|-------------|
| `osisRef` | string | Validated | Unique identifier using the Open Scriptural Information Standard |
| `verseNum` | string | Validated | Verse Number (integer) |
| `verseText` | string | Validated | King James Version text, unformatted. |
| `book` | array | Validated | An array containing the record ID of the book this verse belongs to. |
| `people` | array | Validated | An array of record IDs linking to the 'people' table, representing individuals mentioned in this verse. |
| `peopleCount` | integer | Validated | Number of people mentioned by name |
| `placesCount` | integer | Validated | Number of place mentioned by name |
| `places` | array | Validated | An array of record IDs linking to the 'places' table, representing locations mentioned in this verse. |
| `yearNum` | integer | Populated | Year related to the verse from Torrey's Treasury of Scripture Knowledge. Not aligned with the events table. |
| `peopleGroups` | array | Incomplete | An array of record IDs linking to the 'peopleGroups' table, representing groups mentioned in this verse. |
| `chapter` | array | Validated | An array containing the record ID of the chapter this verse belongs to. |
| `status` | string | Temporary | The validation status of the linkage between the verse and people, places, or events. |
| `mdText` | string | Populated | King James Version text, with markdown formatting for exports. |
| `richText` | string | Populated | King James Version text, with Rich Text formatting for Airtable. |
| `verseID` | string | Validated | Unique sequential identifier, useful for sorting. |
| `modified` | string | Unknown | Last modified date and time |
| `event` | array | Unknown | An array of record IDs linking to the 'events' table, representing events associated with this verse. |

### Relationships
- `book` → References field `id` of `books` table records
- `people` → References field `id` of `people` table records
- `places` → References field `id` of `places` table records
- `chapter` → References field `id` of `chapters` table records
- `peopleGroups` → References field `id` of `peopleGroups` table records
- `event` → References field `id` of `events` table records

### Example
```json
{
  "osisRef": "Gen.2.8",
  "verseNum": "8",
  "verseText": "And the LORD God planted a garden eastward in Eden; and there he put the man whom he had formed.",
  "book": [
    "recIFusdNl6d8dj3L"
  ],
  "people": [
    "reccZB8SVU5bEMcgo"
  ],
  "peopleCount": 1,
  "placesCount": 1,
  "places": [
    "recLIUK6VRKNjnGo6"
  ],
  "yearNum": -4004,
  "chapter": [
    "recParAnlMHJy8vSQ"
  ],
  "status": "publish",
  "mdText": "And the [LORD]([/person/god_1324) [God]([/person/god_1324) planted a garden eastward in Eden; and there he put the man whom he had formed.",
  "richText": "And the [LORD](/person/god_1324) [God](/person/god_1324) planted a garden eastward in Eden; and there he put the man whom he had formed.\n",
  "verseID": "01002008",
  "modified": "2021-01-08T15:07:18.000Z",
  "event": [
    "recTU3ZxG7zQ61N9d"
  ]
}
```