# Epistemic Forge

The source corpus for [Epistemic Forge](https://epistemicforge.blogspot.com), by Andraž Đurič.

**The live taxonomy cleanup and final export verification are complete.** See the [application record](applied/2026-10-02/README.md) for the verified results and the [original review](review/taxonomy-2026-10-02/README.md) for its evidence and reverse mapping.

**[`feed.atom`](feed.atom) contains the verified final export:** 149 published posts and one empty draft, with reader-comment records removed. It is identical to the fixed [post-cleanup snapshot](snapshots/2026-10-02-post-cleanup/feed.atom). The earlier source remains preserved at `snapshots/2026-10-02/feed.atom`.

The final export matches the approved labels on all 150 records: 434 distinct labels and 893 assignments, with no unlabelled published posts. Labels changed on 114 posts. Ten dated editorial notes match their exact planned HTML; removing each inserted note restores the original body. The other 140 bodies are byte-for-byte unchanged. All post IDs, titles, URLs, statuses, creation dates and exact publication timestamps are preserved. Updated timestamps changed on precisely the 115 posts with a label or note edit. The empty draft's complete entry is unchanged.

No historical era names or boundaries have been established, and the philosophical reconstruction has not begun.

## Files and conventions

| Path | Meaning |
| --- | --- |
| [`feed.atom`](feed.atom) | Latest verified comment-free export, after the approved cleanup. |
| [`snapshots/2026-10-02-post-cleanup/feed.atom`](snapshots/2026-10-02-post-cleanup/feed.atom) | Fixed final export after taxonomy changes and editorial notes. |
| [`snapshots/2026-10-02-post-cleanup/manifest.json`](snapshots/2026-10-02-post-cleanup/manifest.json) | Final source/output checksums, counts, transformation scope and provenance. |
| [`snapshots/2026-10-02/feed.atom`](snapshots/2026-10-02/feed.atom) | Fixed source before taxonomy cleanup, used by the historical review. |
| [`snapshots/2026-10-02/manifest.json`](snapshots/2026-10-02/manifest.json) | Historical source/output checksums and provenance as recorded before cleanup. Its root-feed alias describes that earlier state. |
| [`snapshots/legacy/2026-07-17/feed.atom`](snapshots/legacy/2026-07-17/feed.atom) | Comment-free copy of the original July upload: 129 LIVE, 41 DRAFT, 2 SOFT_TRASHED post records. |
| [`snapshots/legacy/2026-08-12/feed.atom`](snapshots/legacy/2026-08-12/feed.atom) | Comment-free copy of the August upload: 136 LIVE and 3 DRAFT post records. |
| [`feed2.atom`](feed2.atom) | Legacy compatibility copy of the August snapshot. **Not the current corpus.** |
| [`audit/2026-10-02/`](audit/2026-10-02/README.md) | Initial post/label inventory, comparison with earlier exports, and review candidates. |
| [`review/taxonomy-2026-10-02/`](review/taxonomy-2026-10-02/README.md) | Historical proposal: complete label map, context, lineage, notice drafts and evidence. Its proposal-status fields describe the package when issued. |
| [`applied/2026-10-02/`](applied/2026-10-02/README.md) | Application record, exact before/after labels, inserted notices, live observations and final export comparison. |
| [`tools/build_post_cleanup_2026_10_02.py`](tools/build_post_cleanup_2026_10_02.py) | Reproduce the final snapshot and comparison from the exact final ZIP. |
| [`tools/build_snapshot_2026_10_02.py`](tools/build_snapshot_2026_10_02.py) | Reproduce the historical pre-cleanup outputs from the original ZIP and existing Git history. |

Legacy dates mean **GitHub upload dates**, not verified export dates. The two original files were added on July 17 and August 12, 2026. Their originals remain available at the commits recorded in the manifest. Git history has not been rewritten.

## What was removed and what was preserved

Both October backups are retained unchanged outside this public repository. Each ZIP's SHA-256 and exact Atom member's SHA-256 are recorded in its snapshot manifest. Raw ZIPs, comments-only feeds, settings, theme and media files are excluded from this corpus update.

Each original main feed contained 17 Blogger COMMENT records. All six Atom files in the current repository tree exclude those records. The separate October comments feeds contain 15 of those same 17 comments and are excluded entirely. Older Git commits still contain their original comments; Git history has not been rewritten.

Every retained POST entry is **byte-for-byte identical** to its respective source export. Removing COMMENT records preserves post ordering, titles, content, labels, identifiers, dates, draft/trash statuses and authoring markup. HTML/XML comments within article content are part of that preserved markup. The approved live label and editorial-note changes appear in the final export and are documented under `applied/`. Live Blogger comments and settings were not changed.

Atom files are excluded from Git line-ending conversion so that their recorded byte hashes remain reproducible on Windows as well as Linux. Source whitespace is preserved deliberately.

Historical drafts are explicitly historical records. In particular, the July export contains 43 non-live posts absent from the October export. Their absence does not establish why they disappeared or whether another article supersedes them.

## Initial inventory and next steps

The pre-cleanup October snapshot has 448 distinct labels and 811 label assignments. Its initial inventory found 37 published posts without labels and eight groups differing only under a case/spacing/punctuation comparison. The subsequent contextual review and approved application are documented in `review/` and `applied/`.

The review established an explicit original-to-normalized mapping and evidence-typed version relationships. Historical arguments remain available, with dated status information added where supported. Topic labels, public content channels, and historical era labels are separate classification systems.

The final Blogger backup has been ingested and fully reconciled. Public-surface consistency, era architecture and intellectual reconstruction follow separately; they are not claimed complete here.

## Verification

With Python 3.9 or newer, verify the stored application record and both October snapshots offline:

```sh
python tools/verify_applied_cleanup_2026_10_02.py
```

With the final uploaded ZIP, reproduce and compare all four final generated outputs:

```sh
python tools/build_post_cleanup_2026_10_02.py /path/to/takeout-20261002T022607Z-1-001.zip --check
```

From a clone containing the original Git history, verify the ten historical outputs while leaving the newer root alias alone:

```sh
python tools/build_snapshot_2026_10_02.py /path/to/epistemic-forge-blogger-export-2026-10-02.xml.zip --check --snapshot-only
```

The builders check ZIP integrity, source SHA-256 values, XML validity, unique entry IDs, removal of COMMENT entries, retained-entry byte equality and exact output reproduction. The final comparison checks every post against the approved labels and reversible notices and rejects other body or metadata changes. These tools use Python's standard library and make no network requests.

Each builder is specific to its fixed source. Future exports need new dated snapshots and provenance; do not overwrite these fixed snapshots or reuse their source assertions for another export.

License: CC BY 4.0
