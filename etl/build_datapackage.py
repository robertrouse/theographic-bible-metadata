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

LINK_NOTE = " In the CSV this is a comma-separated list of lookup values (e.g. personLookup, placeLookup, osisRef) rather than record IDs."

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
    fields = []
    for i, col in enumerate(header):
        f = {"name": col, "type": infer_type(cols[i])}
        if col in docfields:
            typ, status, desc = docfields[col]
            if typ.strip() == "array":
                desc = (desc + LINK_NOTE).strip()
            if desc:
                f["description"] = desc
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
            "description": f"{title} as an array of Airtable records ({{id, createdTime, fields}}); link fields hold arrays of record IDs. Fields are documented in docs/json-fields-documentation.md.",
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
        "description": "A knowledge graph of the Bible that links every verse of the King James Version to the people, places, events, people groups, and Easton's Bible Dictionary entries it mentions. Documentation: https://github.com/robertrouse/theographic-bible-metadata/tree/master/docs",
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
