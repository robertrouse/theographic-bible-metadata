//! Graph construction: loads JSON data and builds a petgraph graph.

use crate::model::*;
use petgraph::graph::{DiGraph, NodeIndex};
use std::collections::HashMap;

pub type BibleGraph = DiGraph<NodeData, EdgeType>;

/// Build the full graph from raw JSON strings.
/// Each parameter is the contents of the corresponding JSON file.
pub fn build_graph(
    books_json: &str,
    chapters_json: &str,
    verses_json: &str,
    people_json: &str,
    places_json: &str,
    events_json: &str,
    groups_json: &str,
    easton_json: &str,
) -> (BibleGraph, RecordIndex) {
    // Pre-allocate for ~43K nodes, ~200K edges
    let mut g = BibleGraph::with_capacity(44_000, 220_000);
    let mut idx: RecordIndex = HashMap::with_capacity(44_000);

    // ── Phase 1: Create all nodes ──────────────────────────────────────

    load_books(&mut g, &mut idx, books_json);
    load_chapters(&mut g, &mut idx, chapters_json);
    load_verses(&mut g, &mut idx, verses_json);
    load_people(&mut g, &mut idx, people_json);
    load_places(&mut g, &mut idx, places_json);
    load_events(&mut g, &mut idx, events_json);
    load_groups(&mut g, &mut idx, groups_json);
    load_easton(&mut g, &mut idx, easton_json);

    // ── Phase 2: Create all edges (needs all nodes present) ────────────

    link_books(&mut g, &idx, books_json);
    link_chapters(&mut g, &idx, chapters_json);
    link_verses(&mut g, &idx, verses_json);
    link_people(&mut g, &idx, people_json);
    link_places(&mut g, &idx, places_json);
    link_events(&mut g, &idx, events_json);
    link_groups(&mut g, &idx, groups_json);
    link_easton(&mut g, &idx, easton_json);

    (g, idx)
}

// ═══════════════════════════════════════════════════════════════════════════
// Node creation helpers
// ═══════════════════════════════════════════════════════════════════════════

fn load_books(g: &mut BibleGraph, idx: &mut RecordIndex, json: &str) {
    let records: Vec<BookRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        let node = NodeData::Book {
            rec_id: r.id.clone(),
            name: f.book_name.clone().unwrap_or_default(),
            osis: f.osis_name.clone().unwrap_or_default(),
            order: f.book_order.unwrap_or(0),
            testament: f.testament.clone().unwrap_or_default(),
            division: f.book_div.clone().unwrap_or_default(),
        };
        let ni = g.add_node(node);
        idx.insert(r.id, ni);
    }
}

fn load_chapters(g: &mut BibleGraph, idx: &mut RecordIndex, json: &str) {
    let records: Vec<ChapterRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        let node = NodeData::Chapter {
            rec_id: r.id.clone(),
            osis_ref: f.osis_ref.clone().unwrap_or_default(),
            chapter_num: f.chapter_num.unwrap_or(0),
        };
        let ni = g.add_node(node);
        idx.insert(r.id, ni);
    }
}

fn load_verses(g: &mut BibleGraph, idx: &mut RecordIndex, json: &str) {
    let records: Vec<VerseRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        let node = NodeData::Verse {
            rec_id: r.id.clone(),
            osis_ref: f.osis_ref.clone().unwrap_or_default(),
            text: f.verse_text.clone().unwrap_or_default(),
            verse_id: f.verse_id.clone().unwrap_or_default(),
            year: f.year_num,
        };
        let ni = g.add_node(node);
        idx.insert(r.id, ni);
    }
}

fn load_people(g: &mut BibleGraph, idx: &mut RecordIndex, json: &str) {
    let records: Vec<PersonRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        let node = NodeData::Person {
            rec_id: r.id.clone(),
            name: f.name.clone().unwrap_or_default(),
            lookup: f.person_lookup.clone().unwrap_or_default(),
            gender: f.gender.clone().unwrap_or_default(),
            birth_year: f.birth_year.clone(),
            death_year: f.death_year.clone(),
        };
        let ni = g.add_node(node);
        idx.insert(r.id, ni);
    }
}

fn load_places(g: &mut BibleGraph, idx: &mut RecordIndex, json: &str) {
    let records: Vec<PlaceRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        let lat = f
            .latitude
            .as_deref()
            .and_then(|s| s.parse::<f64>().ok());
        let lng = f
            .longitude
            .as_deref()
            .and_then(|s| s.parse::<f64>().ok());
        let node = NodeData::Place {
            rec_id: r.id.clone(),
            name: f.display_title.clone().unwrap_or_default(),
            lookup: f.place_lookup.clone().unwrap_or_default(),
            lat,
            lng,
            feature_type: f.feature_type.clone().unwrap_or_default(),
        };
        let ni = g.add_node(node);
        idx.insert(r.id, ni);
    }
}

fn load_events(g: &mut BibleGraph, idx: &mut RecordIndex, json: &str) {
    let records: Vec<EventRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        let node = NodeData::Event {
            rec_id: r.id.clone(),
            title: f.title.clone().unwrap_or_default(),
            start_date: f.start_date.clone(),
            sort_key: f.sort_key,
        };
        let ni = g.add_node(node);
        idx.insert(r.id, ni);
    }
}

fn load_groups(g: &mut BibleGraph, idx: &mut RecordIndex, json: &str) {
    let records: Vec<PeopleGroupRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        let node = NodeData::PeopleGroup {
            rec_id: r.id.clone(),
            name: f.group_name.clone().unwrap_or_default(),
        };
        let ni = g.add_node(node);
        idx.insert(r.id, ni);
    }
}

fn load_easton(g: &mut BibleGraph, idx: &mut RecordIndex, json: &str) {
    let records: Vec<EastonRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        let node = NodeData::Easton {
            rec_id: r.id.clone(),
            term: f.term_label.clone().unwrap_or_default(),
            text: f.dict_text.clone().unwrap_or_default(),
        };
        let ni = g.add_node(node);
        idx.insert(r.id, ni);
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Edge creation helpers
// ═══════════════════════════════════════════════════════════════════════════

/// Helper: add edge if both endpoints exist in the index
fn link(
    g: &mut BibleGraph,
    idx: &RecordIndex,
    from: &str,
    to: &str,
    edge: EdgeType,
) {
    if let (Some(&a), Some(&b)) = (idx.get(from), idx.get(to)) {
        g.add_edge(a, b, edge);
    }
}

fn link_books(_g: &mut BibleGraph, _idx: &RecordIndex, _json: &str) {
    // Book→Chapter and Book→Verse edges are created from the chapter/verse side
    // to avoid double-parsing. No-op here.
}

fn link_chapters(g: &mut BibleGraph, idx: &RecordIndex, json: &str) {
    let records: Vec<ChapterRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        // Book → Chapter
        for book_id in f.book.as_deref().unwrap_or_default() {
            link(g, idx, book_id, &r.id, EdgeType::BookHasChapter);
        }
        // Writer → Chapter
        for writer_id in f.writer.as_deref().unwrap_or_default() {
            link(g, idx, writer_id, &r.id, EdgeType::WriterOf);
        }
    }
}

fn link_verses(g: &mut BibleGraph, idx: &RecordIndex, json: &str) {
    let records: Vec<VerseRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        // Chapter → Verse
        for ch_id in f.chapter.as_deref().unwrap_or_default() {
            link(g, idx, ch_id, &r.id, EdgeType::ChapterHasVerse);
        }
        // Book → Verse
        for book_id in f.book.as_deref().unwrap_or_default() {
            link(g, idx, book_id, &r.id, EdgeType::BookHasVerse);
        }
        // Person → Verse
        for pid in f.people.as_deref().unwrap_or_default() {
            link(g, idx, pid, &r.id, EdgeType::PersonMentionedIn);
        }
        // Place → Verse
        for pid in f.places.as_deref().unwrap_or_default() {
            link(g, idx, pid, &r.id, EdgeType::PlaceMentionedIn);
        }
        // Event → Verse
        for eid in f.event.as_deref().unwrap_or_default() {
            link(g, idx, eid, &r.id, EdgeType::EventDescribedIn);
        }
        // PeopleGroup → Verse
        for gid in f.people_groups.as_deref().unwrap_or_default() {
            link(g, idx, gid, &r.id, EdgeType::GroupMentionedIn);
        }
    }
}

fn link_people(g: &mut BibleGraph, idx: &RecordIndex, json: &str) {
    let records: Vec<PersonRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        // Father → Person
        for fid in f.father.as_deref().unwrap_or_default() {
            link(g, idx, fid, &r.id, EdgeType::FatherOf);
        }
        // Mother → Person
        for mid in f.mother.as_deref().unwrap_or_default() {
            link(g, idx, mid, &r.id, EdgeType::MotherOf);
        }
        // Siblings (bidirectional — we store one direction; queries handle both)
        for sid in f.siblings.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, sid, EdgeType::SiblingOf);
        }
        // Half-siblings
        for sid in f.half_siblings_same_mother.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, sid, EdgeType::HalfSiblingSameMother);
        }
        for sid in f.half_siblings_same_father.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, sid, EdgeType::HalfSiblingSameFather);
        }
        // Partners
        for pid in f.partners.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, pid, EdgeType::PartnerOf);
        }
        // Children (Person → Child)
        for cid in f.children.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, cid, EdgeType::ChildOf);
        }
        // Member of group
        for gid in f.member_of.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, gid, EdgeType::MemberOfGroup);
        }
        // Birth/death places
        for pid in f.birth_place.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, pid, EdgeType::BornIn);
        }
        for pid in f.death_place.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, pid, EdgeType::DiedIn);
        }
        // Dictionary entries
        for eid in f.eastons.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, eid, EdgeType::DictionaryEntry);
        }
    }
}

fn link_places(g: &mut BibleGraph, idx: &RecordIndex, json: &str) {
    let records: Vec<PlaceRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        // Place hierarchy (rootID = parent)
        for rid in f.root_id.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, rid, EdgeType::PlacePartOf);
        }
        // Dictionary entries
        for eid in f.eastons.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, eid, EdgeType::DictionaryEntry);
        }
    }
}

fn link_events(g: &mut BibleGraph, idx: &RecordIndex, json: &str) {
    let records: Vec<EventRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        // Participants
        for pid in f.participants.as_deref().unwrap_or_default() {
            link(g, idx, pid, &r.id, EdgeType::ParticipatedIn);
        }
        // Locations
        for lid in f.locations.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, lid, EdgeType::EventAtLocation);
        }
        // Predecessor chain
        for pid in f.predecessor.as_deref().unwrap_or_default() {
            link(g, idx, pid, &r.id, EdgeType::EventPredecessor);
        }
        // Part-of hierarchy
        for pid in f.part_of.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, pid, EdgeType::EventPartOf);
        }
    }
}

fn link_groups(g: &mut BibleGraph, idx: &RecordIndex, json: &str) {
    let records: Vec<PeopleGroupRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        // Group hierarchy
        for pid in f.part_of.as_deref().unwrap_or_default() {
            link(g, idx, &r.id, pid, EdgeType::EventPartOf);
        }
    }
}

fn link_easton(g: &mut BibleGraph, idx: &RecordIndex, json: &str) {
    let records: Vec<EastonRecord> = serde_json::from_str(json).unwrap_or_default();
    for r in records {
        let f = &r.fields;
        // Person links
        for pid in f.person_lookup.as_deref().unwrap_or_default() {
            link(g, idx, pid, &r.id, EdgeType::DictionaryEntry);
        }
        // Place links
        for pid in f.place_lookup.as_deref().unwrap_or_default() {
            link(g, idx, pid, &r.id, EdgeType::DictionaryEntry);
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Graph statistics
// ═══════════════════════════════════════════════════════════════════════════

pub struct GraphStats {
    pub node_count: usize,
    pub edge_count: usize,
    pub books: usize,
    pub chapters: usize,
    pub verses: usize,
    pub people: usize,
    pub places: usize,
    pub events: usize,
    pub groups: usize,
    pub easton: usize,
}

pub fn stats(g: &BibleGraph) -> GraphStats {
    let mut s = GraphStats {
        node_count: g.node_count(),
        edge_count: g.edge_count(),
        books: 0,
        chapters: 0,
        verses: 0,
        people: 0,
        places: 0,
        events: 0,
        groups: 0,
        easton: 0,
    };
    for nd in g.node_weights() {
        match nd {
            NodeData::Book { .. } => s.books += 1,
            NodeData::Chapter { .. } => s.chapters += 1,
            NodeData::Verse { .. } => s.verses += 1,
            NodeData::Person { .. } => s.people += 1,
            NodeData::Place { .. } => s.places += 1,
            NodeData::Event { .. } => s.events += 1,
            NodeData::PeopleGroup { .. } => s.groups += 1,
            NodeData::Easton { .. } => s.easton += 1,
        }
    }
    s
}
