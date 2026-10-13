# Theographic Bible Metadata GraphQL API

This directory contains the GraphQL API for Theographic Bible Metadata. It is a Netlify function that serves the JSON files in `../json`.

**Live endpoint:** `https://theographic-api.netlify.app/api/graphql`

## Structure

- `netlify/functions/graphql.js`: schema, resolvers, and the serverless handler
- `netlify.toml`: build configuration (copies `../json` into the function bundle) and the `/api/graphql` route
- `tests/graphql.test.js`: tests that run against the deployed endpoint

## Development

1. Install dependencies: `npm install`
2. Start the local server: `npm start`
3. Open `http://localhost:8888/api/graphql` for the Apollo Sandbox explorer
4. Run the tests: `npm test`

## Documentation

See [`../docs/api-documentation.md`](../docs/api-documentation.md).
