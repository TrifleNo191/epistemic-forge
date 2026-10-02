#!/usr/bin/env python3
"""Verify the stored cleanup record and reversible notices; makes no network calls."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from build_post_cleanup_2026_10_02 import SNAPSHOT, json_bytes, reconcile, summary

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'applied/2026-10-02'
A = '{http://www.w3.org/2005/Atom}'


def load(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = load(RECORD / 'package-manifest.json')
    for name, expected in manifest['files'].items():
        data = (RECORD / name).read_bytes()
        assert len(data) == expected['bytes'] and digest(data) == expected['sha256'], name
    source = (ROOT / 'snapshots/2026-10-02/feed.atom').read_bytes()
    record = load(RECORD / 'posts.json')
    assert digest(source) == record['source_atom_sha256']
    entries = {e.findtext(A+'id'): e for e in ET.fromstring(source).findall(A+'entry')}
    preview = load(ROOT / 'review/taxonomy-2026-10-02/post-change-preview.json')
    targets = {p['id']: p for p in preview['posts']}
    actual = {p['id']: p for p in record['posts']}
    assert len(actual) == len(record['posts']) == 150 and set(actual) == set(entries) == set(targets)
    labels = Counter()
    for key, p in actual.items():
        original = entries[key].findtext(A+'content') or ''
        assert digest(original.encode()) == p['source_content_sha256']
        assert sorted(p['labels_before']) == sorted(targets[key]['before'])
        assert sorted(p['labels_after']) == sorted(targets[key]['stage3_missing_label_proposal'])
        assert p['status'] == targets[key]['status']
        labels.update(p['labels_after'])
        assert p['status'] != 'LIVE' or p['labels_after']
    assert len(labels) == 434 and sum(labels.values()) == 893
    assert sum(p['label_changed'] for p in actual.values()) == 114
    observation = load(RECORD / 'live-ui-observation.json')['posts']
    assert len(observation) == 150 and {p['id'] for p in observation} == set(actual)
    for observed in observation:
        p = actual[observed['id']]
        assert sorted(observed['labels']) == sorted(p['labels_after'])
        assert observed['status'] == p['status']
        assert ' '.join(observed['title'].split()) == ' '.join((p['title'] or '(Untitled)').split())
        if p['status'] == 'LIVE':
            assert observed['url'] == p['url']
    verification = load(RECORD / 'verification.json')
    checks = {p['id']: p for p in verification['notice_checks']}
    patches = load(RECORD / 'notices.json')['applied']
    assert len(patches) == len(checks) == 10
    for patch in patches:
        before = entries[patch['id']].findtext(A+'content') or ''
        offset = patch['insertion_offset']
        after = before[:offset] + patch['snippet'] + before[offset:]
        assert digest(before.encode()) == patch['before_sha256']
        assert digest(after.encode()) == patch['after_sha256'] == checks[patch['id']]['content_sha256']
        assert after[:offset] + after[offset+len(patch['snippet']):] == before
    latest = (ROOT / SNAPSHOT / 'feed.atom').read_bytes()
    assert (ROOT / 'feed.atom').read_bytes() == latest
    final_manifest = load(ROOT / SNAPSHOT / 'manifest.json')
    for key, value in summary(latest).items():
        assert final_manifest['latest'][key] == value, key
    comparison = (RECORD / 'export-verification.json').read_bytes()
    assert comparison == json_bytes(reconcile(source, latest))
    assert digest(comparison) == final_manifest['export_verification']['sha256']
    assert manifest['post_cleanup_export_verified'] is True
    assert manifest['latest_snapshot'] == SNAPSHOT + '/feed.atom'
    assert verification['post_cleanup_export_verified'] is True
    print('Verified final export and stored record: 150 posts; 114 label changes; 434 labels; 893 assignments; 10 exact reversible notices; 140 other bodies unchanged; no unexpected changes.')


if __name__ == '__main__':
    main()
