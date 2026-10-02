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

## Source export remains pending

The fresh pre-edit Takeout feed matched the reviewed source exactly across all 150 records. After the live cleanup, the cloud browser's URL security policy blocked the Takeout download. A new one-time Blogger backup was requested after final verification.

**No post-cleanup Atom export has been downloaded or compared.** The root `feed.atom` and all fixed snapshots still contain the pre-cleanup source. They have not been synthesized or silently replaced. A full comparison of all article bytes and exact timestamps will be completed when the new backup is supplied. The live checks establish post identity, displayed titles/statuses, exact label sets, public URLs, publication dates to the minute, and the ten saved notice bodies. They do not substitute for an export-level comparison of the other 140 bodies.

Reader-comment records remain excluded from the public source corpus; live Blogger comments were not deleted. The raw Takeout archives, settings and account data are not published in this record.

## Files

- `posts.json`: all 150 source IDs, original and final labels, source content hashes, and notice flags.
- `labels.json`: the final 434-label inventory and counts.
- `notices.json`: the ten exact HTML insertions, source/target hashes, evidence IDs and held attribution.
- `verification.json`: completed checks, observation times, pre-edit reconciliation and the export limitation.
- `live-ui-observation.json`: the freshly loaded post-list metadata used for the full comparison; title whitespace is compared as displayed.
- `package-manifest.json`: checksums of this application record.

The original proposal remains under [`review/taxonomy-2026-10-02`](../../review/taxonomy-2026-10-02/README.md). Its `not_applied` fields describe the proposal when issued; this directory records the subsequent application.

Verify the stored record offline with:

```sh
python tools/verify_applied_cleanup_2026_10_02.py
```

This verifies the recorded evidence and reversible patches against the pinned source. It does not contact Blogger or claim to be an independent live audit. Public-surface consistency, historical era architecture, philosophical reconstruction and external fact-checking remain later work.
