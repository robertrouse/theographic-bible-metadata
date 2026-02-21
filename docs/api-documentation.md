# Theographic Bible Metadata GraphQL API

This document describes the GraphQL API for Theographic Bible Metadata, built using JSON data sources and hosted on Netlify.

## Overview

The API provides access to biblical data including books, chapters, verses, people, places, events, people groups, and Easton's dictionary entries. It is structured similarly to the original Neo4j-based API but uses static JSON files as the data source.

## Deployment

The API is designed to be hosted on Netlify as a serverless function.

### Local Development

1. Navigate to the `api` directory:
   ```
   cd api
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

   This will start Netlify Dev, which serves the functions locally.

### Production Deployment

1. Push the code to a Git repository connected to Netlify.
2. Netlify will automatically detect the `netlify.toml` configuration and deploy the functions.
3. The GraphQL endpoint will be available at `https://your-site.netlify.app/.netlify/functions/graphql`

## GraphQL Endpoint

- **URL**: `/.netlify/functions/graphql`
- **Method**: POST
- **Content-Type**: application/json

## GraphiQL Interface

The API includes a built-in GraphiQL interface for exploration and testing.

- **URL**: Same as the GraphQL endpoint
- **Access**: Visit the endpoint URL in a web browser to access the interactive GraphiQL interface

## Schema

The GraphQL schema includes the following main types:

- `Book`: Biblical books with metadata and relationships
- `Chapter`: Book chapters
- `Verse`: Individual verses with text and references
- `Person`: Individuals mentioned in the Bible
- `Place`: Geographic locations
- `Event`: Biblical events
- `PeopleGroup`: Groups of people (tribes, nations, etc.)
- `Easton`: Entries from Easton's Bible Dictionary

### Root Queries

- `books`: Get all books
- `chapters`: Get all chapters
- `verses`: Get all verses
- `people`: Get all people
- `places`: Get all places
- `events`: Get all events
- `peopleGroups`: Get all people groups
- `easton`: Get all Easton's entries
- `searchVerses(input: String!)`: Search verses by OSIS reference or text
- `searchPeople(input: String!)`: Search people by name or lookup
- `searchPlaces(input: String!)`: Search places by name or lookup

## Example Queries

### Get all books
```graphql
query {
  books {
    id
    bookName
    testament
    chapterCount
  }
}
```

### Search verses
```graphql
query {
  searchVerses(input: "Genesis 1:1") {
    osisRef
    verseText
  }
}
```

### Get person with relationships
```graphql
query {
  people {
    name
    gender
    verses {
      osisRef
      verseText
    }
    birthPlace {
      kjvName
    }
  }
}
```

### Get people with birth and death years
```graphql
query {
  people(where: { name: { eq: "Moses" } }) {
    name
    birthYear
    deathYear
  }
}
```

## Year Numbering Convention

Several fields across the API use **ISO 8601 astronomical year numbering** for dates:

- **`Person.birthYear`** and **`Person.deathYear`**: integers representing the estimated birth or death year.
- **`Verse.yearNum`** and **`Event.sortKey`**: integers/floats representing the approximate year of a verse's events or an event's timeline position.

### How to read negative years

ISO 8601 astronomical year numbering counts backward from AD 1, with **year 0 equal to 1 BC**:

| ISO year | Traditional date |
|----------|-----------------|
| `1`      | AD 1            |
| `0`      | 1 BC            |
| `-1`     | 2 BC            |
| `-1004`  | 1005 BC         |
| `-4003`  | 4004 BC         |

To convert a negative ISO year to a BC year: **negate the value and add 1**.
For example: `-4003 → 4004 BC`, `-1574 → 1575 BC`.

Positive values represent AD years directly (e.g. `30` = AD 30).

## Data Source

The API uses JSON files from the `json/` directory as its data source. These files are generated from Airtable exports and contain structured biblical metadata.

## Differences from Original API

- Uses JSON data instead of Neo4j database
- Simplified search functionality (no full-text indexing)
- Some computed fields (like verse counts) are calculated on-the-fly
- Limited to the data available in the JSON files

## Error Handling

The API returns standard GraphQL errors. Common issues:

- Invalid queries will return validation errors
- Missing data will return null values for optional fields
- Network issues may result in timeout errors

## Rate Limiting

As a Netlify serverless function, the API is subject to Netlify's function limits. For high-traffic applications, consider implementing caching or pagination.

## Support

For issues or questions about the API, please refer to the main project documentation or create an issue in the repository.
