"""Pleiades name helpers shared by Phases 7, 8 and 9.

Names come from the Pleiades bulk dump (geo/working/pleiades-names.csv.gz,
fetched by fetch_sources.py). A name counts as an ancient attestation when its
language is ancient or unspecified and it is dated no later than AD 640
(Pleiades' own horizon); an undated name counts only in an ancient language.
This keeps Antiochia (la, -750) and drops Antakya (tr, "-1750"-2000), whose
span is Pleiades' way of saying "the name of this place over its whole life".
"""
import collections
import csv
import gzip

DUMP = 'geo/working/pleiades-names.csv.gz'
LATEST_ANCIENT = 640
UNKNOWN_SPAN = (-3300, 2000)    # Pleiades' whole-range default
ANCIENT_LANGS = {'grc', 'la', 'akk', 'egy', 'hbo', 'arc', 'cop', 'hit', 'peo', 'phn', 'sux', 'elx',
                 'xur', 'cana', 'xmn', 'xmr', 'xlc', 'syc', 'uga'}


def _int(v):
    return int(float(v)) if v not in ('', None) else None


def load_names(path=DUMP):
    """Pleiades place id -> [{romanized, attested, language, start, end}]."""
    names = collections.defaultdict(list)
    for r in csv.DictReader(gzip.open(path, 'rt')):
        names[r['pid'].rsplit('/', 1)[1]].append({
            'romanized': r['nameTransliterated'].strip(),
            'attested': r['nameAttested'].strip(),
            'language': (r['nameLanguage'] or '').strip(),
            'start': _int(r['minDate']),
            'end': _int(r['maxDate']),
        })
    return names


def dated(n):
    return n['start'] is not None and (n['start'], n['end']) != UNKNOWN_SPAN


def ancient(n):
    lang = n['language'].split('-')[0]
    if lang and lang not in ANCIENT_LANGS:
        return False
    if dated(n):
        return n['start'] <= LATEST_ANCIENT
    return lang in ANCIENT_LANGS


def earliest_attestation(pids, names):
    """(year, pleiades id, name) of the earliest ancient attestation, or None."""
    best = None
    for pid in pids:
        for n in names.get(pid, []):
            if n['romanized'] and ancient(n) and dated(n):
                if best is None or n['start'] < best[0]:
                    best = (n['start'], pid, n['romanized'])
    return best
