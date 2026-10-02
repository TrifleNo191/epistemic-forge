#!/usr/bin/env python3
"""Reproduce or verify the 2026-10-02 corpus snapshot with Python's standard library.

Only whole COMMENT entries are removed. Retained entry bytes are never serialized.
Requires the original uploaded ZIP and this repository's existing Git history.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import urlsplit, unquote
from xml.parsers import expat
import xml.etree.ElementTree as ET
from zipfile import ZipFile

A = "{http://www.w3.org/2005/Atom}"
B = "{http://schemas.google.com/blogger/2018}"
ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-10-02"
BASE = "db243e9ab8d427f07c8a74a4343862d3b87c2486"
SOURCE_MEMBER = "Takeout/Blogger/Blogs/Epistemic Forge/feed.atom"
COMMENT_MEMBER = "Takeout/Blogger/Comments/Epistemic Forge/feed.atom"
SOURCE_SHA = "45dc9ed7da68533b7facaceb6120e03111ab90bdf209595560db58d677619f02"
ZIP_SHA = "9fb8896b1787e09222dbe67fbb934726e7cc50a9e806425685f3be9cd9c1b42b"
LEGACY = [
    ("2026-07-17", "feed.atom", "f3ddc67dbba3c2d1649cd90fe4a09aa3a8feaf61"),
    ("2026-08-12", "feed2.atom", BASE),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def entry_records(data):
    """Use the XML parser's byte positions, avoiding regex-based XML editing."""
    require(b"<!DOCTYPE" not in data.upper(), "DOCTYPE is not supported")
    parser = expat.ParserCreate(namespace_separator="}")
    spans = []
    depth = 0
    start = None

    def on_start(name, attrs):
        nonlocal depth, start
        if depth == 1 and name == A[1:] + "entry":
            start = parser.CurrentByteIndex
        depth += 1

    def on_end(name):
        nonlocal depth
        if depth == 2 and name == A[1:] + "entry":
            end = data.find(b">", parser.CurrentByteIndex) + 1
            require(end > 0, "Entry closing tag not found")
            spans.append((start, end))
        depth -= 1

    parser.StartElementHandler = on_start
    parser.EndElementHandler = on_end
    parser.Parse(data, True)
    root = ET.fromstring(data)
    require(root.tag == A + "feed", "Expected an Atom feed")
    elements = root.findall(A + "entry")
    require(len(spans) == len(elements), "Entry span count mismatch")
    ids = [e.findtext(A + "id") for e in elements]
    require(all(ids) and len(set(ids)) == len(ids), "Missing or duplicate entry IDs")
    return [(element, begin, end) for element, (begin, end) in zip(elements, spans)]


def remove_comments(data):
    records = entry_records(data)
    pieces = []
    cursor = 0
    removed = []
    retained = []
    for element, start, end in records:
        kind = element.findtext(B + "type")
        require(kind in {"POST", "COMMENT"}, "Unexpected record type: " + str(kind))
        if kind == "COMMENT":
            pieces.append(data[cursor:start])
            cursor = end
            removed.append(element.findtext(A + "id"))
        else:
            retained.append((element.findtext(A + "id"), data[start:end]))
    pieces.append(data[cursor:])
    result = b"".join(pieces)
    result_records = entry_records(result)
    require(all(e.findtext(B + "type") == "POST" for e, _, _ in result_records),
            "Comment or unexpected entry remains")
    actual = [(e.findtext(A + "id"), result[s:t]) for e, s, t in result_records]
    require(actual == retained, "Retained entry bytes or ordering changed")
    return result, removed


class BodyParser(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts = []
        self.links = []
        self.feed(html)
        self.text = re.sub(r"\s+", " ", " ".join(self.parts)).strip()

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href" and v)

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def posts(data):
    result = []
    for e, start, end in entry_records(data):
        if e.findtext(B + "type") != "POST":
            continue
        content = e.findtext(A + "content") or ""
        filename = e.findtext(B + "filename") or ""
        result.append({
            "id": e.findtext(A + "id"),
            "title": e.findtext(A + "title") or "",
            "status": e.findtext(B + "status"),
            "published": e.findtext(A + "published"),
            "updated": e.findtext(A + "updated"),
            "created": e.findtext(B + "created"),
            "trashed": e.findtext(B + "trashed") or None,
            "filename": filename,
            "url_from_filename": "https://epistemicforge.blogspot.com" + filename if filename else None,
            "labels": [c.get("term") for c in e.findall(A + "category") if c.get("term")],
            "content_sha256": sha(content.encode("utf-8")),
            "entry_sha256": sha(data[start:end]),
            "content_characters": len(content),
        })
    return result


def summary(data):
    records = entry_records(data)
    ps = posts(data)
    live = [p for p in ps if p["status"] == "LIVE" and not p["trashed"]]
    dated = sorted(live, key=lambda p: datetime.fromisoformat(p["published"].replace("Z", "+00:00")))
    labels = Counter(label for p in ps for label in p["labels"])
    return {
        "bytes": len(data), "sha256": sha(data),
        "entry_count": len(records),
        "types": dict(sorted(Counter(e.findtext(B + "type") for e, _, _ in records).items())),
        "post_statuses": dict(sorted(Counter(p["status"] for p in ps).items())),
        "live_post_published_range_utc": [dated[0]["published"], dated[-1]["published"]],
        "distinct_labels": len(labels), "label_assignments": sum(labels.values()),
    }


def json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build(source_zip):
    zip_bytes = source_zip.read_bytes()
    require(sha(zip_bytes) == ZIP_SHA, "Wrong source ZIP: SHA-256 mismatch")
    with ZipFile(source_zip) as archive:
        require(archive.testzip() is None, "ZIP integrity failure")
        source = archive.read(SOURCE_MEMBER)
        separate = archive.read(COMMENT_MEMBER)
    require(sha(source) == SOURCE_SHA, "Wrong source Atom: SHA-256 mismatch")
    cleaned, removed = remove_comments(source)
    separate_ids = {e.findtext(A + "id") for e, _, _ in entry_records(separate)}
    require(separate_ids <= set(removed), "Unexpected extra comment IDs in separate feed")
    artifacts = {"feed.atom": cleaned, f"snapshots/{DATE}/feed.atom": cleaned}
    raw_posts = posts(source)
    source_by_id = {p["id"]: p for p in raw_posts}
    comparisons = []
    legacy_sources = []
    for date, old_path, commit in LEGACY:
        original = subprocess.check_output(["git", "show", f"{commit}:{old_path}"], cwd=ROOT)
        legacy_clean, legacy_removed = remove_comments(original)
        path = f"snapshots/legacy/{date}/feed.atom"
        artifacts[path] = legacy_clean
        if old_path == "feed2.atom":
            artifacts["feed2.atom"] = legacy_clean
        old = {p["id"]: p for p in posts(original)}
        common = sorted(old.keys() & source_by_id.keys())
        changes = []
        fields = ["title", "status", "published", "updated", "labels", "content_sha256", "filename"]
        for key in common:
            fields_changed = [f for f in fields if old[key][f] != source_by_id[key][f]]
            if fields_changed:
                changes.append({"id": key, "title": source_by_id[key]["title"],
                                "changed_fields": fields_changed,
                                "old_status": old[key]["status"], "new_status": source_by_id[key]["status"]})
        comparisons.append({
            "legacy_upload_date": date, "legacy_commit": commit, "legacy_path": path,
            "common_post_ids": len(common),
            "absent_from_latest": [old[k] for k in sorted(old.keys() - source_by_id.keys())],
            "new_in_latest": [source_by_id[k] for k in sorted(source_by_id.keys() - old.keys())],
            "changes": changes,
            "interpretation": "Absence, revision and status changes are observations, not supersession decisions.",
        })
        legacy_sources.append({
            "date_basis": "Git upload date; original export time is unknown",
            "date": date, "original_path": old_path, "original_commit": commit,
            "original": summary(original), "derivative_path": path,
            "comments_removed": len(legacy_removed), "derivative": summary(legacy_clean),
        })
    manifest = {
        "schema_version": 1, "snapshot_date": DATE, "timezone": "Europe/Ljubljana",
        "status": "Pre-taxonomy-cleanup source snapshot; no era designation established",
        "repository_base_commit": BASE,
        "source_zip": {"filename": source_zip.name, "sha256": ZIP_SHA, "bytes": len(zip_bytes),
                       "storage": "Original owner-held uploaded backup; not committed to this public repository"},
        "source_atom": {"zip_member": SOURCE_MEMBER, **summary(source)},
        "separate_comment_feed": {"zip_member": COMMENT_MEMBER, "sha256": sha(separate),
                                  "entries": len(separate_ids), "all_also_in_main_feed": True,
                                  "published_in_repository": False},
        "transformation": {
            "operation": "Remove complete Atom entries whose blogger:type is COMMENT",
            "comments_removed_from_main_feed": len(removed),
            "retained_post_entries": len(raw_posts), "retained_entries_byte_identical": True,
            "post_order_preserved": True, "empty_draft_retained": True,
            "post_text_labels_dates_ids_and_statuses_unchanged": True,
            "raw_zip_unchanged": True, "live_blogger_changed": False,
            "git_history_rewritten": False,
            "scope_note": "Blogger comment records removed; HTML/XML authoring comments inside post bodies are retained.",
        },
        "latest": {"path": "feed.atom", "snapshot_path": f"snapshots/{DATE}/feed.atom", **summary(cleaned)},
        "legacy_sources": legacy_sources,
        "atom_files": {p: {"sha256": sha(d), "bytes": len(d)} for p, d in sorted(artifacts.items())},
    }
    artifacts[f"snapshots/{DATE}/manifest.json"] = json_bytes(manifest)
    ordered = sorted(raw_posts, key=lambda p: (p["published"], p["id"]))
    by_label = defaultdict(list)
    for p in ordered:
        for label in p["labels"]:
            by_label[label].append(p["id"])
    label_rows = [{"label": label, "assignments": len(ids), "post_ids": ids}
                  for label, ids in sorted(by_label.items(), key=lambda item: (item[0].casefold(), item[0]))]
    groups = defaultdict(list)
    for label in by_label:
        key = "".join(c for c in unicodedata.normalize("NFKC", label).casefold() if c.isalnum())
        groups[key].append(label)
    collisions = [{"comparison_key": key, "labels": sorted(labels), "status": "needs_context_review"}
                  for key, labels in sorted(groups.items()) if len(labels) > 1]
    candidates = {
        "status": "Review candidates only. No labels changed; string similarity does not establish semantic identity.",
        "mechanical_rule": "Unicode NFKC, case-fold, retain alphanumeric characters",
        "mechanical_groups": collisions,
        "additional_semantic_candidates": [
            {"labels": ["is-ought", "is–ought", "Is-Ought Problem"],
             "question": "Do all occurrences denote the same topic or distinct uses of the relation/problem?"},
            {"labels": ["AI", "Artificial intelligence", "Artificial Intelligence", "ArtificialIntelligence", "artificial intelligence"],
             "question": "Are abbreviation and expanded labels coextensive across these posts? Keep narrower AI topics separate."},
        ],
    }
    titles = defaultdict(list)
    body_hashes = defaultdict(list)
    for p in ordered:
        if p["title"]:
            titles[p["title"]].append(p["id"])
        if p["content_characters"]:
            body_hashes[p["content_sha256"]].append(p["id"])
    all_paths = {p["filename"] for p in ordered if p["filename"]}
    unindexed_links = []
    markers = []
    pattern = re.compile(r"\b(?:version\s*|revision\s*|rev\.?\s*|v\s*)\d+(?:\.\d+)*\b|\bsupersed\w*|\bretract\w*", re.I)
    for e, _, _ in entry_records(cleaned):
        parsed = BodyParser(e.findtext(A + "content") or "")
        post_id = e.findtext(A + "id")
        hits = [{"match": m.group(), "context": parsed.text[max(0, m.start()-90):m.end()+130]}
                for m in pattern.finditer(parsed.text)]
        if hits:
            markers.append({"post_id": post_id, "text_matches": hits,
                            "note": "Search clues only; may refer to citations or other works rather than this post."})
        for href in sorted(set(parsed.links)):
            url = urlsplit(href)
            if url.hostname in {"epistemicforge.blogspot.com", "www.epistemicforge.blogspot.com"} or (not url.hostname and href.startswith("/")):
                path = unquote(url.path)
                if re.match(r"^/\d{4}/\d{2}/.+\.html$", path) and path not in all_paths:
                    unindexed_links.append({"from_post_id": post_id, "href": href,
                                           "status": "Target absent from export; HTTP availability not checked"})
    structure = {
        "scope": "Mechanical inventory, not a completed semantic, lineage, live-link or philosophical audit",
        "live_posts_without_labels": [p["id"] for p in ordered if p["status"] == "LIVE" and not p["labels"]],
        "empty_draft_ids": [p["id"] for p in ordered if p["status"] == "DRAFT" and not p["title"] and not p["content_characters"]],
        "duplicate_titles": [{"title": t, "post_ids": ids} for t, ids in titles.items() if len(ids) > 1],
        "exact_duplicate_html_bodies": [{"sha256": h, "post_ids": ids} for h, ids in body_hashes.items() if len(ids) > 1],
        "internal_article_links_absent_from_export": unindexed_links,
        "version_and_status_text_candidates": markers,
    }
    audit = f"audit/{DATE}"
    artifacts[audit + "/posts.json"] = json_bytes({"source_sha256": SOURCE_SHA, "posts": ordered,
                                                  "url_note": "URLs derived from Blogger filenames; not live-verified"})
    artifacts[audit + "/labels.json"] = json_bytes({"distinct_labels": len(by_label),
        "assignments": sum(len(v) for v in by_label.values()),
        "labels_used_once": sum(len(v) == 1 for v in by_label.values()), "labels": label_rows})
    artifacts[audit + "/label-candidates.json"] = json_bytes(candidates)
    artifacts[audit + "/structure.json"] = json_bytes(structure)
    artifacts[audit + "/history-comparison.json"] = json_bytes(comparisons)
    return artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_zip", type=Path)
    parser.add_argument("--check", action="store_true", help="Verify outputs without writing")
    args = parser.parse_args()
    artifacts = build(args.source_zip)
    for name, data in artifacts.items():
        path = ROOT / name
        if args.check:
            require(path.is_file() and path.read_bytes() == data, "Output mismatch: " + name)
        else:
            if path.exists() and name.startswith("snapshots/"):
                require(path.read_bytes() == data, "Refusing to overwrite a different immutable snapshot: " + name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({"mode": "verified" if args.check else "written", "files": len(artifacts),
                      "latest": summary(artifacts["feed.atom"])}))


if __name__ == "__main__":
    main()
