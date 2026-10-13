"""Phase 9b: "part of" and "near" relations between places, and kingdoms.

Each relation sits on the child feature, LPF style:
  {"relationType": "gvp:broaderPartitive",       # part of; "gvp:tgn3000_related_to" = near
   "relationTo": "<parent @id>", "label": "part of Jerusalem",
   "when": {"timespans": [{"start": {"in": "-1444"}}]},   # when the source dates it
   "certainty": "certain" | "less certain",
   "citations": [{"label": "Josh.15.33", "@id": "https://theographic.netlify.app/josh#Josh.15.33"}]}

Sources (geo/decisions.json unless noted), merged when they agree:
  polities     kingdoms: members are part of the kingdom between its start and end;
               the kingdom gets when{} with start AND end and a MultiPoint of its members
  allotments   cities and sites (fclass P/S) in Joshua's tribal city lists are part of
               the tribe's territory from the year of the verse
  DM regions   the Digital Manna editors' "Region:" lines (dm-places-cache.json):
               stated or historical = certain, implied only = less certain
  part_of/near curated pairs (from the retired Airtable rootID links and the text)
  Airtable     the partOf / near links and startYear / endYear in json/places.json
               (once exported): a link added in Airtable becomes a relation here,
               cited by the verses its two records share; a parent's years date it.
               Airtable never raises or lowers a certainty set by another source.

Reads:  geo/working/phase-9-output.geojson, phase-8-index.json, dm-places-cache.json,
        json/places.json, json/verses.json, geo/decisions.json
Writes: geo/working/phase-9b-output.geojson   the complete LPF file
        geo/working/phase-9b-report.md

Usage: python3 geo/pipeline/phase9b_relations.py
"""
import collections
import json
from datetime import date

WORK = 'geo/working'
PART_OF, NEAR = 'gvp:broaderPartitive', 'gvp:tgn3000_related_to'
RANK = {'certain': 2, 'less certain': 1, 'uncertain': 0}
ORDER = ['@id', 'properties', 'type', 'geometry', 'when', 'names', 'relations', 'links']


def verse_cite(osis):
    return {'label': osis, '@id': f'https://theographic.netlify.app/{osis.split(".")[0].lower()}#{osis}'}


def main():
    fc = json.load(open(f'{WORK}/phase-9-output.geojson'))
    index = json.load(open(f'{WORK}/phase-8-index.json'))
    dec = json.load(open('geo/decisions.json'))
    dm = {e['id']: e for e in json.load(open(f'{WORK}/dm-places-cache.json'))['entries']}
    places = {p['id']: p['fields'] for p in json.load(open('json/places.json'))}
    verses = sorted((int(v['fields']['verseID']), {**v['fields'], '_rec': v['id']})
                    for v in json.load(open('json/verses.json')))
    by_osis = {f['osisRef']: (vid, f) for vid, f in verses}

    feats = {f['@id']: f for f in fc['features']}
    feat_of = {}                                   # dm_id or "theographic:<placeID>" -> @id
    pid_feat = {}
    for x in index:
        if x['@id'] not in feats:
            continue
        for d in x['dm_ids']:
            feat_of[d] = x['@id']
        for p in x['placeIDs']:
            pid_feat[p] = x['@id']
            feat_of.setdefault(f'theographic:{p}', x['@id'])
    title = {i: f['properties']['title'] for i, f in feats.items()}
    fclass = {i: f['properties']['fclasses'][0] for i, f in feats.items()}
    rec_pid = {rid: f['placeID'] for rid, f in places.items()}

    rels = {}                                      # (child, parent, type) -> relation
    sources = collections.Counter()
    skipped = collections.Counter()

    def add(child, parent, rtype, source, certainty='certain', start=None, end=None, cites=()):
        # certainty=None: no opinion (new relations default to certain)
        if not child or not parent or child == parent or child not in feats or parent not in feats:
            skipped[f'{source}: place not in the data'] += 1
            return
        key = (child, parent, rtype)
        r = rels.get(key)
        if r is None:
            r = rels[key] = {'relationType': rtype, 'relationTo': parent,
                             'label': f'{"part of" if rtype == PART_OF else "near"} {title[parent]}',
                             'certainty': certainty or 'certain', '_start': start, '_end': end, 'citations': []}
            sources[source] += 1
        else:
            sources[f'{source} (merged)'] += 1
            if certainty and RANK[certainty] > RANK[r['certainty']]:
                r['certainty'] = certainty
            if start is not None and (r['_start'] is None or start < r['_start']):
                r['_start'] = start
            if end is not None:
                r['_end'] = end
        for c in cites:
            if c not in r['citations']:
                r['citations'].append(c)

    # 1. kingdoms
    for pol in dec.get('polities', []):
        pid = feat_of.get(pol['dm_id'])
        if not pid:
            skipped['polity not in the data'] += 1
            continue
        f = feats[pid]
        f['properties']['title'] = pol['label']
        f['when'] = {'timespans': [{'start': {'in': str(pol['start'])}, 'end': {'in': str(pol['end'])}}],
                     'label': f'{pol["note"]} ({pol["start_ref"]} to {pol["end_ref"]}), Theographic chronology'}
        members = [feat_of.get(m) for m in pol['members']]
        pts = [feats[m]['geometry']['coordinates'] for m in members if m and feats[m]['geometry'].get('coordinates')]
        if pts:
            f['geometry'] = {'type': 'MultiPoint', 'coordinates': pts, 'certainty': 'less-certain'}
        for m in members:
            add(m, pid, PART_OF, 'kingdoms', 'certain', pol['start'], pol['end'],
                [verse_cite(pol['start_ref']), verse_cite(pol['end_ref'])])

    # 2. Joshua allotments (minus decisions.json "allotment_exclude": border wording, mislinked verses)
    excluded = {(feat_of.get(x['child']), feat_of.get(x['territory'])) for x in dec.get('allotment_exclude', [])}
    for a in dec.get('allotments', []):
        parent = feat_of.get(a['territory'])
        first, last = a['verses'].split('-')
        lo, hi = by_osis[first][0], by_osis[last][0]
        for vid, v in verses:
            if not lo <= vid <= hi:
                continue
            for rec in v.get('places') or []:
                child = pid_feat.get(rec_pid.get(rec))
                if child and fclass.get(child) in ('P', 'S') and (child, parent) not in excluded:
                    add(child, parent, PART_OF, 'Joshua allotments', a['certainty'], v.get('yearNum'), None,
                        [verse_cite(v['osisRef'])])

    # 3. Digital Manna region notes
    for d, e in dm.items():
        for reg in e.get('regions') or []:
            basis = reg['basis'].lower()
            certainty = 'certain' if ('stated' in basis or 'historical' in basis) else 'less certain'
            add(feat_of.get(d), feat_of.get(reg['id']), PART_OF, 'Digital Manna regions', certainty,
                cites=[{'label': 'Digital Manna', '@id': f'https://www.digitalmanna.org/encyclopedia/places/{e["slug"]}'}])

    # 4. curated pairs
    for kind, rtype in (('part_of', PART_OF), ('near', NEAR)):
        for p in dec.get(kind, []):
            add(feat_of.get(p['child']), feat_of.get(p['parent']), rtype, f'decisions.json {kind}', p['certainty'])

    # 5. Airtable partOf / near (present after an export that includes the fields)
    by_rec = {rid: f for rid, f in places.items()}
    rec_feat = {rid: pid_feat.get(f['placeID']) for rid, f in places.items()}
    for rid, f in places.items():
        for field, rtype in (('partOf', PART_OF), ('near', NEAR)):
            for prid in f.get(field) or []:
                p = by_rec.get(prid, {})
                shared = sorted(set(f.get('verses') or []) & set(p.get('verses') or []))
                osis = sorted({vf['osisRef'] for vid, vf in verses if vf.get('_rec') in shared})[:3] if shared else []
                add(rec_feat.get(rid), rec_feat.get(prid), rtype, f'Airtable {field}', None,
                    p.get('startYear'), p.get('endYear'), [verse_cite(o) for o in osis])

    # write relations onto children
    per_child = collections.defaultdict(list)
    for (child, _, _), r in sorted(rels.items(), key=lambda kv: (kv[0][0], kv[1]['label'])):
        out = {k: r[k] for k in ('relationType', 'relationTo', 'label')}
        if r['_start'] is not None:
            span = {'start': {'in': str(r['_start'])}}
            if r['_end'] is not None:
                span['end'] = {'in': str(r['_end'])}
            out['when'] = {'timespans': [span]}
        out['certainty'] = r['certainty']
        if r['citations']:
            out['citations'] = r['citations']
        per_child[child].append(out)
    for i, f in feats.items():
        if per_child.get(i):
            f['relations'] = per_child[i]
    fc['features'] = [{k: f[k] for k in ORDER if k in f} for f in fc['features']]
    fc['features'].sort(key=lambda f: f['properties']['title'].lower())
    json.dump(fc, open(f'{WORK}/phase-9b-output.geojson', 'w'), indent=2, ensure_ascii=False)

    by_type = collections.Counter(r['relationType'] for r in rels.values())
    parents = collections.Counter(r['relationTo'] for r in rels.values() if r['relationType'] == PART_OF)
    lines = [
        '# Phase 9b Report: relations', '',
        f'**Generated:** {date.today().isoformat()}', '',
        '| Relations | Count |', '|---|---|',
        f'| part of (gvp:broaderPartitive) | {by_type[PART_OF]} |',
        f'| near (gvp:tgn3000_related_to) | {by_type[NEAR]} |',
        f'| Features with at least one relation | {len(per_child)} |', '',
        '| Source | New relations |', '|---|---|',
    ] + [f'| {k} | {v} |' for k, v in sorted(sources.items())] + [
        '', 'Skipped: ' + (', '.join(f'{k} {v}' for k, v in skipped.items()) or 'none'), '',
        '## Kingdoms', '',
    ] + [f'- {p["label"]}: {p["start"]} to {p["end"]}, '
         f'{sum(1 for (c, par, t) in rels if par == feat_of.get(p["dm_id"]) and t == PART_OF)} members'
         for p in dec.get('polities', [])] + [
        '', '## Places with the most parts', '',
    ] + [f'- {title[p]}: {n}' for p, n in parents.most_common(15)]
    open(f'{WORK}/phase-9b-report.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
