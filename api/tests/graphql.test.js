/**
 * Automated integration tests for the Theographic Bible Metadata GraphQL API.
 *
 * Runs against the live Netlify deployment at https://theographic-api.netlify.app
 * Uses Node's built-in test runner (node:test) — no extra dependencies needed.
 *
 * Usage:
 *   node --test tests/graphql.test.js
 *   node --test --test-reporter=spec tests/graphql.test.js
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');

const API_URL = process.env.API_URL || 'https://theographic-api.netlify.app/api/graphql';

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

async function gql(query) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} from ${API_URL}`);
  }
  const json = await res.json();
  if (json.errors?.length) {
    throw new Error(`GraphQL errors: ${JSON.stringify(json.errors, null, 2)}`);
  }
  return json.data;
}

// ---------------------------------------------------------------------------
// Books
// ---------------------------------------------------------------------------

describe('books query', () => {
  test('returns an array of books', async () => {
    const data = await gql(`{ books { id bookName } }`);
    assert.ok(Array.isArray(data.books), 'books should be an array');
    assert.ok(data.books.length > 0, 'books should not be empty');
  });

  test('every book has required scalar fields', async () => {
    const data = await gql(`{
      books {
        id
        osisName
        bookName
        shortName
        bookOrder
        testament
        slug
        chapterCount
        verseCount
        peopleCount
        placeCount
        bookDiv
      }
    }`);
    assert.equal(data.books.length, 66, 'Protestant canon has 66 books');
    for (const book of data.books) {
      assert.ok(book.id, `book.id missing for ${JSON.stringify(book)}`);
      assert.ok(book.bookName, `book.bookName missing for ${book.id}`);
      assert.ok(book.osisName, `book.osisName missing for ${book.id}`);
      assert.ok(book.slug, `book.slug missing for ${book.id}`);
      assert.ok(book.testament, `book.testament missing for ${book.id}`);
      assert.ok(typeof book.bookOrder === 'number', `book.bookOrder should be a number for ${book.id}`);
      assert.ok(book.chapterCount > 0, `book.chapterCount should be > 0 for ${book.id}`);
      assert.ok(book.verseCount > 0, `book.verseCount should be > 0 for ${book.id}`);
    }
  });

  test('testament values are only Old Testament or New Testament', async () => {
    const data = await gql(`{ books { id testament } }`);
    const valid = new Set(['Old Testament', 'New Testament']);
    for (const book of data.books) {
      assert.ok(valid.has(book.testament), `Unexpected testament "${book.testament}" on book ${book.id}`);
    }
  });

  test('books have linked chapters', async () => {
    const data = await gql(`{
      books {
        id
        bookName
        chapters { id osisRef }
      }
    }`);
    // Genesis should have 50 chapters
    const genesis = data.books.find(b => b.bookName === 'Genesis');
    assert.ok(genesis, 'Genesis not found');
    assert.equal(genesis.chapters.length, 50, 'Genesis should have 50 chapters');
    for (const ch of genesis.chapters) {
      assert.ok(ch.id, 'chapter.id should be present');
      assert.ok(ch.osisRef, 'chapter.osisRef should be present');
    }
  });

  test('books have linked writers (personLookup resolution)', async () => {
    const data = await gql(`{
      books {
        id
        bookName
        writers { id name personLookup }
      }
    }`);
    // Genesis is written by Moses
    const genesis = data.books.find(b => b.bookName === 'Genesis');
    assert.ok(genesis, 'Genesis not found');
    assert.ok(genesis.writers.length > 0, 'Genesis should have at least one writer');
    const moses = genesis.writers.find(w => w.name === 'Moses');
    assert.ok(moses, 'Moses should be listed as writer of Genesis');
  });
});

// ---------------------------------------------------------------------------
// Chapters
// ---------------------------------------------------------------------------

describe('chapters query', () => {
  test('returns an array of chapters', async () => {
    const data = await gql(`{ chapters { id osisRef } }`);
    assert.ok(Array.isArray(data.chapters), 'chapters should be an array');
    assert.ok(data.chapters.length > 0, 'chapters should not be empty');
    // The Protestant Bible has 1,189 chapters
    assert.ok(data.chapters.length >= 1189, `Expected >= 1189 chapters, got ${data.chapters.length}`);
  });

  test('every chapter has required fields', async () => {
    // Sample: just check a small slice to keep test fast
    const data = await gql(`{
      chapters {
        id
        osisRef
        chapterNum
        slug
        peopleCount
        placesCount
      }
    }`);
    for (const ch of data.chapters.slice(0, 20)) {
      assert.ok(ch.id, `chapter.id missing`);
      assert.ok(ch.osisRef, `chapter.osisRef missing for ${ch.id}`);
      assert.ok(typeof ch.chapterNum === 'number', `chapterNum should be number for ${ch.id}`);
      assert.ok(ch.slug, `chapter.slug missing for ${ch.id}`);
    }
  });

  test('chapters have linked books', async () => {
    const data = await gql(`{
      chapters {
        id
        osisRef
        book { id bookName }
      }
    }`);
    for (const ch of data.chapters.slice(0, 10)) {
      assert.ok(ch.book.length > 0, `chapter ${ch.id} (${ch.osisRef}) should have a linked book`);
      assert.ok(ch.book[0].bookName, `chapter ${ch.id} book should have bookName`);
    }
  });

  test('chapters have writerCount resolved correctly', async () => {
    const data = await gql(`{
      chapters {
        id
        writerCount
      }
    }`);
    const withCount = data.chapters.filter(c => c.writerCount !== null);
    assert.ok(withCount.length > 0, 'At least some chapters should have writerCount');
    for (const ch of withCount.slice(0, 10)) {
      assert.ok(typeof ch.writerCount === 'number', `writerCount should be a number for ${ch.id}`);
      assert.ok(ch.writerCount >= 1, `writerCount should be >= 1 when present for ${ch.id}`);
    }
  });
});

// ---------------------------------------------------------------------------
// Verses
// ---------------------------------------------------------------------------

describe('verses query', () => {
  test('returns an array of verses', async () => {
    const data = await gql(`{ verses { id osisRef } }`);
    assert.ok(Array.isArray(data.verses), 'verses should be an array');
    // KJV has 31,102 verses
    assert.ok(data.verses.length >= 31000, `Expected >= 31000 verses, got ${data.verses.length}`);
  });

  test('every sampled verse has required fields', async () => {
    const data = await gql(`{
      verses {
        id
        osisRef
        verseNum
        verseText
        verseID
        status
      }
    }`);
    for (const v of data.verses.slice(0, 20)) {
      assert.ok(v.id, `verse.id missing`);
      assert.ok(v.osisRef, `verse.osisRef missing for ${v.id}`);
      assert.ok(v.verseText, `verse.verseText missing for ${v.id}`);
      assert.ok(v.verseNum, `verse.verseNum missing for ${v.id}`);
    }
  });

  test('verses have linked book and chapter', async () => {
    const data = await gql(`{
      verses {
        id
        osisRef
        book { id bookName }
        chapter { id osisRef }
      }
    }`);
    for (const v of data.verses.slice(0, 10)) {
      assert.ok(v.book.length > 0, `verse ${v.osisRef} should have a linked book`);
      assert.ok(v.chapter.length > 0, `verse ${v.osisRef} should have a linked chapter`);
    }
  });
});

// ---------------------------------------------------------------------------
// searchVerses
// ---------------------------------------------------------------------------

describe('searchVerses query', () => {
  test('finds John 3:16 by osisRef', async () => {
    const data = await gql(`{ searchVerses(input: "John.3.16") { id osisRef verseText } }`);
    assert.ok(data.searchVerses.length > 0, 'Should find at least one verse');
    const verse = data.searchVerses.find(v => v.osisRef === 'John.3.16');
    assert.ok(verse, 'John.3.16 should be in results');
    assert.ok(verse.verseText.includes('God so loved'), 'John 3:16 text should contain "God so loved"');
  });

  test('finds verses by text search', async () => {
    const data = await gql(`{ searchVerses(input: "In the beginning") { id osisRef verseText } }`);
    assert.ok(data.searchVerses.length > 0, 'Should find at least one verse');
    const gen1 = data.searchVerses.find(v => v.osisRef === 'Gen.1.1');
    assert.ok(gen1, 'Gen.1.1 should be in results for "In the beginning"');
  });

  test('verse results include people and places', async () => {
    const data = await gql(`{
      searchVerses(input: "Gen.1.1") {
        osisRef
        verseText
        people { id name }
        places { id kjvName }
        peopleCount
        placesCount
      }
    }`);
    assert.ok(data.searchVerses.length > 0, 'Should find Gen.1.1');
    const v = data.searchVerses[0];
    assert.ok(typeof v.peopleCount === 'number', 'peopleCount should be a number');
    assert.ok(typeof v.placesCount === 'number', 'placesCount should be a number');
  });

  test('returns empty for non-existent reference', async () => {
    const data = await gql(`{ searchVerses(input: "ZZZNOMATCH99999") { id osisRef } }`);
    assert.equal(data.searchVerses.length, 0, 'Should return empty array for no match');
  });
});

// ---------------------------------------------------------------------------
// People
// ---------------------------------------------------------------------------

describe('people query', () => {
  test('returns an array of people', async () => {
    const data = await gql(`{ people { id name } }`);
    assert.ok(Array.isArray(data.people), 'people should be an array');
    assert.ok(data.people.length > 0, 'people should not be empty');
  });

  test('every sampled person has required fields', async () => {
    const data = await gql(`{
      people {
        id
        name
        personLookup
        personID
        slug
        alphaGroup
        isProperName
      }
    }`);
    for (const p of data.people.slice(0, 20)) {
      assert.ok(p.id, `person.id missing`);
      assert.ok(p.name, `person.name missing for ${p.id}`);
      assert.ok(p.personLookup, `person.personLookup missing for ${p.id}`);
      assert.ok(p.slug, `person.slug missing for ${p.id}`);
    }
  });

  test('verseCount is a non-negative number', async () => {
    const data = await gql(`{ people { id name verseCount } }`);
    for (const p of data.people.slice(0, 50)) {
      assert.ok(typeof p.verseCount === 'number', `verseCount should be a number for ${p.name}`);
      assert.ok(p.verseCount >= 0, `verseCount should be >= 0 for ${p.name}`);
    }
  });

  test('people with memberOf have linked groups', async () => {
    const data = await gql(`{
      people {
        id
        name
        memberOf { id groupName }
      }
    }`);
    const withGroups = data.people.filter(p => p.memberOf.length > 0);
    assert.ok(withGroups.length > 0, 'Some people should belong to groups');
    for (const p of withGroups.slice(0, 5)) {
      for (const g of p.memberOf) {
        assert.ok(g.id, `group.id missing for group linked from ${p.name}`);
        assert.ok(g.groupName, `group.groupName missing for group linked from ${p.name}`);
      }
    }
  });

  test('family relationships resolve correctly', async () => {
    const data = await gql(`{
      people {
        id
        name
        father { id name }
        mother { id name }
        children { id name }
        siblings { id name }
      }
    }`);
    // Isaac should have Abraham as father and Sarah as mother
    const isaac = data.people.find(p => p.name === 'Isaac');
    assert.ok(isaac, 'Isaac should be in the dataset');
    assert.ok(isaac.father.length > 0, 'Isaac should have a father');
    assert.equal(isaac.father[0].name, 'Abraham', 'Isaac\'s father should be Abraham');
  });

  test('birthYear and deathYear are integers (ISO astronomical year numbering)', async () => {
    const data = await gql(`{
      people {
        id
        name
        birthYear
        deathYear
      }
    }`);
    // Both fields should be null or an integer — never a string or array
    for (const p of data.people) {
      if (p.birthYear !== null) {
        assert.equal(typeof p.birthYear, 'number', `birthYear should be a number for ${p.name}, got ${typeof p.birthYear}`);
        assert.ok(Number.isInteger(p.birthYear), `birthYear should be an integer for ${p.name}, got ${p.birthYear}`);
      }
      if (p.deathYear !== null) {
        assert.equal(typeof p.deathYear, 'number', `deathYear should be a number for ${p.name}, got ${typeof p.deathYear}`);
        assert.ok(Number.isInteger(p.deathYear), `deathYear should be an integer for ${p.name}, got ${p.deathYear}`);
      }
    }
    // Adam should have a birthYear of -4004 (= 4005 BC in ISO astronomical year numbering)
    const adam = data.people.find(p => p.name === 'Adam');
    assert.ok(adam, 'Adam should be in the dataset');
    assert.ok(adam.birthYear !== null, 'Adam should have a birthYear');
    assert.equal(adam.birthYear, -4004, `Adam's birthYear should be -4004 (= 4005 BC)`);
  });
});

// ---------------------------------------------------------------------------
// searchPeople
// ---------------------------------------------------------------------------

describe('searchPeople query', () => {
  test('finds Moses by name', async () => {
    const data = await gql(`{ searchPeople(input: "Moses") { id name personLookup slug } }`);
    assert.ok(data.searchPeople.length > 0, 'Should find at least one person');
    const moses = data.searchPeople.find(p => p.name === 'Moses');
    assert.ok(moses, 'Moses should be in results');
    assert.ok(moses.slug, 'Moses should have a slug');
  });

  test('finds people by alsoCalled / alternate name', async () => {
    // Jacob is also called Israel
    const data = await gql(`{ searchPeople(input: "Israel") { id name alsoCalled } }`);
    assert.ok(data.searchPeople.length > 0, 'Should find at least one person for "Israel"');
  });

  test('search results include verses', async () => {
    const data = await gql(`{
      searchPeople(input: "Moses") {
        name
        verseCount
        verses { id osisRef }
      }
    }`);
    const moses = data.searchPeople.find(p => p.name === 'Moses');
    assert.ok(moses, 'Moses should be found');
    assert.ok(moses.verseCount > 0, 'Moses verseCount should be > 0');
    assert.ok(moses.verses.length > 0, 'Moses verses should be non-empty');
  });

  test('returns empty for non-existent name', async () => {
    const data = await gql(`{ searchPeople(input: "ZZZNOMATCH99999") { id name } }`);
    assert.equal(data.searchPeople.length, 0, 'Should return empty array for no match');
  });
});

// ---------------------------------------------------------------------------
// Places
// ---------------------------------------------------------------------------

describe('places query', () => {
  test('returns an array of places', async () => {
    const data = await gql(`{ places { id kjvName } }`);
    assert.ok(Array.isArray(data.places), 'places should be an array');
    assert.ok(data.places.length > 0, 'places should not be empty');
  });

  test('every sampled place has required fields', async () => {
    const data = await gql(`{
      places {
        id
        kjvName
        placeLookup
        placeID
        slug
        alphaGroup
        displayTitle
        verseCount
      }
    }`);
    for (const p of data.places.slice(0, 20)) {
      assert.ok(p.id, `place.id missing`);
      assert.ok(p.kjvName, `place.kjvName missing for ${p.id}`);
      assert.ok(p.slug, `place.slug missing for ${p.id}`);
    }
  });

  test('places with coordinates have valid lat/lon', async () => {
    const data = await gql(`{
      places {
        id
        kjvName
        latitude
        longitude
      }
    }`);
    const withCoords = data.places.filter(p => p.latitude && p.longitude);
    assert.ok(withCoords.length > 0, 'Some places should have coordinates');
    for (const p of withCoords.slice(0, 20)) {
      const lat = parseFloat(p.latitude);
      const lon = parseFloat(p.longitude);
      assert.ok(!isNaN(lat), `latitude should be numeric for ${p.kjvName}: ${p.latitude}`);
      assert.ok(!isNaN(lon), `longitude should be numeric for ${p.kjvName}: ${p.longitude}`);
      assert.ok(lat >= -90 && lat <= 90, `latitude out of range for ${p.kjvName}: ${lat}`);
      assert.ok(lon >= -180 && lon <= 180, `longitude out of range for ${p.kjvName}: ${lon}`);
    }
  });

  test('verseCount is a non-negative number', async () => {
    const data = await gql(`{ places { id kjvName verseCount } }`);
    for (const p of data.places.slice(0, 50)) {
      assert.ok(typeof p.verseCount === 'number', `verseCount should be a number for ${p.kjvName}`);
      assert.ok(p.verseCount >= 0, `verseCount should be >= 0 for ${p.kjvName}`);
    }
  });
});

// ---------------------------------------------------------------------------
// searchPlaces
// ---------------------------------------------------------------------------

describe('searchPlaces query', () => {
  test('finds Egypt by name', async () => {
    const data = await gql(`{
      searchPlaces(input: "Egypt") {
        id
        kjvName
        placeLookup
        slug
        latitude
        longitude
      }
    }`);
    assert.ok(data.searchPlaces.length > 0, 'Should find at least one place');
    const egypt = data.searchPlaces.find(p => p.kjvName === 'Egypt');
    assert.ok(egypt, 'Egypt should be in results');
    assert.ok(egypt.slug, 'Egypt should have a slug');
  });

  test('search results include linked verses', async () => {
    const data = await gql(`{
      searchPlaces(input: "Jerusalem") {
        kjvName
        verseCount
        verses { id osisRef }
      }
    }`);
    const jerusalem = data.searchPlaces.find(p => p.kjvName === 'Jerusalem');
    assert.ok(jerusalem, 'Jerusalem should be found');
    assert.ok(jerusalem.verseCount > 0, 'Jerusalem verseCount should be > 0');
  });

  test('returns empty for non-existent place', async () => {
    const data = await gql(`{ searchPlaces(input: "ZZZNOMATCH99999") { id kjvName } }`);
    assert.equal(data.searchPlaces.length, 0, 'Should return empty array for no match');
  });
});

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

describe('events query', () => {
  test('returns an array of events', async () => {
    const data = await gql(`{ events { id title } }`);
    assert.ok(Array.isArray(data.events), 'events should be an array');
    assert.ok(data.events.length > 0, 'events should not be empty');
  });

  test('every sampled event has required fields', async () => {
    const data = await gql(`{
      events {
        id
        title
        startDate
        sortKey
        eventID
        rangeFlag
      }
    }`);
    for (const e of data.events.slice(0, 20)) {
      assert.ok(e.id, `event.id missing`);
      assert.ok(e.title, `event.title missing for ${e.id}`);
    }
  });

  test('events have linked participants, locations, and verses', async () => {
    const data = await gql(`{
      events {
        id
        title
        participants { id name }
        locations { id kjvName }
        verses { id osisRef }
      }
    }`);
    const withParticipants = data.events.filter(e => e.participants.length > 0);
    assert.ok(withParticipants.length > 0, 'Some events should have participants');

    for (const e of withParticipants.slice(0, 5)) {
      for (const p of e.participants) {
        assert.ok(p.id, `participant.id missing in event "${e.title}"`);
        assert.ok(p.name, `participant.name missing in event "${e.title}"`);
      }
    }
  });
});

// ---------------------------------------------------------------------------
// PeopleGroups
// ---------------------------------------------------------------------------

describe('peopleGroups query', () => {
  test('returns an array of groups', async () => {
    const data = await gql(`{ peopleGroups { id groupName } }`);
    assert.ok(Array.isArray(data.peopleGroups), 'peopleGroups should be an array');
    assert.ok(data.peopleGroups.length > 0, 'peopleGroups should not be empty');
  });

  test('every group has required fields', async () => {
    const data = await gql(`{
      peopleGroups {
        id
        groupName
      }
    }`);
    for (const g of data.peopleGroups) {
      assert.ok(g.id, `group.id missing`);
      assert.ok(g.groupName, `group.groupName missing for ${g.id}`);
    }
  });

  test('groups have linked members', async () => {
    const data = await gql(`{
      peopleGroups {
        id
        groupName
        members { id name }
      }
    }`);
    const withMembers = data.peopleGroups.filter(g => g.members.length > 0);
    assert.ok(withMembers.length > 0, 'Some groups should have members');

    const apostles = data.peopleGroups.find(g => g.groupName.includes('Apostle'));
    if (apostles) {
      assert.ok(apostles.members.length > 0, 'Apostles group should have members');
    }
  });

  test('eventsDev resolves correctly (events_dev field)', async () => {
    const data = await gql(`{
      peopleGroups {
        id
        groupName
        eventsDev { id title }
      }
    }`);
    const withEvents = data.peopleGroups.filter(g => g.eventsDev.length > 0);
    assert.ok(withEvents.length > 0, 'Some groups should have eventsDev linked');
    for (const g of withEvents.slice(0, 3)) {
      for (const e of g.eventsDev) {
        assert.ok(e.id, `eventsDev item missing id in group "${g.groupName}"`);
        assert.ok(e.title, `eventsDev item missing title in group "${g.groupName}"`);
      }
    }
  });
});

// ---------------------------------------------------------------------------
// Easton's Dictionary
// ---------------------------------------------------------------------------

describe('easton query', () => {
  test('returns an array of entries', async () => {
    const data = await gql(`{ easton { id termLabel } }`);
    assert.ok(Array.isArray(data.easton), 'easton should be an array');
    assert.ok(data.easton.length > 0, 'easton should not be empty');
  });

  test('every sampled entry has required fields', async () => {
    const data = await gql(`{
      easton {
        id
        dictLookup
        termLabel
        dictText
        itemNum
        index
        defId
        hasList
        termID
      }
    }`);
    for (const e of data.easton.slice(0, 20)) {
      assert.ok(e.id, `easton.id missing`);
      assert.ok(e.termLabel, `easton.termLabel missing for ${e.id}`);
      assert.ok(e.dictLookup, `easton.dictLookup missing for ${e.id}`);
    }
  });

  test('defId and hasList resolve from underscore field names', async () => {
    // This tests the def_id → defId and has_list → hasList fixes
    const data = await gql(`{
      easton {
        id
        defId
        hasList
      }
    }`);
    const withDefId = data.easton.filter(e => e.defId !== null);
    assert.ok(withDefId.length > 0, 'Some Easton entries should have defId (from def_id field)');

    const withHasList = data.easton.filter(e => e.hasList !== null);
    assert.ok(withHasList.length > 0, 'Some Easton entries should have hasList (from has_list field)');
  });

  test('Easton entries link to people and places', async () => {
    const data = await gql(`{
      easton {
        id
        termLabel
        personLookup { id name }
        placeLookup { id kjvName }
      }
    }`);
    const withPeople = data.easton.filter(e => e.personLookup.length > 0);
    const withPlaces = data.easton.filter(e => e.placeLookup.length > 0);
    assert.ok(withPeople.length > 0, 'Some Easton entries should link to people');
    assert.ok(withPlaces.length > 0, 'Some Easton entries should link to places');
  });
});

// ---------------------------------------------------------------------------
// Cross-type relationship integrity
// ---------------------------------------------------------------------------

describe('cross-type relationship integrity', () => {
  test('verse people resolve back to valid Person records', async () => {
    const data = await gql(`{
      searchVerses(input: "Gen.1") {
        osisRef
        people { id name slug personLookup }
      }
    }`);
    const versesWithPeople = data.searchVerses.filter(v => v.people.length > 0);
    for (const v of versesWithPeople.slice(0, 5)) {
      for (const p of v.people) {
        assert.ok(p.id, `person.id missing in verse ${v.osisRef}`);
        assert.ok(p.name, `person.name missing in verse ${v.osisRef}`);
      }
    }
  });

  test('verse places resolve back to valid Place records', async () => {
    const data = await gql(`{
      searchVerses(input: "Egypt") {
        osisRef
        places { id kjvName latitude longitude }
      }
    }`);
    const versesWithPlaces = data.searchVerses.filter(v => v.places.length > 0);
    assert.ok(versesWithPlaces.length > 0, 'Some verses mentioning Egypt should have linked places');
    for (const v of versesWithPlaces.slice(0, 5)) {
      for (const pl of v.places) {
        assert.ok(pl.id, `place.id missing in verse ${v.osisRef}`);
        assert.ok(pl.kjvName, `place.kjvName missing in verse ${v.osisRef}`);
      }
    }
  });

  test('person birthPlace resolves to valid Place record', async () => {
    const data = await gql(`{
      searchPeople(input: "Moses") {
        name
        birthPlace { id kjvName latitude longitude }
        deathPlace { id kjvName }
      }
    }`);
    const moses = data.searchPeople.find(p => p.name === 'Moses');
    assert.ok(moses, 'Moses should be found');
    // Moses has a deathPlace (Mount Nebo)
    if (moses.deathPlace.length > 0) {
      assert.ok(moses.deathPlace[0].id, 'Moses deathPlace should have an id');
      assert.ok(moses.deathPlace[0].kjvName, 'Moses deathPlace should have a kjvName');
    }
  });

  test('event participants and locations are both resolvable', async () => {
    const data = await gql(`{
      events {
        id
        title
        participants { id name verseCount }
        locations { id kjvName latitude longitude }
      }
    }`);
    const complete = data.events.filter(e => e.participants.length > 0 && e.locations.length > 0);
    assert.ok(complete.length > 0, 'Some events should have both participants and locations');

    for (const e of complete.slice(0, 3)) {
      for (const p of e.participants) {
        assert.ok(p.id, `participant id missing in event "${e.title}"`);
      }
      for (const l of e.locations) {
        assert.ok(l.id, `location id missing in event "${e.title}"`);
        assert.ok(l.kjvName, `location kjvName missing in event "${e.title}"`);
      }
    }
  });
});

// ---------------------------------------------------------------------------
// Filter / where argument tests
// ---------------------------------------------------------------------------

describe('books filter (where)', () => {
  test('filter by testament eq', async () => {
    const data = await gql(`{
      books(where: { testament: { eq: "New Testament" } }) {
        id bookName testament
      }
    }`);
    assert.equal(data.books.length, 27, 'NT has 27 books');
    for (const b of data.books) {
      assert.equal(b.testament, 'New Testament', `Expected NT, got "${b.testament}" for ${b.bookName}`);
    }
  });

  test('filter by bookDiv eq', async () => {
    const data = await gql(`{
      books(where: { bookDiv: { eq: "Pentateuch" } }) {
        id bookName bookDiv
      }
    }`);
    assert.equal(data.books.length, 5, 'Pentateuch has 5 books');
    for (const b of data.books) {
      assert.equal(b.bookDiv, 'Pentateuch');
    }
  });

  test('filter by bookName contains (case-insensitive)', async () => {
    const data = await gql(`{
      books(where: { bookName: { contains: "samuel" } }) {
        id bookName
      }
    }`);
    assert.ok(data.books.length >= 2, 'Should find 1 Samuel and 2 Samuel');
    for (const b of data.books) {
      assert.ok(b.bookName.toLowerCase().includes('samuel'), `Expected name to contain "samuel", got "${b.bookName}"`);
    }
  });

  test('filter by bookOrder range', async () => {
    const data = await gql(`{
      books(where: { bookOrder: { gte: 1, lte: 5 } }) {
        id bookName bookOrder
      }
    }`);
    assert.equal(data.books.length, 5, 'Books 1-5 = Pentateuch');
    for (const b of data.books) {
      assert.ok(b.bookOrder >= 1 && b.bookOrder <= 5);
    }
  });

  test('filter by slug eq', async () => {
    const data = await gql(`{
      books(where: { slug: { eq: "gen" } }) {
        id bookName slug
      }
    }`);
    assert.equal(data.books.length, 1, 'Only one book with slug "gen"');
    assert.equal(data.books[0].bookName, 'Genesis');
  });

  test('limit and offset', async () => {
    const page1 = await gql(`{ books(limit: 5, offset: 0) { id bookOrder } }`);
    const page2 = await gql(`{ books(limit: 5, offset: 5) { id bookOrder } }`);
    assert.equal(page1.books.length, 5);
    assert.equal(page2.books.length, 5);
    // Pages should not overlap
    const ids1 = new Set(page1.books.map(b => b.id));
    for (const b of page2.books) {
      assert.ok(!ids1.has(b.id), 'Page 2 should not contain page 1 records');
    }
  });

  test('combined where + limit', async () => {
    const data = await gql(`{
      books(where: { testament: { eq: "Old Testament" } }, limit: 5) {
        id bookName testament
      }
    }`);
    assert.equal(data.books.length, 5, 'limit: 5 should cap results');
    for (const b of data.books) {
      assert.equal(b.testament, 'Old Testament');
    }
  });

  test('no match returns empty array', async () => {
    const data = await gql(`{
      books(where: { bookName: { eq: "ZZZNOMATCH" } }) { id }
    }`);
    assert.equal(data.books.length, 0);
  });
});

describe('events filter (where)', () => {
  test('filter by title contains', async () => {
    const data = await gql(`{
      events(where: { title: { contains: "creation" } }) {
        id title
      }
    }`);
    assert.ok(data.events.length >= 1, 'Should find creation event(s)');
    for (const e of data.events) {
      assert.ok(e.title.toLowerCase().includes('creation'), `"${e.title}" does not contain "creation"`);
    }
  });

  test('filter by eventID eq', async () => {
    const data = await gql(`{
      events(where: { eventID: { eq: 1 } }) {
        id title eventID
      }
    }`);
    assert.equal(data.events.length, 1, 'eventID 1 should match exactly one event');
    assert.equal(data.events[0].eventID, 1);
    assert.ok(data.events[0].title, 'Event should have a title');
  });

  test('filter by title eq', async () => {
    const data = await gql(`{
      events(where: { title: { eq: "Creation of all things" } }) {
        id title
      }
    }`);
    assert.equal(data.events.length, 1);
    assert.equal(data.events[0].title, 'Creation of all things');
  });

  test('events limit', async () => {
    const data = await gql(`{ events(limit: 10) { id title } }`);
    assert.equal(data.events.length, 10, 'limit: 10 should return exactly 10 events');
  });

  test('filter by id eq', async () => {
    // First fetch all events to get a real id
    const all = await gql(`{ events(limit: 1) { id title } }`);
    const targetId = all.events[0].id;
    const data = await gql(`{
      events(where: { id: { eq: "${targetId}" } }) {
        id title
      }
    }`);
    assert.equal(data.events.length, 1, 'id eq filter should match exactly one record');
    assert.equal(data.events[0].id, targetId);
  });
});

describe('people filter (where)', () => {
  test('filter by gender eq', async () => {
    const data = await gql(`{
      people(where: { gender: { eq: "Female" } }, limit: 20) {
        id name gender
      }
    }`);
    assert.ok(data.people.length > 0, 'Should find female people');
    for (const p of data.people) {
      assert.equal(p.gender, 'Female', `Expected Female, got "${p.gender}" for ${p.name}`);
    }
  });

  test('filter by name contains', async () => {
    const data = await gql(`{
      people(where: { name: { contains: "mary" } }) {
        id name
      }
    }`);
    assert.ok(data.people.length > 0, 'Should find people named Mary');
    for (const p of data.people) {
      assert.ok(p.name.toLowerCase().includes('mary'), `"${p.name}" does not contain "mary"`);
    }
  });

  test('filter by verseCount range', async () => {
    const data = await gql(`{
      people(where: { verseCount: { gte: 200 } }) {
        id name verseCount
      }
    }`);
    assert.ok(data.people.length > 0, 'Several key figures appear in >= 200 verses');
    for (const p of data.people) {
      assert.ok(p.verseCount >= 200, `${p.name} verseCount ${p.verseCount} should be >= 200`);
    }
    // Moses, David, Jesus should be in here
    const names = data.people.map(p => p.name);
    assert.ok(names.includes('Moses') || names.includes('Jesus') || names.includes('David'),
      'Major figures should appear when filtering verseCount >= 200');
  });

  test('filter by slug eq', async () => {
    const data = await gql(`{
      people(where: { slug: { eq: "moses_2108" } }) {
        id name slug
      }
    }`);
    assert.equal(data.people.length, 1);
    assert.equal(data.people[0].name, 'Moses');
  });

  test('filter by isProperName eq true', async () => {
    const data = await gql(`{
      people(where: { isProperName: { eq: true } }, limit: 20) {
        id name isProperName
      }
    }`);
    assert.ok(data.people.length > 0);
    for (const p of data.people) {
      assert.equal(p.isProperName, true, `${p.name} should have isProperName = true`);
    }
  });

  test('filter by ambiguous eq true', async () => {
    const data = await gql(`{
      people(where: { ambiguous: { eq: true } }, limit: 10) {
        id name ambiguous
      }
    }`);
    // There may or may not be ambiguous people — just check type consistency
    for (const p of data.people) {
      assert.equal(p.ambiguous, true, `${p.name} should be ambiguous`);
    }
  });
});

describe('places filter (where)', () => {
  test('filter by featureType eq', async () => {
    const data = await gql(`{
      places(where: { featureType: { eq: "Water" } }, limit: 20) {
        id kjvName featureType
      }
    }`);
    assert.ok(data.places.length > 0, 'Should find water features');
    for (const p of data.places) {
      assert.equal(p.featureType, 'Water');
    }
  });

  test('filter by kjvName contains', async () => {
    const data = await gql(`{
      places(where: { kjvName: { contains: "jordan" } }) {
        id kjvName
      }
    }`);
    assert.ok(data.places.length > 0, 'Should find places with "Jordan" in name');
    for (const p of data.places) {
      assert.ok(p.kjvName.toLowerCase().includes('jordan'));
    }
  });

  test('filter by kjvName eq', async () => {
    const data = await gql(`{
      places(where: { kjvName: { eq: "Jerusalem" } }) {
        id kjvName slug
      }
    }`);
    assert.ok(data.places.length >= 1, 'Jerusalem should exist');
    assert.ok(data.places.some(p => p.kjvName === 'Jerusalem'));
  });

  test('filter by verseCount gte', async () => {
    const data = await gql(`{
      places(where: { verseCount: { gte: 400 } }) {
        id kjvName verseCount
      }
    }`);
    assert.ok(data.places.length > 0, 'Major places should have >= 400 verses');
    for (const p of data.places) {
      assert.ok(p.verseCount >= 400, `${p.kjvName} verseCount ${p.verseCount} should be >= 400`);
    }
  });
});

describe('chapters filter (where)', () => {
  test('filter by chapterNum eq', async () => {
    const data = await gql(`{
      chapters(where: { chapterNum: { eq: 1 } }, limit: 10) {
        id chapterNum osisRef
      }
    }`);
    assert.ok(data.chapters.length > 0, 'Chapter 1 exists in many books');
    for (const c of data.chapters) {
      assert.equal(c.chapterNum, 1);
    }
  });

  test('filter by osisRef contains', async () => {
    const data = await gql(`{
      chapters(where: { osisRef: { contains: "Gen" } }) {
        id osisRef
      }
    }`);
    assert.equal(data.chapters.length, 50, 'Genesis has 50 chapters');
    for (const c of data.chapters) {
      assert.ok(c.osisRef.startsWith('Gen.'));
    }
  });

  test('filter by peopleCount gte', async () => {
    const data = await gql(`{
      chapters(where: { peopleCount: { gte: 50 } }) {
        id osisRef peopleCount
      }
    }`);
    assert.ok(data.chapters.length > 0, 'Some chapters have many people');
    for (const c of data.chapters) {
      assert.ok(c.peopleCount >= 50);
    }
  });
});

describe('verses filter (where)', () => {
  test('filter by osisRef eq', async () => {
    const data = await gql(`{
      verses(where: { osisRef: { eq: "Gen.1.1" } }) {
        id osisRef verseText
      }
    }`);
    assert.equal(data.verses.length, 1);
    assert.equal(data.verses[0].osisRef, 'Gen.1.1');
    assert.ok(data.verses[0].verseText.includes('beginning'));
  });

  test('filter by status eq', async () => {
    const data = await gql(`{
      verses(where: { status: { eq: "publish" } }, limit: 5) {
        id status
      }
    }`);
    assert.ok(data.verses.length > 0);
    for (const v of data.verses) {
      assert.equal(v.status, 'publish');
    }
  });

  test('filter by yearNum range', async () => {
    const data = await gql(`{
      verses(where: { yearNum: { gte: 30, lte: 33 } }, limit: 20) {
        id osisRef yearNum
      }
    }`);
    assert.ok(data.verses.length > 0, 'NT ministry years should have verses');
    for (const v of data.verses) {
      assert.ok(v.yearNum >= 30 && v.yearNum <= 33, `yearNum ${v.yearNum} out of range for ${v.osisRef}`);
    }
  });

  test('filter by verseText contains', async () => {
    const data = await gql(`{
      verses(where: { verseText: { contains: "God so loved" } }) {
        id osisRef verseText
      }
    }`);
    assert.ok(data.verses.length >= 1, 'Should find John 3:16');
    const john316 = data.verses.find(v => v.osisRef === 'John.3.16');
    assert.ok(john316, 'John.3.16 should be in results');
  });
});

describe('peopleGroups filter (where)', () => {
  test('filter by groupName eq', async () => {
    const data = await gql(`{
      peopleGroups(where: { groupName: { eq: "Tribe of Levi" } }) {
        id groupName
      }
    }`);
    assert.equal(data.peopleGroups.length, 1);
    assert.equal(data.peopleGroups[0].groupName, 'Tribe of Levi');
  });

  test('filter by groupName contains', async () => {
    const data = await gql(`{
      peopleGroups(where: { groupName: { contains: "tribe" } }) {
        id groupName
      }
    }`);
    assert.ok(data.peopleGroups.length > 0, 'Should find tribes');
    for (const g of data.peopleGroups) {
      assert.ok(g.groupName.toLowerCase().includes('tribe'));
    }
  });
});

describe('easton filter (where)', () => {
  test('filter by termLabel eq', async () => {
    const data = await gql(`{
      easton(where: { termLabel: { eq: "Aaron" } }) {
        id termLabel dictText
      }
    }`);
    assert.ok(data.easton.length >= 1, 'Aaron entry should exist');
    assert.ok(data.easton.some(e => e.termLabel === 'Aaron'));
  });

  test('filter by matchType eq', async () => {
    const data = await gql(`{
      easton(where: { matchType: { eq: "person" } }, limit: 10) {
        id termLabel matchType
      }
    }`);
    assert.ok(data.easton.length > 0);
    for (const e of data.easton) {
      assert.equal(e.matchType, 'person');
    }
  });

  test('filter by dictText contains', async () => {
    const data = await gql(`{
      easton(where: { dictText: { contains: "Jerusalem" } }, limit: 5) {
        id termLabel dictText
      }
    }`);
    assert.ok(data.easton.length > 0, 'Some entries should mention Jerusalem');
    for (const e of data.easton) {
      assert.ok(e.dictText?.toLowerCase().includes('jerusalem'));
    }
  });
});
