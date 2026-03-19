//! Theographic Graph — Rust+WASM in-browser graph engine for Bible metadata.
//!
//! This crate loads the Theographic JSON data into a petgraph directed graph
//! and exposes query functions via wasm-bindgen for use in JavaScript/TypeScript.

mod graph;
mod model;
mod query;

use graph::BibleGraph;
use model::RecordIndex;
use wasm_bindgen::prelude::*;

/// The main graph engine, holding the constructed graph and lookup index.
/// Instantiated once via `TheographicGraph::new()` and then queried.
#[wasm_bindgen]
pub struct TheographicGraph {
    g: BibleGraph,
    idx: RecordIndex,
}

#[wasm_bindgen]
impl TheographicGraph {
    /// Build the graph from the 8 JSON file contents.
    /// Call this once at startup, passing each file's text.
    #[wasm_bindgen(constructor)]
    pub fn new(
        books_json: &str,
        chapters_json: &str,
        verses_json: &str,
        people_json: &str,
        places_json: &str,
        events_json: &str,
        groups_json: &str,
        easton_json: &str,
    ) -> TheographicGraph {
        // Set panic hook for better WASM error messages
        #[cfg(feature = "console_error_panic_hook")]
        console_error_panic_hook::set_once();

        let (g, idx) = graph::build_graph(
            books_json,
            chapters_json,
            verses_json,
            people_json,
            places_json,
            events_json,
            groups_json,
            easton_json,
        );
        TheographicGraph { g, idx }
    }

    /// Return graph statistics as JSON.
    pub fn stats(&self) -> String {
        let s = graph::stats(&self.g);
        serde_json::json!({
            "nodeCount": s.node_count,
            "edgeCount": s.edge_count,
            "books": s.books,
            "chapters": s.chapters,
            "verses": s.verses,
            "people": s.people,
            "places": s.places,
            "events": s.events,
            "groups": s.groups,
            "easton": s.easton,
        })
        .to_string()
    }

    /// Find a node by its Airtable record ID. Returns JSON or null.
    pub fn find_by_id(&self, id: &str) -> Option<String> {
        query::find_by_id(&self.g, &self.idx, id)
            .map(|r| serde_json::to_string(&r).unwrap_or_default())
    }

    /// Search nodes by label substring (case-insensitive). Returns JSON array.
    pub fn search(&self, query: &str, limit: usize) -> String {
        let results = query::search(&self.g, query, limit);
        serde_json::to_string(&results).unwrap_or_else(|_| "[]".to_string())
    }

    /// Search nodes filtered by type. Returns JSON array.
    /// `node_type`: "Book", "Chapter", "Verse", "Person", "Place", "Event", "PeopleGroup", "Easton"
    pub fn search_by_type(&self, node_type: &str, query: &str, limit: usize) -> String {
        let q = if query.is_empty() { None } else { Some(query) };
        let results = query::search_by_type(&self.g, node_type, q, limit);
        serde_json::to_string(&results).unwrap_or_else(|_| "[]".to_string())
    }

    /// Get immediate neighbors of a node. Returns JSON subgraph {nodes, edges}.
    /// `edge_filter`: optional edge type string (e.g., "FATHER_OF")
    /// `direction`: "incoming", "outgoing", or "" for both
    pub fn neighbors(&self, id: &str, edge_filter: &str, direction: &str) -> String {
        let ef = if edge_filter.is_empty() {
            None
        } else {
            Some(edge_filter)
        };
        let dir = if direction.is_empty() {
            None
        } else {
            Some(direction)
        };
        let result = query::neighbors(&self.g, &self.idx, id, ef, dir);
        serde_json::to_string(&result).unwrap_or_else(|_| r#"{"nodes":[],"edges":[]}"#.to_string())
    }

    /// Extract an ego graph (BFS neighborhood) around a node.
    /// Returns JSON subgraph {nodes, edges}.
    pub fn ego_graph(
        &self,
        id: &str,
        max_depth: usize,
        node_type_filter: &str,
        max_nodes: usize,
    ) -> String {
        let filter = if node_type_filter.is_empty() {
            None
        } else {
            Some(node_type_filter)
        };
        let result = query::ego_graph(&self.g, &self.idx, id, max_depth, filter, max_nodes);
        serde_json::to_string(&result).unwrap_or_else(|_| r#"{"nodes":[],"edges":[]}"#.to_string())
    }

    /// Find shortest path between two nodes. Returns JSON {nodes, length} or null.
    pub fn shortest_path(&self, from_id: &str, to_id: &str) -> Option<String> {
        query::shortest_path(&self.g, &self.idx, from_id, to_id)
            .map(|r| serde_json::to_string(&r).unwrap_or_default())
    }

    /// Get family tree for a person. Returns JSON or null.
    pub fn family_tree(&self, person_id: &str) -> Option<String> {
        query::family_tree(&self.g, &self.idx, person_id)
            .map(|r| serde_json::to_string(&r).unwrap_or_default())
    }

    /// Get ancestor generations for a person. Returns JSON array of arrays.
    pub fn ancestors(&self, person_id: &str, max_generations: usize) -> String {
        let result = query::ancestors(&self.g, &self.idx, person_id, max_generations);
        serde_json::to_string(&result).unwrap_or_else(|_| "[]".to_string())
    }

    /// Get descendant generations for a person. Returns JSON array of arrays.
    pub fn descendants(&self, person_id: &str, max_generations: usize) -> String {
        let result = query::descendants(&self.g, &self.idx, person_id, max_generations);
        serde_json::to_string(&result).unwrap_or_else(|_| "[]".to_string())
    }

    /// Get events in chronological order, optionally filtered by year range.
    /// Pass NaN for no filter on that bound.
    pub fn events_timeline(&self, start_year: f64, end_year: f64) -> String {
        let sy = if start_year.is_nan() {
            None
        } else {
            Some(start_year)
        };
        let ey = if end_year.is_nan() {
            None
        } else {
            Some(end_year)
        };
        let results = query::events_timeline(&self.g, sy, ey);
        serde_json::to_string(&results).unwrap_or_else(|_| "[]".to_string())
    }

    /// Get all places that have GPS coordinates. Returns JSON array.
    pub fn places_with_coords(&self) -> String {
        let results = query::places_with_coords(&self.g);
        serde_json::to_string(&results).unwrap_or_else(|_| "[]".to_string())
    }

    /// Get verses that mention a specific entity. Returns JSON array.
    pub fn verses_for_entity(&self, entity_id: &str, limit: usize) -> String {
        let results = query::verses_for_entity(&self.g, &self.idx, entity_id, limit);
        serde_json::to_string(&results).unwrap_or_else(|_| "[]".to_string())
    }

    /// Find entities that co-occur with the given entity in verses.
    /// Returns JSON array of {node, count} pairs, sorted by frequency.
    pub fn co_occurrences(&self, entity_id: &str, target_type: &str, limit: usize) -> String {
        let results = query::co_occurrences(&self.g, &self.idx, entity_id, target_type, limit);
        let output: Vec<serde_json::Value> = results
            .into_iter()
            .map(|(node, count)| {
                serde_json::json!({
                    "node": node,
                    "count": count,
                })
            })
            .collect();
        serde_json::to_string(&output).unwrap_or_else(|_| "[]".to_string())
    }
}
