//! Data model types matching the Theographic JSON schema.
//! Each entity mirrors the Airtable-derived JSON structure:
//!   { "id": "recXXX", "createdTime": "...", "fields": { ... } }

use serde::Deserialize;
use std::collections::HashMap;

// ---------------------------------------------------------------------------
// Generic Airtable record wrapper
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct Record<T> {
    pub id: String,
    #[serde(rename = "createdTime")]
    pub created_time: Option<String>,
    pub fields: T,
}

// ---------------------------------------------------------------------------
// Books
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct BookFields {
    #[serde(rename = "osisName", default)]
    pub osis_name: Option<String>,
    #[serde(rename = "bookName", default)]
    pub book_name: Option<String>,
    #[serde(rename = "shortName", default)]
    pub short_name: Option<String>,
    #[serde(rename = "bookOrder", default)]
    pub book_order: Option<i32>,
    #[serde(rename = "bookDiv", default)]
    pub book_div: Option<String>,
    #[serde(rename = "chapterCount", default)]
    pub chapter_count: Option<i32>,
    #[serde(rename = "verseCount", default)]
    pub verse_count: Option<i32>,
    #[serde(default)]
    pub testament: Option<String>,
    #[serde(default)]
    pub slug: Option<String>,
    #[serde(default)]
    pub chapters: Option<Vec<String>>,
    #[serde(default)]
    pub verses: Option<Vec<String>>,
    #[serde(default)]
    pub writers: Option<Vec<String>>,
}

// ---------------------------------------------------------------------------
// Chapters
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct ChapterFields {
    #[serde(rename = "osisRef", default)]
    pub osis_ref: Option<String>,
    #[serde(rename = "chapterNum", default)]
    pub chapter_num: Option<i32>,
    #[serde(default)]
    pub slug: Option<String>,
    #[serde(default)]
    pub book: Option<Vec<String>>,
    #[serde(default)]
    pub verses: Option<Vec<String>>,
    #[serde(default)]
    pub writer: Option<Vec<String>>,
    #[serde(rename = "peopleCount", default)]
    pub people_count: Option<i32>,
    #[serde(rename = "placesCount", default)]
    pub places_count: Option<i32>,
}

// ---------------------------------------------------------------------------
// Verses
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct VerseFields {
    #[serde(rename = "osisRef", default)]
    pub osis_ref: Option<String>,
    #[serde(rename = "verseNum", default)]
    pub verse_num: Option<String>,
    #[serde(rename = "verseText", default)]
    pub verse_text: Option<String>,
    #[serde(rename = "verseID", default)]
    pub verse_id: Option<String>,
    #[serde(rename = "yearNum", default)]
    pub year_num: Option<f64>,
    #[serde(default)]
    pub book: Option<Vec<String>>,
    #[serde(default)]
    pub chapter: Option<Vec<String>>,
    #[serde(default)]
    pub people: Option<Vec<String>>,
    #[serde(default)]
    pub places: Option<Vec<String>>,
    #[serde(rename = "peopleGroups", default)]
    pub people_groups: Option<Vec<String>>,
    #[serde(default)]
    pub event: Option<Vec<String>>,
    #[serde(rename = "peopleCount", default)]
    pub people_count: Option<i32>,
    #[serde(rename = "placesCount", default)]
    pub places_count: Option<i32>,
}

// ---------------------------------------------------------------------------
// People
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct PersonFields {
    #[serde(rename = "personLookup", default)]
    pub person_lookup: Option<String>,
    #[serde(rename = "personID", default)]
    pub person_id: Option<i32>,
    #[serde(default)]
    pub name: Option<String>,
    #[serde(default)]
    pub surname: Option<String>,
    #[serde(rename = "displayTitle", default)]
    pub display_title: Option<String>,
    #[serde(default)]
    pub slug: Option<String>,
    #[serde(default)]
    pub gender: Option<String>,
    #[serde(rename = "birthYear", default)]
    pub birth_year: Option<String>,
    #[serde(rename = "deathYear", default)]
    pub death_year: Option<String>,
    #[serde(rename = "isProperName", default)]
    pub is_proper_name: Option<bool>,
    #[serde(default)]
    pub status: Option<String>,
    #[serde(rename = "alphaGroup", default)]
    pub alpha_group: Option<String>,
    #[serde(rename = "alsoCalled", default)]
    pub also_called: Option<String>,
    #[serde(rename = "dictionaryText", default)]
    pub dictionary_text: Option<String>,
    #[serde(rename = "dictionaryLink", default)]
    pub dictionary_link: Option<String>,
    #[serde(rename = "verseCount", default)]
    pub verse_count: Option<i32>,
    // Relationships (Airtable record IDs)
    #[serde(default)]
    pub father: Option<Vec<String>>,
    #[serde(default)]
    pub mother: Option<Vec<String>>,
    #[serde(default)]
    pub siblings: Option<Vec<String>>,
    #[serde(rename = "halfSiblingsSameMother", default)]
    pub half_siblings_same_mother: Option<Vec<String>>,
    #[serde(rename = "halfSiblingsSameFather", default)]
    pub half_siblings_same_father: Option<Vec<String>>,
    #[serde(default)]
    pub children: Option<Vec<String>>,
    #[serde(default)]
    pub partners: Option<Vec<String>>,
    #[serde(rename = "memberOf", default)]
    pub member_of: Option<Vec<String>>,
    #[serde(rename = "birthPlace", default)]
    pub birth_place: Option<Vec<String>>,
    #[serde(rename = "deathPlace", default)]
    pub death_place: Option<Vec<String>>,
    #[serde(default)]
    pub verses: Option<Vec<String>>,
    #[serde(default)]
    pub eastons: Option<Vec<String>>,
}

// ---------------------------------------------------------------------------
// Places
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct PlaceFields {
    #[serde(rename = "placeLookup", default)]
    pub place_lookup: Option<String>,
    #[serde(rename = "placeID", default)]
    pub place_id: Option<i32>,
    #[serde(rename = "displayTitle", default)]
    pub display_title: Option<String>,
    #[serde(default)]
    pub slug: Option<String>,
    #[serde(rename = "kjvName", default)]
    pub kjv_name: Option<String>,
    #[serde(rename = "esvName", default)]
    pub esv_name: Option<String>,
    #[serde(rename = "alphaGroup", default)]
    pub alpha_group: Option<String>,
    #[serde(rename = "featureType", default)]
    pub feature_type: Option<String>,
    #[serde(rename = "featureSubType", default)]
    pub feature_sub_type: Option<String>,
    #[serde(default)]
    pub latitude: Option<String>,
    #[serde(default)]
    pub longitude: Option<String>,
    #[serde(rename = "openBibleLat", default)]
    pub open_bible_lat: Option<String>,
    #[serde(rename = "openBibleLong", default)]
    pub open_bible_long: Option<String>,
    #[serde(rename = "recogitoLat", default)]
    pub recogito_lat: Option<String>,
    #[serde(rename = "recogitoLon", default)]
    pub recogito_lon: Option<String>,
    #[serde(rename = "recogitoUri", default)]
    pub recogito_uri: Option<String>,
    #[serde(rename = "recogitoStatus", default)]
    pub recogito_status: Option<String>,
    #[serde(rename = "verseCount", default)]
    pub verse_count: Option<i32>,
    #[serde(default)]
    pub comment: Option<String>,
    #[serde(default)]
    pub status: Option<String>,
    // Relationships
    #[serde(default)]
    pub verses: Option<Vec<String>>,
    #[serde(rename = "rootID", default)]
    pub root_id: Option<Vec<String>>,
    #[serde(default)]
    pub eastons: Option<Vec<String>>,
    #[serde(rename = "peopleBorn", default)]
    pub people_born: Option<Vec<String>>,
    #[serde(rename = "peopleDied", default)]
    pub people_died: Option<Vec<String>>,
}

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct EventFields {
    #[serde(default)]
    pub title: Option<String>,
    #[serde(rename = "startDate", default)]
    pub start_date: Option<String>,
    #[serde(default)]
    pub duration: Option<String>,
    #[serde(rename = "sortKey", default)]
    pub sort_key: Option<f64>,
    #[serde(rename = "verseSort", default)]
    pub verse_sort: Option<String>,
    #[serde(rename = "eventID", default)]
    pub event_id: Option<i32>,
    #[serde(default)]
    pub notes: Option<String>,
    // Relationships
    #[serde(default)]
    pub participants: Option<Vec<String>>,
    #[serde(default)]
    pub locations: Option<Vec<String>>,
    #[serde(default)]
    pub verses: Option<Vec<String>>,
    #[serde(default)]
    pub predecessor: Option<Vec<String>>,
    #[serde(rename = "partOf", default)]
    pub part_of: Option<Vec<String>>,
    #[serde(default)]
    pub lag: Option<String>,
    #[serde(rename = "lagType", default)]
    pub lag_type: Option<String>,
}

// ---------------------------------------------------------------------------
// People Groups
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct PeopleGroupFields {
    #[serde(rename = "groupName", default)]
    pub group_name: Option<String>,
    #[serde(default)]
    pub members: Option<Vec<String>>,
    #[serde(rename = "partOf", default)]
    pub part_of: Option<Vec<String>>,
    #[serde(default)]
    pub verses: Option<Vec<String>>,
    #[serde(default)]
    pub events: Option<Vec<String>>,
}

// ---------------------------------------------------------------------------
// Easton's Dictionary
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct EastonFields {
    #[serde(rename = "dictLookup", default)]
    pub dict_lookup: Option<String>,
    #[serde(rename = "termID", default)]
    pub term_id: Option<String>,
    #[serde(rename = "termLabel", default)]
    pub term_label: Option<String>,
    #[serde(rename = "def_id", default)]
    pub def_id: Option<String>,
    #[serde(rename = "dictText", default)]
    pub dict_text: Option<String>,
    #[serde(rename = "has_list", default)]
    pub has_list: Option<String>,
    #[serde(rename = "itemNum", default)]
    pub item_num: Option<i32>,
    #[serde(rename = "matchType", default)]
    pub match_type: Option<String>,
    #[serde(rename = "matchSlugs", default)]
    pub match_slugs: Option<String>,
    #[serde(default)]
    pub index: Option<i32>,
    #[serde(rename = "personLookup", default)]
    pub person_lookup: Option<Vec<String>>,
    #[serde(rename = "placeLookup", default)]
    pub place_lookup: Option<Vec<String>>,
}

// ---------------------------------------------------------------------------
// Convenience type aliases
// ---------------------------------------------------------------------------

pub type BookRecord = Record<BookFields>;
pub type ChapterRecord = Record<ChapterFields>;
pub type VerseRecord = Record<VerseFields>;
pub type PersonRecord = Record<PersonFields>;
pub type PlaceRecord = Record<PlaceFields>;
pub type EventRecord = Record<EventFields>;
pub type PeopleGroupRecord = Record<PeopleGroupFields>;
pub type EastonRecord = Record<EastonFields>;

// ---------------------------------------------------------------------------
// Lightweight node stored in the graph (not the full record)
// ---------------------------------------------------------------------------

#[derive(Debug, Clone)]
pub enum NodeData {
    Book {
        rec_id: String,
        name: String,
        osis: String,
        order: i32,
        testament: String,
        division: String,
    },
    Chapter {
        rec_id: String,
        osis_ref: String,
        chapter_num: i32,
    },
    Verse {
        rec_id: String,
        osis_ref: String,
        text: String,
        verse_id: String,
        year: Option<f64>,
    },
    Person {
        rec_id: String,
        name: String,
        lookup: String,
        gender: String,
        birth_year: Option<String>,
        death_year: Option<String>,
    },
    Place {
        rec_id: String,
        name: String,
        lookup: String,
        lat: Option<f64>,
        lng: Option<f64>,
        feature_type: String,
    },
    Event {
        rec_id: String,
        title: String,
        start_date: Option<String>,
        sort_key: Option<f64>,
    },
    PeopleGroup {
        rec_id: String,
        name: String,
    },
    Easton {
        rec_id: String,
        term: String,
        text: String,
    },
}

impl NodeData {
    pub fn rec_id(&self) -> &str {
        match self {
            NodeData::Book { rec_id, .. }
            | NodeData::Chapter { rec_id, .. }
            | NodeData::Verse { rec_id, .. }
            | NodeData::Person { rec_id, .. }
            | NodeData::Place { rec_id, .. }
            | NodeData::Event { rec_id, .. }
            | NodeData::PeopleGroup { rec_id, .. }
            | NodeData::Easton { rec_id, .. } => rec_id,
        }
    }

    pub fn label(&self) -> &str {
        match self {
            NodeData::Book { name, .. } => name,
            NodeData::Chapter { osis_ref, .. } => osis_ref,
            NodeData::Verse { osis_ref, .. } => osis_ref,
            NodeData::Person { name, .. } => name,
            NodeData::Place { name, .. } => name,
            NodeData::Event { title, .. } => title,
            NodeData::PeopleGroup { name, .. } => name,
            NodeData::Easton { term, .. } => term,
        }
    }

    pub fn node_type(&self) -> &'static str {
        match self {
            NodeData::Book { .. } => "Book",
            NodeData::Chapter { .. } => "Chapter",
            NodeData::Verse { .. } => "Verse",
            NodeData::Person { .. } => "Person",
            NodeData::Place { .. } => "Place",
            NodeData::Event { .. } => "Event",
            NodeData::PeopleGroup { .. } => "PeopleGroup",
            NodeData::Easton { .. } => "Easton",
        }
    }
}

// ---------------------------------------------------------------------------
// Edge types
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum EdgeType {
    // Scripture structure
    BookHasChapter,
    ChapterHasVerse,
    BookHasVerse,
    // Entity ↔ Verse
    PersonMentionedIn,
    PlaceMentionedIn,
    EventDescribedIn,
    GroupMentionedIn,
    // People relationships
    FatherOf,
    MotherOf,
    SiblingOf,
    HalfSiblingSameMother,
    HalfSiblingSameFather,
    PartnerOf,
    ChildOf,
    MemberOfGroup,
    // Place relationships
    BornIn,
    DiedIn,
    PlacePartOf,
    // Event relationships
    ParticipatedIn,
    EventAtLocation,
    EventPredecessor,
    EventPartOf,
    // Dictionary
    DictionaryEntry,
    // Book authorship
    WriterOf,
}

impl EdgeType {
    pub fn as_str(&self) -> &'static str {
        match self {
            EdgeType::BookHasChapter => "BOOK_HAS_CHAPTER",
            EdgeType::ChapterHasVerse => "CHAPTER_HAS_VERSE",
            EdgeType::BookHasVerse => "BOOK_HAS_VERSE",
            EdgeType::PersonMentionedIn => "MENTIONED_IN",
            EdgeType::PlaceMentionedIn => "MENTIONED_IN",
            EdgeType::EventDescribedIn => "DESCRIBED_IN",
            EdgeType::GroupMentionedIn => "MENTIONED_IN",
            EdgeType::FatherOf => "FATHER_OF",
            EdgeType::MotherOf => "MOTHER_OF",
            EdgeType::SiblingOf => "SIBLING_OF",
            EdgeType::HalfSiblingSameMother => "HALF_SIBLING_SAME_MOTHER",
            EdgeType::HalfSiblingSameFather => "HALF_SIBLING_SAME_FATHER",
            EdgeType::PartnerOf => "PARTNER_OF",
            EdgeType::ChildOf => "CHILD_OF",
            EdgeType::MemberOfGroup => "MEMBER_OF",
            EdgeType::BornIn => "BORN_IN",
            EdgeType::DiedIn => "DIED_IN",
            EdgeType::PlacePartOf => "PART_OF",
            EdgeType::ParticipatedIn => "PARTICIPATED_IN",
            EdgeType::EventAtLocation => "LOCATED_AT",
            EdgeType::EventPredecessor => "PRECEDED_BY",
            EdgeType::EventPartOf => "PART_OF",
            EdgeType::DictionaryEntry => "HAS_ENTRY",
            EdgeType::WriterOf => "WRITER_OF",
        }
    }
}

/// Lookup index: maps Airtable record IDs → petgraph NodeIndex
pub type RecordIndex = HashMap<String, petgraph::graph::NodeIndex>;
