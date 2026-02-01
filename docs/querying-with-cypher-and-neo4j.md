# Querying with Cypher and Neo4j

[Neo4j](https://neo4j.com/) is a graph database optimized for finding connections throughout data. It simplifies analysis of ancestry, social networks, and influence (i.e PageRank). The Neo4j platform powers Theographic's GraphQL API and offers powerful capabilities for advanced research.

Everything in a graph database is represented by nodes and relationships. Queries in Neo4j are written in the [Cypher](https://neo4j.com/cypher-graph-query-language/) language, which matches a pattern of nodes and connections between them. Neo4j's website describes it this way:

> Cypher is a vendor-neutral open graph query language employed across the graph ecosystem. Cypher’s ASCII-art style syntax provides a familiar, readable way to match patterns of nodes and relationships within graph datasets.
> 

![Illustration of nodes, relationships, and related Cypher by Neo4j](https://s3.amazonaws.com/dev.assets.neo4j.com/wp-content/uploads/20170731135122/Property-Graph-Cypher.svg)

Illustration of nodes, relationships, and related Cypher by Neo4j

This language lets us find everything connected to a passage: people, places, events, words, years, etc. You can easily find a person's complete ancestry or apply advanced graph algorithms with minimal code. Refer to the resources below to get started.

---

## Theographic in **Neo4j**

A Neo4j dump file of the Theographic data is available upon request by e-mailing robert@viz.bible.

## Helpful Resources

[Video introduction to Neo4j](https://neo4j.com/graphacademy/online-training/introduction-to-neo4j/)

[Cypher Refcard](https://neo4j.com/docs/cypher-refcard/current/)

[Graph Sandoboxes with example use cases](https://neo4j.com/sandbox-v2/)