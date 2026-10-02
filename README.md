# Epistemic Forge

The source corpus for [Epistemic Forge](https://epistemicforge.blogspot.com), by Andraž Đurič.

**The live taxonomy cleanup is applied.** See the [application record](applied/2026-10-02/README.md) for the verified results and the [original review](review/taxonomy-2026-10-02/README.md) for its evidence and reverse mapping.

**[`feed.atom`](feed.atom) still contains the pre-cleanup source export:** 149 published posts and one empty draft. Its reader-comment records are removed, but its labels and article bodies predate the live cleanup. The final Takeout download was blocked by the cloud browser's URL security policy. A new backup has been requested; the feed will be refreshed only after that export is available and reconciled.

The live check covered all 150 post IDs, displayed titles and statuses, all saved labels, and all 149 public URLs and publication dates to the minute. It found 434 distinct labels and 893 assignments, with no unlabelled published posts. Labels differ from the source on 114 posts. Ten dated editorial notes were added and their complete HTML was verified after reopening; removing each inserted note restores the exact original HTML. The other article bodies were not edited, but a complete post-cleanup export comparison remains pending.

No historical era names or boundaries have been established, and the philosophical reconstruction has not begun.

## Files and conventions

| Path | Meaning |
| --- | --- |
| [`feed.atom`](feed.atom) | Latest verified comment-free export; currently the **pre-cleanup** source. |
| [`snapshots/2026-10-02/feed.atom`](snapshots/2026-10-02/feed.atom) | Fixed copy of the latest corpus before taxonomy cleanup. |
| [`snapshots/2026-10-02/manifest.json`](snapshots/2026-10-02/manifest.json) | Source and output checksums, record counts, transformation scope, and provenance. |
| [`snapshots/legacy/2026-07-17/feed.atom`](snapshots/legacy/2026-07-17/feed.atom) | Comment-free copy of the original July upload: 129 LIVE, 41 DRAFT, 2 SOFT_TRASHED post records. |
| [`snapshots/legacy/2026-08-12/feed.atom`](snapshots/legacy/2026-08-12/feed.atom) | Comment-free copy of the August upload: 136 LIVE and 3 DRAFT post records. |
| [`feed2.atom`](feed2.atom) | Legacy compatibility copy of the August snapshot. **Not the current corpus.** |
| [`audit/2026-10-02/`](audit/2026-10-02/README.md) | Initial post/label inventory, comparison with earlier exports, and review candidates. |
| [`review/taxonomy-2026-10-02/`](review/taxonomy-2026-10-02/README.md) | Historical proposal: complete label map, context, lineage, notice drafts and evidence. Its proposal-status fields describe the package when issued. |
| [`applied/2026-10-02/`](applied/2026-10-02/README.md) | Current application record, exact before/after labels, inserted notices, and verification limits. |
| [`tools/build_snapshot_2026_10_02.py`](tools/build_snapshot_2026_10_02.py) | Reproduce or verify this particular snapshot from its exact source ZIP and the existing Git history. |

Legacy dates mean **GitHub upload dates**, not verified export dates. The two original files were added on July 17 and August 12, 2026. Their originals remain available at the commits recorded in the manifest. Git history has not been rewritten.

## What was removed and what was preserved

The original October backup is retained unchanged outside this public repository. Its SHA-256 and the exact Atom member's SHA-256 are recorded in the manifest. The raw ZIP, comments-only feed, settings, theme, and media files are not included in this corpus update.

Each original main feed contained 17 Blogger COMMENT records. Those records were removed from all five Atom files in the current repository tree. The separate October comments feed contains 15 of those same 17 comments and was excluded entirely. Older Git commits still contain their original comments; this is corpus cleanup, not a historical data purge.

Every retained POST entry in these fixed source exports is **byte-for-byte identical** to its respective source. Post ordering, titles, content, labels, identifiers, dates, draft/trash statuses, and authoring markup are preserved. HTML/XML comments within article content are part of that preserved markup. The later live label and editorial-note changes are recorded separately under `applied/`. Live Blogger comments and settings were not changed.

Atom files are excluded from Git line-ending conversion so that their recorded byte hashes remain reproducible on Windows as well as Linux. Source whitespace is preserved deliberately.

Historical drafts are explicitly historical records. In particular, the July export contains 43 non-live posts absent from the October export. Their absence does not establish why they disappeared or whether another article supersedes them.

## Initial inventory and next steps

The pre-cleanup October snapshot has 448 distinct labels and 811 label assignments. Its initial inventory found 37 published posts without labels and eight groups differing only under a case/spacing/punctuation comparison. The subsequent contextual review and approved application are documented in `review/` and `applied/`.

The review established an explicit original-to-normalized mapping and evidence-typed version relationships. Historical arguments remain available, with dated status information added where supported. Topic labels, public content channels, and historical era labels are separate classification systems.

The remaining immediate step is to ingest and reconcile the final Blogger backup. Public-surface consistency, era architecture and intellectual reconstruction follow separately; they are not claimed complete here.

## Verification

From a clone containing the original Git history, with Python 3.9 or newer and the original uploaded ZIP:

```sh
python tools/build_snapshot_2026_10_02.py /path/to/epistemic-forge-blogger-export-2026-10-02.xml.zip --check
```

The verifier checks ZIP integrity, source SHA-256 values, XML validity, unique entry IDs, removal of COMMENT entries, retained-entry byte equality, and exact reproduction of all 11 generated outputs. It uses Python's standard library and makes no network requests.

The script is deliberately specific to this source snapshot. Future exports need new dated snapshots and provenance; do not overwrite this fixed snapshot or reuse its source assertions for another export.

License: CC BY 4.0
