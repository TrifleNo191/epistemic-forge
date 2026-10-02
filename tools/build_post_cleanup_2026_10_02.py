#!/usr/bin/env python3
"""Reproduce the verified post-cleanup snapshot from its exact final Takeout ZIP.

Uses Python's standard library. Makes no network calls or live Blogger edits.
Only complete COMMENT records are removed from the supplied export.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from zipfile import ZipFile

from build_snapshot_2026_10_02 import (
    A, B, ROOT, SOURCE_MEMBER, COMMENT_MEMBER, entry_records, json_bytes,
    posts, remove_comments, require, sha, summary,
)

SOURCE_FILENAME = "takeout-20261002T022607Z-1-001.zip"
ZIP_SHA = "6ba43d2768d938b95d6ac59b153140f84392f26b42ae09b14e271254386e02f6"
SOURCE_SHA = "e606c633e86d29576876b626cd6dd6d379e5496bee6bd6b56e74be4a5d7ced29"
BEFORE_PATH = "snapshots/2026-10-02/feed.atom"
BEFORE_SHA = "2d7fa0be88fd2781f0e68ef248de98a99e92cf3a8e0c6709617b9e1bbdc6ca6d"
SNAPSHOT = "snapshots/2026-10-02-post-cleanup"
RECORD = "applied/2026-10-02"
BASE = "97c178090d034b8092d894a2b3c25e27a5a98c68"


def load(name):
    return json.loads((ROOT / name).read_bytes())


def stable_metadata(element):
    return [element.tag, dict(element.attrib), element.text,
            [stable_metadata(child) for child in element
             if child.tag not in {A + "category", A + "content", A + "updated"}]]


def reconcile(before, after):
    require(sha(before) == BEFORE_SHA, "Pre-cleanup snapshot changed")
    before_records = entry_records(before)
    after_records = entry_records(after)
    require(len(before_records) == len(after_records) == 150, "Expected 150 post records")
    require(all(e.findtext(B + "type") == "POST" for e, _, _ in after_records),
            "Final snapshot contains a non-POST entry")
    old = {p["id"]: p for p in posts(before)}
    new = {p["id"]: p for p in posts(after)}
    old_xml = {e.findtext(A + "id"): e for e, _, _ in before_records}
    new_xml = {e.findtext(A + "id"): e for e, _, _ in after_records}
    application = load(RECORD + "/posts.json")
    require(application["source_atom_sha256"] == BEFORE_SHA, "Application source mismatch")
    targets = {p["id"]: p for p in application["posts"]}
    patches = {p["id"]: p for p in load(RECORD + "/notices.json")["applied"]}
    require(len(targets) == 150 and old.keys() == new.keys() == targets.keys(), "Post IDs differ")
    require(len(patches) == 10 and patches.keys() <= old.keys(), "Notice IDs differ")
    unchanged_fields = ("id", "title", "status", "published", "created", "trashed",
                        "filename", "url_from_filename")
    label_changes, body_changes, updated_changes, entry_changes = set(), set(), set(), set()
    field_counts = Counter()
    records = []
    for key, p in old.items():
        q, target = new[key], targets[key]
        for field in unchanged_fields:
            require(p[field] == q[field], f"Unexpected {field} change: {key}")
        require(stable_metadata(old_xml[key]) == stable_metadata(new_xml[key]),
                "Unexpected XML metadata change: " + key)
        require(sorted(p["labels"]) == sorted(target["labels_before"]), "Original labels differ: " + key)
        require(sorted(q["labels"]) == sorted(target["labels_after"]), "Final labels differ: " + key)
        require(len(q["labels"]) == len(set(q["labels"])), "Duplicate labels: " + key)
        require(p["content_sha256"] == target["source_content_sha256"], "Original body differs: " + key)
        original = old_xml[key].findtext(A + "content") or ""
        expected = original
        if key in patches:
            patch = patches[key]
            offset = patch["insertion_offset"]
            require(0 <= offset <= len(original), "Invalid notice offset: " + key)
            expected = original[:offset] + patch["snippet"] + original[offset:]
            require(p["content_sha256"] == patch["before_sha256"], "Notice source differs: " + key)
            require(sha(expected.encode("utf-8")) == patch["after_sha256"], "Notice target differs: " + key)
        require((new_xml[key].findtext(A + "content") or "") == expected,
                "Unexpected article content: " + key)
        changed = [field for field in p if p[field] != q[field]]
        require(set(changed) <= {"labels", "updated", "entry_sha256", "content_sha256", "content_characters"},
                "Unexpected changed field: " + key)
        field_counts.update(changed)
        if set(p["labels"]) != set(q["labels"]):
            label_changes.add(key)
        if p["content_sha256"] != q["content_sha256"]:
            body_changes.add(key)
        if p["updated"] != q["updated"]:
            updated_changes.add(key)
        if p["entry_sha256"] != q["entry_sha256"]:
            entry_changes.add(key)
        if p["status"] == "DRAFT":
            require(p["entry_sha256"] == q["entry_sha256"], "Draft entry changed")
        require(q["status"] != "LIVE" or q["labels"], "Published post lacks labels: " + key)
        records.append({"id": key, "title": q["title"], "changed_fields": changed,
                        "before_content_sha256": p["content_sha256"],
                        "after_content_sha256": q["content_sha256"],
                        "before_entry_sha256": p["entry_sha256"],
                        "after_entry_sha256": q["entry_sha256"],
                        "before_updated": p["updated"], "after_updated": q["updated"]})
    require(len(label_changes) == 114, "Expected 114 label changes")
    require(label_changes == {key for key, p in targets.items() if p["label_changed"]},
            "Label change flags differ")
    require(body_changes == set(patches), "Body changes differ from the ten notices")
    require(updated_changes == entry_changes == label_changes | body_changes,
            "Unexpected entry or updated timestamp changes")
    require(len(entry_changes) == 115, "Expected 115 changed post entries")
    labels = Counter(label for p in new.values() for label in p["labels"])
    require(len(labels) == 434 and sum(labels.values()) == 893, "Final label totals differ")
    return {
        "status": "verified_against_approved_application",
        "before_snapshot": BEFORE_PATH, "before_sha256": sha(before),
        "after_snapshot": SNAPSHOT + "/feed.atom", "after_sha256": sha(after),
        "records_checked": 150, "live_posts": 149, "drafts": 1,
        "all_post_ids_titles_statuses_urls_and_publication_timestamps_preserved": True,
        "all_created_timestamps_and_other_post_metadata_preserved": True,
        "all_final_labels_match_approved_stage3": True,
        "label_changed_posts": len(label_changes), "distinct_labels": len(labels),
        "label_assignments": sum(labels.values()), "unlabelled_live_posts": 0,
        "exact_editorial_insertions": len(body_changes), "other_bodies_byte_identical": 140,
        "original_html_recovered_by_removing_each_inserted_notice": True,
        "draft_entry_byte_identical": True,
        "post_entries_changed": len(entry_changes), "post_entries_byte_identical": 35,
        "updated_timestamps_changed_only_on_edited_posts": len(updated_changes),
        "changed_field_counts": dict(sorted(field_counts.items())),
        "unexpected_changes": [], "posts": records,
    }


def build(source_zip):
    zip_bytes = source_zip.read_bytes()
    require(sha(zip_bytes) == ZIP_SHA, "Wrong final ZIP: SHA-256 mismatch")
    with ZipFile(source_zip) as archive:
        require(archive.testzip() is None, "ZIP integrity failure")
        source = archive.read(SOURCE_MEMBER)
        separate = archive.read(COMMENT_MEMBER)
    require(sha(source) == SOURCE_SHA, "Wrong final Atom: SHA-256 mismatch")
    cleaned, removed = remove_comments(source)
    require(len(removed) == 17, "Expected 17 COMMENT entries")
    separate_records = entry_records(separate)
    require(all(e.findtext(B + "type") == "COMMENT" for e, _, _ in separate_records),
            "Separate comments feed contains a non-comment entry")
    separate_ids = {e.findtext(A + "id") for e, _, _ in separate_records}
    require(separate_ids <= set(removed), "Unexpected extra comment IDs in separate feed")
    verification = reconcile((ROOT / BEFORE_PATH).read_bytes(), cleaned)
    manifest = {
        "schema_version": 1, "snapshot_date": "2026-10-02",
        "status": "Final post-cleanup export verified against the approved application",
        "repository_base_commit": BASE,
        "source_zip": {"filename": SOURCE_FILENAME, "sha256": ZIP_SHA, "bytes": len(zip_bytes),
                       "storage": "Original owner-supplied backup; excluded from this public repository"},
        "source_atom": {"zip_member": SOURCE_MEMBER, **summary(source)},
        "separate_comment_feed": {"zip_member": COMMENT_MEMBER, "sha256": sha(separate),
                                  "entries": len(separate_records), "all_also_in_main_feed": True,
                                  "published_in_repository": False},
        "transformation": {
            "operation": "Remove complete Atom entries whose blogger:type is COMMENT",
            "comments_removed_from_main_feed": len(removed), "retained_post_entries": 150,
            "retained_entries_byte_identical_to_final_export": True, "post_order_preserved": True,
            "raw_zip_unchanged": True, "git_history_rewritten": False,
            "scope_note": "HTML/XML authoring comments within post bodies are preserved. No live changes are made by this builder."},
        "latest": {"path": "feed.atom", "snapshot_path": SNAPSHOT + "/feed.atom", **summary(cleaned)},
        "pre_cleanup_snapshot": {"path": BEFORE_PATH, "sha256": BEFORE_SHA, "unchanged": True},
        "application_record": RECORD + "/README.md",
        "export_verification": {"path": RECORD + "/export-verification.json",
                                "sha256": sha(json_bytes(verification)),
                                "all_approved_changes_match": True, "unexpected_changes": 0},
    }
    return {"feed.atom": cleaned, SNAPSHOT + "/feed.atom": cleaned,
            SNAPSHOT + "/manifest.json": json_bytes(manifest),
            RECORD + "/export-verification.json": json_bytes(verification)}


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
        elif path.exists():
            if name.startswith("snapshots/"):
                require(path.read_bytes() == data, "Refusing to overwrite an immutable snapshot: " + name)
            elif name == "feed.atom":
                require(sha(path.read_bytes()) in {BEFORE_SHA, sha(data)},
                        "Current feed is an unexpected version; reconcile before replacing")
    if not args.check:
        for name, data in artifacts.items():
            path = ROOT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({"mode": "verified" if args.check else "written", "files": len(artifacts),
                      "latest": summary(artifacts["feed.atom"])}))


if __name__ == "__main__":
    main()
