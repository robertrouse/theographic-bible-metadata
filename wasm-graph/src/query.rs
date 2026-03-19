//! Graph query functions: traversal, path finding, filtering, family trees.

use crate::model::*;
use petgraph::algo::astar;
use petgraph::graph::NodeIndex;
use petgraph::visit::EdgeRef;
use petgraph::Direction;
use serde::Serialize;
use std::collections::{HashSet, VecDeque};

use crate::graph::BibleGraph;

// ---------------------------------------------------------------------------
// Serializable result types (returned as JSON to JS)
// ---------------------------------------------------------------------------

#[derive(Serialize)]
pub struct NodeResult {
    pub id: String,
    pub label: String,
    pub node_type: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extra: Option<serde_json::Value>,
}

#[derive(Serialize)]
pub struct EdgeResult {
    pub source: String,
    pub target: String,
    pub edge_type: String,
}

#[derive(Serialize)]
pub struct SubgraphResult {
    pub nodes: Vec<NodeResult>,
    pub edges: Vec<EdgeResult>,
}

#[derive(Serialize)]
pub struct PathResult {
    pub nodes: Vec<NodeResult>,
    pub length: usize,
}

#[derive(Serialize)]
pub struct FamilyTree {
    pub person: NodeResult,
    pub father: Option<NodeResult>,
    pub mother: Option<NodeResult>,
    pub siblings: Vec<NodeResult>,
    pub partners: Vec<NodeResult>,
    pub children: Vec<NodeResult>,
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn node_to_result(g: &BibleGraph, ni: NodeIndex) -> NodeResult {
    let nd = &g[ni];
    let extra = match nd {
        NodeData::Person {
            gender,
            birth_year,
            death_year,
            ..
        } => Some(serde_json::json!({
            "gender": gender,
            "birthYear": birth_year,
            "deathYear": death_year,
        })),
        NodeData::Place {
            lat,
            lng,
            feature_type,
            ..
        } => Some(serde_json::json!({
            "lat": lat,
            "lng": lng,
            "featureType": feature_type,
        })),
        NodeData::Event {
            start_date,
            sort_key,
            ..
        } => Some(serde_json::json!({
            "startDate": start_date,
            "sortKey": sort_key,
        })),
        NodeData::Verse { text, year, .. } => Some(serde_json::json!({
            "text": text,
            "year": year,
        })),
        NodeData::Book {
            order,
            testament,
            division,
            ..
        } => Some(serde_json::json!({
            "order": order,
            "testament": testament,
            "division": division,
        })),
        _ => None,
    };
    NodeResult {
        id: nd.rec_id().to_string(),
        label: nd.label().to_string(),
        node_type: nd.node_type().to_string(),
        extra,
    }
}

// ---------------------------------------------------------------------------
// Query: find node by record ID
// ---------------------------------------------------------------------------

pub fn find_by_id(g: &BibleGraph, idx: &RecordIndex, id: &str) -> Option<NodeResult> {
    idx.get(id).map(|&ni| node_to_result(g, ni))
}

// ---------------------------------------------------------------------------
// Query: search nodes by label substring (case-insensitive)
// ---------------------------------------------------------------------------

pub fn search(g: &BibleGraph, query: &str, limit: usize) -> Vec<NodeResult> {
    let q = query.to_lowercase();
    let mut results = Vec::new();
    for ni in g.node_indices() {
        if g[ni].label().to_lowercase().contains(&q) {
            results.push(node_to_result(g, ni));
            if results.len() >= limit {
                break;
            }
        }
    }
    results
}

// ---------------------------------------------------------------------------
// Query: search nodes by type and optional label filter
// ---------------------------------------------------------------------------

pub fn search_by_type(
    g: &BibleGraph,
    node_type: &str,
    query: Option<&str>,
    limit: usize,
) -> Vec<NodeResult> {
    let q = query.map(|s| s.to_lowercase());
    let mut results = Vec::new();
    for ni in g.node_indices() {
        let nd = &g[ni];
        if nd.node_type() == node_type {
            if let Some(ref q) = q {
                if !nd.label().to_lowercase().contains(q) {
                    continue;
                }
            }
            results.push(node_to_result(g, ni));
            if results.len() >= limit {
                break;
            }
        }
    }
    results
}

// ---------------------------------------------------------------------------
// Query: get neighbors of a node
// ---------------------------------------------------------------------------

pub fn neighbors(
    g: &BibleGraph,
    idx: &RecordIndex,
    id: &str,
    edge_filter: Option<&str>,
    direction: Option<&str>,
) -> SubgraphResult {
    let mut nodes = Vec::new();
    let mut edges = Vec::new();

    let Some(&ni) = idx.get(id) else {
        return SubgraphResult { nodes, edges };
    };

    let dir = match direction {
        Some("incoming") => Some(Direction::Incoming),
        Some("outgoing") => Some(Direction::Outgoing),
        _ => None,
    };

    let directions = match dir {
        Some(d) => vec![d],
        None => vec![Direction::Outgoing, Direction::Incoming],
    };

    let mut seen = HashSet::new();
    seen.insert(ni);
    nodes.push(node_to_result(g, ni));

    for d in directions {
        for edge in g.edges_directed(ni, d) {
            let et = edge.weight().as_str();
            if let Some(filter) = edge_filter {
                if et != filter {
                    continue;
                }
            }
            let other = if d == Direction::Outgoing {
                edge.target()
            } else {
                edge.source()
            };
            let (src, tgt) = if d == Direction::Outgoing {
                (id.to_string(), g[other].rec_id().to_string())
            } else {
                (g[other].rec_id().to_string(), id.to_string())
            };
            edges.push(EdgeResult {
                source: src,
                target: tgt,
                edge_type: et.to_string(),
            });
            if seen.insert(other) {
                nodes.push(node_to_result(g, other));
            }
        }
    }

    SubgraphResult { nodes, edges }
}

// ---------------------------------------------------------------------------
// Query: BFS subgraph extraction (ego graph)
// ---------------------------------------------------------------------------

pub fn ego_graph(
    g: &BibleGraph,
    idx: &RecordIndex,
    id: &str,
    max_depth: usize,
    node_type_filter: Option<&str>,
    max_nodes: usize,
) -> SubgraphResult {
    let mut nodes = Vec::new();
    let mut edges = Vec::new();

    let Some(&start) = idx.get(id) else {
        return SubgraphResult { nodes, edges };
    };

    let mut visited: HashSet<NodeIndex> = HashSet::new();
    let mut queue: VecDeque<(NodeIndex, usize)> = VecDeque::new();
    visited.insert(start);
    queue.push_back((start, 0));
    nodes.push(node_to_result(g, start));

    while let Some((current, depth)) = queue.pop_front() {
        if nodes.len() >= max_nodes {
            break;
        }
        if depth >= max_depth {
            continue;
        }
        for edge in g.edges(current) {
            let neighbor = edge.target();
            if let Some(filter) = node_type_filter {
                if g[neighbor].node_type() != filter {
                    continue;
                }
            }
            edges.push(EdgeResult {
                source: g[current].rec_id().to_string(),
                target: g[neighbor].rec_id().to_string(),
                edge_type: edge.weight().as_str().to_string(),
            });
            if visited.insert(neighbor) {
                nodes.push(node_to_result(g, neighbor));
                queue.push_back((neighbor, depth + 1));
            }
        }
        // Also traverse incoming edges
        for edge in g.edges_directed(current, Direction::Incoming) {
            let neighbor = edge.source();
            if let Some(filter) = node_type_filter {
                if g[neighbor].node_type() != filter {
                    continue;
                }
            }
            edges.push(EdgeResult {
                source: g[neighbor].rec_id().to_string(),
                target: g[current].rec_id().to_string(),
                edge_type: edge.weight().as_str().to_string(),
            });
            if visited.insert(neighbor) {
                nodes.push(node_to_result(g, neighbor));
                queue.push_back((neighbor, depth + 1));
            }
        }
    }

    SubgraphResult { nodes, edges }
}

// ---------------------------------------------------------------------------
// Query: shortest path between two nodes
// ---------------------------------------------------------------------------

pub fn shortest_path(
    g: &BibleGraph,
    idx: &RecordIndex,
    from_id: &str,
    to_id: &str,
) -> Option<PathResult> {
    let (&start, &goal) = (idx.get(from_id)?, idx.get(to_id)?);

    let result = astar(
        g,
        start,
        |n| n == goal,
        |_| 1u32,
        |_| 0u32,
    );

    result.map(|(cost, path)| {
        let nodes: Vec<NodeResult> = path.iter().map(|&ni| node_to_result(g, ni)).collect();
        PathResult {
            length: cost as usize,
            nodes,
        }
    })
}

// ---------------------------------------------------------------------------
// Query: family tree for a person
// ---------------------------------------------------------------------------

pub fn family_tree(
    g: &BibleGraph,
    idx: &RecordIndex,
    person_id: &str,
) -> Option<FamilyTree> {
    let &ni = idx.get(person_id)?;

    // Verify it's a person node
    if g[ni].node_type() != "Person" {
        return None;
    }

    let person = node_to_result(g, ni);
    let mut father = None;
    let mut mother = None;
    let mut siblings = Vec::new();
    let mut partners = Vec::new();
    let mut children = Vec::new();

    // Incoming edges: someone → this person
    for edge in g.edges_directed(ni, Direction::Incoming) {
        let src = edge.source();
        match edge.weight() {
            EdgeType::FatherOf => father = Some(node_to_result(g, src)),
            EdgeType::MotherOf => mother = Some(node_to_result(g, src)),
            EdgeType::ChildOf => children.push(node_to_result(g, src)),
            _ => {}
        }
    }

    // Outgoing edges: this person → someone
    for edge in g.edges_directed(ni, Direction::Outgoing) {
        let tgt = edge.target();
        match edge.weight() {
            EdgeType::SiblingOf
            | EdgeType::HalfSiblingSameMother
            | EdgeType::HalfSiblingSameFather => {
                siblings.push(node_to_result(g, tgt));
            }
            EdgeType::PartnerOf => partners.push(node_to_result(g, tgt)),
            EdgeType::ChildOf => children.push(node_to_result(g, tgt)),
            EdgeType::FatherOf | EdgeType::MotherOf => {
                // This person is a parent — the target is their child
                // (handled from the other side already)
            }
            _ => {}
        }
    }

    // Also check incoming sibling/partner edges
    for edge in g.edges_directed(ni, Direction::Incoming) {
        let src = edge.source();
        match edge.weight() {
            EdgeType::SiblingOf
            | EdgeType::HalfSiblingSameMother
            | EdgeType::HalfSiblingSameFather => {
                siblings.push(node_to_result(g, src));
            }
            EdgeType::PartnerOf => partners.push(node_to_result(g, src)),
            _ => {}
        }
    }

    Some(FamilyTree {
        person,
        father,
        mother,
        siblings,
        partners,
        children,
    })
}

// ---------------------------------------------------------------------------
// Query: ancestor chain (walk up father/mother edges)
// ---------------------------------------------------------------------------

pub fn ancestors(
    g: &BibleGraph,
    idx: &RecordIndex,
    person_id: &str,
    max_generations: usize,
) -> Vec<Vec<NodeResult>> {
    let Some(&start) = idx.get(person_id) else {
        return Vec::new();
    };

    let mut generations: Vec<Vec<NodeResult>> = Vec::new();
    let mut current_gen = vec![start];

    for _ in 0..max_generations {
        let mut next_gen = Vec::new();
        let mut gen_results = Vec::new();

        for &ni in &current_gen {
            for edge in g.edges_directed(ni, Direction::Incoming) {
                match edge.weight() {
                    EdgeType::FatherOf | EdgeType::MotherOf => {
                        let parent = edge.source();
                        gen_results.push(node_to_result(g, parent));
                        next_gen.push(parent);
                    }
                    _ => {}
                }
            }
        }

        if gen_results.is_empty() {
            break;
        }
        generations.push(gen_results);
        current_gen = next_gen;
    }

    generations
}

// ---------------------------------------------------------------------------
// Query: descendants (walk down child edges)
// ---------------------------------------------------------------------------

pub fn descendants(
    g: &BibleGraph,
    idx: &RecordIndex,
    person_id: &str,
    max_generations: usize,
) -> Vec<Vec<NodeResult>> {
    let Some(&start) = idx.get(person_id) else {
        return Vec::new();
    };

    let mut generations: Vec<Vec<NodeResult>> = Vec::new();
    let mut current_gen = vec![start];

    for _ in 0..max_generations {
        let mut next_gen = Vec::new();
        let mut gen_results = Vec::new();

        for &ni in &current_gen {
            // Outgoing ChildOf edges: this person → child
            for edge in g.edges_directed(ni, Direction::Outgoing) {
                if matches!(edge.weight(), EdgeType::ChildOf) {
                    let child = edge.target();
                    gen_results.push(node_to_result(g, child));
                    next_gen.push(child);
                }
            }
            // Also: FatherOf/MotherOf outgoing means this person is parent
            for edge in g.edges_directed(ni, Direction::Outgoing) {
                if matches!(edge.weight(), EdgeType::FatherOf | EdgeType::MotherOf) {
                    let child = edge.target();
                    gen_results.push(node_to_result(g, child));
                    next_gen.push(child);
                }
            }
        }

        if gen_results.is_empty() {
            break;
        }
        generations.push(gen_results);
        current_gen = next_gen;
    }

    generations
}

// ---------------------------------------------------------------------------
// Query: events timeline (sorted by sortKey)
// ---------------------------------------------------------------------------

pub fn events_timeline(
    g: &BibleGraph,
    start_year: Option<f64>,
    end_year: Option<f64>,
) -> Vec<NodeResult> {
    let mut events: Vec<(f64, NodeIndex)> = Vec::new();

    for ni in g.node_indices() {
        if let NodeData::Event { sort_key, .. } = &g[ni] {
            if let Some(sk) = sort_key {
                let include = match (start_year, end_year) {
                    (Some(s), Some(e)) => *sk >= s && *sk <= e,
                    (Some(s), None) => *sk >= s,
                    (None, Some(e)) => *sk <= e,
                    (None, None) => true,
                };
                if include {
                    events.push((*sk, ni));
                }
            }
        }
    }

    events.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal));
    events.iter().map(|(_, ni)| node_to_result(g, *ni)).collect()
}

// ---------------------------------------------------------------------------
// Query: places with coordinates (for map visualization)
// ---------------------------------------------------------------------------

pub fn places_with_coords(g: &BibleGraph) -> Vec<NodeResult> {
    let mut results = Vec::new();
    for ni in g.node_indices() {
        if let NodeData::Place { lat, lng, .. } = &g[ni] {
            if lat.is_some() && lng.is_some() {
                results.push(node_to_result(g, ni));
            }
        }
    }
    results
}

// ---------------------------------------------------------------------------
// Query: verses mentioning a specific person/place
// ---------------------------------------------------------------------------

pub fn verses_for_entity(
    g: &BibleGraph,
    idx: &RecordIndex,
    entity_id: &str,
    limit: usize,
) -> Vec<NodeResult> {
    let Some(&ni) = idx.get(entity_id) else {
        return Vec::new();
    };

    let mut results = Vec::new();
    for edge in g.edges_directed(ni, Direction::Outgoing) {
        match edge.weight() {
            EdgeType::PersonMentionedIn
            | EdgeType::PlaceMentionedIn
            | EdgeType::EventDescribedIn
            | EdgeType::GroupMentionedIn => {
                results.push(node_to_result(g, edge.target()));
                if results.len() >= limit {
                    break;
                }
            }
            _ => {}
        }
    }
    results
}

// ---------------------------------------------------------------------------
// Query: co-occurrence (entities that appear together in the same verses)
// ---------------------------------------------------------------------------

pub fn co_occurrences(
    g: &BibleGraph,
    idx: &RecordIndex,
    entity_id: &str,
    target_type: &str,
    limit: usize,
) -> Vec<(NodeResult, usize)> {
    let Some(&ni) = idx.get(entity_id) else {
        return Vec::new();
    };

    // Find all verses this entity appears in
    let mut verse_nodes: Vec<NodeIndex> = Vec::new();
    for edge in g.edges_directed(ni, Direction::Outgoing) {
        match edge.weight() {
            EdgeType::PersonMentionedIn
            | EdgeType::PlaceMentionedIn
            | EdgeType::EventDescribedIn
            | EdgeType::GroupMentionedIn => {
                verse_nodes.push(edge.target());
            }
            _ => {}
        }
    }

    // For each verse, find other entities of the target type
    let mut counts: std::collections::HashMap<NodeIndex, usize> = std::collections::HashMap::new();
    for &vni in &verse_nodes {
        for edge in g.edges_directed(vni, Direction::Incoming) {
            let src = edge.source();
            if src != ni && g[src].node_type() == target_type {
                *counts.entry(src).or_insert(0) += 1;
            }
        }
    }

    // Sort by count descending
    let mut pairs: Vec<(NodeIndex, usize)> = counts.into_iter().collect();
    pairs.sort_by(|a, b| b.1.cmp(&a.1));
    pairs.truncate(limit);

    pairs
        .into_iter()
        .map(|(ni, count)| (node_to_result(g, ni), count))
        .collect()
}
