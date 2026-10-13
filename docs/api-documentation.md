# Theographic Bible Metadata GraphQL API

A read-only GraphQL API over the JSON files in this repository. It covers books, chapters, verses, people, places, events, people groups, and Easton's Bible Dictionary entries. The source is in [`api/`](../api) and runs as a Netlify serverless function.

## Endpoint

| | |
|---|---|
| **URL** | `https://theographic-api.netlify.app/api/graphql` |
| **Method** | `POST`, with `Content-Type: application/json` and a body of `{"query": "..."}` |
| **Explorer** | Open the URL in a browser for the Apollo Sandbox explorer |
| **Auth** | None |

```bash
curl -s https://theographic-api.netlify.app/api/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ people(where: { name: { eq: \"Moses\" } }) { name birthYear deathYear } }"}'
```

The API serves the JSON that was bundled at deploy time, so it can lag behind the files on `master` until the next deploy.

## Queries

Every collection query takes the same three optional arguments:

| Argument | Description |
|---|---|
| `where` | A filter object. All conditions are combined with AND. |
| `limit` | Maximum number of records to return. |
| `offset` | Number of records to skip, for pagination. |

| Query | Returns | Filterable fields (`where`) |
|---|---|---|
| `books` | `[Book]` | `id`, `bookName`, `osisName`, `shortName`, `testament`, `bookDiv`, `bookOrder`, `chapterCount`, `verseCount`, `slug` |
| `chapters` | `[Chapter]` | `id`, `osisRef`, `slug`, `chapterNum`, `peopleCount`, `placesCount`, `writerCount` |
| `verses` | `[Verse]` | `id`, `osisRef`, `verseText`, `yearNum`, `peopleCount`, `status` |
| `people` | `[Person]` | `id`, `name`, `displayTitle`, `personLookup`, `gender`, `slug`, `alsoCalled`, `alphaGroup`, `status`, `ambiguous`, `isProperName`, `verseCount`, `minYear`, `maxYear` |
| `places` | `[Place]` | `id`, `kjvName`, `esvName`, `displayTitle`, `placeLookup`, `featureType`, `featureSubType`, `slug`, `alphaGroup`, `status`, `ambiguous`, `verseCount` |
| `events` | `[Event]` | `id`, `title`, `notes`, `startDate`, `duration`, `lagType`, `rangeFlag`, `eventID`, `sortKey` |
| `peopleGroups` | `[PeopleGroup]` | `id`, `groupName` |
| `easton` | `[Easton]` | `id`, `termLabel`, `dictLookup`, `matchType`, `dictText` |

### Filter operators

| Field type | Operators |
|---|---|
| String | `eq` (exact, case-sensitive), `contains` (case-insensitive substring) |
| Int / Float | `eq`, `gte`, `lte` |
| Boolean | `eq` |

### Search queries

| Query | Matches (case-insensitive substring) |
|---|---|
| `searchVerses(input: String!)` | `osisRef` or `verseText`. Use OSIS form: `"John.3.16"`, not `"John 3:16"`. |
| `searchPeople(input: String!)` | `name`, `alsoCalled`, or `personLookup` |
| `searchPlaces(input: String!)` | `kjvName`, `displayTitle`, or `placeLookup` |

Search is substring matching, not ranked full-text search, so `searchVerses(input: "Gen.1.1")` also returns `Gen.1.10` through `Gen.1.19`. For ranked full-text search, use the [Neo4j import](neo4j-graph-documentation.md).

### Relationships

Link fields resolve to full objects, so queries can traverse the graph. For example: `Person.father`, `mother`, `children`, `siblings`, `partners`, `memberOf`, `birthPlace`, `deathPlace`, and `verses`; `Verse.people`, `places`, and `book`; `Event.participants`, `locations`, `verses`, and `predecessor`. Nested lists do not accept `where`/`limit`. To keep responses small, paginate at the top level.

The explorer shows the full schema with a description for every field.

## Examples

### New Testament books
```graphql
{
  books(where: { testament: { eq: "New Testament" } }) {
    bookName
    chapterCount
    verseCount
  }
}
```

### A verse by reference
```graphql
{
  verses(where: { osisRef: { eq: "John.3.16" } }) {
    osisRef
    verseText
  }
}
```

### A person with family and birthplace
```graphql
{
  people(where: { slug: { eq: "paul_2479" } }) {
    displayTitle
    birthPlace { kjvName latitude longitude }
    verses { osisRef }
  }
}
```

### Events in a date range, in timeline order
```graphql
{
  events(where: { sortKey: { gte: -1100, lte: -1000 } }) {
    title
    startDate
    duration
    participants { name }
    locations { kjvName }
  }
}
```

### Paginating through verses
```graphql
{
  verses(limit: 1000, offset: 2000) { osisRef verseText }
}
```

## Dates and year numbering

Dates follow the chronology of Dr. Floyd Nolen Jones. Every year field uses **ISO 8601 astronomical year numbering**, so `-4003` is 4004 BC, `0` is 1 BC, and `30` is AD 30:

| Field | Type | Example |
|---|---|---|
| `Event.startDate` | String | `"-4003"`, or a `YYYY-MM-DD` date such as `"0030-04-04"` |
| `Event.sortKey` | Float | `-4002.98998999` |
| `Person.birthYear`, `Person.deathYear` | Int | Moses: `-1570`, `-1451` |
| `Verse.yearNum` | Int | `Gen.1.1`: `-4003` (Ussher, via the *Treasury of Scripture Knowledge*) |

BC year = `1 - value` for values ≤ 0. See [Chronology and Dates](chronology-and-dates.md).

## Limits

- **Response size:** Netlify functions return at most about 6 MB. An unpaginated `verses` query that asks for `verseText` comes close to that limit, and adding more fields pushes it over (HTTP 502). Always use `limit`/`offset` with `verses`.
- **Rate limits:** The API runs on Netlify's function quotas, which have no published per-client rate limit. For heavy or bulk use, download the [JSON files](../json) directly.

## Running locally

```bash
cd api
npm install
npm start
```

`npm start` runs `netlify dev`, which serves the function at `http://localhost:8888/.netlify/functions/graphql` (also routed at `/api/graphql`). It reads JSON from the repository's `json/` directory.

```bash
npm test
```

Runs the test suite in `api/tests/` against the deployed endpoint.

## Deploying

The site in `api/` deploys to Netlify. `api/netlify.toml` copies `../json` into the function bundle at build time and routes `/api/graphql` to the function.

## Support

For bugs or questions, [open an issue](https://github.com/robertrouse/theographic-bible-metadata/issues).
