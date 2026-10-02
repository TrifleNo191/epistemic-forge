# Approved cleanup applied on 2 October 2026

The approved three-stage taxonomy proposal was applied to Epistemic Forge in Blogger. The saved labels on all 150 records were checked against the exact Stage 3 mapping. The 149 published posts remain published, the empty draft remains a draft, and all public URLs and displayed publication dates match the source.

| Measure | Before | After |
| --- | ---: | ---: |
| Distinct labels | 448 | 434 |
| Label assignments | 811 | 893 |
| Published posts without labels | 37 | 0 |
| Posts with a net label change | — | 114 |
| New dated editorial notes | — | 10 |

Ten evidence-supported notices identify superseded editions, revisions or partial corrections. Each complete article HTML was reread after saving and matched the planned SHA-256. Each insertion is reversible: removing the exact snippet recovers the original HTML. The uncertain retraction attribution remains held. Historical framework names, existing notices, original arguments and unresolved date/citation questions remain preserved.

Blogger initially retained older capitalization from its shared label registry. Those spellings were removed and the intended label sets restored; the duplicate Ethics/ethics pair required a separate merge. The final check used a freshly loaded complete post list, not the values typed into the editor. All 150 label sets match, with zero mismatches. The draft was excluded from bulk edits.

## Final source export verified

The fresh pre-edit Takeout feed matched the reviewed source exactly across all 150 records. After the cloud browser's URL security policy blocked the final download, the owner supplied `takeout-20261002T022607Z-1-001.zip`, requested after the final live verification. Its main Atom feed was checked against the fixed pre-cleanup source and the exact approved application.

**The complete final export comparison passed with no unexpected changes.** All 150 label sets match the approved mapping, the ten article bodies match their exact notice insertions, and the remaining 140 bodies are byte-for-byte unchanged. All IDs, titles, URLs, statuses, creation dates and exact publication timestamps are preserved. Updated timestamps and entry bytes changed on precisely the 115 posts receiving a label or note edit. The empty draft's entire entry is byte-for-byte unchanged.

The root [`feed.atom`](../../feed.atom) now matches the fixed [`2026-10-02-post-cleanup` snapshot](../../snapshots/2026-10-02-post-cleanup/feed.atom). The earlier source and legacy snapshots remain fixed. Only the final export's 17 COMMENT records were removed; every retained POST entry and its order match the supplied final Atom bytes exactly. The [snapshot manifest](../../snapshots/2026-10-02-post-cleanup/manifest.json) records source and output hashes, and `export-verification.json` records the complete per-post comparison.

Reader-comment records remain excluded from the public source corpus; live Blogger comments were not deleted. The raw Takeout archives, settings and account data are not published in this record.

## Files

- `posts.json`: all 150 source IDs, original and final labels, source content hashes, and notice flags.
- `labels.json`: the final 434-label inventory and counts.
- `notices.json`: the ten exact HTML insertions, source/target hashes, evidence IDs and held attribution.
- `verification.json`: completed live checks, observation times, pre-edit reconciliation and final export status.
- `export-verification.json`: all 150 final content/entry hashes, exact update timestamps, changed fields and reconciliation results.
- `live-ui-observation.json`: the freshly loaded post-list metadata used for the full comparison; title whitespace is compared as displayed.
- `package-manifest.json`: checksums of this application record.

The original proposal remains under [`review/taxonomy-2026-10-02`](../../review/taxonomy-2026-10-02/README.md). Its `not_applied` fields describe the proposal when issued; this directory records the subsequent application.

Verify the stored record offline with:

```sh
python tools/verify_applied_cleanup_2026_10_02.py
```

This verifies the recorded evidence and reversible patches against the pinned source, then recomputes the complete final export comparison. It does not contact Blogger. To reproduce the comment-free final feed directly from the supplied ZIP, use `tools/build_post_cleanup_2026_10_02.py` as documented in the root README. Public-surface consistency, historical era architecture, philosophical reconstruction and external fact-checking remain later work.
