# Epistemic Forge

The source corpus for [Epistemic Forge](https://epistemicforge.blogspot.com), by Andraž Đurič.

**Start with [`feed.atom`](feed.atom).** It is the latest checked Blogger export with reader-comment records removed. As of the **2026-10-02 snapshot**, it contains **149 published posts and one empty draft**. “Latest” identifies the current source snapshot, not an endorsement of every historical argument in it.

This repository is preparing for a corpus and taxonomy review. No historical era names or boundaries have been established, and the philosophical reconstruction has not begun.

## Files and conventions

| Path | Meaning |
| --- | --- |
| [`feed.atom`](feed.atom) | Latest comment-free corpus; stable path for readers and tools. |
| [`snapshots/2026-10-02/feed.atom`](snapshots/2026-10-02/feed.atom) | Fixed copy of the latest corpus before taxonomy cleanup. |
| [`snapshots/2026-10-02/manifest.json`](snapshots/2026-10-02/manifest.json) | Source and output checksums, record counts, transformation scope, and provenance. |
| [`snapshots/legacy/2026-07-17/feed.atom`](snapshots/legacy/2026-07-17/feed.atom) | Comment-free copy of the original July upload: 129 LIVE, 41 DRAFT, 2 SOFT_TRASHED post records. |
| [`snapshots/legacy/2026-08-12/feed.atom`](snapshots/legacy/2026-08-12/feed.atom) | Comment-free copy of the August upload: 136 LIVE and 3 DRAFT post records. |
| [`feed2.atom`](feed2.atom) | Legacy compatibility copy of the August snapshot. **Not the current corpus.** |
| [`audit/2026-10-02/`](audit/2026-10-02/README.md) | Initial post/label inventory, comparison with earlier exports, and review candidates. |
| [`tools/build_snapshot_2026_10_02.py`](tools/build_snapshot_2026_10_02.py) | Reproduce or verify this particular snapshot from its exact source ZIP and the existing Git history. |

Legacy dates mean **GitHub upload dates**, not verified export dates. The two original files were added on July 17 and August 12, 2026. Their originals remain available at the commits recorded in the manifest. Git history has not been rewritten.

## What was removed and what was preserved

The original October backup is retained unchanged outside this public repository. Its SHA-256 and the exact Atom member's SHA-256 are recorded in the manifest. The raw ZIP, comments-only feed, settings, theme, and media files are not included in this corpus update.

Each original main feed contained 17 Blogger COMMENT records. Those records were removed from all five Atom files in the current repository tree. The separate October comments feed contains 15 of those same 17 comments and was excluded entirely. Older Git commits still contain their original comments; this is corpus cleanup, not a historical data purge.

Every retained POST entry is **byte-for-byte identical** to its respective source. Post ordering, titles, content, labels, identifiers, dates, draft/trash statuses, and authoring markup are preserved. HTML/XML comments within article content are part of that preserved markup. No changes have been made to live Blogger comments, posts, labels, or settings.

Atom files are excluded from Git line-ending conversion so that their recorded byte hashes remain reproducible on Windows as well as Linux. Source whitespace is preserved deliberately.

Historical drafts are explicitly historical records. In particular, the July export contains 43 non-live posts absent from the October export. Their absence does not establish why they disappeared or whether another article supersedes them.

## Initial inventory and next steps

The October snapshot has 448 distinct labels and 811 label assignments. The initial inventory found 37 published posts without labels and eight groups of labels differing only under a case/spacing/punctuation comparison. These are review candidates, not approved merges.

The next stage is to read the relevant posts, establish label meanings and version relationships, and produce an explicit original-to-normalized mapping. Preserve historical arguments and add visible status information where warranted. Topic labels, public content channels, and historical era labels are separate classification systems.

The working sequence is: source snapshot; corpus and taxonomy review; reviewed cleanup; public-surface consistency; era architecture; a fixed cleaned boundary snapshot; intellectual reconstruction. This commit completes the source update and initial inventory, not the full review.

## Verification

From a clone containing the original Git history, with Python 3.9 or newer and the original uploaded ZIP:

```sh
python tools/build_snapshot_2026_10_02.py /path/to/epistemic-forge-blogger-export-2026-10-02.xml.zip --check
```

The verifier checks ZIP integrity, source SHA-256 values, XML validity, unique entry IDs, removal of COMMENT entries, retained-entry byte equality, and exact reproduction of all 11 generated outputs. It uses Python's standard library and makes no network requests.

The script is deliberately specific to this source snapshot. Future exports need new dated snapshots and provenance; do not overwrite this fixed snapshot or reuse its source assertions for another export.

License: CC BY 4.0
