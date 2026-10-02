#!/usr/bin/env python3
"""Build a source-pinned proposal. This script never edits a feed or contacts Blogger."""
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = '{http://www.w3.org/2005/Atom}'
B = '{http://schemas.google.com/blogger/2018}'
D = json.loads((HERE / 'decisions.json').read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Text(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []
        self.links = []
        self.feed(content)
        self.text = '\n'.join(x for line in ''.join(self.parts).splitlines()
                              if (x := re.sub(r'\s+', ' ', line).strip()))

    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self.skip += 1
        if tag in ('p', 'div', 'section', 'article', 'header', 'footer', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'br', 'tr'):
            self.parts.append('\n')
        if tag == 'a':
            self.links.extend(v for k, v in attrs if k == 'href' and v)

    def handle_endtag(self, tag):
        if tag in ('style', 'script') and self.skip:
            self.skip -= 1
        if tag in ('p', 'div', 'section', 'article', 'header', 'footer', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def read_posts(data):
    result = []
    for e in ET.fromstring(data).findall(A + 'entry'):
        if e.findtext(B + 'type') != 'POST':
            continue
        html = e.findtext(A + 'content') or ''
        parsed = Text(html)
        published = e.findtext(A + 'published')
        updated = e.findtext(A + 'updated')
        result.append(dict(id=e.findtext(A + 'id'), title=e.findtext(A + 'title') or '',
            status=e.findtext(B + 'status'), published_utc=published, updated_utc=updated,
            published_local=datetime.fromisoformat(published.replace('Z', '+00:00')).astimezone(ZoneInfo('Europe/Ljubljana')).isoformat(),
            updated_local=datetime.fromisoformat(updated.replace('Z', '+00:00')).astimezone(ZoneInfo('Europe/Ljubljana')).isoformat(),
            url='https://epistemicforge.blogspot.com' + (e.findtext(B + 'filename') or ''),
            labels=[c.get('term') for c in e.findall(A + 'category') if c.get('term')],
            content_sha256=digest(html.encode()), text_sha256=digest(parsed.text.encode()),
            text=parsed.text, links=parsed.links))
    result.sort(key=lambda p: p['published_utc'])
    for ordinal, p in enumerate(result, 1):
        p['ordinal'] = ordinal
    return result


raw = (ROOT / 'feed.atom').read_bytes()
assert digest(raw) == D['source_atom_sha256'], 'Source changed: reconcile before rebuilding'
POSTS = read_posts(raw)
P = {p['ordinal']: p for p in POSTS}
BY_ID = {p['id']: p for p in POSTS}
EVIDENCE = []


def evidence(ordinal, needle, purpose, limit=1000):
    post = P[ordinal]
    text = post['text']
    at = text.find(needle)
    assert at >= 0, (ordinal, needle)
    start = max(text.rfind('\n', 0, at) + 1, at - 160)
    end = text.find('\n', at)
    if end < 0:
        end = len(text)
    end = min(end, max(start + limit, at + len(needle)))
    item = dict(evidence_id=f'E{len(EVIDENCE)+1:03}', post_id=post['id'], title=post['title'],
                url=post['url'], content_sha256=post['content_sha256'], text_sha256=post['text_sha256'],
                start_character=start, end_character=end, line=text.count('\n', 0, start)+1,
                quote=text[start:end], purpose=purpose)
    EVIDENCE.append(item)
    return item['evidence_id']


def summary(post):
    return {k: post[k] for k in ('id', 'ordinal', 'title', 'status', 'url', 'published_utc', 'published_local', 'updated_utc', 'updated_local', 'content_sha256')}


all_labels = sorted({s for p in POSTS for s in p['labels']}, key=lambda s: (s.casefold(), s))
counts = Counter(s for p in POSTS for s in p['labels'])
rename = dict(D['presentation_changes'])
group_by_original = {}
for group in D['alias_groups']:
    assert set(group['originals']) <= set(all_labels)
    for label in group['originals']:
        rename[label] = group['canonical']
        group_by_original[label] = group
assert set(D['presentation_changes']) <= set(all_labels)


def canonical(label):
    return rename.get(label, label)


def unique(items):
    return list(dict.fromkeys(items))


rules = []
for label in all_labels:
    target = canonical(label)
    group = group_by_original.get(label)
    kind = 'alias_normalization' if group and target != label else 'presentation' if target != label else 'retain'
    rules.append(dict(original=label, proposed=target, operation=kind, assignments=counts[label],
        source_post_ids=[p['id'] for p in POSTS if label in p['labels']],
        rationale=group['rationale'] if group else
            'Presentation only: ordinary topics use lowercase; acronyms and named entities keep meaningful capitals; separate concatenated words.' if kind == 'presentation' else
            'No edit proposed in this pass. Retention is not validation of the term or the article claims.'))

group_evidence = [
    (140, 'Clarification note', 'metaethics'), (107, 'Where the', 'metaethics'),
    (33, 'The is-ought problem dissolved', 'is-ought problem'), (140, 'is–ought', 'is-ought problem'),
    (87, 'Meta-specification', 'philosophy of science'), (113, 'architecture', 'philosophy of science'),
    (22, 'K: recoverable complexity', 'information theory'), (66, "Landauer's principle", 'information theory'),
    (17, 'moral uncertainty', 'ethics'), (20, 'ethical behavior', 'ethics'),
    (23, 'artificial superintelligence', 'AI'), (37, 'AI systems', 'AI'), (124, 'one AI system', 'AI'),
    (68, 'Writing for the receiving paths', 'writing'), (87, 'A document is a map', 'writing'),
    (22, 'A1 Embeddedness', 'control theory'), (136, 'control', 'control theory'),
    (1, 'Landauer’s principle', "Landauer's principle"), (2, 'Landauer’s principle', "Landauer's principle"),
    (66, "Landauer's principle", "Landauer's principle"), (96, "Landauer's principle", "Landauer's principle"),
    (98, 'The firewall is what keeps them', 'is-ought firewall'), (100, 'is/ought firewall', 'is-ought firewall')]
for group in D['alias_groups']:
    group['evidence_ids'] = [evidence(n, needle, 'Label context: ' + c) for n, needle, c in group_evidence if c == group['canonical']]
    group['all_source_post_ids'] = unique(p['id'] for p in POSTS if any(l in p['labels'] for l in group['originals']))
    group['reviewed_context_post_ids'] = [P[n]['id'] for n in group['reviewed_context_ordinals']]

repair_evidence = {
    33: evidence(33, 'The is-ought problem dissolved', 'Title-fragment repair'),
    59: evidence(59, 'epistemic-fidelity dimension', 'Title-fragment repair; retain fidelity as the topic'),
    63: evidence(63, 'I use "unintentional" rather than "unconscious"', 'Explicit author choice contradicts existing label'),
}
missing = {int(k): v for k, v in D['missing_label_proposals'].items()}
assert set(missing) == {p['ordinal'] for p in POSTS if p['status'] == 'LIVE' and not p['labels']}
repairs = {r['ordinal']: r for r in D['post_specific_repairs']}
patches = []
for post in POSTS:
    before = post['labels']
    s1 = unique(canonical(x) for x in before)
    s2 = list(s1)
    if post['ordinal'] in repairs:
        repair = repairs[post['ordinal']]
        assert set(repair['remove']) <= set(before)
        s2 = [x for x in s2 if x not in {canonical(l) for l in repair['remove']}]
        s2 = unique(s2 + repair['add'])
    s3 = unique(s2 + [canonical(x) for x in missing.get(post['ordinal'], [])])
    patches.append(dict(**summary(post), before=before, stage1_existing_label_normalization=s1,
                        stage2_contextual_repairs=s2, stage3_missing_label_proposal=s3,
                        application_status='not_applied',
                        repair_evidence_id=repair_evidence.get(post['ordinal']),
                        missing_label_basis='Title, opening and relevant body context; navigation proposal, not claim validation.' if post['ordinal'] in missing else None))

EDGES = []


def edge(old, new, relation, basis, source, needle, note=''):
    EDGES.append(dict(edge_id=f'R{len(EDGES)+1:03}', source_post_id=P[old]['id'], target_post_id=P[new]['id'],
                      source_title=P[old]['title'], target_title=P[new]['title'], relation=relation,
                      basis=basis, evidence_id=evidence(source, needle, relation), note=note))


edge(60, 67, 'later_numbered_revision', 'same title plus explicit revision number; predecessor inferred', 67, 'Revised draft (rev. 2)', 'Do not assign an invented Version 1 number to the unnumbered first post.')
edge(67, 70, 'later_numbered_revision', 'same title plus explicit revision number', 70, 'Draft (rev. 3)')
for old in (70, 71, 72, 73):
    edge(old, 77, 'supersedes_and_consolidates', 'explicit author statement; target matched to uniquely named work/type', 77, 'This document supersedes and consolidates')
edge(64, 77, 'possible_consolidated_predecessor', 'target inference requires confirmation', 77, 'is-ought dissolution paper', 'The source gives a description, not a unique URL; do not automatically add a supersession notice.')
for old in (77, 73, 81):
    edge(old, 82, 'supersedes_and_consolidates', 'explicit author statement; target matched to named work/type', 82, 'This document consolidates')
edge(78, 82, 'possible_consolidated_predecessor', 'target inference requires confirmation', 82, 'meta-ethical defense', 'The phrase could denote more than one defense text.')
for old in (93, 98):
    edge(old, 100, 'supersedes_and_consolidates', 'explicit and reciprocal author notices', old, 'Now consolidated.', 'Existing notices should be preserved, not duplicated.')
edge(97, 111, 'supersedes', 'explicit named predecessor and date', 111, 'Supersedes Thermodynamic Realism: The Apex Synthesis')
edge(105, 121, 'later_edition_of_same_work', 'headers Version 2/4 and shared version history', 121, 'Version 4, 11 July 2026', 'Keep both URLs; prefer the July Version 4 for latest-edition navigation, without silently retargeting historical citations.')
edge(34, 41, 'revises', 'explicit author statement and named earlier work', 41, 'This post revises and refines the original theory')
edge(38, 39, 'follow_up', 'explicit previous-post title', 39, 'see our previous post:')
edge(39, 40, 'follow_up', 'explicit earlier-post title', 40, 'After publishing "The Failure Report')
for old in (38, 39, 40):
    edge(old, 41, 'informs_revision', 'explicit list of testing accounts', 41, 'See our testing process documented')
edge(5, 6, 'same_prompt_series', 'title and content; unnumbered predecessor', 6, 'Advanced Implementation v3.0', 'No v1/v2 post is inferred or reconstructed.')
edge(6, 7, 'later_numbered_prompt', 'explicit v3/v4 labels', 7, 'STORY ENGINE v4.0_MAXIMAL', 'Final is a historical title, not a rule against future revision.')
edge(9, 84, 'related_reformulation', 'shared name and method; supersession not asserted', 84, 'Memory anchoring is a technique', 'Do not impose a global version sequence on an independently numbered Version 1.')
edge(50, 51, 'parallel_language_version', 'English and Slovenian texts share date, ten-part sequence and corresponding prose', 51, '5. februar 2026', 'Preserve both; language variants are not duplicate posts to delete.')
edge(87, 88, 'companion', 'explicit author statement', 88, 'Companion to the High-Fidelity Maps specification')
edge(112, 113, 'companion', 'explicit parent-program description', 112, 'the companion piece, The Spine and the Web')
edge(141, 147, 'companion_without_amendment', 'explicit scope statement', 147, 'It amends nothing in the parent note')
edge(145, 146, 'extends', 'explicit dependency and next question', 146, 'The present paper takes the next step')
edge(76, 115, 'partial_correction', 'explicit target and retained/retracted scope', 115, 'One pre-pivot piece, The Undivided Mind', 'Correction concerns specific claims, not a claim that every sentence is false.')
edge(80, 82, 'closure_claim_retracted', 'retraction explicit; target identity inferred from matching distinctive closure claim', 82, 'A previous post declared it closed', 'Review the attribution before installing a notice; do not label the entire earlier article retracted.')
edge(125, 136, 'related_distinct_work', 'different titles, scopes and independent version records', 136, 'Version 3 · 12 August 2026', 'Version 3 belongs to Persistence Strategy. It is not Version 3 of Reality Alignment.')

legacy = {d: {p['id']: p for p in read_posts((ROOT / f'snapshots/legacy/{d}/feed.atom').read_bytes())}
          for d in ('2026-07-17', '2026-08-12')}
register = []
for post in POSTS:
    lines = post['text'].splitlines()
    headers = [line for line in lines[:10] if re.search(r'\b(?:Version\s+\d|Revision\s+\d|rev\.?\s*\d|v\d)', line, re.I)]
    histories = []
    for i, line in enumerate(lines):
        if line.startswith(('Version history', 'Revision history')):
            histories.append('\n'.join(lines[i:i+8]) if len(line) < 50 else line)
    available = []
    for label, indexed in list(legacy.items()) + [('2026-10-02', BY_ID)]:
        if post['id'] in indexed:
            old = indexed[post['id']]
            available.append(dict(snapshot=label, content_sha256=old['content_sha256'], status=old['status'],
                                  header_lines=[l for l in old['text'].splitlines()[:10] if re.search(r'\b(?:Version\s+\d|Revision\s+\d|rev\.?\s*\d|v\d)', l, re.I)]))
    register.append(dict(**summary(post), observed_title=post['title'], header_version_lines=headers,
                         self_reported_version_history=histories, available_snapshot_states=available,
                         caveat='Version histories are author statements. Only available snapshot states establish captured text; absent versions are not reconstructed.'))

notices = []


def notice(ordinal, target, text, status='recommended', evidence_id=None):
    notices.append(dict(post=summary(P[ordinal]), target=summary(P[target]), status=status,
                        draft=text, evidence_id=evidence_id,
                        application='Prepend a dated editorial notice outside the historical article text; do not change the URL, original title or original prose.'))


notice(97, 111, 'Historical apex statement. The author explicitly superseded this June 12, 2026 statement with Epistemic Forge: The Apex Synthesis on June 21, 2026, retiring the earlier project name. The original text remains below.')
notice(105, 121, 'Earlier edition. This page preserves Version 2 of What You Actually Are. The July page contains Version 4 and its revision history. Both editions remain available; use the July page when you intend to cite the latest edition present in the October 2, 2026 snapshot.')
notice(76, 115, 'Later correction. Section 5 of The Two Ways to Be Wrong revisits this article, retracting several claims while retaining and narrowing others. Read that correction alongside the historical text preserved below.')
notice(80, 82, 'Later qualification. Thermodynamic Realism: What It Proves and What It Bets explicitly reopens the inter-agent normativity gap and retracts an earlier closure claim. Read that passage alongside this historical article.', 'review_target_attribution')
notice(34, 41, 'Later revision. Art as Compression of Reality: Revised After Testing explicitly revises and refines this January 10, 2026 proposal. The original text remains below.')
for old, new in [(70, 77), (71, 77), (72, 77), (73, 82), (77, 82), (81, 82)]:
    notice(old, new, f'Historical source. {P[new]["title"]} explicitly identifies this work or its uniquely named role among the material it consolidates and supersedes. The original text remains below. This identifies a documented editorial relationship, not independent confirmation of the later arguments.')

for draft in notices:
    draft['evidence_id'] = next(e['evidence_id'] for e in EDGES
                                if e['source_post_id'] == draft['post']['id']
                                and e['target_post_id'] == draft['target']['id'])

issues = [
    dict(id='I01', priority='high', posts=[P[n]['id'] for n in (105, 121)], issue='Two same-title pages contain different explicit versions: 2 and 4. The June page has no link to the July edition in the snapshot.', recommendation='Retain both URLs and add the dated earlier-edition notice; store work ID and edition ID separately.'),
    dict(id='I02', priority='high', posts=[P[n]['id'] for n in (97, 111)], issue='The later apex explicitly supersedes the earlier one, whose opening still calls itself current as of June 12.', recommendation='Add an archive notice. Keep Thermodynamic Realism as a historical label; do not replace it globally with Epistemic Forge.'),
    dict(id='I03', priority='high', posts=[P[n]['id'] for n in (76, 115)], issue='The self-audit says a correction notice still needs to be added at The Undivided Mind. No reference to The Two Ways to Be Wrong appears in that older post.', recommendation='Add a partial-correction notice, preserving the distinction between withdrawn and retained claims.'),
    dict(id='I04', priority='high', posts=[P[63]['id']], issue='The label says Unconscious Semantic Distortion; the article explicitly chooses Unintentional instead.', recommendation='Use the article\'s term in the label, recording the old spelling as an alias.'),
    dict(id='I05', priority='medium', posts=[P[60]['id']], issue='The unnumbered deductive presentation says Draft, June 2026; both export publication and update dates are in May 2026. This is not explained by the timezone.', recommendation='Record the discrepancy and ask the author which field is wrong during the metadata edit. Do not invent a corrected date.'),
    dict(id='I06', priority='medium', posts=[P[n]['id'] for n in (58, 82)], issue='The May 7 work says Draft v5; the differently titled May 29 consolidation says Revision 5.', recommendation='Maintain separate work/series identities; numbers alone cannot establish a single revision chain.'),
    dict(id='I07', priority='medium', posts=[P[n]['id'] for n in (125, 136)], issue='Reality Alignment is Version 2; Reality Alignment as a Persistence Strategy is Version 3 of a different work.', recommendation='Keep their titles, scopes and version histories separate.'),
    dict(id='I08', priority='medium', posts=[P[n]['id'] for n in (105, 121, 147)], issue='What the Audit Leaves Open cites What You Actually Are as Version 2 although a Version 4 page also exists.', recommendation='Determine whether the citation intentionally depends on Version 2 before updating it. Preserve historical version-specific citations.'),
    dict(id='I09', priority='medium', posts=[P[20]['id']], issue='The article explicitly states Public domain / CC0, while the repository README states CC BY 4.0.', recommendation='Keep article-specific license text visible and audit license metadata separately. This review makes no legal determination and changes no licenses.'),
    dict(id='I10', priority='low', posts=[P[n]['id'] for n in (93, 98, 100)], issue='The two older firewall pieces already have explicit consolidation notices.', recommendation='Preserve them as an example for the missing notices; do not add duplicate banners.'),
    dict(id='I11', priority='medium', posts=[P[n]['id'] for n in missing], issue='37 published posts have no labels. The empty draft is a separate record.', recommendation='Review the proposed additions separately from existing-label normalization; do not label or delete the empty draft as part of this pass.'),
]

evidence(60, 'Draft, June 2026', 'Date discrepancy I05')
evidence(58, 'Draft v5', 'Distinct version namespace I06')
evidence(82, 'Revision 5 (fidelity edit)', 'Distinct version namespace I06')
evidence(147, 'What You Actually Are (June 2026, Version 2 July 2026)', 'Version-specific citation I08')
evidence(20, 'License: Public domain / CC0', 'Metadata difference I09; no legal conclusion')


def stage_stats(key):
    labels = [s for patch in patches for s in patch[key]]
    return dict(distinct_labels=len(set(labels)), assignments=len(labels),
                changed_posts=sum(patch[key] != patch['before'] for patch in patches),
                unlabelled_live_posts=sum(not patch[key] and patch['status'] == 'LIVE' for patch in patches))


stats = {key: stage_stats(key) for key in ['before', 'stage1_existing_label_normalization', 'stage2_contextual_repairs', 'stage3_missing_label_proposal']}
new_labels = sorted(set(s for patch in patches for s in patch['stage3_missing_label_proposal']) - set(s for patch in patches for s in patch['stage2_contextual_repairs']))
coverage = dict(source_commit=D['source_commit'], source_atom_sha256=D['source_atom_sha256'],
                records=150, live_posts=149, empty_drafts=1, exact_original_labels=448,
                scope='All current records and labels indexed; version headers and full-text relationship markers screened. Targeted context review supports the alias groups, repair proposals and typed lineage edges. This is not a cover-to-cover philosophical or source-validity review of the roughly 503,000 extracted words.',
                historical_scope='July/August snapshots used to distinguish captured textual states from self-reported version history. Historical-only drafts are retained unchanged and are not relabeled by this proposal.',
                external_verification='No live Blogger edits, HTTP link validation, literature review or factual verification of article claims was performed.',
                recommendation_status='All changes proposed; none applied.', stages=stats,
                presentation_rules=len(D['presentation_changes']), alias_groups=len(D['alias_groups']),
                changed_original_label_spellings=sum(r['original'] != r['proposed'] for r in rules),
                relationships=len(EDGES), new_topics_from_missing_label_pass=new_labels)

outputs = {
    'normalization-map.json': dict(coverage=coverage, rules=rules, alias_groups=D['alias_groups'], holds=D['hold_groups']),
    'post-change-preview.json': dict(source_sha256=D['source_atom_sha256'], stages_are_cumulative=True, posts=patches),
    'lineage-register.json': dict(scope='Editorial/document relationships, not philosophical dependency proofs', posts=register, relationships=EDGES),
    'issues-and-notices.json': dict(issues=issues, notice_drafts=notices, application_status='not_applied'),
    'evidence.json': dict(extraction='HTMLParser; exclude style/script; normalize within-line whitespace; preserve block line breaks. Character offsets refer to this extracted text, not raw XML.', evidence=EVIDENCE),
    'coverage.json': coverage,
}
for ev in EVIDENCE:
    assert BY_ID[ev['post_id']]['text'][ev['start_character']:ev['end_character']] == ev['quote']
for e in EDGES:
    assert e['source_post_id'] in BY_ID and e['target_post_id'] in BY_ID
assert len(rules) == 448 and len({r['original'] for r in rules}) == 448
assert all(p['before'] == BY_ID[p['id']]['labels'] for p in patches)
assert not patches[-1]['before'] and not patches[-1]['stage3_missing_label_proposal']

for name, obj in outputs.items():
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def table(headers, rows):
    return '<table><thead><tr>' + ''.join('<th>' + escape(h) + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + escape(str(c)) + '</td>' for c in row) + '</tr>' for row in rows) + '</tbody></table>'


html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Epistemic Forge - Taxonomy and lineage review</title><style>
body{font:16px/1.55 system-ui,sans-serif;color:#17202a;background:#f7f6f1;margin:0}main{max-width:1150px;margin:auto;padding:44px 24px 80px}h1{font-size:2.3rem;line-height:1.12}h2{margin-top:48px}h3{margin-top:30px}a{color:#145765}code{overflow-wrap:anywhere}.status{padding:14px 18px;background:#fff2c9;border-left:5px solid #af861f}.muted{color:#52616b}table{width:100%;border-collapse:collapse;background:white;margin:18px 0;font-size:.9rem}th,td{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #dce1e2;overflow-wrap:anywhere}th{background:#e6edeb}details{background:white;border:1px solid #dce1e2;padding:14px 18px;margin:14px 0}summary{font-weight:650;cursor:pointer}blockquote{border-left:3px solid #b9cecb;margin:12px 0;padding:6px 16px;color:#394d56}input{font:inherit;padding:10px;width:min(95%,650px);border:1px solid #7e939b;border-radius:5px}nav{display:flex;flex-wrap:wrap;gap:16px}section{scroll-margin-top:20px}@media(max-width:700px){main{padding:24px 14px}table{font-size:.8rem}th,td{padding:7px}h1{font-size:1.8rem}}@media print{input,nav{display:none}body{background:white}details{break-inside:avoid}}
</style><main><p class="muted">EPISTEMIC FORGE / source snapshot 2 October 2026</p><h1>Taxonomy and version-lineage review</h1><p class="status"><strong>Proposal only.</strong> The source export, historical text and live Blogger remain unchanged.</p>
<nav><a href="#summary">Decisions</a><a href="#aliases">Aliases</a><a href="#issues">Issues</a><a href="#lineage">Lineage</a><a href="#missing">Missing labels</a><a href="#map">448-label map</a><a href="#evidence">Evidence</a></nav>'''
html += '<section id="summary"><h2>Scope and decisions</h2><p>' + escape(coverage['scope']) + '</p>'
html += '<p>Use lowercase for ordinary topics, preserve proper names and acronyms, and keep historical framework names. A topic label does not certify the argument tagged with it. Do not mix topic, document type, work/series, revision status, brand channel and era into one flat classification.</p>'
html += table(['Cumulative stage', 'Distinct labels', 'Assignments', 'Posts changed', 'Published posts without labels'], [(k.replace('_', ' '), s['distinct_labels'], s['assignments'], s['changed_posts'], s['unlabelled_live_posts']) for k, s in stats.items()])
html += '<p>Stage 1 regularizes existing labels. Stage 2 repairs five isolated fragments and one explicit terminology mismatch. Stage 3 separately proposes labels for all 37 unlabelled published posts. Counts are previews, not live results.</p></section>'
html += '<section id="aliases"><h2>Recommended alias groups</h2>' + table(['Original labels', 'Proposed label', 'Why'], [(' / '.join(g['originals']), g['canonical'], g['rationale']) for g in D['alias_groups']])
html += '<h3>Keep separate or hold for judgment</h3>' + table(['Labels', 'Reason'], [(' / '.join(g['labels']), g['reason']) for g in D['hold_groups']]) + '</section>'
html += '<section id="issues"><h2>Issues and notice repairs</h2>' + table(['ID', 'Priority', 'Observation', 'Recommendation'], [(i['id'], i['priority'], i['issue'], i['recommendation']) for i in issues])
for n in notices:
    html += '<details><summary>Draft notice: ' + escape(n['post']['title']) + '</summary><p>' + escape(n['draft']) + '</p><p>Status: ' + escape(n['status']) + '. Target: <a href="' + escape(n['target']['url'], quote=True) + '">' + escape(n['target']['title']) + '</a></p></details>'
html += '</section><section id="lineage"><h2>Typed relationships</h2><p>Supersession, partial correction, companion work, parallel language edition and ordinary follow-up are recorded separately. An explicit author claim establishes an editorial relationship; it does not prove the later philosophy.</p>'
html += table(['Earlier/source work', 'Later/related work', 'Relation', 'Basis and limits', 'Evidence'], [(e['source_title'], e['target_title'], e['relation'], e['basis'] + '. ' + e['note'], e['evidence_id']) for e in EDGES]) + '</section>'
html += '<section id="missing"><h2>37 missing-label proposals</h2><p>These are a separate editorial pass. Proposed new topics: ' + escape(', '.join(new_labels)) + '.</p>'
html += table(['Post', 'Proposed labels'], [(p['title'], ', '.join(p['stage3_missing_label_proposal'])) for p in patches if p['ordinal'] in missing]) + '</section>'
html += '<section id="map"><h2>Complete label map</h2><p>Every original label has an entry. Retain means no edit is proposed, not that its conceptual adequacy has been validated.</p><label>Filter labels or rationale <input id="filter" placeholder="e.g. metaethics, AI, historical"></label><div id="labels">'
html += table(['Original', 'Proposed', 'Operation', 'Uses', 'Rationale'], [(r['original'], r['proposed'], r['operation'], r['assignments'], r['rationale']) for r in rules]) + '</div></section>'
html += '<section id="evidence"><h2>Source excerpts</h2><p>Excerpts are tied to the fixed source export and stable post IDs. Live links are navigation conveniences, not fresh verification of the current pages.</p>'
for ev in EVIDENCE:
    html += '<details id="' + ev['evidence_id'] + '"><summary>' + ev['evidence_id'] + ' · ' + escape(ev['purpose']) + '</summary><p><a href="' + escape(ev['url'], quote=True) + '">' + escape(ev['title']) + '</a> · extracted line ' + str(ev['line']) + '</p><blockquote>' + escape(ev['quote']) + '</blockquote><p class="muted">Post ID: ' + escape(ev['post_id']) + '</p></details>'
html += '</section><h2>Application sequence</h2><ol><li>Review the proposed batches and notice drafts.</li><li>Before editing Blogger, take a fresh backup and reconcile stable IDs, current labels and content hashes with this snapshot.</li><li>Apply label changes separately from historical status notices, preserving URLs, titles and article text.</li><li>Check the resulting label pages, cross-links and per-post metadata; keep an explicit reverse mapping.</li><li>Export and snapshot the cleaned result. Only then continue public-surface consistency and era design.</li></ol><p>No live changes or new era labels were applied by this review.</p></main><script>document.getElementById("filter").addEventListener("input",function(){const q=this.value.toLocaleLowerCase();document.querySelectorAll("#labels tbody tr").forEach(r=>{r.hidden=!r.textContent.toLocaleLowerCase().includes(q)});});</script></html>'
(HERE / 'review.html').write_text(html)

report = f'''# Epistemic Forge: taxonomy and version-lineage review

Proposal against source commit `{D['source_commit']}` and Atom SHA-256 `{D['source_atom_sha256']}`. No source or live-site edits applied.

Open `review.html` for the readable report, complete searchable 448-label map, lineage table, proposed notices, missing-label suggestions and source excerpts.

## Scope

{coverage['scope']}

{coverage['historical_scope']}

## Results

- {len(rules)} original labels have explicit mappings; {coverage['changed_original_label_spellings']} original spellings would change in Stage 1.
- {len(D['alias_groups'])} alias groups are proposed, with supporting context and all affected post IDs.
- Stage 1: 448 to {stats['stage1_existing_label_normalization']['distinct_labels']} distinct labels; {stats['stage1_existing_label_normalization']['changed_posts']} posts affected.
- Stage 2 removes five isolated title/stance fragments and corrects Unconscious Semantic Distortion to the author's explicitly chosen Unintentional Semantic Distortion.
- Stage 3 separately proposes labels for all 37 unlabelled LIVE posts. New topics introduced: {', '.join(new_labels)}.
- {len(EDGES)} relationships are typed by evidence: supersession, partial correction, revision, companion, follow-up, parallel language version or unresolved association.
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
- `build_review.py`: reproduces this proposal from the unchanged repository feed and legacy snapshots. It makes no network requests and never edits those feeds.

## Applying later

Review the batches separately. Before changing live labels, take a fresh backup and reconcile the source IDs, labels and content hashes. Preserve URLs, titles and original prose. Add editorial notices outside the historical text. Verify the resulting label navigation and references, preserve the reverse mapping, and make a new export after application. Public-surface consistency and era architecture follow that cleaned snapshot.

This package is ready for review, not evidence that the corpus's arguments or cited external sources have been validated.
'''
(HERE / 'README.md').write_text(report)
assert digest((ROOT / 'feed.atom').read_bytes()) == D['source_atom_sha256']
files = {p.name: dict(bytes=p.stat().st_size, sha256=digest(p.read_bytes())) for p in HERE.iterdir() if p.is_file() and p.name != 'package-manifest.json'}
(HERE / 'package-manifest.json').write_text(json.dumps(dict(source_commit=D['source_commit'], source_atom_sha256=D['source_atom_sha256'], files=files, source_unchanged=True, all_excerpts_verified=True, all_label_mappings_covered=True), indent=2) + '\n')
print(json.dumps(coverage, ensure_ascii=False, indent=2))
