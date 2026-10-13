"""Phase 8: validate and expand Pleiades links.

Runs after Phase 6 and before Phase 7, because Phase 7 takes Pleiades names
from the links this phase settles.

1. Validate each linked Pleiades place against the feature: it must exist,
   lie within a distance limit for its kind (rivers and regions are exempt),
   and have a compatible type or a strong name match. Picks in
   geo/decisions.json ("pleiades", "pleiades_add") are always kept;
   "pleiades_reject" removes a link from one feature.
2. For features left without a link, search the Pleiades dump for places near
   the feature whose names match one of the feature's own names
   (Digital Manna, Theographic, title). A close name, compatible type and
   unambiguous best match is accepted; weaker candidates go to review.
3. One Pleiades place stays on one feature: the best-matching claimant.
4. Record each feature's earliest ancient Pleiades attestation
   (index "pleiades_start"), which Phase 9 uses for the feature's when{}.

Reads:  geo/working/phase-6-output.geojson, phase-6-index.json, dm-places-cache.json,
        pleiades-places.csv.gz, pleiades-names.csv.gz;
        json/places.json; geo/decisions.json
Writes: geo/working/phase-8-output.geojson     Phase 6 features with Pleiades links settled
        geo/working/phase-8-index.json         index with final pleiades + evidence
        geo/working/phase-8-review-pleiades.csv
        geo/working/phase-8-report.md

Usage: python3 geo/pipeline/phase8_pleiades.py
"""
import collections
import csv
import difflib
import gzip
import json
import math
import re
import unicodedata
from datetime import date

from pleiades import earliest_attestation, load_names

WORK = 'geo/working'
ACCEPT, REVIEW, CHECK = 0.85, 0.70, 0.90
# How far to search, by our feature class and by the Pleiades place's own kind:
# a settlement has to be close whatever we call the feature.
SEARCH_KM = {'P': 15, 'S': 15, 'T': 40, 'H': 40, 'L': 250, 'R': 250}
POINTLIKE_KM, LANDFORM_KM, AREAL_KM = 15, 40, 250
# An existing link to a precisely located point-like place is dropped beyond:
FAR_POINTLIKE_KM, FAR_LANDFORM_KM = 50, 100

SETTLEMENT = {'settlement', 'urban', 'fortified-settlement', 'village', 'fort', 'fort-2', 'station', 'port',
              'tell', 'settlement-modern', 'archaeological-site', 'vicus', 'acropolis', 'city-wall', 'hillfort',
              'castle', 'ruin', 'temple', 'temple-2', 'sanctuary', 'harbor', 'findspot', 'estate', 'villa'}
SITE = {'well', 'spring', 'cistern', 'reservoir', 'city-gate', 'building', 'palace', 'tomb', 'monument', 'church',
        'church-2', 'cave', 'garden-hortus', 'tower-defensive', 'tower-single', 'aqueduct', 'bath', 'stoa', 'forum',
        'agora', 'plaza', 'street', 'architecturalcomplex', 'oasis'}
LANDFORM = {'mountain', 'hill', 'island', 'cape', 'pass', 'peninsula', 'cave', 'oasis', 'tell', 'spring', 'well'}
COMPAT = {
    'P': SETTLEMENT,
    'S': SETTLEMENT | SITE,
    'T': {'mountain', 'hill', 'island', 'cape', 'plain', 'pass', 'peninsula', 'forest', 'valley', 'cave',
          'archipelago', 'oasis', 'cultural-landscape', 'tell', 'desert'},
    'H': {'river', 'lake', 'spring', 'water-open', 'water-inland', 'bay', 'canal', 'marsh-wetland', 'mouth',
          'harbor', 'well', 'reservoir', 'cistern', 'fountain', 'dam'},
    'L': {'region', 'province', 'province-2', 'people', 'state', 'kingdom', 'district', 'nome-gr',
          'cultural-landscape', 'island', 'archipelago', 'label', 'plain', 'valley', 'oasis', 'peninsula', 'desert'},
    'R': {'road', 'street', 'pass', 'bridge'},
}
NEUTRAL = {'unknown', 'unlabeled', 'feature', 'labeled feature', 'numbered feature', 'unlocated'}
SKIP_TYPES = {'false toponym', 'false', 'fiction'}
# Words that may be dropped when comparing names. A descriptor word (mount,
# valley, river...) may only be dropped when the Pleiades place is that kind of
# thing, so "Valley of Lebanon" cannot match Mount Lebanon.
FILLER = {'of', 'the', 'city', 'land', 'el', 'al', 'ha', 'tel', 'tell', 'khirbet'}
DESCRIPTOR = {'mount': 'mountain', 'mountain': 'mountain', 'mons': 'mountain', 'oros': 'mountain',
              'hill': 'mountain', 'valley': 'valley', 'vale': 'valley', 'river': 'water', 'brook': 'water',
              'sea': 'water', 'wadi': 'water', 'lake': 'water'}
DESCRIPTOR_TYPES = {'mountain': {'mountain', 'hill', 'pass', 'cape'}, 'valley': {'valley', 'plain'},
                    'water': COMPAT['H']}


def km(a, b):
    (lon1, lat1), (lon2, lat2) = a, b
    p = math.pi / 180
    h = (math.sin((lat2 - lat1) * p / 2) ** 2 +
         math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 12742 * math.asin(math.sqrt(h))


def fold(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def name_forms(name):
    """(full key, core key, descriptor kinds dropped to make the core key)."""
    words = re.findall(r'[a-z]+', fold(re.sub(r'\([^)]*\)', '', name)))
    full = ''.join(words)
    core = ''.join(w for w in words if w not in FILLER and w not in DESCRIPTOR)
    kinds = {DESCRIPTOR[w] for w in words if w in DESCRIPTOR}
    return full, core, kinds


def pleiades_keys(names):
    out = set()
    for n in names:
        full, core, _ = name_forms(n)
        out |= {k for k in (full, core) if len(k) >= 3}
    return out


def similarity(own_forms, place):
    best = 0.0
    for full, core, kinds in own_forms:
        mine = [full]
        if all(place['types'] & DESCRIPTOR_TYPES[k] or not (place['types'] - NEUTRAL) for k in kinds):
            mine.append(core)
        for a in mine:
            if len(a) < 3:
                continue
            for b in place['keys']:
                best = max(best, 1.0 if a == b else difflib.SequenceMatcher(None, a, b).ratio())
    return best


def compatible(fclasses, types):
    if not (types - NEUTRAL):
        return True
    return any(types & COMPAT.get(c, set()) for c in fclasses)


def place_kind_km(types, landform, pointlike, areal):
    if types & (SETTLEMENT | SITE) and not types & (COMPAT['L'] | {'river', 'mountain'}):
        return pointlike
    if types & LANDFORM:
        return landform
    return areal


def load_pleiades():
    places = {}
    for r in csv.DictReader(gzip.open(f'{WORK}/pleiades-places.csv.gz', 'rt')):
        types = {t.strip() for t in r['featureTypes'].split(',') if t.strip()}
        pt = [float(r['reprLong']), float(r['reprLat'])] if r['reprLat'] and r['reprLong'] else None
        names = set(re.split(r'[/,]', r['title']))
        places[r['id']] = {'title': r['title'], 'types': types, 'point': pt,
                           'precision': r['locationPrecision'], 'names': names}
    for r in csv.DictReader(gzip.open(f'{WORK}/pleiades-names.csv.gz', 'rt')):
        pid = r['pid'].rsplit('/', 1)[1]
        if pid in places:
            for field in ('nameTransliterated', 'nameAttested'):
                places[pid]['names'].update(n.strip() for n in r[field].split(',') if n.strip())
    for p in places.values():
        p['keys'] = pleiades_keys(p['names'])
    return places


def main():
    fc = json.load(open(f'{WORK}/phase-6-output.geojson'))
    index = {x['@id']: x for x in json.load(open(f'{WORK}/phase-6-index.json'))}
    dm = {e['id']: e for e in json.load(open(f'{WORK}/dm-places-cache.json'))['entries']}
    places = {p['fields']['placeID']: p['fields'] for p in json.load(open('json/places.json'))}
    dec = json.load(open('geo/decisions.json'))
    pinned = {p['dm_id']: p['id'] for p in dec['pleiades']}
    for a in dec.get('pleiades_add', []):
        pinned[a['dm_id']] = a['id']
    rejected = {(p['dm_id'], r) for p in dec['pleiades'] for r in p['reject']} | \
               {(r['dm_id'], r['id']) for r in dec.get('pleiades_reject', [])}
    pl = load_pleiades()

    grid = collections.defaultdict(list)
    for pid, p in pl.items():
        if p['point'] and p['precision'] != 'unlocated' and not (p['types'] & SKIP_TYPES):
            grid[(math.floor(p['point'][0]), math.floor(p['point'][1]))].append(pid)

    def nearby(point, radius):
        span = math.ceil(radius / 80) + 1
        cx, cy = math.floor(point[0]), math.floor(point[1])
        for dx in range(-span, span + 1):
            for dy in range(-span, span + 1):
                for pid in grid.get((cx + dx, cy + dy), []):
                    d = km(point, pl[pid]['point'])
                    if d <= radius:
                        yield pid, d

    stats = collections.Counter()
    review = []
    claims = collections.defaultdict(list)   # pleiades id -> [(feature, score, km, how)]
    feats = {f['@id']: f for f in fc['features']}

    def row_for(feat, pid, d=None, score=None):
        p = pl.get(pid, {})
        return {'title': feat['properties']['title'], 'fclasses': ' '.join(feat['properties']['fclasses']),
                'pleiades': pid, 'pleiades_title': p.get('title', ''), 'types': ' '.join(sorted(p.get('types', []))),
                'km': None if d is None else round(d, 1), 'name_score': None if score is None else round(score, 2)}

    for feat in fc['features']:
        x = index[feat['@id']]
        fcl = set(feat['properties']['fclasses'])
        point = feat['geometry']['coordinates'] if feat.get('geometry') else None
        canon = x['dm_ids'][0] if x['dm_ids'] else None
        own = {feat['properties']['title']}
        for d in x['dm_ids']:
            own |= {dm[d]['name']} | set(dm[d].get('names') or [])
        for p in x['placeIDs']:
            if p in places:
                own |= {places[p].get(k) for k in ('displayTitle', 'kjvName', 'esvName') if places[p].get(k)}
        own_forms = [name_forms(n) for n in own if n]
        x['_own_forms'] = own_forms

        if canon in pinned:
            claims[pinned[canon]].append((feat['@id'], 2.0, 1.0, 0.0, 'decision'))
            stats['kept: decision'] += 1
            continue

        found = False
        for pid in x['pleiades']:
            if (canon, pid) in rejected:
                stats['dropped: rejected in decisions'] += 1
                continue
            p = pl.get(pid)
            if not p:
                stats['dropped: not in Pleiades'] += 1
                review.append({**row_for(feat, pid), 'kind': 'existing link dropped: not in Pleiades'})
                continue
            d = km(point, p['point']) if point and p['point'] else None
            score = similarity(own_forms, p)
            far = place_kind_km(p['types'], FAR_LANDFORM_KM, FAR_POINTLIKE_KM, None)
            if far and d is not None and d > far and p['precision'] == 'precise':
                stats['dropped: too far'] += 1
                review.append({**row_for(feat, pid, d, score), 'kind': f'existing link dropped: more than {far} km away'})
                continue
            if not compatible(fcl, p['types']):
                if score < ACCEPT:
                    stats['dropped: type mismatch and weak name'] += 1
                    review.append({**row_for(feat, pid, d, score), 'kind': 'existing link dropped: type mismatch, weak name'})
                    continue
                stats['kept, flagged: type mismatch'] += 1
                review.append({**row_for(feat, pid, d, score), 'kind': 'existing link kept: type mismatch'})
            claims[pid].append((feat['@id'], score, similarity([name_forms(feat['properties']['title'])], p),
                                d or 0.0, 'existing'))
            found = True
            stats['kept: existing'] += 1

        if found or not point:
            continue
        cands = []
        for pid, d in nearby(point, max(SEARCH_KM.get(c, 15) for c in fcl)):
            p = pl[pid]
            if d > place_kind_km(p['types'], LANDFORM_KM, POINTLIKE_KM, AREAL_KM):
                continue
            score = similarity(own_forms, p)
            if score >= REVIEW and (canon, pid) not in rejected:
                cands.append((score, -d, pid, d))
        if not cands:
            continue
        cands.sort(reverse=True)
        score, _, pid, d = cands[0]
        ok_type = compatible(fcl, pl[pid]['types'])
        rival = next((c for c in cands[1:] if c[0] >= score - 0.02), None)
        if score >= ACCEPT and ok_type and not rival:
            claims[pid].append((feat['@id'], score, similarity([name_forms(feat['properties']['title'])], pl[pid]),
                                d, f'matched: name {score:.2f}, {d:.1f} km'))
            stats['added: matched'] += 1
        else:
            why = 'name below threshold' if score < ACCEPT else (
                'type mismatch' if not ok_type else f'ambiguous with {rival[2]} {pl[rival[2]]["title"]}')
            review.append({**row_for(feat, pid, d, score), 'kind': f'candidate not applied: {why}'})
            stats['candidates for review'] += 1

    # One Pleiades place, one feature: a decision wins, then the closer name,
    # then the closer title (Ono over Chephirim), then the nearer point.
    final = collections.defaultdict(dict)
    for pid, cl in claims.items():
        cl.sort(key=lambda c: (c[4] == 'decision', c[1], c[2], -c[3]), reverse=True)
        keep = [c for c in cl if c[4] == 'decision'] or cl[:1]
        for c in keep:
            final[c[0]][pid] = c[4]
            if c[4].startswith('matched') and c[1] < CHECK:
                review.append({**row_for(feats[c[0]], pid, c[3], c[1]),
                               'kind': f'new match applied: check (name score < {CHECK})'})
        for c in cl:
            if c not in keep:
                stats['dropped: Pleiades place kept by another feature'] += 1
                review.append({**row_for(feats[c[0]], pid, c[3], c[1]),
                               'kind': f'link dropped: belongs to {feats[keep[0][0]]["properties"]["title"]}'})

    pl_names = load_names()
    for feat in fc['features']:
        x = index[feat['@id']]
        x.pop('_own_forms', None)
        kept = list(final.get(feat['@id'], {}))
        x['pleiades'] = kept
        x['pleiades_evidence'] = final.get(feat['@id'], {})
        first = earliest_attestation(kept, pl_names)
        x['pleiades_start'] = {'year': first[0], 'pleiades': first[1], 'name': first[2]} if first else None
        stats['features with a Pleiades start'] += bool(first)
        links = [l for l in feat['links'] if 'pleiades.stoa.org' not in l['identifier']]
        at = next((i for i, l in enumerate(links) if 'wikidata.org' in l['identifier']), len(links))
        links[at:at] = [{'type': 'seeAlso', 'identifier': f'https://pleiades.stoa.org/places/{p}'} for p in kept]
        feat['links'] = links
        stats['features with pleiades'] += bool(kept)

    json.dump(fc, open(f'{WORK}/phase-8-output.geojson', 'w'), indent=2, ensure_ascii=False)
    json.dump(list(index.values()), open(f'{WORK}/phase-8-index.json', 'w'), indent=1, ensure_ascii=False)
    cols = ['kind', 'title', 'fclasses', 'pleiades', 'pleiades_title', 'types', 'km', 'name_score']
    with open(f'{WORK}/phase-8-review-pleiades.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols + ['decision'])
        w.writeheader()
        w.writerows(sorted(review, key=lambda r: (r['kind'], r['title'])))

    before = sum(1 for x in json.load(open(f'{WORK}/phase-6-index.json')) if x['pleiades'])
    kinds = collections.Counter(r['kind'] for r in review)
    lines = [
        '# Phase 8 Report: Pleiades links', '',
        f'**Generated:** {date.today().isoformat()}  ',
        f'**Thresholds:** accept name score >= {ACCEPT} (listed for checking below {CHECK}); review >= {REVIEW}. '
        f'Search radius by our class {SEARCH_KM}, capped by the Pleiades place kind: point-like {POINTLIKE_KM} km, '
        f'landform {LANDFORM_KM} km, areal {AREAL_KM} km. Existing links to precisely located point-like places '
        f'dropped beyond {FAR_POINTLIKE_KM} km, landforms beyond {FAR_LANDFORM_KM} km; rivers and regions are not distance-checked.', '',
        '| Metric | Count |', '|---|---|',
        f'| Features with a Pleiades link | {stats["features with pleiades"]} (was {before}) |',
        f'| Kept from decisions | {stats["kept: decision"]} |',
        f'| Kept existing links | {stats["kept: existing"]} |',
        f'| Existing links dropped: not in Pleiades | {stats["dropped: not in Pleiades"]} |',
        f'| Existing links dropped: too far | {stats["dropped: too far"]} |',
        f'| Existing links dropped: type mismatch and weak name | {stats["dropped: type mismatch and weak name"]} |',
        f'| Existing links kept but type mismatch | {stats["kept, flagged: type mismatch"]} |',
        f'| Links dropped: same Pleiades place kept by a better-matching feature | {stats["dropped: Pleiades place kept by another feature"]} |',
        f'| New matches from the Pleiades dump | {stats["added: matched"]} |',
        f'| Candidates left for review | {stats["candidates for review"]} |',
        f'| Features with an ancient Pleiades attestation (start date for Phase 9) | {stats["features with a Pleiades start"]} |', '',
        '## Review list (`phase-8-review-pleiades.csv`)', '',
    ] + [f'- {k}: {v}' for k, v in sorted(kinds.items())]
    open(f'{WORK}/phase-8-report.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
