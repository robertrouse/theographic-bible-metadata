const { ApolloServer } = require('@apollo/server');
const { ApolloServerPluginLandingPageLocalDefault } = require('@apollo/server/plugin/landingPage/default');
const { gql } = require('graphql-tag');
const fs = require('fs');
const path = require('path');

const typeDefs = gql`
  # ── Filter input types ───────────────────────────────────────────────────────

  """
  Filter a string field. All specified sub-fields are combined with AND logic.
  """
  input StringFilter {
    "Exact, case-sensitive match. Example: { eq: \\"Genesis\\" }"
    eq: String
    "Case-insensitive substring match. Example: { contains: \\"samuel\\" }"
    contains: String
  }

  """
  Filter an integer field. All specified sub-fields are combined with AND logic.
  """
  input IntFilter {
    "Exact match. Example: { eq: 1 }"
    eq: Int
    "Greater than or equal. Example: { gte: 100 }"
    gte: Int
    "Less than or equal. Example: { lte: 500 }"
    lte: Int
  }

  """
  Filter a boolean field.
  """
  input BooleanFilter {
    "Exact match. Example: { eq: true }"
    eq: Boolean
  }

  """
  Filter arguments for the books query. All fields are combined with AND logic.

  Examples:
  - New Testament books: { testament: { eq: "New Testament" } }
  - Books with "samuel" in the name: { bookName: { contains: "samuel" } }
  - First five books: { bookOrder: { gte: 1, lte: 5 } }
  """
  input BookFilter {
    "Filter by record ID"
    id: StringFilter
    "Full book name, e.g. \\"Genesis\\", \\"Revelation\\""
    bookName: StringFilter
    "OSIS abbreviation, e.g. \\"Gen\\", \\"Rev\\""
    osisName: StringFilter
    "Short name abbreviation"
    shortName: StringFilter
    "Canon division: \\"Old Testament\\" or \\"New Testament\\""
    testament: StringFilter
    "Canonical section: \\"Pentateuch\\", \\"Gospels\\", \\"Epistles\\", etc."
    bookDiv: StringFilter
    "Canonical order (1 = Genesis, 66 = Revelation)"
    bookOrder: IntFilter
    "Number of chapters in the book"
    chapterCount: IntFilter
    "Total number of verses in the book"
    verseCount: IntFilter
    "URL-friendly slug, e.g. \\"gen\\", \\"rev\\""
    slug: StringFilter
  }

  """
  Filter arguments for the chapters query. All fields are combined with AND logic.

  Examples:
  - All Genesis chapters: { osisRef: { contains: "Gen" } }
  - Chapter 1 of any book: { chapterNum: { eq: 1 } }
  - Chapters with many people: { peopleCount: { gte: 50 } }
  """
  input ChapterFilter {
    "Filter by record ID"
    id: StringFilter
    "OSIS reference, e.g. \\"Gen.1\\", \\"John.3\\""
    osisRef: StringFilter
    "URL-friendly slug, e.g. \\"gen_1\\""
    slug: StringFilter
    "Chapter number within its book"
    chapterNum: IntFilter
    "Number of distinct people mentioned in this chapter"
    peopleCount: IntFilter
    "Number of distinct places mentioned in this chapter"
    placesCount: IntFilter
    "Number of writers attributed to this chapter"
    writerCount: IntFilter
  }

  """
  Filter arguments for the verses query. All fields are combined with AND logic.

  Examples:
  - A specific verse: { osisRef: { eq: "Gen.1.1" } }
  - Verses from the NT ministry period: { yearNum: { gte: 30, lte: 33 } }
  - Full-text search: { verseText: { contains: "God so loved" } }
  """
  input VerseFilter {
    "Filter by record ID"
    id: StringFilter
    "OSIS reference, e.g. \\"Gen.1.1\\", \\"John.3.16\\""
    osisRef: StringFilter
    "Case-insensitive substring search across verse text"
    verseText: StringFilter
    "Estimated year of the verse's events (negative = BC)"
    yearNum: IntFilter
    "Number of people mentioned in this verse"
    peopleCount: IntFilter
    "Publication status: \\"publish\\" or \\"draft\\""
    status: StringFilter
  }

  """
  Filter arguments for the people query. All fields are combined with AND logic.

  Examples:
  - All women: { gender: { eq: "Female" } }
  - People named Mary: { name: { contains: "mary" } }
  - Major figures: { verseCount: { gte: 200 } }
  - By slug: { slug: { eq: "moses_2108" } }
  """
  input PersonFilter {
    "Filter by record ID"
    id: StringFilter
    "Primary name, e.g. \\"Moses\\", \\"Mary\\""
    name: StringFilter
    "Display title (may include disambiguation, e.g. \\"Mary Magdalene\\")"
    displayTitle: StringFilter
    "Internal lookup key, e.g. \\"moses_2108\\""
    personLookup: StringFilter
    "Gender: \\"Male\\" or \\"Female\\""
    gender: StringFilter
    "URL-friendly slug"
    slug: StringFilter
    "Alternate names or titles this person is known by"
    alsoCalled: StringFilter
    "Alphabetical grouping letter"
    alphaGroup: StringFilter
    "Record status"
    status: StringFilter
    "Whether this person's identity is disputed or unclear"
    ambiguous: BooleanFilter
    "Whether this is a proper name (vs. a title or role)"
    isProperName: BooleanFilter
    "Number of verses this person appears in"
    verseCount: IntFilter
    "Earliest estimated year of activity (negative = BC)"
    minYear: IntFilter
    "Latest estimated year of activity (negative = BC)"
    maxYear: IntFilter
  }

  """
  Filter arguments for the places query. All fields are combined with AND logic.

  Examples:
  - Rivers and seas: { featureType: { eq: "Water" } }
  - Places with Jordan in the name: { kjvName: { contains: "jordan" } }
  - Exact match: { kjvName: { eq: "Jerusalem" } }
  - Major locations: { verseCount: { gte: 400 } }
  """
  input PlaceFilter {
    "Filter by record ID"
    id: StringFilter
    "KJV place name, e.g. \\"Jerusalem\\", \\"Egypt\\""
    kjvName: StringFilter
    "ESV place name (may differ from KJV)"
    esvName: StringFilter
    "Display title (may include disambiguation)"
    displayTitle: StringFilter
    "Internal lookup key, e.g. \\"jerusalem_1\\""
    placeLookup: StringFilter
    "Geographic feature type: \\"City\\", \\"Water\\", \\"Mountain\\", \\"Region\\", \\"Country\\", etc."
    featureType: StringFilter
    "More specific feature sub-type"
    featureSubType: StringFilter
    "URL-friendly slug"
    slug: StringFilter
    "Alphabetical grouping letter"
    alphaGroup: StringFilter
    "Record status"
    status: StringFilter
    "Whether this place's identification is disputed"
    ambiguous: BooleanFilter
    "Number of verses that mention this place"
    verseCount: IntFilter
  }

  """
  Filter arguments for the events query. All fields are combined with AND logic.

  Examples:
  - Events about creation: { title: { contains: "creation" } }
  - A specific event: { eventID: { eq: 1 } }
  - Events in a time range (BC): { sortKey: { gte: -1000, lte: -900 } }
  - Exact title: { title: { eq: "Exodus from Egypt" } }
  """
  input EventFilter {
    "Filter by record ID"
    id: StringFilter
    "Event title, e.g. \\"Creation of all things\\""
    title: StringFilter
    "Additional notes about the event"
    notes: StringFilter
    "Start date string (may be a year number as string)"
    startDate: StringFilter
    "Duration string, e.g. \\"7D\\" (7 days), \\"40Y\\" (40 years)"
    duration: StringFilter
    "Type of time lag: \\"YR\\", \\"DAY\\", etc."
    lagType: StringFilter
    "Whether this event spans a range of time rather than a point"
    rangeFlag: BooleanFilter
    "Sequential event ID number"
    eventID: IntFilter
    "Numeric sort key representing approximate year (negative = BC). Use gte/lte for time ranges."
    sortKey: IntFilter
  }

  """
  Filter arguments for the peopleGroups query. All fields are combined with AND logic.

  Examples:
  - Exact group: { groupName: { eq: "Tribe of Levi" } }
  - All tribes: { groupName: { contains: "tribe" } }
  """
  input PeopleGroupFilter {
    "Filter by record ID"
    id: StringFilter
    "Group name, e.g. \\"Tribe of Levi\\", \\"The Twelve Apostles\\""
    groupName: StringFilter
  }

  """
  Filter arguments for the easton query. All fields are combined with AND logic.

  Examples:
  - A specific entry: { termLabel: { eq: "Aaron" } }
  - Person entries only: { matchType: { eq: "person" } }
  - Entries mentioning Jerusalem: { dictText: { contains: "Jerusalem" } }
  """
  input EastonFilter {
    "Filter by record ID"
    id: StringFilter
    "Dictionary term label, e.g. \\"Aaron\\", \\"Baptism\\""
    termLabel: StringFilter
    "Dictionary lookup key"
    dictLookup: StringFilter
    "Match type: \\"person\\", \\"place\\", or \\"unmatched\\""
    matchType: StringFilter
    "Case-insensitive substring search within the definition text"
    dictText: StringFilter
  }

  # ── Core types ────────────────────────────────────────────────────────────────

  """
  A book of the Bible. Contains metadata, canonical ordering, and links to
  its chapters, verses, writers, and places where it was written.
  """
  type Book {
    "Unique record ID"
    id: String!
    "OSIS standard abbreviation, e.g. \\"Gen\\", \\"Matt\\""
    osisName: String
    "Full book name, e.g. \\"Genesis\\", \\"Matthew\\""
    bookName: String
    "Number of chapters in this book"
    chapterCount: Int
    "Canonical section, e.g. \\"Pentateuch\\", \\"Gospels\\", \\"Epistles\\""
    bookDiv: String
    "Short abbreviation, e.g. \\"Ge\\", \\"Mt\\""
    shortName: String
    "Canonical order (1 = Genesis, 66 = Revelation)"
    bookOrder: Int
    "All verses in this book"
    verses: [Verse]
    "Estimated year(s) the book was written"
    yearWritten: [String]
    "Place(s) where the book was written"
    placeWritten: [Place]
    "Total number of verses in this book"
    verseCount: Int
    "All chapters in this book"
    chapters: [Chapter]
    "Attributed author(s) of this book"
    writers: [Person]
    "\\"Old Testament\\" or \\"New Testament\\""
    testament: String
    "URL-friendly slug, e.g. \\"gen\\", \\"matt\\""
    slug: String
    "Number of distinct people mentioned across this book"
    peopleCount: Int
    "Number of distinct places mentioned across this book"
    placeCount: Int
  }

  """
  A single chapter within a book of the Bible.
  """
  type Chapter {
    "Unique record ID"
    id: String!
    "OSIS reference, e.g. \\"Gen.1\\", \\"John.3\\""
    osisRef: String
    "The book this chapter belongs to"
    book: [Book]
    "Chapter number within its book"
    chapterNum: Int
    "Attributed writer(s) of this chapter"
    writer: [Person]
    "All verses in this chapter"
    verses: [Verse]
    "URL-friendly slug, e.g. \\"gen_1\\""
    slug: String
    "Number of distinct people mentioned in this chapter"
    peopleCount: Int
    "Number of distinct places mentioned in this chapter"
    placesCount: Int
    "Last modified timestamp"
    modified: String
    "Number of writers attributed to this chapter"
    writerCount: Int
  }

  """
  A single verse of the Bible, including its text and all linked entities
  (people, places, events, groups).
  """
  type Verse {
    "Unique record ID"
    id: String!
    "OSIS reference, e.g. \\"Gen.1.1\\", \\"John.3.16\\""
    osisRef: String
    "Verse number within its chapter"
    verseNum: String
    "Full KJV verse text"
    verseText: String
    "The book this verse belongs to"
    book: [Book]
    "People mentioned or referenced in this verse"
    people: [Person]
    "Number of people mentioned in this verse"
    peopleCount: Int
    "Places mentioned or referenced in this verse"
    places: [Place]
    "Number of places mentioned in this verse"
    placesCount: Int
    "Estimated year of the verse's events (negative = BC)"
    yearNum: Int
    "People groups mentioned in this verse"
    peopleGroups: [PeopleGroup]
    "The chapter this verse belongs to"
    chapter: [Chapter]
    "Publication status: \\"publish\\" or \\"draft\\""
    status: String
    "Verse text with Markdown entity links"
    mdText: String
    "Verse text with rich-text formatting"
    richText: String
    "Legacy verse ID string"
    verseID: String
    "Last modified timestamp"
    modified: String
    "Biblical events that include this verse"
    event: [Event]
  }

  """
  A biblical person, including biographical data, family relationships,
  and links to verses, groups, places, and events.
  """
  type Person {
    "Unique record ID"
    id: String!
    "Internal lookup key, e.g. \\"moses_2108\\""
    personLookup: String
    "Sequential person ID number"
    personID: Int
    "Primary name, e.g. \\"Moses\\", \\"Mary\\""
    name: String
    "Surname or family name, if applicable"
    surname: String
    "Whether this is a proper name (vs. a title or collective role)"
    isProperName: Boolean
    "\\"Male\\" or \\"Female\\""
    gender: String
    """
    Estimated birth year as an ISO 8601 astronomical year integer (e.g. -1574).

    Uses ISO 8601 astronomical year numbering: 0 = 1 BC, -1 = 2 BC, etc.
    To convert to a traditional BC year: negate and add 1 (e.g. -1574 = 1575 BC,
    -4003 = 4004 BC). Positive values are AD years (e.g. 30 = AD 30).
    """
    birthYear: Int
    """
    Estimated death year as an ISO 8601 astronomical year integer (e.g. -1451).

    Uses ISO 8601 astronomical year numbering: 0 = 1 BC, -1 = 2 BC, etc.
    To convert to a traditional BC year: negate and add 1 (e.g. -1451 = 1452 BC).
    Positive values are AD years (e.g. 96 = AD 96).
    """
    deathYear: Int
    "People groups this person belongs to (tribes, nations, sects, etc.)"
    memberOf: [PeopleGroup]
    "Place(s) where this person was born"
    birthPlace: [Place]
    "Place(s) where this person died"
    deathPlace: [Place]
    "URL to an external dictionary entry"
    dictionaryLink: String
    "Text of the external dictionary entry"
    dictionaryText: String
    "Legacy events string"
    events: String
    "Number of verses this person appears in"
    verseCount: Int
    "All verses this person appears in"
    verses: [Verse]
    "Full siblings (same father and mother)"
    siblings: [Person]
    "Half-siblings sharing the same mother"
    halfSiblingsSameMother: [Person]
    "Half-siblings sharing the same father"
    halfSiblingsSameFather: [Person]
    "Chapters attributed to this person as writer"
    chaptersWritten: [Chapter]
    "Mother of this person"
    mother: [Person]
    "Father of this person"
    father: [Person]
    "Children of this person"
    children: [Person]
    "Earliest estimated year of activity (negative = BC)"
    minYear: Int
    "Latest estimated year of activity (negative = BC)"
    maxYear: Int
    "Display title, may include disambiguation"
    displayTitle: String
    "Record status"
    status: String
    "Alphabetical grouping letter"
    alphaGroup: String
    "URL-friendly slug, e.g. \\"moses_2108\\""
    slug: String
    "Spouses or partners"
    partners: [Person]
    "Alternate names or titles this person is also known by"
    alsoCalled: String
    "Whether this person's identity is disputed or unclear"
    ambiguous: Boolean
    "Easton's Bible Dictionary entries linked to this person"
    eastons: [Easton]
    "Dictionary text snippets"
    dictText: [String]
    "Last modified timestamp"
    modified: String
    "Events this person was involved in, in chronological order"
    timeline: [Event]
  }

  """
  A named group of people — a tribe, nation, sect, army, or other collective.
  Examples: Tribe of Levi, Pharisees, The Twelve Apostles.
  """
  type PeopleGroup {
    "Unique record ID"
    id: String!
    "Group name, e.g. \\"Tribe of Levi\\", \\"Pharisees\\""
    groupName: String
    "Individual members of this group"
    members: [Person]
    "Verses that mention this group"
    verses: [Verse]
    "Last modified timestamp"
    modified: String
    "Legacy events string"
    events: String
    "Events associated with this group"
    eventsDev: [Event]
    "Parent group(s) this group is a part of"
    partOf: [PeopleGroup]
  }

  """
  A geographical location mentioned in the Bible, with coordinates,
  feature type, and links to people and events associated with it.
  """
  type Place {
    "Unique record ID"
    id: String!
    "Internal lookup key, e.g. \\"jerusalem_1\\""
    placeLookup: String
    "Latitude from the OpenBible dataset"
    openBibleLat: String
    "Longitude from the OpenBible dataset"
    openBibleLong: String
    "Place name as it appears in the KJV"
    kjvName: String
    "Place name as it appears in the ESV"
    esvName: String
    "Notes or comments about this place"
    comment: String
    "Coordinate precision level"
    precision: String
    "Geographic feature type: \\"City\\", \\"Water\\", \\"Mountain\\", \\"Region\\", \\"Country\\", etc."
    featureType: String
    "Root place IDs this place is derived from"
    rootID: [String]
    "Alternate names or aliases"
    aliases: String
    "URL to an external dictionary entry"
    dictionaryLink: String
    "Text of the external dictionary entry"
    dictionaryText: String
    "Number of verses that mention this place"
    verseCount: Int
    "Sequential place ID number"
    placeID: Int
    "Recogito annotation URI"
    recogitoUri: String
    "Latitude from the Recogito dataset"
    recogitoLat: String
    "Longitude from the Recogito dataset"
    recogitoLon: String
    "People born at this place"
    peopleBorn: [Person]
    "People who died at this place"
    peopleDied: [Person]
    "Books written at this place"
    booksWritten: [Book]
    "Verses that mention this place"
    verses: [Verse]
    "Recogito annotation status"
    recogitoStatus: String
    "Recogito place type"
    recogitoType: String
    "Recogito annotation comments"
    recogitoComments: String
    "Recogito display label"
    recogitoLabel: String
    "Recogito unique ID"
    recogitoUID: String
    "People or groups recorded as having been at this place"
    hasBeenHere: String
    "Preferred latitude (decimal degrees)"
    latitude: String
    "Preferred longitude (decimal degrees)"
    longitude: String
    "Record status"
    status: String
    "Display title, may include disambiguation"
    displayTitle: String
    "Alphabetical grouping letter"
    alphaGroup: String
    "URL-friendly slug"
    slug: String
    "If this is a duplicate, the canonical place record(s)"
    duplicateOf: [Place]
    "Whether this place's identification is disputed"
    ambiguous: Boolean
    "Easton's Bible Dictionary entries linked to this place"
    eastons: [Easton]
    "Dictionary text snippets"
    dictText: [String]
    "Last modified timestamp"
    modified: String
    "Events that took place here"
    eventsHere: [Event]
    "More specific feature sub-type"
    featureSubType: String
  }

  """
  A biblical event — a narrative occurrence with a title, timeframe,
  participants, locations, and linked verses.

  sortKey is a float representing the approximate year (negative = BC),
  useful for chronological ordering and range filtering.
  """
  type Event {
    "Unique record ID"
    id: String!
    "Event title, e.g. \\"Creation of all things\\", \\"Baptism of Jesus\\""
    title: String
    "Start date string (may be a year number)"
    startDate: String
    "Duration string, e.g. \\"7D\\" (7 days), \\"40Y\\" (40 years)"
    duration: String
    "People who participated in this event"
    participants: [Person]
    "Places where this event occurred"
    locations: [Place]
    "Verses that describe or relate to this event"
    verses: [Verse]
    "The event that immediately precedes this one in the narrative"
    predecessor: [Event]
    "Time lag value between predecessor and this event"
    lag: String
    "Parent event(s) this event is part of"
    partOf: [Event]
    "Additional notes about this event"
    notes: String
    "Sort string based on verse reference"
    verseSort: String
    "People groups involved in this event"
    groups: [PeopleGroup]
    "Last modified timestamp"
    modified: String
    "Numeric sort key representing approximate year (negative = BC)"
    sortKey: Float
    "Whether this event spans a range of time rather than a single point"
    rangeFlag: Boolean
    "Type of time lag to the predecessor: \\"YR\\", \\"DAY\\", etc."
    lagType: String
    "Sequential event ID number"
    eventID: Int
  }

  """
  An entry from Easton's Bible Dictionary, optionally linked to
  a person or place in the dataset.
  """
  type Easton {
    "Unique record ID"
    id: String!
    "Dictionary lookup key"
    dictLookup: String
    "Term identifier within the dictionary"
    termID: String
    "The dictionary term (heading), e.g. \\"Aaron\\", \\"Baptism\\""
    termLabel: String
    "Definition paragraph ID"
    defId: String
    "Whether the entry includes a list"
    hasList: String
    "Item number within a multi-part entry"
    itemNum: Int
    "How this entry was matched to dataset records: \\"person\\", \\"place\\", or \\"unmatched\\""
    matchType: String
    "Slugs of matched records"
    matchSlugs: String
    "Full definition text"
    dictText: String
    "Person records linked to this dictionary entry"
    personLookup: [Person]
    "Place records linked to this dictionary entry"
    placeLookup: [Place]
    "Index position within the dictionary"
    index: Int
  }

  # ── Queries ───────────────────────────────────────────────────────────────────

  type Query {
    """
    Return books of the Bible, optionally filtered and paginated.

    Examples:
    \`\`\`graphql
    # All New Testament books
    books(where: { testament: { eq: "New Testament" } }) { bookName chapterCount }

    # Books with "samuel" in the name
    books(where: { bookName: { contains: "samuel" } }) { bookName }

    # Page 2 of Old Testament books (10 per page)
    books(where: { testament: { eq: "Old Testament" } }, limit: 10, offset: 10) { bookName }
    \`\`\`
    """
    books(
      "Filter books by one or more fields (AND logic)"
      where: BookFilter
      "Maximum number of results to return"
      limit: Int
      "Number of results to skip (for pagination)"
      offset: Int
    ): [Book]

    """
    Return chapters, optionally filtered and paginated.

    Examples:
    \`\`\`graphql
    # All 50 chapters of Genesis
    chapters(where: { osisRef: { contains: "Gen" } }) { osisRef chapterNum }

    # Chapter 1 of every book
    chapters(where: { chapterNum: { eq: 1 } }) { osisRef book { bookName } }
    \`\`\`
    """
    chapters(
      "Filter chapters by one or more fields (AND logic)"
      where: ChapterFilter
      "Maximum number of results to return"
      limit: Int
      "Number of results to skip (for pagination)"
      offset: Int
    ): [Chapter]

    """
    Return verses, optionally filtered and paginated.

    Examples:
    \`\`\`graphql
    # A specific verse by OSIS reference
    verses(where: { osisRef: { eq: "John.3.16" } }) { verseText }

    # Verses from the NT ministry period
    verses(where: { yearNum: { gte: 30, lte: 33 } }, limit: 50) { osisRef verseText }

    # Full-text search within verse text
    verses(where: { verseText: { contains: "God so loved" } }) { osisRef verseText }
    \`\`\`
    """
    verses(
      "Filter verses by one or more fields (AND logic)"
      where: VerseFilter
      "Maximum number of results to return"
      limit: Int
      "Number of results to skip (for pagination)"
      offset: Int
    ): [Verse]

    """
    Return people, optionally filtered and paginated.

    Examples:
    \`\`\`graphql
    # All women in the dataset
    people(where: { gender: { eq: "Female" } }) { name verseCount }

    # Major figures (appearing in 200+ verses)
    people(where: { verseCount: { gte: 200 } }) { name verseCount }

    # Look up by slug
    people(where: { slug: { eq: "moses_2108" } }) { name father { name } }
    \`\`\`
    """
    people(
      "Filter people by one or more fields (AND logic)"
      where: PersonFilter
      "Maximum number of results to return"
      limit: Int
      "Number of results to skip (for pagination)"
      offset: Int
    ): [Person]

    """
    Return places, optionally filtered and paginated.

    Examples:
    \`\`\`graphql
    # Rivers and seas
    places(where: { featureType: { eq: "Water" } }) { kjvName latitude longitude }

    # Places with "jordan" in the name
    places(where: { kjvName: { contains: "jordan" } }) { kjvName verseCount }

    # Major locations (400+ verse mentions)
    places(where: { verseCount: { gte: 400 } }) { kjvName verseCount }
    \`\`\`
    """
    places(
      "Filter places by one or more fields (AND logic)"
      where: PlaceFilter
      "Maximum number of results to return"
      limit: Int
      "Number of results to skip (for pagination)"
      offset: Int
    ): [Place]

    """
    Return events, optionally filtered and paginated.

    Events are sorted by their natural dataset order. Use sortKey for
    chronological ordering (negative values = BC).

    Examples:
    \`\`\`graphql
    # Events with "exodus" in the title
    events(where: { title: { contains: "exodus" } }) {
      title startDate participants { name }
    }

    # A specific event by ID
    events(where: { eventID: { eq: 1 } }) { title startDate }

    # Events in a chronological range (1000–900 BC)
    events(where: { sortKey: { gte: -1000, lte: -900 } }) {
      title sortKey locations { kjvName }
    }

    # First 20 events
    events(limit: 20) { title startDate sortKey }
    \`\`\`
    """
    events(
      "Filter events by one or more fields (AND logic)"
      where: EventFilter
      "Maximum number of results to return"
      limit: Int
      "Number of results to skip (for pagination)"
      offset: Int
    ): [Event]

    """
    Return people groups (tribes, nations, sects, etc.), optionally filtered.

    Examples:
    \`\`\`graphql
    # All tribes
    peopleGroups(where: { groupName: { contains: "tribe" } }) { groupName members { name } }

    # An exact group
    peopleGroups(where: { groupName: { eq: "The Twelve Apostles" } }) {
      groupName members { name }
    }
    \`\`\`
    """
    peopleGroups(
      "Filter groups by one or more fields (AND logic)"
      where: PeopleGroupFilter
      "Maximum number of results to return"
      limit: Int
      "Number of results to skip (for pagination)"
      offset: Int
    ): [PeopleGroup]

    """
    Return entries from Easton's Bible Dictionary, optionally filtered.

    Examples:
    \`\`\`graphql
    # Look up a specific term
    easton(where: { termLabel: { eq: "Aaron" } }) { termLabel dictText }

    # All person-matched entries
    easton(where: { matchType: { eq: "person" } }, limit: 20) { termLabel personLookup { name } }
    \`\`\`
    """
    easton(
      "Filter dictionary entries by one or more fields (AND logic)"
      where: EastonFilter
      "Maximum number of results to return"
      limit: Int
      "Number of results to skip (for pagination)"
      offset: Int
    ): [Easton]

    """
    Full-text search across verses by OSIS reference or verse text.
    Returns all verses where the input string appears in either field.

    Example: searchVerses(input: "John.3.16") or searchVerses(input: "God so loved")
    """
    searchVerses(
      "Text to search for in osisRef or verseText (case-insensitive)"
      input: String!
    ): [Verse]

    """
    Full-text search for people by name, alternate name, or lookup key.
    Returns all people where the input string matches any of those fields.

    Example: searchPeople(input: "Moses") or searchPeople(input: "Israel")
    """
    searchPeople(
      "Text to search for in name, alsoCalled, or personLookup (case-insensitive)"
      input: String!
    ): [Person]

    """
    Full-text search for places by KJV name, display title, or lookup key.
    Returns all places where the input string matches any of those fields.

    Example: searchPlaces(input: "Jerusalem") or searchPlaces(input: "egypt")
    """
    searchPlaces(
      "Text to search for in kjvName, displayTitle, or placeLookup (case-insensitive)"
      input: String!
    ): [Place]
  }
`;

// ── Data loading ──────────────────────────────────────────────────────────────

// Resolve the json/ directory. Try candidate paths in order:
//   1. Repo root relative to this file (local dev): api/netlify/functions/ -> ../../../json
//   2. Bundled alongside function at Lambda root (Netlify deploy): ../../../json same as above
//      but NFT places included_files relative to repo root, so also try ../../json and ./json
const candidateDirs = [
  path.join(__dirname, '../../../json'), // local dev: api/netlify/functions -> repo root/json
  path.join(__dirname, '../../json'),    // one level shallower (nft bundle layout)
  path.join(__dirname, 'json'),          // same directory as function
  path.join(process.cwd(), 'json'),      // cwd-relative (Lambda /var/task/json)
];

const dataDir = candidateDirs.find(dir => fs.existsSync(path.join(dir, 'books.json'))) || candidateDirs[0];
console.log('[graphql] dataDir resolved to:', dataDir);

const data = {};
const maps = {};

const types = ['books', 'chapters', 'verses', 'people', 'places', 'events', 'peopleGroups', 'easton'];

types.forEach(type => {
  const filePath = path.join(dataDir, `${type}.json`);
  if (fs.existsSync(filePath)) {
    data[type] = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    maps[type] = new Map(data[type].map(item => [item.id, item]));
  } else {
    console.warn('[graphql] WARNING: could not find', filePath);
    data[type] = [];
    maps[type] = new Map();
  }
});

// Secondary lookup maps for fields that use alternate keys instead of record IDs
const peopleByLookup = new Map(data.people.map(p => [p.fields.personLookup, p]));

// ── Filter helpers ────────────────────────────────────────────────────────────

/**
 * Test a single StringFilter against a value.
 * { eq } — case-sensitive exact match
 * { contains } — case-insensitive substring match
 * Returns true if the filter is satisfied (or if filter is null/undefined).
 */
function matchString(filter, value) {
  if (!filter) return true;
  const str = value == null ? '' : String(value);
  if (filter.eq !== undefined && filter.eq !== null) {
    if (str !== filter.eq) return false;
  }
  if (filter.contains !== undefined && filter.contains !== null) {
    if (!str.toLowerCase().includes(filter.contains.toLowerCase())) return false;
  }
  return true;
}

/**
 * Test a single IntFilter against a value.
 * { eq } — exact match; { gte } — >=; { lte } — <=
 */
function matchInt(filter, value) {
  if (!filter) return true;
  const num = value == null ? null : Number(value);
  if (filter.eq !== undefined && filter.eq !== null) {
    if (num !== filter.eq) return false;
  }
  if (filter.gte !== undefined && filter.gte !== null) {
    if (num == null || num < filter.gte) return false;
  }
  if (filter.lte !== undefined && filter.lte !== null) {
    if (num == null || num > filter.lte) return false;
  }
  return true;
}

/**
 * Test a BooleanFilter against a value.
 */
function matchBool(filter, value) {
  if (!filter) return true;
  if (filter.eq !== undefined && filter.eq !== null) {
    if (Boolean(value) !== filter.eq) return false;
  }
  return true;
}

/**
 * Apply a where clause + optional limit/offset to an array of raw records.
 * fieldMap is an object keyed by filter field name, each value is a function
 * (record) => rawValue to extract the field from the raw JSON record.
 */
function applyFilter(records, where, limit, offset, fieldMap) {
  let results = records;

  if (where) {
    results = records.filter(record => {
      for (const [key, extract] of Object.entries(fieldMap)) {
        const filterValue = where[key];
        if (!filterValue) continue;
        const rawValue = extract(record);
        // Determine filter kind by the fields present in the filter object
        if ('eq' in filterValue || 'contains' in filterValue) {
          if (!matchString(filterValue, rawValue)) return false;
        } else if ('gte' in filterValue || 'lte' in filterValue) {
          if (!matchInt(filterValue, rawValue)) return false;
        } else if ('eq' in filterValue && typeof filterValue.eq === 'boolean') {
          if (!matchBool(filterValue, rawValue)) return false;
        }
      }
      return true;
    });
  }

  if (offset) results = results.slice(offset);
  if (limit)  results = results.slice(0, limit);

  return results;
}

/**
 * Generic filter dispatcher: inspects the filter object's keys and applies
 * the correct matcher based on the filter type (String/Int/Boolean).
 *
 * We detect filter type from the keys present:
 *   StringFilter  has { eq?, contains? }  where eq is a string
 *   IntFilter     has { eq?, gte?, lte? } where eq is a number
 *   BooleanFilter has { eq }              where eq is a boolean
 */
function testFilter(filterValue, rawValue) {
  if (!filterValue || typeof filterValue !== 'object') return true;
  const keys = Object.keys(filterValue).filter(k => filterValue[k] !== null && filterValue[k] !== undefined);
  if (keys.length === 0) return true;

  // Boolean filter: eq is explicitly boolean
  if ('eq' in filterValue && typeof filterValue.eq === 'boolean' && !('contains' in filterValue)) {
    return matchBool(filterValue, rawValue);
  }
  // Int filter: has gte or lte, or eq is a number
  if ('gte' in filterValue || 'lte' in filterValue || ('eq' in filterValue && typeof filterValue.eq === 'number')) {
    return matchInt(filterValue, rawValue);
  }
  // Default: string filter
  return matchString(filterValue, rawValue);
}

/**
 * Build a filter function for a given where clause and field-extractor map.
 * Returns a predicate (record) => boolean.
 */
function buildPredicate(where, fieldMap) {
  if (!where) return () => true;
  return (record) => {
    for (const [key, extract] of Object.entries(fieldMap)) {
      const filterValue = where[key];
      if (!filterValue) continue;
      const rawValue = extract(record);
      if (!testFilter(filterValue, rawValue)) return false;
    }
    return true;
  };
}

/**
 * Filter, then paginate a dataset.
 */
function query(records, where, limit, offset, fieldMap) {
  const predicate = buildPredicate(where, fieldMap);
  let results = where ? records.filter(predicate) : records;
  if (offset) results = results.slice(offset);
  if (limit)  results = results.slice(0, limit);
  return results;
}

// ── Field-extractor maps (one per type) ───────────────────────────────────────

const bookFields = {
  id:           r => r.id,
  bookName:     r => r.fields.bookName,
  osisName:     r => r.fields.osisName,
  shortName:    r => r.fields.shortName,
  testament:    r => r.fields.testament,
  bookDiv:      r => r.fields.bookDiv,
  bookOrder:    r => r.fields.bookOrder,
  chapterCount: r => r.fields.chapterCount,
  verseCount:   r => r.fields.verseCount,
  slug:         r => r.fields.slug,
};

const chapterFields = {
  id:           r => r.id,
  osisRef:      r => r.fields.osisRef,
  slug:         r => r.fields.slug,
  chapterNum:   r => r.fields.chapterNum,
  peopleCount:  r => r.fields.peopleCount,
  placesCount:  r => r.fields.placesCount,
  writerCount:  r => r.fields['writer count'],
};

const verseFields = {
  id:          r => r.id,
  osisRef:     r => r.fields.osisRef,
  verseText:   r => r.fields.verseText,
  yearNum:     r => r.fields.yearNum,
  peopleCount: r => r.fields.peopleCount,
  status:      r => r.fields.status,
};

const personFields = {
  id:            r => r.id,
  name:          r => r.fields.name,
  displayTitle:  r => r.fields.displayTitle,
  personLookup:  r => r.fields.personLookup,
  gender:        r => r.fields.gender,
  slug:          r => r.fields.slug,
  alsoCalled:    r => r.fields.alsoCalled,
  alphaGroup:    r => r.fields.alphaGroup,
  status:        r => r.fields.status,
  ambiguous:     r => r.fields.ambiguous,
  isProperName:  r => r.fields.isProperName,
  verseCount:    r => r.fields.verseCount ?? r.fields.verses?.length ?? 0,
  minYear:       r => r.fields.minYear,
  maxYear:       r => r.fields.maxYear,
};

const placeFields = {
  id:             r => r.id,
  kjvName:        r => r.fields.kjvName,
  esvName:        r => r.fields.esvName,
  displayTitle:   r => r.fields.displayTitle,
  placeLookup:    r => r.fields.placeLookup,
  featureType:    r => r.fields.featureType,
  featureSubType: r => r.fields.featureSubType,
  slug:           r => r.fields.slug,
  alphaGroup:     r => r.fields.alphaGroup,
  status:         r => r.fields.status,
  ambiguous:      r => r.fields.ambiguous,
  verseCount:     r => r.fields.verseCount ?? r.fields.verses?.length ?? 0,
};

const eventFields = {
  id:        r => r.id,
  title:     r => r.fields.title,
  notes:     r => r.fields.notes,
  startDate: r => r.fields.startDate,
  duration:  r => r.fields.duration,
  lagType:   r => r.fields.lagType,
  rangeFlag: r => r.fields.rangeFlag,
  eventID:   r => r.fields.eventID,
  sortKey:   r => r.fields.sortKey,
};

const peopleGroupFields = {
  id:        r => r.id,
  groupName: r => r.fields.groupName,
};

const eastonFields = {
  id:         r => r.id,
  termLabel:  r => r.fields.termLabel,
  dictLookup: r => r.fields.dictLookup,
  matchType:  r => r.fields.matchType,
  dictText:   r => r.fields.dictText,
};

// ── Resolvers ─────────────────────────────────────────────────────────────────

const resolvers = {
  Query: {
    books:        (_, { where, limit, offset } = {}) => query(data.books,        where, limit, offset, bookFields),
    chapters:     (_, { where, limit, offset } = {}) => query(data.chapters,     where, limit, offset, chapterFields),
    verses:       (_, { where, limit, offset } = {}) => query(data.verses,       where, limit, offset, verseFields),
    people:       (_, { where, limit, offset } = {}) => query(data.people,       where, limit, offset, personFields),
    places:       (_, { where, limit, offset } = {}) => query(data.places,       where, limit, offset, placeFields),
    events:       (_, { where, limit, offset } = {}) => query(data.events,       where, limit, offset, eventFields),
    peopleGroups: (_, { where, limit, offset } = {}) => query(data.peopleGroups, where, limit, offset, peopleGroupFields),
    easton:       (_, { where, limit, offset } = {}) => query(data.easton,       where, limit, offset, eastonFields),

    searchVerses: (_, { input }) => {
      const lowerInput = input.toLowerCase();
      return data.verses.filter(v =>
        v.fields.osisRef?.toLowerCase().includes(lowerInput) ||
        v.fields.verseText?.toLowerCase().includes(lowerInput)
      );
    },
    searchPeople: (_, { input }) => {
      const lowerInput = input.toLowerCase();
      return data.people.filter(p =>
        p.fields.name?.toLowerCase().includes(lowerInput) ||
        p.fields.alsoCalled?.toLowerCase().includes(lowerInput) ||
        p.fields.personLookup?.toLowerCase().includes(lowerInput)
      );
    },
    searchPlaces: (_, { input }) => {
      const lowerInput = input.toLowerCase();
      return data.places.filter(p =>
        p.fields.kjvName?.toLowerCase().includes(lowerInput) ||
        p.fields.displayTitle?.toLowerCase().includes(lowerInput) ||
        p.fields.placeLookup?.toLowerCase().includes(lowerInput)
      );
    },
  },

  Book: {
    osisName:    (book) => book.fields.osisName,
    bookName:    (book) => book.fields.bookName,
    chapterCount:(book) => book.fields.chapterCount,
    bookDiv:     (book) => book.fields.bookDiv,
    shortName:   (book) => book.fields.shortName,
    bookOrder:   (book) => book.fields.bookOrder,
    verses:      (book) => book.fields.verses?.map(id => maps.verses.get(id)).filter(Boolean) || [],
    yearWritten: (book) => book.fields.yearWritten || [],
    placeWritten:(book) => book.fields.placeWritten?.map(id => maps.places.get(id)).filter(Boolean) || [],
    verseCount:  (book) => book.fields.verseCount,
    chapters:    (book) => book.fields.chapters?.map(id => maps.chapters.get(id)).filter(Boolean) || [],
    writers:     (book) => book.fields.writers?.map(id => maps.people.get(id) || peopleByLookup.get(id)).filter(Boolean) || [],
    testament:   (book) => book.fields.testament,
    slug:        (book) => book.fields.slug,
    peopleCount: (book) => book.fields.peopleCount,
    placeCount:  (book) => book.fields.placeCount,
  },

  Chapter: {
    osisRef:     (chapter) => chapter.fields.osisRef,
    book:        (chapter) => chapter.fields.book?.map(id => maps.books.get(id)).filter(Boolean) || [],
    chapterNum:  (chapter) => chapter.fields.chapterNum,
    writer:      (chapter) => chapter.fields.writer?.map(id => maps.people.get(id)).filter(Boolean) || [],
    verses:      (chapter) => chapter.fields.verses?.map(id => maps.verses.get(id)).filter(Boolean) || [],
    slug:        (chapter) => chapter.fields.slug,
    peopleCount: (chapter) => chapter.fields.peopleCount,
    placesCount: (chapter) => chapter.fields.placesCount,
    modified:    (chapter) => chapter.fields.modified,
    writerCount: (chapter) => chapter.fields['writer count'],
  },

  Verse: {
    osisRef:     (verse) => verse.fields.osisRef,
    verseNum:    (verse) => verse.fields.verseNum,
    verseText:   (verse) => verse.fields.verseText,
    book:        (verse) => verse.fields.book?.map(id => maps.books.get(id)).filter(Boolean) || [],
    people:      (verse) => verse.fields.people?.map(id => maps.people.get(id)).filter(Boolean) || [],
    peopleCount: (verse) => verse.fields.peopleCount,
    places:      (verse) => verse.fields.places?.map(id => maps.places.get(id)).filter(Boolean) || [],
    placesCount: (verse) => verse.fields.placesCount,
    yearNum:     (verse) => verse.fields.yearNum,
    peopleGroups:(verse) => verse.fields.peopleGroups?.map(id => maps.peopleGroups.get(id)).filter(Boolean) || [],
    chapter:     (verse) => verse.fields.chapter?.map(id => maps.chapters.get(id)).filter(Boolean) || [],
    status:      (verse) => verse.fields.status,
    mdText:      (verse) => verse.fields.mdText,
    richText:    (verse) => verse.fields.richText,
    verseID:     (verse) => verse.fields.verseID,
    modified:    (verse) => verse.fields.modified,
    event:       (verse) => verse.fields.event?.map(id => maps.events.get(id)).filter(Boolean) || [],
  },

  Person: {
    personLookup:          (person) => person.fields.personLookup,
    personID:              (person) => person.fields.personID,
    name:                  (person) => person.fields.name,
    surname:               (person) => person.fields.surname,
    isProperName:          (person) => person.fields.isProperName,
    gender:                (person) => person.fields.gender,
    birthYear:             (person) => person.fields.birthYear != null ? parseInt(person.fields.birthYear, 10) : null,
    deathYear:             (person) => person.fields.deathYear != null ? parseInt(person.fields.deathYear, 10) : null,
    memberOf:              (person) => person.fields.memberOf?.map(id => maps.peopleGroups.get(id)).filter(Boolean) || [],
    birthPlace:            (person) => person.fields.birthPlace?.map(id => maps.places.get(id)).filter(Boolean) || [],
    deathPlace:            (person) => person.fields.deathPlace?.map(id => maps.places.get(id)).filter(Boolean) || [],
    dictionaryLink:        (person) => person.fields.dictionaryLink,
    dictionaryText:        (person) => person.fields.dictionaryText,
    events:                (person) => person.fields.events,
    verseCount:            (person) => person.fields.verseCount ?? person.fields.verses?.length ?? 0,
    verses:                (person) => person.fields.verses?.map(id => maps.verses.get(id)).filter(Boolean) || [],
    siblings:              (person) => person.fields.siblings?.map(id => maps.people.get(id)).filter(Boolean) || [],
    halfSiblingsSameMother:(person) => person.fields.halfSiblingsSameMother?.map(id => maps.people.get(id)).filter(Boolean) || [],
    halfSiblingsSameFather:(person) => person.fields.halfSiblingsSameFather?.map(id => maps.people.get(id)).filter(Boolean) || [],
    chaptersWritten:       (person) => person.fields.chaptersWritten?.map(id => maps.chapters.get(id)).filter(Boolean) || [],
    mother:                (person) => person.fields.mother?.map(id => maps.people.get(id)).filter(Boolean) || [],
    father:                (person) => person.fields.father?.map(id => maps.people.get(id)).filter(Boolean) || [],
    children:              (person) => person.fields.children?.map(id => maps.people.get(id)).filter(Boolean) || [],
    minYear:               (person) => person.fields.minYear,
    maxYear:               (person) => person.fields.maxYear,
    displayTitle:          (person) => person.fields.displayTitle,
    status:                (person) => person.fields.status,
    alphaGroup:            (person) => person.fields.alphaGroup,
    slug:                  (person) => person.fields.slug,
    partners:              (person) => person.fields.partners?.map(id => maps.people.get(id)).filter(Boolean) || [],
    alsoCalled:            (person) => person.fields.alsoCalled,
    ambiguous:             (person) => person.fields.ambiguous,
    eastons:               (person) => person.fields.eastons?.map(id => maps.easton.get(id)).filter(Boolean) || [],
    dictText:              (person) => person.fields.dictText ? [person.fields.dictText] : [],
    modified:              (person) => person.fields.modified,
    timeline:              (person) => person.fields.timeline?.map(id => maps.events.get(id)).filter(Boolean) || [],
  },

  PeopleGroup: {
    groupName: (group) => group.fields.groupName,
    members:   (group) => group.fields.members?.map(id => maps.people.get(id)).filter(Boolean) || [],
    verses:    (group) => group.fields.verses?.map(id => maps.verses.get(id)).filter(Boolean) || [],
    modified:  (group) => group.fields.modified,
    events:    (group) => group.fields.events,
    eventsDev: (group) => group.fields.events_dev?.map(id => maps.events.get(id)).filter(Boolean) || [],
    partOf:    (group) => group.fields.partOf?.map(id => maps.peopleGroups.get(id)).filter(Boolean) || [],
  },

  Place: {
    placeLookup:     (place) => place.fields.placeLookup,
    openBibleLat:    (place) => place.fields.openBibleLat,
    openBibleLong:   (place) => place.fields.openBibleLong,
    kjvName:         (place) => place.fields.kjvName,
    esvName:         (place) => place.fields.esvName,
    comment:         (place) => place.fields.comment,
    precision:       (place) => place.fields.precision,
    featureType:     (place) => place.fields.featureType,
    rootID:          (place) => place.fields.rootID || [],
    aliases:         (place) => place.fields.aliases,
    dictionaryLink:  (place) => place.fields.dictionaryLink,
    dictionaryText:  (place) => place.fields.dictionaryText,
    verseCount:      (place) => place.fields.verseCount ?? place.fields.verses?.length ?? 0,
    placeID:         (place) => place.fields.placeID,
    recogitoUri:     (place) => place.fields.recogitoUri,
    recogitoLat:     (place) => place.fields.recogitoLat,
    recogitoLon:     (place) => place.fields.recogitoLon,
    peopleBorn:      (place) => place.fields.peopleBorn?.map(id => maps.people.get(id)).filter(Boolean) || [],
    peopleDied:      (place) => place.fields.peopleDied?.map(id => maps.people.get(id)).filter(Boolean) || [],
    booksWritten:    (place) => place.fields.booksWritten?.map(id => maps.books.get(id)).filter(Boolean) || [],
    verses:          (place) => place.fields.verses?.map(id => maps.verses.get(id)).filter(Boolean) || [],
    recogitoStatus:  (place) => place.fields.recogitoStatus,
    recogitoType:    (place) => place.fields.recogitoType,
    recogitoComments:(place) => place.fields.recogitoComments,
    recogitoLabel:   (place) => place.fields.recogitoLabel,
    recogitoUID:     (place) => place.fields.recogitoUID,
    hasBeenHere:     (place) => place.fields.hasBeenHere,
    latitude:        (place) => place.fields.latitude,
    longitude:       (place) => place.fields.longitude,
    status:          (place) => place.fields.status,
    displayTitle:    (place) => place.fields.displayTitle,
    alphaGroup:      (place) => place.fields.alphaGroup,
    slug:            (place) => place.fields.slug,
    duplicateOf:     (place) => place.fields.duplicateOf?.map(id => maps.places.get(id)).filter(Boolean) || [],
    ambiguous:       (place) => place.fields.ambiguous,
    eastons:         (place) => place.fields.eastons?.map(id => maps.easton.get(id)).filter(Boolean) || [],
    dictText:        (place) => place.fields.dictText ? [place.fields.dictText] : [],
    modified:        (place) => place.fields.modified,
    eventsHere:      (place) => place.fields.eventsHere?.map(id => maps.events.get(id)).filter(Boolean) || [],
    featureSubType:  (place) => place.fields.featureSubType,
  },

  Event: {
    title:        (event) => event.fields.title,
    startDate:    (event) => event.fields.startDate,
    duration:     (event) => event.fields.duration,
    participants: (event) => event.fields.participants?.map(id => maps.people.get(id)).filter(Boolean) || [],
    locations:    (event) => event.fields.locations?.map(id => maps.places.get(id)).filter(Boolean) || [],
    verses:       (event) => event.fields.verses?.map(id => maps.verses.get(id)).filter(Boolean) || [],
    predecessor:  (event) => event.fields.predecessor?.map(id => maps.events.get(id)).filter(Boolean) || [],
    lag:          (event) => event.fields.lag,
    partOf:       (event) => event.fields.partOf?.map(id => maps.events.get(id)).filter(Boolean) || [],
    notes:        (event) => event.fields.notes,
    verseSort:    (event) => event.fields.verseSort,
    groups:       (event) => event.fields.groups?.map(id => maps.peopleGroups.get(id)).filter(Boolean) || [],
    modified:     (event) => event.fields.modified,
    sortKey:      (event) => event.fields.sortKey,
    rangeFlag:    (event) => event.fields.rangeFlag,
    lagType:      (event) => event.fields.lagType,
    eventID:      (event) => event.fields.eventID,
  },

  Easton: {
    dictLookup:   (easton) => easton.fields.dictLookup,
    termID:       (easton) => easton.fields.termID,
    termLabel:    (easton) => easton.fields.termLabel,
    defId:        (easton) => easton.fields.def_id,
    hasList:      (easton) => easton.fields.has_list,
    itemNum:      (easton) => easton.fields.itemNum,
    matchType:    (easton) => easton.fields.matchType,
    matchSlugs:   (easton) => easton.fields.matchSlugs,
    dictText:     (easton) => easton.fields.dictText,
    personLookup: (easton) => easton.fields.personLookup?.map(id => maps.people.get(id)).filter(Boolean) || [],
    placeLookup:  (easton) => easton.fields.placeLookup?.map(id => maps.places.get(id)).filter(Boolean) || [],
    index:        (easton) => easton.fields.index,
  },
};

// ── Apollo server ─────────────────────────────────────────────────────────────

let apolloServer;

const getApolloServer = async () => {
  if (!apolloServer) {
    apolloServer = new ApolloServer({
      typeDefs,
      resolvers,
      plugins: [ApolloServerPluginLandingPageLocalDefault()],
    });
    await apolloServer.start();
  }
  return apolloServer;
};

exports.handler = async (event, context) => {
  try {
    const server = await getApolloServer();

    // Decode body: Netlify may base64-encode it; Apollo 4 needs a parsed object
    let body = event.body;
    if (event.isBase64Encoded && body) {
      body = Buffer.from(body, 'base64').toString('utf8');
    }
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (_) { /* leave as string, Apollo will error */ }
    }

    const response = await server.executeHTTPGraphQLRequest({
      httpGraphQLRequest: {
        method: event.httpMethod,
        headers: {
          get: (name) => event.headers[name.toLowerCase()] || event.headers[name],
        },
        body,
        search: event.queryStringParameters ? new URLSearchParams(event.queryStringParameters) : undefined,
      },
      context: async () => ({}),
    });
    return {
      statusCode: response.status || 200,
      headers: Object.fromEntries(response.headers.entries()),
      body: response.body.kind === 'complete' ? response.body.string : JSON.stringify(response.body),
    };
  } catch (err) {
    console.error('[graphql] handler error:', err);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ errors: [{ message: err.message }] }),
    };
  }
};
