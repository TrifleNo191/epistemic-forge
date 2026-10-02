# Corpus inventory: 2026-10-02

This is the initial structural inventory accompanying the source update. It is **not** a completed semantic taxonomy audit, a philosophical assessment, or a declaration of historical eras. No labels or article contents have been changed.

## Findings

| Observation | Result |
| --- | --- |
| Current post records | 150: 149 LIVE, 1 empty DRAFT |
| Reader-comment records in the current corpus | 0; 17 removed from the main export |
| Separate comments feed | Excluded; its 15 entries duplicate comments in the main export |
| Published post date range, UTC | 2025-11-05 through 2026-09-30 |
| Distinct non-empty labels | 448 |
| Label assignments | 811 |
| Labels appearing once | 352 |
| Published posts without labels | 37 |
| Mechanical label-collision groups | 8 |
| Repeated exact title | “What You Actually Are”, at separate June and July URLs |
| Exact duplicate non-empty HTML bodies | 0 |
| Posts with version/revision/supersession/retraction search matches | 75; matches require contextual interpretation |
| Recognized internal article links with targets absent from this export | 0; this is not a live HTTP check |

The empty draft has a `published` field of `2026-10-01T23:04:18.500Z` (October 2 in Europe/Ljubljana). That timestamp must not be mistaken for the date of the newest published article. The latest LIVE article is “Private Use Ends Where an Escaped File Would Do Harm”, dated September 30.

The two “What You Actually Are” entries have different HTML body hashes. Their shared title alone does not establish duplication, revision direction, or supersession. Both are retained.

## Labels to examine first

| Mechanically related labels | Assignments before any merge |
| --- | --- |
| `Meta-ethics`, `MetaEthics`, `metaethics` | 7, 20, 1 |
| `is-ought`, `is–ought` | 8, 2 |
| `Philosophy of Science`, `philosophy of science` | 8, 1 |
| `information theory`, `information-theory` | 11, 1 |
| `Ethics`, `ethics` | 7, 1 |
| `Artificial intelligence`, `Artificial Intelligence`, `ArtificialIntelligence`, `artificial intelligence` | 1, 2, 1, 1 |
| `writing`, `Writing` | 1, 1 |
| `control-theory`, `control theory` | 1, 1 |

`AI` and `Is-Ought Problem` are additional semantic-review candidates alongside their expanded or differently phrased counterparts. The mechanical comparison cannot establish whether all uses are equivalent. No replacement spellings have been selected and no merge has been applied.

The 352 one-use labels are an inventory observation, not proof that those labels should be removed. The review must distinguish useful narrow topics from accidental fragmentation, slogans, document types, project names, and status markers.

## What the repository history establishes

The old `feed.atom` was uploaded on July 17, 2026; `feed2.atom` was uploaded on August 12. Their commit messages do not explain the naming choice. There is no evidence that the filenames originally represented different corpus types.

| Comparison with October | July upload | August upload |
| --- | ---: | ---: |
| Shared POST identifiers | 129 | 139 |
| Old POST identifiers absent from October | 43 | 0 |
| October POST identifiers absent from old snapshot | 21 | 11 |
| Shared posts with changed HTML content | 2 | 1 |

All 43 July-only records were already non-live in July: 41 drafts and two soft-trashed posts. They remain in the historical snapshot, with those statuses intact. All LIVE posts in both earlier uploads have corresponding identifiers in October.

Three August drafts are LIVE in October: “The Representational Attraction Map”, “Zero Is Indexed Absence”, and “You Do Not Need to Be Uncaused to Be a Cause”. This is an observed publication-status transition, not a supersession judgment.

“The Death of Generic Media: From Infinite Cinema to the Market of One” has changed HTML content since August. “Reality Alignment” also differs from July. The machine-readable comparison identifies these changes without assigning theoretical significance to them.

## Review files

- [`posts.json`](posts.json): all 150 current records, with stable IDs, metadata, labels, and per-entry/content hashes. URLs are derived from Blogger filenames and have not been checked over HTTP.
- [`labels.json`](labels.json): exact labels, assignment counts, and the post IDs carrying each label. Empty `<category/>` placeholders are not labels.
- [`label-candidates.json`](label-candidates.json): the eight mechanical groups and two semantic-review groups. All remain unapproved.
- [`structure.json`](structure.json): label gaps, duplicate-title candidates, and text excerpts around version/status terms. Matches may refer to citations or other works.
- [`history-comparison.json`](history-comparison.json): identifier-based comparisons against both earlier snapshots, including historical-only records.
- [`../../snapshots/2026-10-02/manifest.json`](../../snapshots/2026-10-02/manifest.json): source hashes, output hashes, and exact transformation scope.

## Next review

Read the posts associated with each candidate label group before choosing canonical labels. Then inventory explicit versions, revision notices, and cross-links; build a reviewed lineage map; and assess whether older posts give readers sufficient notice of subsequent revisions. Keep textual evidence separate from editorial inference.

Only after that review should a normalization map be applied to Blogger and mirrored here. The later website/public-surface audit and era design remain separate stages. Historical text should not be silently rewritten to match later conclusions.

## Verification completed

The exact source ZIP passed integrity and SHA-256 checks. All 11 generated files were reproduced and compared successfully. A separate verification compared the source and output XML fields and raw POST-entry byte sequences; current, July, and August records all matched their respective sources. All five Atom files in the current tree contain only POST records, and the documentation's relative file links resolve locally.

Original trailing whitespace inside Atom content is preserved as source data. It has not been reformatted to satisfy code whitespace conventions.
