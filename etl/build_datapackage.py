#!/usr/bin/env python3
"""Build datapackage.json (Frictionless Data Package) for Theographic.

Field descriptions come from docs/json-fields-documentation.md, and field
names and types come from the CSV files themselves, so the package stays in
sync with each monthly export. Run from the repository root:

    python3 etl/build_datapackage.py
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "json-fields-documentation.md"
csv.field_size_limit(sys.maxsize)

# CSV file -> (resource name, docs section, title, description, primary key)
TABLES = [
    ("Books.csv", "books", "Books", "Books",
     "The 66 books of the Protestant canon: names, OSIS abbreviations, canonical divisions, writers, and chapter, verse, people, and place counts.", "osisName"),
    ("Chapters.csv", "chapters", "Chapters", "Chapters",
     "All 1,189 chapters, with their book, traditional writer, verses, and people and place counts.", "osisRef"),
    ("Verses.csv", "verses", "Verses", "Verses",
     "All 31,102 verses of the King James Version (1769 Cambridge Edition), with plain, Markdown, and rich text, and the people, places, people groups, and events each verse mentions.", "osisRef"),
    ("People.csv", "people", "People", "People",
     "Every individual named in the Bible (3,067 records), with family relationships, birth and death years and places, group membership, and the verses that mention them.", "personLookup"),
    ("PeopleGroups.csv", "people-groups", "PeopleGroups", "People groups",
     "Tribes, nations, and other collective groups, with their members, the verses that mention them, and their events.", "groupName"),
    ("Places.csv", "places", "Places", "Places",
     "Every biblical place record (1,298), with coordinates from OpenBible.info and Recogito, feature types, place-to-place relations, and the verses that mention them.", "placeLookup"),
    ("Events.csv", "events", "Events", "Events",
     "A timeline of 450 biblical events with dates, durations, predecessors, participants, locations, and verses. Old Testament and Gospel dates follow Floyd Nolen Jones; Acts dates follow Todd Atwood. Years are ISO 8601 astronomical years (-4003 = 4004 BC).", "eventID"),
    ("Easton.csv", "easton", "Easton", "Easton's Bible Dictionary",
     "Entries from Easton's Bible Dictionary (1897), parsed from the CCEL XML edition and linked to people and places.", "dictLookup"),
]

REPO = "https://github.com/robertrouse/theographic-bible-metadata/blob/master/"

# What each CSV link column holds. In the JSON these are arrays of record IDs;
# in the CSV they are comma-separated keys of the linked records.
KIND = {
    "person": "`personLookup` values",
    "place": "`placeLookup` values",
    "verse": "verse `osisRef` values",
    "chapter": "chapter `osisRef` values",
    "book": "book `osisName` values",
    "group": "`groupName` values",
    "event": "event titles",
    "easton": "`dictLookup` values",
}
CSV_LINKS = {
    "Books": {"placeWritten": ("Where the book was written", "place"),
              "chapters": ("The chapters in this book", "chapter"),
              "writers": ("The traditional writer(s) of the book", "person")},
    "Chapters": {"book": ("The book this chapter belongs to", "book"),
                 "writer": ("The traditional writer(s) of this chapter", "person"),
                 "verses": ("The verses in this chapter", "verse")},
    "Verses": {"book": ("The book this verse belongs to", "book"),
               "chapter": ("The chapter this verse belongs to", "chapter"),
               "people": ("People mentioned by name in this verse", "person"),
               "places": ("Places mentioned by name in this verse", "place"),
               "peopleGroups": ("People groups mentioned in this verse", "group"),
               "event": ("Events this verse belongs to", "event")},
    "People": {"birthPlace": ("Where the person was born", "place"),
               "deathPlace": ("Where the person died", "place"),
               "memberOf": ("Groups (tribes, families, etc.) the person belongs to", "group"),
               "eastons": ("Matching Easton's Bible Dictionary entries", "easton"),
               "verses": ("Every verse where this person is mentioned by name", "verse"),
               "mother": ("The person's mother", "person"),
               "father": ("The person's father", "person"),
               "partners": ("The person's spouse(s) or partner(s)", "person"),
               "children": ("The person's children", "person"),
               "siblings": ("The person's full siblings", "person"),
               "halfSiblingsSameMother": ("The person's maternal half-siblings", "person"),
               "halfSiblingsSameFather": ("The person's paternal half-siblings", "person"),
               "chaptersWritten": ("Chapters attributed to this person", "chapter")},
    "PeopleGroups": {"members": ("Members of this group", "person"),
                     "partOf": ("The parent group", "group"),
                     "verses": ("Verses where this group is mentioned", "verse"),
                     "events_dev": ("Events involving this group", "event")},
    "Places": {"canonicalPlace": ("The place this record is another name for (e.g. Salem -> Jerusalem); empty on canonical records", "place"),
               "otherNames": ("On a canonical record, the records that are other names of this place", "place"),
               "partOf": ("Places this place lies within: a city's tribal territory, a site's city, a city's Roman region, a territory's kingdom", "place"),
               "parts": ("On a containing place, the places whose `partOf` points to it", "place"),
               "near": ("Places this place lies beside or just outside (Gethsemane -> Jerusalem)", "place"),
               "nearby": ("The places whose `near` points to this place", "place"),
               "verses": ("Verses where this place is mentioned by name", "verse"),
               "eastons": ("Matching Easton's Bible Dictionary entries", "easton"),
               "peopleBorn": ("People born here", "person"),
               "peopleDied": ("People who died here", "person"),
               "booksWritten": ("Books written here", "book"),
               "eventsHere": ("Events that happened here", "event")},
    "Events": {"predecessor": ("The immediately preceding event in the timeline", "event"),
               "partOf": ("The parent event this event is part of", "event"),
               "verses": ("The verses that describe this event", "verse"),
               "participants": ("People who took part in the event", "person"),
               "locations": ("Where the event happened", "place"),
               "groups": ("People groups involved in the event", "group")},
    "Easton": {"personLookup": ("People this entry describes", "person"),
               "placeLookup": ("Places this entry describes", "place")},
}
# Other CSV-specific wording, where the CSV differs from the JSON docs.
CSV_TEXT = {
    "People": {
        "isProperName": "`checked` for people with proper names, blank for descriptive names like \"Wife of...\" or \"Son of...\"",
        "ambiguous": "`checked` for display titles that have not yet been edited for disambiguation, otherwise blank.",
        "birthYear": "Estimated birth year from Jones's chronology, as an ISO 8601 astronomical year (`-4003` = 4004 BC; positive values are AD). Same convention as `events.startDate`. Populated for 70 people.",
        "deathYear": "Estimated death year, in the same convention as `birthYear` (`-1014` = 1015 BC). Populated for 61 people.",
        "dictText": "Markdown-formatted text of the matching sub-section of Easton's Bible Dictionary.",
        "events": "Comma-separated titles of events the person took part in. Titles that contain commas are wrapped in double quotes.",
        "occupations": "Reserved for future use; currently empty on every record.",
        "eventGroups": "Reserved for future use; currently empty on every record.",
    },
    "Places": {
        "ambiguous": "`checked` for display titles that have not yet been edited for disambiguation, otherwise blank.",
        "dictText": "Markdown-formatted text of the matching sub-section of Easton's Bible Dictionary.",
    },
    "Easton": {
        "itemNum": "Item number for a definition that is one of several numbered meanings of the same word (1.0, 2.0, 3.0...); 0.0 for entries that are not itemized. Written with a decimal in the CSV.",
    },
    "Verses": {"verseNum": "Verse number within the chapter."},
    "Books": {"yearWritten": "Approximate year written, if known (e.g. `57` for Romans). Populated for 21 of 66 books."},
}
MODIFIED_UTC = "Last modified date and time in UTC, formatted `YYYY-MM-DD HH:MM` (e.g. `2026-10-23 04:46`)."
MODIFIED_EVENTS = "Last modified date and time in US Central time, formatted `MM/DD/YYYY h:mmam` (e.g. `10/22/2026 12:37am`). Note this differs from the UTC format used in the other CSV files."


def absolute_links(text):
    """Point relative doc links at GitHub so they work outside the repo."""
    def fix(m):
        target = m.group(2)
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            return m.group(0)
        path = target[3:] if target.startswith("../") else "docs/" + target
        return f"[{m.group(1)}]({REPO}{path})"
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", fix, text)


def example(col):
    for v in col:
        if v:
            first = next(csv.reader([v]))[0]
            return first
    return None

WORDINDEX_FIELDS = {
    "BookID": "Book number in canonical order (1 = Genesis).",
    "Chapter": "Chapter number.",
    "VerseNum": "Verse number within the chapter.",
    "VerseID": "Sequential verse number.",
    "Word": "The KJV word.",
    "Punc": "Punctuation following the word.",
    "Italic": "1 if the word is italicized in the KJV (supplied by the translators), else 0.",
    "Syllables": "Number of syllables in the word.",
    "YearNum": "Approximate year of the verse, ISO 8601 astronomical year (-4003 = 4004 BC).",
    "PersonID": "personID of the person this word refers to, or 0.",
    "PlaceID": "placeID of the place this word refers to, or 0.",
}


def parse_docs():
    """Return {section title: {field: (type, status, description)}}."""
    sections, current = {}, None
    for line in DOCS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\w+)", line)
        if m:
            current = m.group(1)
            sections.setdefault(current, {})
            continue
        m = re.match(r"^\|\s*`([^`]+)`(?:\s*,\s*`[^`]+`)*\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*(.*)\|\s*$", line)
        if m and current:
            name, typ, status, desc = (s.strip() for s in m.groups())
            sections[current][name] = (typ, status, desc)
    return sections


def infer_type(values):
    vals = [v for v in values if v != ""]
    if not vals:
        return "string"
    if all(re.fullmatch(r"-?\d+", v) for v in vals):
        return "integer"
    if all(re.fullmatch(r"-?\d+(\.\d+)?", v) for v in vals):
        return "number"
    return "string"


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def table_resource(fname, name, section, title, description, pk, docs):
    header, rows = read_csv(ROOT / "CSV" / fname)
    cols = list(zip(*rows)) if rows else [[] for _ in header]
    docfields = docs.get(section, {})
    links, texts = CSV_LINKS.get(section, {}), CSV_TEXT.get(section, {})
    fields = []
    for i, col in enumerate(header):
        f = {"name": col, "type": infer_type(cols[i])}
        typ, status, desc = docfields.get(col, ("", "", ""))
        if col in links:
            meaning, kind = links[col]
            desc = f"{meaning}, as comma-separated {KIND[kind]}"
            ex = example(cols[i])
            desc += f" (e.g. `{ex}`)." if ex else "."
            if kind == "event":
                desc += " Titles that contain commas are wrapped in double quotes."
        elif col in texts:
            desc = texts[col]
        elif col == "modified":
            desc = MODIFIED_EVENTS if section == "Events" else MODIFIED_UTC
        if desc:
            # JSON docs quote string values ("-4003"); CSV values are unquoted.
            desc = re.sub(r'`"([^"`]*)"`', r'`\1`', desc)
            f["description"] = absolute_links(desc)
        if status:
            f["status"] = status  # custom property: Validated, Populated, Incomplete, Temporary, Unknown
        fields.append(f)
    schema = {"fields": fields}
    if pk and pk in header and len(set(cols[header.index(pk)])) == len(rows):
        schema["primaryKey"] = pk
    return {
        "name": name, "title": title, "description": description,
        "path": f"CSV/{fname}", "format": "csv", "mediatype": "text/csv",
        "encoding": "utf-8-sig", "profile": "tabular-data-resource", "schema": schema,
    }


def main():
    docs = parse_docs()
    resources = [table_resource(*t, docs) for t in TABLES]

    header, rows = read_csv(ROOT / "CSV" / "WordIndex.csv")
    cols = list(zip(*rows))
    resources.append({
        "name": "word-index", "title": "Word index",
        "description": "One row per KJV word (about 790,000 rows) with its position, punctuation, italics, syllables, and the person, place, and year tied to it. Maintained by hand, not exported from Airtable.",
        "path": "CSV/WordIndex.csv", "format": "csv", "mediatype": "text/csv",
        "encoding": "utf-8", "profile": "tabular-data-resource",
        "schema": {"fields": [
            dict({"name": c, "type": infer_type(cols[i])},
                 **({"description": WORDINDEX_FIELDS[c]} if c in WORDINDEX_FIELDS else {}))
            for i, c in enumerate(header)]},
    })

    json_names = [("books", "Books"), ("chapters", "Chapters"), ("verses", "Verses"),
                  ("people", "People"), ("peopleGroups", "People groups"),
                  ("places", "Places"), ("events", "Events"), ("easton", "Easton's Bible Dictionary")]
    for stem, title in json_names:
        resources.append({
            "name": f"{re.sub(r'(?<!^)(?=[A-Z])', '-', stem).lower()}-json", "title": f"{title} (JSON)",
            "description": f"{title} as an array of Airtable records ({{id, createdTime, fields}}); link fields hold arrays of record IDs. Fields are documented in the [JSON Fields Documentation]({REPO}docs/json-fields-documentation.md).",
            "path": f"json/{stem}.json", "format": "json", "mediatype": "application/json",
        })

    resources += [
        {"name": "bible-places-geojson", "title": "Bible places (Linked Places Format)",
         "description": "Every biblical place (1,030, with other names merged) as a Linked Places Format GeoJSON FeatureCollection, valid against the World Historical Gazetteer LPF schema v1.2.2, with names, dates, relations, and links to Pleiades, Wikidata, OpenBible.info, and Digital Manna.",
         "path": "geo/bible-places.geojson", "format": "geojson", "mediatype": "application/geo+json"},
        {"name": "pauls-journeys-geojson", "title": "Paul's missionary journeys",
         "description": "Paul's missionary journeys as a GeoJSON FeatureCollection: 44 stops and 68 route segments, with verse references for each journey.",
         "path": "geo/pauls_journeys_all.geojson", "format": "geojson", "mediatype": "application/geo+json"},
    ]

    package = {
        "profile": "data-package",
        "name": "theographic-bible-metadata",
        "title": "Theographic Bible Metadata",
        "description": "A knowledge graph of the Bible that links every verse of the King James Version (1769 Cambridge Edition) to the people, places, events, people groups, and Easton's Bible Dictionary entries it mentions: 66 books, 1,189 chapters, 31,102 verses, 3,067 people, 1,298 place records (1,030 distinct places), 450 events, 23 people groups, and 6,519 dictionary entries. Documentation: https://github.com/robertrouse/theographic-bible-metadata/tree/master/docs",
        "homepage": "https://viz.bible/",
        "keywords": ["Bible", "King James Version", "knowledge graph", "biblical people", "biblical places",
                     "biblical chronology", "gazetteer", "Linked Places Format", "Easton's Bible Dictionary"],
        "licenses": [{"name": "CC-BY-SA-4.0", "path": "https://creativecommons.org/licenses/by-sa/4.0/",
                      "title": "Creative Commons Attribution-ShareAlike 4.0"}],
        "contributors": [{"title": "Robert Rouse", "role": "author", "email": "robert@viz.bible", "path": "https://viz.bible/"}],
        "sources": [
            {"title": "King James Version, 1769 Cambridge Edition"},
            {"title": "Easton's Bible Dictionary (1897), CCEL XML edition", "path": "https://www.ccel.org/ccel/easton/ebd2.xml"},
            {"title": "STEPBible TIPNR", "path": "https://github.com/STEPBible/STEPBible-Data"},
            {"title": "OpenBible.info Bible Geocoding", "path": "https://www.openbible.info/geo/"},
            {"title": "Pleiades: A Gazetteer of Past Places", "path": "https://pleiades.stoa.org/"},
            {"title": "Floyd Nolen Jones, The Chronology of the Old Testament", "path": "https://floydnolenjonesministries.com/chronology/"},
        ],
        "resources": resources,
    }
    out = ROOT / "datapackage.json"
    out.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out} with {len(resources)} resources")


if __name__ == "__main__":
    main()
