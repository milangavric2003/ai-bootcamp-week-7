"""Recheck M1 evidence from the repository root; does not change the pipeline."""
import hashlib
import json
from pathlib import Path

manifest = json.loads(Path('docs/evidence/001-baseline-manifest.json').read_text())
changed = {'src/chunking.py', 'src/config.py', 'tests/test_chunking.py'}
protected = {
    p: hashlib.sha256(Path(p).read_bytes()).hexdigest() == h
    for p, h in manifest['files_sha256'].items() if p not in changed
}
assert all(protected.values())
baseline = hashlib.sha256(Path('results/before.json').read_bytes()).hexdigest()
assert baseline == manifest['baseline_file_sha256']
starter = {
    p: hashlib.sha256((Path('rag-week-7-weak-checkpoint') / p).read_bytes()).hexdigest() == h
    for p, h in manifest['files_sha256'].items()
}
assert all(starter.values())
before = json.loads(Path('results/before.json').read_text())
after = json.loads(Path('results/after.json').read_text())
assert before['eval_set_sha256'] == after['eval_set_sha256']
assert len(before['results']) == len(after['results']) == 12
settings = [k for k in before['config'] if before['config'][k] != after['config'][k]]
assert settings == ['CHUNK_STRATEGY']
regressions = []
for old, new in zip(before['results'], after['results']):
    assert old['id'] == new['id']
    for key in ('behaviour_correct', 'retrieval_hit', 'fact_in_citations', 'citation_precision', 'pass'):
        if old[key] is not None and new[key] is not None and new[key] < old[key]:
            regressions.append([old['id'], key, old[key], new[key]])
assert not regressions, regressions
report = {
    'baseline_sha256': baseline,
    'protected_files_unchanged': protected,
    'original_starter_matches_baseline': starter,
    'eval_set_sha256': after['eval_set_sha256'],
    'question_count': 12,
    'changed_settings': settings,
    'per_question_metric_regressions': regressions,
    'implementation_diff_files': sorted(changed),
}
Path('docs/evidence/001-integrity-after.json').write_text(
    json.dumps(report, indent=2) + '\n', encoding='utf-8'
)
logs = list(Path('docs/evidence').glob('001-*-after.txt'))
logs.append(Path('docs/evidence/001-eval-compare.txt'))
for path in logs:
    raw = path.read_bytes()
    if raw.startswith(b'\xff\xfe'):
        path.write_text(raw.decode('utf-16'), encoding='utf-8')
print('Verified baseline, protected files, starter, fixed eval, one setting and no metric regressions.')
