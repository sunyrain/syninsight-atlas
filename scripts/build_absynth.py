"""Deterministic ABSynth-shaped view of existing route-step exports; no new chemistry."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/database'
FIELDS = ['PathId', 'TargetName', 'Year', 'DOI', 'Author', 'StepId', 'RxnSMILES', 'RxnName', 'Conditions']

def read_csv(name):
    with (OUT/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def text(value):
    if value is None: return ''
    if isinstance(value, (list, dict)): return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    return str(value)

def build():
    papers = {p['paper_id']: p for p in read_csv('papers.csv')}
    bib = {p['paper_id']: p for p in json.loads((ROOT/'data/papers.json').read_text(encoding='utf-8-sig'))}
    route_export = {(r['paper_id'], r['route_id']): r for r in read_csv('route_smiles.csv')}
    datasets, paths, rows = {}, {}, []
    sources = ['data/database/route_steps.csv', 'data/database/route_smiles.csv', 'data/database/papers.csv', 'data/papers.json']
    seen = set()
    condition_keys = ['agents', 'solvents', 'temperature', 'temperature_reported', 'time', 'duration_hours', 'pressure', 'current_mA', 'operation_stages']
    for r in sorted(read_csv('route_steps.csv'), key=lambda x: (x['paper_id'], x['route_id'], int(x['step_index']))):
        pid, rid = r['paper_id'], r['route_id']
        if pid not in datasets:
            source = f'data/routes/{pid}/dataset.json'
            d = json.loads((ROOT/source).read_text(encoding='utf-8-sig'))
            datasets[pid] = (d, {s['step_id']: s for s in d['steps']}, {(v['route_id'] if v['route_id'].startswith(pid + ':route:') else f"{pid}:route:{v['route_id']}"): v for v in d['routes']})
            sources.append(source)
        d, steps, routes = datasets[pid]
        step, route = steps[r['local_step_id']], routes[rid]
        assert route['ordered_step_ids'][int(r['step_index']) - 1] == r['local_step_id']
        normalize = lambda rxn: [sorted(side.split('.')) for side in rxn.split('>')]
        assert normalize(step['substrate_product_smiles']) == normalize(r['canonical_reaction_smiles'])
        key = (rid, r['step_index'])
        assert key not in seen
        seen.add(key)
        p = bib.get(pid, {})
        conditions = '; '.join(f'{k}={text(step[k])}' for k in condition_keys if step.get(k) not in (None, '', []))
        route_label = route['route_id'].removeprefix(pid + ':route:')
        rows.append(dict(zip(FIELDS, [rid, route_label, p.get('publication_date', '')[:4], papers[pid]['doi'], p.get('first_author', ''), r['step_index'], r['canonical_reaction_smiles'], step.get('transformation', ''), conditions])))
        if rid not in paths:
            paths[rid] = {'paper_id': pid, 'title': papers[pid]['title'], 'route_type': route['route_type'], 'coverage_scope': route_export[(pid, rid)]['coverage_scope'], 'review_status': papers[pid]['review_status'], 'target_label': route['target_label'], 'target_name_basis': 'existing route label (may describe a branch or endpoint)', 'report': f'pages/data/routes/{pid}/report.html', 'dataset': f'data/routes/{pid}/dataset.json', 'steps': {}}
        paths[rid]['steps'][r['step_index']] = {'local_step_id': r['local_step_id'], 'local_event_id': r['local_event_id'], 'yield_percent': r['yield_percent'], 'structure_basis': r['structure_basis'], 'source_references': step['source_references']}
    with (OUT/'SynInsight_ABSynth_Dataset.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader(); writer.writerows(rows)
    # The supplied reference has a .csv suffix but is tab-delimited; provide an explicit TSV too.
    with (OUT/'SynInsight_ABSynth_Dataset.tsv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter='\t')
        writer.writeheader(); writer.writerows(rows)
    manifest = {'schema_version': '1.0', 'fields': FIELDS, 'rows': len(rows), 'paths_count': len(paths), 'papers_count': len(datasets), 'unique_operations': len({(r['paper_id'], r['local_step_id']) for r in read_csv('route_steps.csv')}), 'blank_counts': {k: sum(not r[k] for r in rows) for k in FIELDS}, 'scope': 'One row per operation occurrence within an existing path. Shared operations repeat across paths. Includes partial and control branches; no independent chemical admission.', 'sources_sha256': {s: hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources}, 'csv_sha256': hashlib.sha256((OUT/'SynInsight_ABSynth_Dataset.csv').read_bytes()).hexdigest(), 'paths': paths}
    (OUT/'absynth_metadata.json').write_text(json.dumps(manifest, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ('paths', 'sources_sha256', 'fields')}, ensure_ascii=False, indent=2))

if __name__ == '__main__': build()
