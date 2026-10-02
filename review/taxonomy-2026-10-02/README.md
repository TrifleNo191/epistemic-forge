# Epistemic Forge: taxonomy and version-lineage review

Historical proposal against source commit `aa0555c5e1595571ac185bb9870cf493226eae1e` and Atom SHA-256 `2d7fa0be88fd2781f0e68ef248de98a99e92cf3a8e0c6709617b9e1bbdc6ca6d`. Its proposal-status fields describe the package when issued. The subsequent approved application and final export verification are recorded under [`applied/2026-10-02`](../../applied/2026-10-02/README.md).

Open `review.html` for the readable report, complete searchable 448-label map, lineage table, proposed notices, missing-label suggestions and source excerpts.

## Scope

All current records and labels indexed; version headers and full-text relationship markers screened. Targeted context review supports the alias groups, repair proposals and typed lineage edges. This is not a cover-to-cover philosophical or source-validity review of the roughly 503,000 extracted words.

July/August snapshots used to distinguish captured textual states from self-reported version history. Historical-only drafts are retained unchanged and are not relabeled by this proposal.

## Results

- 448 original labels have explicit mappings; 104 original spellings would change in Stage 1.
- 10 alias groups are proposed, with supporting context and all affected post IDs.
- Stage 1: 448 to 432 distinct labels; 75 posts affected.
- Stage 2 removes five isolated title/stance fragments and corrects Unconscious Semantic Distortion to the author's explicitly chosen Unintentional Semantic Distortion.
- Stage 3 separately proposes labels for all 37 unlabelled LIVE posts. New topics introduced: AI memory, AI prompts, Fermi paradox, Ukraine, aesthetics, casualty analysis, simulation hypothesis.
- 32 relationships are typed by evidence: supersession, partial correction, revision, companion, follow-up, parallel language version or unresolved association.
- The register covers all 150 records, including the untouched empty draft. Self-reported version histories are separate from actually captured text states in July, August and October.

## Most consequential findings

1. What You Actually Are exists at two URLs containing Version 2 and Version 4. Preserve both and add earlier-edition navigation.
2. The June 21 Epistemic Forge apex explicitly supersedes the June 12 Thermodynamic Realism apex and retires the old project name. Retain the old name as a historical label.
3. The Two Ways to Be Wrong explicitly identifies a missing correction notice for The Undivided Mind. Its correction is partial, not a blanket withdrawal.
4. The two older firewall posts already have reciprocal consolidation notices. Preserve those notices.
5. Reality Alignment Version 2 and Reality Alignment as a Persistence Strategy Version 3 are different works. Likewise, separate works each use a version/revision number 5.
6. A May-dated export record says Draft, June 2026. Keep the discrepancy unresolved; do not silently manufacture a date. UTC/local date differences elsewhere are accounted for before flagging conflicts.
7. One article explicitly declares CC0 while the repository README says CC BY 4.0. Preserve the local declarations and audit license metadata separately; no licenses are changed here.

## Proposed convention

Ordinary topics use lowercase. Proper names, acronyms and named frameworks keep meaningful capitalization. Matching topic tags group disagreement as well as agreement. Keep topic, document type, work/series, edition, status, content channel and historical era as separate fields. No era boundaries or names are proposed in this package.

Only context-supported aliases are merged. Related labels such as alignment variants, information/information theory, emotion regulation/self-regulation and historically distinct framework names remain separate. The complete hold list is in `normalization-map.json`.

## Files

- `decisions.json`: editorial input rules, specific repairs and missing-label suggestions.
- `normalization-map.json`: all 448 original labels, proposed spellings, rationale, affected IDs and held distinctions.
- `post-change-preview.json`: exact before labels and three cumulative after previews for each source record, pinned to its content hash.
- `lineage-register.json`: every record's metadata and captured versions, plus evidence-typed relationships.
- `issues-and-notices.json`: issue list and dated-notice drafts; ambiguous attributions remain marked.
- `evidence.json`: exact excerpt offsets in deterministically extracted text, source IDs and hashes.
- `coverage.json`: scope, limits and quantitative dry-run totals.
- `build_review.py`: reproduces this proposal from the fixed pre-cleanup snapshot at `snapshots/2026-10-02/feed.atom` and the legacy snapshots. It makes no network requests and never edits those feeds.

## Applying later

Review the batches separately. Before changing live labels, take a fresh backup and reconcile the source IDs, labels and content hashes. Preserve URLs, titles and original prose. Add editorial notices outside the historical text. Verify the resulting label navigation and references, preserve the reverse mapping, and make a new export after application. Public-surface consistency and era architecture follow that cleaned snapshot.

This package is ready for review, not evidence that the corpus's arguments or cited external sources have been validated.
