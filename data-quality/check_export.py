#!/usr/bin/env python3
"""Automated data-quality checks against a Theographic export.

Runs the classes of problem first reported in the Nov 2026 external audit
(same-name places that share coordinates with no canonicalPlace, events dated before their
predecessor (successor start before predecessor start, honoring SS/FS only as context), person deathYear vs Death-of-*
event year, and a child listed on a parent record without a reciprocal
father/mother link).

Anything already referenced in data-quality/issues.yaml (by Airtable
record id or slug/key) is omitted from the report, including fixed and
wontfix entries, so decided items are not re-flagged.

The script exits 0 when it finishes, even if it found problems — the
GitHub Action opens or updates a summary issue rather than failing CI.
It exits 2 only if the export or ledger cannot be read.
"""

from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

REC_RE = re.compile(r"^rec[A-Za-z0-9]{14}$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9_]+\d*$")
# Astronomical years can be <= 0; datetime.date cannot, so shift.
YEAR_OFFSET = 5000
ISSUE_MARKER = "<!-- theographic-export-quality-checks -->"


# ---------------------------------------------------------------------------
# Dates and lag spans
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class YMD:
    year: int
    month: int = 1
    day: int = 1
    precision: str = "day"  # year | month | day

    def start(self) -> "YMD":
        if self.precision == "year":
            return YMD(self.year, 1, 1, "year")
        if self.precision == "month":
            return YMD(self.year, self.month, 1, "month")
        return self

    def end(self) -> "YMD":
        if self.precision == "year":
            return YMD(self.year, 12, 31, "year")
        if self.precision == "month":
            last = calendar.monthrange(self.year + YEAR_OFFSET, self.month)[1]
            return YMD(self.year, self.month, last, "month")
        return self

    def to_date(self) -> date:
        y = self.year + YEAR_OFFSET
        last = calendar.monthrange(y, self.month)[1]
        return date(y, self.month, min(self.day, last))

    def __lt__(self, other: "YMD") -> bool:
        return self.to_date() < other.to_date()

    def __add__(self, span: "Span") -> "YMD":
        d = self.to_date()
        # years first, then months, then days
        y = d.year + span.years
        m = d.month + span.months
        while m > 12:
            y += 1
            m -= 12
        while m < 1:
            y -= 1
            m += 12
        last = calendar.monthrange(y, m)[1]
        d = date(y, m, min(d.day, last)) + timedelta(days=span.days)
        precision = self.precision
        if span.days and precision == "year":
            precision = "day"
        elif span.months and precision == "year":
            precision = "month"
        return YMD(d.year - YEAR_OFFSET, d.month, d.day, precision)

    def __str__(self) -> str:
        if self.precision == "year":
            return str(self.year)
        if self.precision == "month":
            return f"{self.year}-{self.month:02d}"
        return f"{self.year}-{self.month:02d}-{self.day:02d}"


@dataclass(frozen=True)
class Span:
    years: int = 0
    months: int = 0
    days: int = 0


def parse_date(value: Any) -> YMD | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if re.fullmatch(r"-?\d+", s):
        return YMD(int(s), 1, 1, "year")
    m = re.fullmatch(r"(-?\d+)-(\d{1,2})-(\d{1,2})", s)
    if m:
        return YMD(int(m.group(1)), int(m.group(2)), int(m.group(3)), "day")
    m = re.fullmatch(r"(-?\d+)-(\d{1,2})", s)
    if m:
        return YMD(int(m.group(1)), int(m.group(2)), 1, "month")
    return None


def parse_span(value: Any) -> Span | None:
    """Parse a lag or duration such as 130Y, 1D, 7Y6M, 2.5Y, 0Y. Empty is 0."""
    if value is None:
        return Span()
    s = str(value).strip()
    if not s:
        return Span()
    years = months = days = 0
    parts = list(re.finditer(r"(\d+(?:\.\d+)?)([YMD])", s))
    if not parts or "".join(p.group(0) for p in parts) != s:
        return None
    for part in parts:
        n = float(part.group(1))
        unit = part.group(2)
        if unit == "Y":
            whole = int(n)
            frac = n - whole
            years += whole
            if frac:
                months += int(round(frac * 12))
        elif unit == "M":
            months += int(n)
        else:
            days += int(n)
    return Span(years, months, days)


def wholly_before(actual: YMD, expected: YMD) -> bool:
    """True if `actual` is entirely before `expected`, honoring precision.

    A year-only actual date means "sometime that year", so it is only
    before expected if 31 Dec of that year is before expected's start.
    A year-only expected start is treated as 1 Jan of that year.
    """
    return actual.end() < expected.start()


# ---------------------------------------------------------------------------
# Export + ledger loading
# ---------------------------------------------------------------------------

def load_json_records(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text())
    out = {}
    for row in data:
        rec_id = row.get("id")
        fields = row.get("fields") or {}
        if rec_id:
            out[rec_id] = fields
    return out


def slug_of(fields: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = fields.get(key)
        if value:
            return str(value)
    return ""


def load_ledger(path: Path) -> tuple[set[str], set[str]]:
    """Return (record ids, slugs/keys) referenced anywhere in the ledger."""
    ids: set[str] = set()
    slugs: set[str] = set()
    entries = yaml.safe_load(path.read_text()) or []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for rec in entry.get("records") or []:
            if not isinstance(rec, dict):
                continue
            rec_id = rec.get("id")
            if rec_id:
                ids.add(str(rec_id))
            key = rec.get("key")
            if not key:
                continue
            key = str(key).strip()
            slugs.add(key)
            token = key.split()[0].strip(" ,;:()")
            if token:
                slugs.add(token)
    return ids, slugs


@dataclass
class Finding:
    rule: str
    record_id: str
    slug: str
    summary: str
    extra_ids: list[str] = field(default_factory=list)
    extra_slugs: list[str] = field(default_factory=list)

    def all_ids(self) -> list[str]:
        return [self.record_id, *self.extra_ids]

    def all_slugs(self) -> list[str]:
        return [self.slug, *self.extra_slugs]


def is_logged(finding: Finding, ids: set[str], slugs: set[str]) -> bool:
    """Drop a finding if its primary record is already in the ledger."""
    return finding.record_id in ids or (bool(finding.slug) and finding.slug in slugs)


def filter_group_members(
    members: list[tuple[str, str]], ids: set[str], slugs: set[str]
) -> list[tuple[str, str]]:
    return [
        (rec_id, slug)
        for rec_id, slug in members
        if rec_id not in ids and slug not in slugs
    ]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _coord_key(fields: dict[str, Any]) -> tuple[float, float] | None:
    lat, lon = fields.get("latitude"), fields.get("longitude")
    if lat in (None, "") or lon in (None, ""):
        return None
    try:
        return (round(float(lat), 6), round(float(lon), 6))
    except (TypeError, ValueError):
        return None


def _place_names(fields: dict[str, Any]) -> set[str]:
    names = set()
    for key in ("displayTitle", "kjvName"):
        value = fields.get(key)
        if value and str(value).strip():
            names.add(str(value).strip().lower())
    return names


def check_shared_coords(places: dict[str, dict[str, Any]]) -> list[Finding]:
    """Same displayTitle or kjvName, same point, no canonicalPlace.

    Many distinct places share a regional default point (for example a
    Jerusalem centroid). Those are counted in the report footer but not
    listed unless the records also share a name, which is the class in
    the Nov 2026 audit (Baalath, Valley of Shaveh).
    """
    unlinked_by_coord: dict[tuple[float, float], list[tuple[str, str, set[str], str]]] = defaultdict(list)
    all_unlinked_groups = 0
    for rec_id, fields in places.items():
        key = _coord_key(fields)
        if key is None:
            continue
        if fields.get("canonicalPlace"):
            continue
        slug = slug_of(fields, "slug", "placeLookup")
        title = str(fields.get("displayTitle") or slug)
        unlinked_by_coord[key].append((rec_id, slug, _place_names(fields), title))
    for members in unlinked_by_coord.values():
        if len(members) >= 2:
            all_unlinked_groups += 1

    findings: list[Finding] = []
    for (lat, lon), members in sorted(unlinked_by_coord.items()):
        if len(members) < 2:
            continue
        # Cluster records that share at least one name.
        used: set[str] = set()
        for i, rec in enumerate(members):
            if rec[0] in used or not rec[2]:
                continue
            cluster = [rec]
            for other in members[i + 1 :]:
                if other[0] not in used and rec[2] & other[2]:
                    cluster.append(other)
            if len(cluster) < 2:
                continue
            for item in cluster:
                used.add(item[0])
            rec_ids = [m[0] for m in cluster]
            slugs = [m[1] for m in cluster]
            shared = " / ".join(sorted(set.intersection(*(m[2] for m in cluster))))
            labels = ", ".join(slugs)
            findings.append(
                Finding(
                    rule="shared-coords-no-canonical",
                    record_id=rec_ids[0],
                    slug=slugs[0],
                    summary=f"{lat}, {lon} — same name {shared!r}: {labels}",
                    extra_ids=rec_ids[1:],
                    extra_slugs=slugs[1:],
                )
            )
    # Stash the broader count on the function for the report footer.
    check_shared_coords.unlinked_group_count = all_unlinked_groups  # type: ignore[attr-defined]
    return findings


def check_event_before_predecessor(events: dict[str, dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    for rec_id, fields in events.items():
        preds = fields.get("predecessor") or []
        if not preds:
            continue
        actual = parse_date(fields.get("startDate"))
        if actual is None:
            continue
        lag_type = (fields.get("lagType") or "").strip().upper() or "none"
        title = fields.get("title") or rec_id
        for pred_id in preds:
            pred = events.get(pred_id)
            if not pred:
                continue
            pred_start = parse_date(pred.get("startDate"))
            if pred_start is None:
                continue
            # First version of this check matches the audit class: the
            # event starts before its predecessor starts. Year-only dates
            # are treated as that whole year, so "0030" is not before
            # "0030-05-02". Lag-computed start mismatches that still fall
            # after the predecessor (off-by-one FS spans, duration/lag
            # double counts) are left to a later, stricter rule.
            if not wholly_before(actual, pred_start):
                continue
            pred_title = pred.get("title") or pred_id
            lag_note = f"lag {fields.get('lag') or 'empty'} {lag_type}"
            findings.append(
                Finding(
                    rule="event-before-predecessor",
                    record_id=rec_id,
                    slug=str(title),
                    summary=(
                        f"{title} starts {fields.get('startDate')} before "
                        f"predecessor {pred_title} ({pred.get('startDate')}); "
                        f"{lag_note}"
                    ),
                    extra_ids=[pred_id],
                    extra_slugs=[str(pred_title)],
                )
            )
    return findings


def check_death_year(
    people: dict[str, dict[str, Any]], events: dict[str, dict[str, Any]]
) -> list[Finding]:
    # Index people by displayTitle and name, lowercased.
    by_title: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for rec_id, fields in people.items():
        for key in ("displayTitle", "name"):
            value = fields.get(key)
            if value:
                by_title[str(value).strip().lower()].append((rec_id, fields))

    findings: list[Finding] = []
    for ev_id, ev in events.items():
        title = str(ev.get("title") or "")
        if not title.startswith("Death of "):
            continue
        who = title[len("Death of ") :].strip()
        ev_date = parse_date(ev.get("startDate"))
        if ev_date is None:
            continue
        candidates: list[tuple[str, dict[str, Any]]] = []
        for part_id in ev.get("participants") or []:
            fields = people.get(part_id)
            if not fields:
                continue
            titles = {
                str(fields.get("displayTitle") or "").strip().lower(),
                str(fields.get("name") or "").strip().lower(),
            }
            if who.lower() in titles or any(who.lower() == t.split("(")[0].strip() for t in titles if t):
                candidates.append((part_id, fields))
        if not candidates:
            candidates = list(by_title.get(who.lower()) or [])
        # Unique by id
        seen: set[str] = set()
        unique: list[tuple[str, dict[str, Any]]] = []
        for rec_id, fields in candidates:
            if rec_id not in seen:
                seen.add(rec_id)
                unique.append((rec_id, fields))
        for rec_id, fields in unique:
            death_year = fields.get("deathYear")
            if death_year in (None, ""):
                continue
            person_date = parse_date(death_year)
            if person_date is None:
                continue
            if person_date.year == ev_date.year:
                continue
            slug = slug_of(fields, "slug", "personLookup")
            findings.append(
                Finding(
                    rule="death-year-vs-death-event",
                    record_id=rec_id,
                    slug=slug,
                    summary=(
                        f"{slug or rec_id} deathYear is {death_year}, but "
                        f"{title} ({ev_id}) starts {ev.get('startDate')}"
                    ),
                    extra_ids=[ev_id],
                    extra_slugs=[title],
                )
            )
    return findings


def check_child_without_parent(people: dict[str, dict[str, Any]]) -> list[Finding]:
    """A appears in B.children, but B is in neither A.father nor A.mother."""
    findings: list[Finding] = []
    for parent_id, parent in people.items():
        for child_id in parent.get("children") or []:
            child = people.get(child_id)
            if not child:
                findings.append(
                    Finding(
                        rule="child-without-parent",
                        record_id=parent_id,
                        slug=slug_of(parent, "slug", "personLookup"),
                        summary=(
                            f"{slug_of(parent, 'slug', 'personLookup') or parent_id} "
                            f"lists missing record {child_id} as a child"
                        ),
                        extra_ids=[child_id],
                    )
                )
                continue
            fathers = set(child.get("father") or [])
            mothers = set(child.get("mother") or [])
            if parent_id in fathers or parent_id in mothers:
                continue
            child_slug = slug_of(child, "slug", "personLookup")
            parent_slug = slug_of(parent, "slug", "personLookup")
            findings.append(
                Finding(
                    rule="child-without-parent",
                    record_id=child_id,
                    slug=child_slug,
                    summary=(
                        f"{child_slug or child_id} "
                        f"({child.get('displayTitle') or child_slug}) is listed as a "
                        f"child of {parent_slug or parent_id} "
                        f"({parent.get('displayTitle') or parent_slug}), "
                        f"but that parent is not set on the child's father or mother field"
                    ),
                    extra_ids=[parent_id],
                    extra_slugs=[parent_slug],
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

RULE_TITLES = {
    "shared-coords-no-canonical": "Same-name places that share coordinates with no canonicalPlace",
    "event-before-predecessor": "Events dated before their predecessor (SS/FS lag rules)",
    "death-year-vs-death-event": "Person deathYear does not match the Death of * event",
    "child-without-parent": "Child listed on a parent without a reciprocal father/mother link",
}

RULE_ORDER = list(RULE_TITLES)


def render_markdown(
    kept: list[Finding],
    skipped: list[Finding],
    sha: str,
    issues_path: str,
    unlinked_coord_groups: int = 0,
) -> str:
    lines = [
        ISSUE_MARKER,
        "# Automated data quality findings",
        "",
        f"Checked export at `{sha or 'unknown'}` against `{issues_path}`.",
        "Already-logged records (any ledger status, including fixed and wontfix) are omitted.",
        "",
        f"**New findings: {len(kept)}.** Already in the ledger, omitted: {len(skipped)}.",
        "",
    ]
    if not kept:
        lines.append("No new findings in the check classes this workflow runs.")
        lines.append("")
    else:
        by_rule: dict[str, list[Finding]] = defaultdict(list)
        for finding in kept:
            by_rule[finding.rule].append(finding)
        for rule in RULE_ORDER:
            group = by_rule.get(rule) or []
            if not group:
                continue
            lines.append(f"## {RULE_TITLES[rule]} ({len(group)})")
            lines.append("")
            if rule == "shared-coords-no-canonical":
                lines.append("| Coordinates | Records |")
                lines.append("| --- | --- |")
                for finding in group:
                    # summary is "lat, lon — labels"
                    if " — " in finding.summary:
                        coords, labels = finding.summary.split(" — ", 1)
                    else:
                        coords, labels = finding.summary, ""
                    slugs = ", ".join(
                        f"`{s}`" for s in finding.all_slugs() if s
                    ) or labels
                    lines.append(f"| `{coords}` | {slugs} |")
                lines.append("")
            else:
                for finding in group:
                    ident = f"`{finding.slug}`" if finding.slug else f"`{finding.record_id}`"
                    lines.append(f"- {ident} (`{finding.record_id}`): {finding.summary}")
                lines.append("")
    if unlinked_coord_groups:
        lines.append(
            f"Note: {unlinked_coord_groups} coordinate-sharing groups have "
            "no canonicalPlace. This check lists only the groups that also "
            "share a displayTitle or kjvName, which is the class from the "
            "Nov 2026 audit. The rest often share a regional default point."
        )
        lines.append("")
    if skipped:
        lines.append("## Omitted because they are already in the ledger")
        lines.append("")
        by_rule = defaultdict(list)
        for finding in skipped:
            by_rule[finding.rule].append(finding)
        for rule in RULE_ORDER:
            group = by_rule.get(rule) or []
            if not group:
                continue
            sample = ", ".join(
                f"`{f.slug or f.record_id}`" for f in group[:8]
            )
            more = f" and {len(group) - 8} more" if len(group) > 8 else ""
            lines.append(f"- {RULE_TITLES[rule]}: {len(group)} ({sample}{more})")
        lines.append("")
    lines.append("---")
    lines.append(
        "Opened or updated by the export data quality checks workflow "
        "(`export-quality-checks.yml`). This is a report only; it does not "
        "open a pull request or change data."
    )
    lines.append("")
    return "\n".join(lines)


def run_checks(
    json_dir: Path, issues_path: Path
) -> tuple[list[Finding], list[Finding], dict[str, int]]:
    people = load_json_records(json_dir / "people.json")
    places = load_json_records(json_dir / "places.json")
    events = load_json_records(json_dir / "events.json")
    ids, slugs = load_ledger(issues_path)

    raw: list[Finding] = []
    raw.extend(check_shared_coords(places))
    extra = {
        "unlinked_coord_groups": int(
            getattr(check_shared_coords, "unlinked_group_count", 0) or 0
        )
    }
    raw.extend(check_event_before_predecessor(events))
    raw.extend(check_death_year(people, events))
    raw.extend(check_child_without_parent(people))

    # For shared-coord groups, drop already-logged members and keep the
    # remainder if two or more unlogged records still share the point.
    kept: list[Finding] = []
    skipped: list[Finding] = []
    for finding in raw:
        if finding.rule == "shared-coords-no-canonical":
            members = list(zip(finding.all_ids(), finding.all_slugs()))
            remaining = filter_group_members(members, ids, slugs)
            omitted = [m for m in members if m not in remaining]
            if omitted and len(remaining) < 2:
                skipped.append(finding)
                continue
            if omitted and remaining:
                # rebuild finding around the unlogged remainder
                rec_ids = [m[0] for m in remaining]
                slugs_left = [m[1] for m in remaining]
                coords = finding.summary.split(" — ", 1)[0]
                finding = Finding(
                    rule=finding.rule,
                    record_id=rec_ids[0],
                    slug=slugs_left[0],
                    summary=f"{coords} — {', '.join(slugs_left)}",
                    extra_ids=rec_ids[1:],
                    extra_slugs=slugs_left[1:],
                )
            kept.append(finding)
            continue
        if is_logged(finding, ids, slugs):
            skipped.append(finding)
        else:
            kept.append(finding)
    return kept, skipped, extra


def self_test() -> int:
    assert parse_date("-1450") == YMD(-1450, 1, 1, "year")
    assert parse_date("0054-04-01") == YMD(54, 4, 1, "day")
    assert parse_date("29") == YMD(29, 1, 1, "year")
    assert parse_span("130Y") == Span(130, 0, 0)
    assert parse_span("7Y6M") == Span(7, 6, 0)
    assert parse_span("2.5Y") == Span(2, 6, 0)
    assert parse_span("1D") == Span(0, 0, 1)
    assert parse_span("") == Span()
    a = parse_date("0053-05-01")
    b = parse_date("0053-09-01")
    assert wholly_before(a, b)
    assert not wholly_before(parse_date("0030"), parse_date("0030-05-02"))
    assert wholly_before(parse_date("0046"), parse_date("0049-10-01"))
    # FS: -4003 + 1D + 130Y is not wholly after year-only -3873
    pred = parse_date("-4003")
    expected = pred + parse_span("1D") + parse_span("130Y")
    assert not wholly_before(parse_date("-3873"), expected)
    print("self-test ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-dir", type=Path, default=Path("json"))
    parser.add_argument("--issues", type=Path, default=Path("data-quality/issues.yaml"))
    parser.add_argument("--out", type=Path, help="Write markdown to this path as well as stdout")
    parser.add_argument("--sha", default="", help="Export or HEAD sha to show in the report")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.json_dir.is_dir():
        print(f"error: json dir not found: {args.json_dir}", file=sys.stderr)
        return 2
    if not args.issues.is_file():
        print(f"error: ledger not found: {args.issues}", file=sys.stderr)
        return 2
    for name in ("people.json", "places.json", "events.json"):
        if not (args.json_dir / name).is_file():
            print(f"error: missing {args.json_dir / name}", file=sys.stderr)
            return 2

    try:
        kept, skipped, extra = run_checks(args.json_dir, args.issues)
        report = render_markdown(
            kept,
            skipped,
            args.sha,
            str(args.issues),
            unlinked_coord_groups=extra.get("unlinked_coord_groups", 0),
        )
    except Exception as exc:  # noqa: BLE001 — surface a clean CI error
        print(f"error: check failed: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(report)
    if not report.endswith("\n"):
        sys.stdout.write("\n")
    if args.out:
        args.out.write_text(report if report.endswith("\n") else report + "\n")
    # Always succeed after a completed run; findings go to the issue, not CI.
    return 0


if __name__ == "__main__":
    sys.exit(main())
