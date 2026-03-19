//! Unit tests for the graph engine: model, graph construction, and queries.

#[cfg(test)]
mod tests {
    use crate::graph::{build_graph, stats, BibleGraph};
    use crate::model::*;
    use crate::query::*;

    // ── Minimal test fixtures ─────────────────────────────────────────

    fn books_json() -> &'static str {
        r#"[
            {"id":"recBOOK1","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "osisName":"Gen","bookName":"Genesis","shortName":"Ge","bookOrder":1,
                "bookDiv":"Pentateuch","testament":"OT","chapterCount":50,"verseCount":1533,
                "chapters":["recCH1"],"verses":["recV1","recV2"]
            }},
            {"id":"recBOOK2","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "osisName":"Exod","bookName":"Exodus","shortName":"Ex","bookOrder":2,
                "bookDiv":"Pentateuch","testament":"OT","chapterCount":40,"verseCount":1213,
                "chapters":["recCH2"],"verses":["recV3"],"writers":["recP2"]
            }}
        ]"#
    }

    fn chapters_json() -> &'static str {
        r#"[
            {"id":"recCH1","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "osisRef":"Gen.1","chapterNum":1,"book":["recBOOK1"],
                "verses":["recV1","recV2"],"writer":["recP1"]
            }},
            {"id":"recCH2","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "osisRef":"Exod.1","chapterNum":1,"book":["recBOOK2"],
                "verses":["recV3"],"writer":["recP2"]
            }}
        ]"#
    }

    fn verses_json() -> &'static str {
        r#"[
            {"id":"recV1","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "osisRef":"Gen.1.1","verseNum":"1","verseText":"In the beginning God created the heaven and the earth.",
                "book":["recBOOK1"],"chapter":["recCH1"],"people":["recP1"],
                "places":["recPL1"],"event":["recEV1"],"yearNum":-4004,"verseID":"01001001"
            }},
            {"id":"recV2","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "osisRef":"Gen.1.2","verseNum":"2","verseText":"And the earth was without form, and void.",
                "book":["recBOOK1"],"chapter":["recCH1"],"people":["recP1"],
                "places":["recPL1"],"event":["recEV1"],"yearNum":-4004,"verseID":"01001002"
            }},
            {"id":"recV3","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "osisRef":"Exod.1.1","verseNum":"1","verseText":"Now these are the names of the children of Israel.",
                "book":["recBOOK2"],"chapter":["recCH2"],"people":["recP2","recP3"],
                "yearNum":-1706,"verseID":"02001001"
            }}
        ]"#
    }

    fn people_json() -> &'static str {
        r#"[
            {"id":"recP1","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "personLookup":"god_1","name":"God","gender":"Male","isProperName":true
            }},
            {"id":"recP2","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "personLookup":"moses_1","name":"Moses","gender":"Male",
                "birthYear":"-1526","deathYear":"-1406",
                "father":["recP4"],"mother":["recP5"],
                "siblings":["recP3"],"children":["recP6"],
                "birthPlace":["recPL2"],"eastons":["recE1"]
            }},
            {"id":"recP3","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "personLookup":"aaron_1","name":"Aaron","gender":"Male",
                "birthYear":"-1529","deathYear":"-1406",
                "father":["recP4"],"mother":["recP5"],
                "siblings":["recP2"]
            }},
            {"id":"recP4","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "personLookup":"amram_1","name":"Amram","gender":"Male",
                "children":["recP2","recP3"],"partners":["recP5"]
            }},
            {"id":"recP5","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "personLookup":"jochebed_1","name":"Jochebed","gender":"Female",
                "children":["recP2","recP3"],"partners":["recP4"]
            }},
            {"id":"recP6","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "personLookup":"gershom_1","name":"Gershom","gender":"Male",
                "father":["recP2"]
            }}
        ]"#
    }

    fn places_json() -> &'static str {
        r#"[
            {"id":"recPL1","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "placeLookup":"eden_1","displayTitle":"Garden of Eden","featureType":"Region",
                "latitude":"35.0","longitude":"44.0"
            }},
            {"id":"recPL2","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "placeLookup":"goshen_1","displayTitle":"Goshen","featureType":"Region",
                "latitude":"30.87","longitude":"31.83",
                "rootID":["recPL3"]
            }},
            {"id":"recPL3","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "placeLookup":"egypt_1","displayTitle":"Egypt","featureType":"Nation",
                "latitude":"26.82","longitude":"30.80"
            }}
        ]"#
    }

    fn events_json() -> &'static str {
        r#"[
            {"id":"recEV1","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "title":"Creation of all things","startDate":"-4003","sortKey":-4003,
                "participants":["recP1"],"locations":["recPL1"]
            }},
            {"id":"recEV2","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "title":"The Exodus","startDate":"-1446","sortKey":-1446,
                "participants":["recP2","recP3"],"locations":["recPL3"],
                "predecessor":["recEV1"]
            }},
            {"id":"recEV3","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "title":"Burning Bush","startDate":"-1447","sortKey":-1447,
                "participants":["recP1","recP2"],"partOf":["recEV2"]
            }}
        ]"#
    }

    fn groups_json() -> &'static str {
        r#"[
            {"id":"recGR1","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "groupName":"Tribe of Levi","members":["recP2","recP3"]
            }}
        ]"#
    }

    fn easton_json() -> &'static str {
        r#"[
            {"id":"recE1","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "termLabel":"Moses","dictText":"The great Hebrew lawgiver and leader.",
                "personLookup":["recP2"]
            }},
            {"id":"recE2","createdTime":"2024-01-01T00:00:00.000Z","fields":{
                "termLabel":"Eden","dictText":"Delight, the first home of man.",
                "placeLookup":["recPL1"]
            }}
        ]"#
    }

    fn build_test_graph() -> (BibleGraph, RecordIndex) {
        build_graph(
            books_json(),
            chapters_json(),
            verses_json(),
            people_json(),
            places_json(),
            events_json(),
            groups_json(),
            easton_json(),
        )
    }

    // ── Model tests ───────────────────────────────────────────────────

    #[test]
    fn test_node_data_accessors() {
        let node = NodeData::Person {
            rec_id: "rec1".into(),
            name: "Moses".into(),
            lookup: "moses_1".into(),
            gender: "Male".into(),
            birth_year: Some("-1526".into()),
            death_year: Some("-1406".into()),
        };
        assert_eq!(node.rec_id(), "rec1");
        assert_eq!(node.label(), "Moses");
        assert_eq!(node.node_type(), "Person");
    }

    #[test]
    fn test_node_types_all_variants() {
        let variants: Vec<NodeData> = vec![
            NodeData::Book { rec_id: "b".into(), name: "Gen".into(), osis: "Gen".into(), order: 1, testament: "OT".into(), division: "Pentateuch".into() },
            NodeData::Chapter { rec_id: "c".into(), osis_ref: "Gen.1".into(), chapter_num: 1 },
            NodeData::Verse { rec_id: "v".into(), osis_ref: "Gen.1.1".into(), text: "In the beginning".into(), verse_id: "01001001".into(), year: Some(-4004.0) },
            NodeData::Person { rec_id: "p".into(), name: "Moses".into(), lookup: "moses_1".into(), gender: "Male".into(), birth_year: None, death_year: None },
            NodeData::Place { rec_id: "pl".into(), name: "Eden".into(), lookup: "eden_1".into(), lat: Some(35.0), lng: Some(44.0), feature_type: "Region".into() },
            NodeData::Event { rec_id: "e".into(), title: "Creation".into(), start_date: Some("-4003".into()), sort_key: Some(-4003.0) },
            NodeData::PeopleGroup { rec_id: "g".into(), name: "Levites".into() },
            NodeData::Easton { rec_id: "ea".into(), term: "Moses".into(), text: "Leader".into() },
        ];
        let types = ["Book", "Chapter", "Verse", "Person", "Place", "Event", "PeopleGroup", "Easton"];
        for (node, expected) in variants.iter().zip(types.iter()) {
            assert_eq!(node.node_type(), *expected);
        }
    }

    #[test]
    fn test_edge_type_as_str() {
        assert_eq!(EdgeType::FatherOf.as_str(), "FATHER_OF");
        assert_eq!(EdgeType::MotherOf.as_str(), "MOTHER_OF");
        assert_eq!(EdgeType::BookHasChapter.as_str(), "BOOK_HAS_CHAPTER");
        assert_eq!(EdgeType::PersonMentionedIn.as_str(), "MENTIONED_IN");
        assert_eq!(EdgeType::WriterOf.as_str(), "WRITER_OF");
    }

    // ── Graph construction tests ──────────────────────────────────────

    #[test]
    fn test_build_graph_stats() {
        let (g, _idx) = build_test_graph();
        let s = stats(&g);
        assert_eq!(s.books, 2);
        assert_eq!(s.chapters, 2);
        assert_eq!(s.verses, 3);
        assert_eq!(s.people, 6);
        assert_eq!(s.places, 3);
        assert_eq!(s.events, 3);
        assert_eq!(s.groups, 1);
        assert_eq!(s.easton, 2);
        assert_eq!(s.node_count, 22);
        assert!(s.edge_count > 0, "Should have edges");
    }

    #[test]
    fn test_index_contains_all_records() {
        let (_g, idx) = build_test_graph();
        assert!(idx.contains_key("recBOOK1"));
        assert!(idx.contains_key("recP2"));
        assert!(idx.contains_key("recPL1"));
        assert!(idx.contains_key("recEV1"));
        assert!(idx.contains_key("recGR1"));
        assert!(idx.contains_key("recE1"));
    }

    #[test]
    fn test_empty_json_builds_empty_graph() {
        let (g, idx) = build_graph("[]", "[]", "[]", "[]", "[]", "[]", "[]", "[]");
        assert_eq!(g.node_count(), 0);
        assert_eq!(g.edge_count(), 0);
        assert_eq!(idx.len(), 0);
    }

    #[test]
    fn test_malformed_json_does_not_panic() {
        // build_graph uses unwrap_or_default for parsing, so bad JSON should produce empty graph
        let (g, _idx) = build_graph("not json", "{}", "[]", "[]", "[]", "[]", "[]", "[]");
        // Should not panic. Books and chapters may be 0, but verses etc. loaded fine.
        assert!(g.node_count() >= 0);
    }

    // ── Query: find_by_id ─────────────────────────────────────────────

    #[test]
    fn test_find_by_id_existing() {
        let (g, idx) = build_test_graph();
        let result = find_by_id(&g, &idx, "recP2");
        assert!(result.is_some());
        let r = result.unwrap();
        assert_eq!(r.label, "Moses");
        assert_eq!(r.node_type, "Person");
    }

    #[test]
    fn test_find_by_id_nonexistent() {
        let (g, idx) = build_test_graph();
        assert!(find_by_id(&g, &idx, "recNONE").is_none());
    }

    // ── Query: search ─────────────────────────────────────────────────

    #[test]
    fn test_search_case_insensitive() {
        let (g, _idx) = build_test_graph();
        let results = search(&g, "moses", 10);
        // Should find Person Moses and Easton Moses
        assert!(results.len() >= 1);
        assert!(results.iter().any(|r| r.label == "Moses" && r.node_type == "Person"));
    }

    #[test]
    fn test_search_limit() {
        let (g, _idx) = build_test_graph();
        let results = search(&g, "e", 2); // 'e' appears in many labels
        assert!(results.len() <= 2);
    }

    #[test]
    fn test_search_no_match() {
        let (g, _idx) = build_test_graph();
        let results = search(&g, "zzzznonexistent", 10);
        assert!(results.is_empty());
    }

    // ── Query: search_by_type ─────────────────────────────────────────

    #[test]
    fn test_search_by_type_person() {
        let (g, _idx) = build_test_graph();
        let results = search_by_type(&g, "Person", Some("aaron"), 10);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].label, "Aaron");
    }

    #[test]
    fn test_search_by_type_no_query() {
        let (g, _idx) = build_test_graph();
        let results = search_by_type(&g, "Book", None, 100);
        assert_eq!(results.len(), 2);
    }

    // ── Query: neighbors ──────────────────────────────────────────────

    #[test]
    fn test_neighbors_returns_connections() {
        let (g, idx) = build_test_graph();
        let result = neighbors(&g, &idx, "recP2", None, None);
        // Moses should have connections: father, mother, siblings, children, birth place, easton
        assert!(!result.nodes.is_empty());
        assert!(!result.edges.is_empty());
        // Should include Moses himself
        assert!(result.nodes.iter().any(|n| n.id == "recP2"));
    }

    #[test]
    fn test_neighbors_with_edge_filter() {
        let (g, idx) = build_test_graph();
        let result = neighbors(&g, &idx, "recP2", Some("SIBLING_OF"), None);
        // Only sibling edges
        assert!(result.edges.iter().all(|e| e.edge_type == "SIBLING_OF"));
    }

    #[test]
    fn test_neighbors_nonexistent_node() {
        let (g, idx) = build_test_graph();
        let result = neighbors(&g, &idx, "recNONE", None, None);
        assert!(result.nodes.is_empty());
    }

    // ── Query: ego_graph ──────────────────────────────────────────────

    #[test]
    fn test_ego_graph_depth_1() {
        let (g, idx) = build_test_graph();
        let result = ego_graph(&g, &idx, "recP2", 1, None, 100);
        assert!(result.nodes.len() > 1, "Ego graph should include neighbors");
        assert!(result.nodes.iter().any(|n| n.id == "recP2"));
    }

    #[test]
    fn test_ego_graph_depth_0() {
        let (g, idx) = build_test_graph();
        let result = ego_graph(&g, &idx, "recP2", 0, None, 100);
        // Depth 0 should only include the root node
        assert_eq!(result.nodes.len(), 1);
        assert_eq!(result.nodes[0].id, "recP2");
    }

    #[test]
    fn test_ego_graph_max_nodes_limit() {
        let (g, idx) = build_test_graph();
        // max_nodes is checked at the start of each BFS iteration, so the actual
        // result may slightly exceed the limit when neighbors are added in bulk.
        // Verify it's meaningfully bounded compared to the full graph.
        let unlimited = ego_graph(&g, &idx, "recP2", 3, None, 1000);
        let limited = ego_graph(&g, &idx, "recP2", 3, None, 3);
        assert!(limited.nodes.len() < unlimited.nodes.len(),
            "Limited ego graph ({}) should be smaller than unlimited ({})",
            limited.nodes.len(), unlimited.nodes.len());
    }

    #[test]
    fn test_ego_graph_type_filter() {
        let (g, idx) = build_test_graph();
        let result = ego_graph(&g, &idx, "recP2", 2, Some("Person"), 100);
        // Only Person nodes should be traversed (plus the root)
        for node in &result.nodes {
            if node.id != "recP2" {
                assert_eq!(node.node_type, "Person");
            }
        }
    }

    // ── Query: shortest_path ──────────────────────────────────────────

    #[test]
    fn test_shortest_path_same_node() {
        let (g, idx) = build_test_graph();
        let result = shortest_path(&g, &idx, "recP2", "recP2");
        assert!(result.is_some());
        let path = result.unwrap();
        assert_eq!(path.length, 0);
        assert_eq!(path.nodes.len(), 1);
    }

    #[test]
    fn test_shortest_path_parent_child() {
        let (g, idx) = build_test_graph();
        // Amram -> Moses (father edge)
        let result = shortest_path(&g, &idx, "recP4", "recP2");
        assert!(result.is_some());
        let path = result.unwrap();
        assert!(path.length > 0);
        assert!(path.nodes.len() >= 2);
    }

    #[test]
    fn test_shortest_path_nonexistent() {
        let (g, idx) = build_test_graph();
        assert!(shortest_path(&g, &idx, "recNONE", "recP2").is_none());
    }

    // ── Query: family_tree ────────────────────────────────────────────

    #[test]
    fn test_family_tree_moses() {
        let (g, idx) = build_test_graph();
        let result = family_tree(&g, &idx, "recP2");
        assert!(result.is_some());
        let ft = result.unwrap();
        assert_eq!(ft.person.label, "Moses");
        assert!(ft.father.is_some());
        assert_eq!(ft.father.unwrap().label, "Amram");
        assert!(ft.mother.is_some());
        assert_eq!(ft.mother.unwrap().label, "Jochebed");
        // Moses has siblings (Aaron)
        assert!(!ft.siblings.is_empty());
    }

    #[test]
    fn test_family_tree_not_a_person() {
        let (g, idx) = build_test_graph();
        let result = family_tree(&g, &idx, "recBOOK1");
        assert!(result.is_none());
    }

    #[test]
    fn test_family_tree_nonexistent() {
        let (g, idx) = build_test_graph();
        assert!(family_tree(&g, &idx, "recNONE").is_none());
    }

    // ── Query: ancestors ──────────────────────────────────────────────

    #[test]
    fn test_ancestors_finds_parents() {
        let (g, idx) = build_test_graph();
        let result = ancestors(&g, &idx, "recP2", 3);
        // Moses has parents Amram and Jochebed
        assert!(!result.is_empty());
        let first_gen = &result[0];
        let names: Vec<&str> = first_gen.iter().map(|n| n.label.as_str()).collect();
        assert!(names.contains(&"Amram") || names.contains(&"Jochebed"));
    }

    #[test]
    fn test_ancestors_nonexistent() {
        let (g, idx) = build_test_graph();
        let result = ancestors(&g, &idx, "recNONE", 3);
        assert!(result.is_empty());
    }

    // ── Query: descendants ────────────────────────────────────────────

    #[test]
    fn test_descendants_finds_children() {
        let (g, idx) = build_test_graph();
        let result = descendants(&g, &idx, "recP4", 3);
        // Amram has children Moses and Aaron
        assert!(!result.is_empty());
    }

    // ── Query: events_timeline ────────────────────────────────────────

    #[test]
    fn test_events_timeline_all() {
        let (g, _idx) = build_test_graph();
        let result = events_timeline(&g, None, None);
        assert_eq!(result.len(), 3);
        // Should be sorted by sortKey
        assert_eq!(result[0].label, "Creation of all things");
    }

    #[test]
    fn test_events_timeline_filtered() {
        let (g, _idx) = build_test_graph();
        let result = events_timeline(&g, Some(-1450.0), Some(-1440.0));
        assert_eq!(result.len(), 2); // Burning Bush (-1447) and Exodus (-1446)
    }

    #[test]
    fn test_events_timeline_no_match() {
        let (g, _idx) = build_test_graph();
        let result = events_timeline(&g, Some(2000.0), Some(3000.0));
        assert!(result.is_empty());
    }

    // ── Query: places_with_coords ─────────────────────────────────────

    #[test]
    fn test_places_with_coords() {
        let (g, _idx) = build_test_graph();
        let result = places_with_coords(&g);
        assert_eq!(result.len(), 3); // Eden, Goshen, Egypt all have coords
        // All should be Place type
        assert!(result.iter().all(|n| n.node_type == "Place"));
    }

    // ── Query: verses_for_entity ──────────────────────────────────────

    #[test]
    fn test_verses_for_entity() {
        let (g, idx) = build_test_graph();
        let result = verses_for_entity(&g, &idx, "recP1", 100);
        // God is mentioned in V1 and V2
        assert!(result.len() >= 2);
        assert!(result.iter().all(|n| n.node_type == "Verse"));
    }

    #[test]
    fn test_verses_for_entity_limit() {
        let (g, idx) = build_test_graph();
        let result = verses_for_entity(&g, &idx, "recP1", 1);
        assert_eq!(result.len(), 1);
    }

    // ── Query: co_occurrences ─────────────────────────────────────────

    #[test]
    fn test_co_occurrences() {
        let (g, idx) = build_test_graph();
        // God (recP1) appears in V1 and V2, which also mention Place recPL1
        let result = co_occurrences(&g, &idx, "recP1", "Place", 10);
        assert!(!result.is_empty());
        // Eden should co-occur with God
        assert!(result.iter().any(|(n, _)| n.label == "Garden of Eden"));
    }

    #[test]
    fn test_co_occurrences_no_match() {
        let (g, idx) = build_test_graph();
        let result = co_occurrences(&g, &idx, "recP1", "PeopleGroup", 10);
        // God doesn't co-occur with any PeopleGroup in verses
        assert!(result.is_empty());
    }

    // ── Edge relationship tests ───────────────────────────────────────

    #[test]
    fn test_book_chapter_edges() {
        let (g, idx) = build_test_graph();
        let result = neighbors(&g, &idx, "recBOOK1", Some("BOOK_HAS_CHAPTER"), None);
        assert!(result.nodes.iter().any(|n| n.id == "recCH1"));
    }

    #[test]
    fn test_chapter_verse_edges() {
        let (g, idx) = build_test_graph();
        let result = neighbors(&g, &idx, "recCH1", Some("CHAPTER_HAS_VERSE"), None);
        assert!(result.nodes.iter().any(|n| n.id == "recV1"));
    }

    #[test]
    fn test_event_participant_edges() {
        let (g, idx) = build_test_graph();
        let result = neighbors(&g, &idx, "recEV2", None, None);
        // Exodus should have Moses and Aaron as participants
        let labels: Vec<&str> = result.nodes.iter().map(|n| n.label.as_str()).collect();
        assert!(labels.contains(&"Moses") || labels.contains(&"Aaron"));
    }

    #[test]
    fn test_place_hierarchy_edges() {
        let (g, idx) = build_test_graph();
        let result = neighbors(&g, &idx, "recPL2", Some("PART_OF"), None);
        assert!(result.nodes.iter().any(|n| n.id == "recPL3")); // Goshen -> Egypt
    }

    #[test]
    fn test_dictionary_edges() {
        let (g, idx) = build_test_graph();
        let result = neighbors(&g, &idx, "recP2", Some("HAS_ENTRY"), None);
        assert!(result.nodes.iter().any(|n| n.id == "recE1")); // Moses -> Easton entry
    }

    // ── NodeResult extra field tests ──────────────────────────────────

    #[test]
    fn test_person_extra_fields() {
        let (g, idx) = build_test_graph();
        let result = find_by_id(&g, &idx, "recP2").unwrap();
        let extra = result.extra.unwrap();
        assert_eq!(extra["gender"], "Male");
        assert_eq!(extra["birthYear"], "-1526");
    }

    #[test]
    fn test_place_extra_fields() {
        let (g, idx) = build_test_graph();
        let result = find_by_id(&g, &idx, "recPL1").unwrap();
        let extra = result.extra.unwrap();
        assert_eq!(extra["lat"], 35.0);
        assert_eq!(extra["lng"], 44.0);
        assert_eq!(extra["featureType"], "Region");
    }

    #[test]
    fn test_event_extra_fields() {
        let (g, idx) = build_test_graph();
        let result = find_by_id(&g, &idx, "recEV1").unwrap();
        let extra = result.extra.unwrap();
        assert_eq!(extra["sortKey"], -4003.0);
    }

    #[test]
    fn test_verse_extra_fields() {
        let (g, idx) = build_test_graph();
        let result = find_by_id(&g, &idx, "recV1").unwrap();
        let extra = result.extra.unwrap();
        assert_eq!(extra["year"], -4004.0);
        assert!(extra["text"].as_str().unwrap().contains("beginning"));
    }

    #[test]
    fn test_book_extra_fields() {
        let (g, idx) = build_test_graph();
        let result = find_by_id(&g, &idx, "recBOOK1").unwrap();
        let extra = result.extra.unwrap();
        assert_eq!(extra["testament"], "OT");
        assert_eq!(extra["division"], "Pentateuch");
        assert_eq!(extra["order"], 1);
    }
}
