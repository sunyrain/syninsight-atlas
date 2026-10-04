"""Compile source-operation tasks, route-endpoint tasks and an auditable review queue.

Candidate tasks are executable; compilation never fabricates independent admission.
Model inputs contain no reference route, condition, paper label or DOI.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
from rdkit import Chem, rdBase
from rdkit.Chem import rdMolDescriptors
from benchmark_common import (ROOT, STOCK, CONDITION_KEYS, Stock, canonical, reaction_key,
                              stable_id, write_json, write_jsonl)


def molsmiles(molecule):
    return molecule.get('canonical_isomeric_smiles') or molecule['canonical_smiles']


def operation_kind(s, event):
    if s.get('benchmark_operation_kind'):
        return s['benchmark_operation_kind']
    category = s.get('category') or event.get('category', '')
    if category in ('physical_separation', 'unsuccessful_target_attempt', 'historical_preparation_boundary'):
        return category
    if category == 'chemical_graph_only':
        return 'graph_only_connection'
    if (s.get('experimental_stage_count') or 0) > 1:
        return 'multistage_operation'
    if s.get('experimental_stage_count') == 1:
        return 'reported_single_operation'
    return 'operation_segmentation_unresolved'


def route_trace(route, steps, molecules):
    """Time-resolved source-label graph; a later product cannot supply an earlier input."""
    producers, dependency, leaves, instances = {}, {}, {}, {}
    errors = []
    for sid in route['ordered_step_ids']:
        if sid not in steps:
            errors.append({'type': 'unknown_step', 'step_id': sid}); continue
        s = steps[sid]
        needed = []
        for label in s['reactant_labels']:
            if label not in molecules:
                errors.append({'type': 'unknown_molecule', 'label': label}); continue
            if label in producers:
                needed.append(producers[label])
            else:
                leaves[label] = canonical(molsmiles(molecules[label]))
        dependency[sid] = needed
        instances[sid] = s
        for label in s['product_labels']:
            producers[label] = sid
    target = route['target_label']
    ancestry = set()
    def visit(sid):
        if sid in ancestry:
            return
        ancestry.add(sid)
        for prev in dependency.get(sid, []):
            visit(prev)
    if target not in producers:
        errors.append({'type': 'target_not_produced', 'label': target})
    else:
        visit(producers[target])
    declared = set(route.get('start_labels') or [route.get('start_label')])
    return {'external_start_smiles': sorted(set(leaves.values())),
            'external_start_labels': sorted(leaves),
            'undeclared_start_labels': sorted(set(leaves) - declared),
            'target_ancestry_step_ids': [s for s in route['ordered_step_ids'] if s in ancestry],
            'off_target_step_ids': [s for s in route['ordered_step_ids'] if s not in ancestry],
            'errors': errors}


class Groups:
    def __init__(self, ids):
        self.parent = {p: p for p in ids}
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def join(self, a, b):
        a, b = self.find(a), self.find(b)
        self.parent[max(a, b)] = min(a, b)


def build(output, stock=None):
    datasets = {p.parent.name: json.loads(p.read_text(encoding='utf-8-sig'))
                for p in sorted((ROOT / 'data/routes').glob('*/dataset.json'))}
    bib = {p['paper_id']: p for p in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8-sig'))}
    groups = Groups(datasets)
    seen_anchors = {}
    operations, routes, issues, sources = [], [], [], {}
    with (ROOT / 'data/database/route_smiles.csv').open(encoding='utf-8-sig', newline='') as f:
        coverage = {(r['paper_id'], r['route_id']): r['coverage_scope'] for r in csv.DictReader(f)}
    for pid, d in datasets.items():
        path = ROOT / 'data/routes' / pid / 'dataset.json'
        sources[str(path.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(path.read_bytes()).hexdigest()
        molecules = {m['label']: m for m in d['molecules']}
        steps = {s['step_id']: s for s in d['steps']}
        events = {e['event_id']: e for e in d['reactions']}
        artifacts = {s['source_id']: s for s in d.get('sources', [])}
        anchors = {('paper_family', str(bib.get(pid, {}).get('article_family_id') or d.get('doi') or pid))}
        for m in molecules.values():
            try:
                mol = Chem.MolFromSmiles(molsmiles(m))
                canonical(molsmiles(m))
                expected = m.get('molecular_formula')
                if expected and expected != rdMolDescriptors.CalcMolFormula(mol):
                    issues.append({'paper_id': pid, 'kind': 'formula_disagreement', 'label': m['label']})
            except Exception as exc:
                issues.append({'paper_id': pid, 'kind': 'invalid_molecule', 'label': m['label'], 'detail': str(exc)})
        for s in d['steps']:
            event = events.get(s['event_id'], {})
            kind = operation_kind(s, event)
            rec = {'paper_id': pid, 'step_id': s['step_id'], 'kind': kind,
                   'doi': d.get('doi'), 'publication_date': bib.get(pid, {}).get('publication_date'),
                   'reaction_smiles': s['substrate_product_smiles'],
                   'source_references': s.get('source_references', []),
                   'conditions': {k: s[k] for k in CONDITION_KEYS if s.get(k) not in (None, '', [], {})},
                   'yield_percent': s.get('yield_percent'), 'yield_scope': s.get('yield_scope'),
                   'product_specific_yields': s.get('product_specific_yields', []),
                   'curation_evidence': s.get('curation_evidence'), 'formal_benchmark_eligible': False,
                   'molecular_stereo_notes': {k: molecules[k].get('stereo_status', molecules[k].get('stereo_note', ''))
                                               for k in s['product_labels'] if k in molecules},
                   'issues': []}
            # Evaluation must retain source qualifications alongside the extracted
            # conditions. Their presence does not resolve a conflicting source.
            for key in ('conditions_extraction_status', 'experimental_stage_count',
                        'operation_scope', 'condition_source_conflicts',
                        'source_yield_claims', 'observed_other_products',
                        'reaction_environment', 'workup_note'):
                if s.get(key) not in (None, '', [], {}):
                    rec[key] = s[key]
            try:
                left, right = reaction_key(rec['reaction_smiles'])
                actual_left = tuple(sorted(frag for lab in s['reactant_labels']
                                           for frag in canonical(molsmiles(molecules[lab])).split('.')))
                actual_right = tuple(sorted(frag for lab in s['product_labels']
                                            for frag in canonical(molsmiles(molecules[lab])).split('.')))
                # Re-canonicalize individual fragments: disconnected canonical order can differ.
                actual_left = tuple(sorted(canonical(x) for x in actual_left))
                actual_right = tuple(sorted(canonical(x) for x in actual_right))
                if (actual_left, actual_right) != (left, right):
                    rec['issues'].append('reaction_label_identity_mismatch')
                rec['precursor_smiles'] = [canonical(molsmiles(molecules[x])) for x in s['reactant_labels']]
                rec['product_smiles'] = [canonical(molsmiles(molecules[x])) for x in s['product_labels']]
                anchors.add(('reaction_without_stereo', str(reaction_key(rec['reaction_smiles'], False))))
                for product in rec['product_smiles']:
                    anchors.add(('product_without_stereo', canonical(product, False)))
            except (ValueError, KeyError) as exc:
                rec['issues'].append('invalid_reaction_or_label:' + str(exc))
            for ref in rec['source_references']:
                src = artifacts.get(ref.get('source_id'))
                if not src or src['sha256'] != ref.get('sha256'):
                    rec['issues'].append('source_hash_or_id_mismatch')
                elif any(page < 1 or (src.get('page_count') and page > src['page_count']) for page in ref.get('pages', [])):
                    rec['issues'].append('source_page_out_of_range')
            if not rec['source_references']:
                rec['issues'].append('missing_source_locator')
            if not rec['conditions']:
                issues.append({'paper_id': pid, 'step_id': s['step_id'], 'kind': 'conditions_not_structured',
                               'operation_kind': kind, 'source_status': s.get('conditions_extraction_status')})
            for issue in rec['issues']:
                issues.append({'paper_id': pid, 'step_id': s['step_id'], 'kind': issue})
            operations.append(rec)
        for r in d['routes']:
            trace = route_trace(r, steps, molecules)
            row = {'paper_id': pid, 'route_id': r['route_id'], 'route_type': r['route_type'],
                   'doi': d.get('doi'), 'publication_date': bib.get(pid, {}).get('publication_date'),
                   'coverage_scope': coverage.get((pid, r['route_id'] if r['route_id'].startswith(pid + ':route:') else pid + ':route:' + r['route_id'])),
                   'source_coverage_definition': d.get('coverage_definition'),
                   'source_unresolved_events': d.get('unresolved_events', []),
                   'target_smiles': canonical(molsmiles(molecules[r['target_label']])),
                   'target_stereo_note': molecules[r['target_label']].get('stereo_status', molecules[r['target_label']].get('stereo_note', '')),
                   'reference_step_ids': r['ordered_step_ids'], 'source_declared_split_group': r.get('split_group'),
                   'source_claims_commercially_complete': r.get('from_commercial_starting_materials_complete', False),
                   'formal_benchmark_eligible': False, **trace}
            if stock:
                row['external_start_stock_membership'] = {x: stock.contains(x) for x in trace['external_start_smiles']}
                row['reference_stock_closed'] = bool(trace['target_ancestry_step_ids']) and not trace['errors'] and all(row['external_start_stock_membership'].values())
                row['target_in_stock'] = stock.contains(row['target_smiles'])
            for issue in trace['errors']:
                issues.append({'paper_id': pid, 'route_id': r['route_id'], 'kind': 'route_trace_error', 'detail': issue})
            routes.append(row)
        for anchor in anchors:
            if anchor in seen_anchors:
                groups.join(pid, seen_anchors[anchor])
            else:
                seen_anchors[anchor] = pid
    components = collections.defaultdict(list)
    for pid in datasets:
        components[groups.find(pid)].append(pid)
    split_by_paper = {}
    group_rows = []
    # These are candidate splits, not temporal holdouts. Large linked groups are indivisible.
    counts = collections.Counter()
    desired = {'development': .15, 'validation': .15, 'test': .70}
    for members in sorted(components.values(), key=lambda x: (-len(x), x)):
        split = max(desired, key=lambda x: desired[x] * len(datasets) - counts[x])
        counts[split] += len(members)
        gid = stable_id('group', members)
        group_rows.append({'group_id': gid, 'split': split, 'paper_ids': members})
        for pid in members:
            split_by_paper[pid] = (split, gid)
    single = collections.defaultdict(list)
    for op in operations:
        op['split'], op['group_id'] = split_by_paper[op['paper_id']]
        if (op['kind'] == 'reported_single_operation' and len(op.get('product_smiles', [])) == 1
                and not op['issues'] and op['yield_percent'] != 0):
            single[op['product_smiles'][0]].append(op)
    multi = collections.defaultdict(list)
    target_types = {'source_bound_successful_synthesis', 'reported_target_synthesis',
                    'reported_total_synthesis_segment', 'reported_racemic_total_synthesis_segment',
                    'total_synthesis', 'total_synthesis_from_known_precursors',
                    'total_synthesis_from_known_intermediate', 'reported_total_synthesis',
                    'reported_analogue_synthesis', 'partially_racemized_synthesis'}
    for r in routes:
        r['split'], r['group_id'] = split_by_paper[r['paper_id']]
        if r['route_type'] in target_types and not r['errors']:
            multi[r['target_smiles']].append(r)
    for track, mapping in [('single_step', single), ('multistep', multi)]:
        questions, answers = [], []
        for target, references in sorted(mapping.items()):
            tid = stable_id(track, target)
            questions.append({'task_id': tid, 'target_smiles': target, 'task_type': track,
                              'max_candidates': 3, 'stock_id': STOCK['source_csv_sha256'] if track == 'multistep' else None})
            answers.append({'task_id': tid, 'split': references[0]['split'], 'group_id': references[0]['group_id'],
                            'reference_status': 'candidate_pending_independent_review',
                            'formal_benchmark_eligible': False, 'references': references})
        write_jsonl(output / 'inputs' / (track + '.jsonl'), questions)
        write_jsonl(output / 'evaluation_only' / (track + '.jsonl'), answers)
    exported = set()
    with (ROOT / 'data/database/route_steps.csv').open(encoding='utf-8-sig', newline='') as f:
        csv_rows = list(csv.DictReader(f))
        exported = {(r['paper_id'], r['local_step_id']) for r in csv_rows}
    absent = [{'paper_id': o['paper_id'], 'step_id': o['step_id'], 'kind': o['kind']}
              for o in operations if (o['paper_id'], o['step_id']) not in exported]
    write_jsonl(output / 'evaluation_only/operation_bank.jsonl', operations)
    write_jsonl(output / 'evaluation_only/route_bank.jsonl', routes)
    write_jsonl(output / 'evaluation_only/review_queue.jsonl', issues)
    write_json(output / 'evaluation_only/operations_absent_from_path_csv.json', absent)
    write_json(output / 'splits.json', group_rows)
    write_json(output / 'stock.json', STOCK)
    summary = {'status': 'executable_candidate_not_chemically_admitted', 'papers': len(datasets),
               'molecular_records': sum(len(d['molecules']) for d in datasets.values()),
               'source_operations': len(operations), 'source_paths': len(routes),
               'csv_path_occurrences': len(csv_rows), 'unique_operations_in_path_csv': len(exported),
               'operations_absent_from_path_csv': len(absent),
               'single_step_candidate_targets': len(single), 'multistep_candidate_targets': len(multi),
               'operation_kinds': dict(collections.Counter(o['kind'] for o in operations)),
               'review_queue_counts': dict(collections.Counter(i['kind'] for i in issues)),
               'formally_admitted_tasks': 0, 'split_paper_counts': dict(counts),
               'largest_linked_group_papers': max(map(len, components.values())),
               'inventory_checked': stock is not None, 'rdkit_version': rdBase.rdkitVersion,
               'normalization': 'remove atom maps, canonical isomeric SMILES; no tautomer/charge/largest-fragment normalization',
               'relaxed_metric': 'connectivity only (stereo and isotopes omitted), diagnostic not primary',
               'split_policy': 'paper + declared article family + shared stereo-relaxed products/reactions; common reactants alone do not join groups; not scaffold-disjoint or temporal',
               'implementation_sha256': {name: hashlib.sha256((ROOT / 'scripts' / name).read_bytes()).hexdigest()
                                          for name in ['build_benchmark.py', 'benchmark_common.py', 'score_benchmark.py']},
               'task_file_sha256': {str(p.relative_to(output)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted((output / 'inputs').glob('*.jsonl'))},
               'source_sha256': sources}
    if stock:
        summary['reference_paths_stock_closed'] = sum(r['reference_stock_closed'] for r in routes)
        summary['candidate_multistep_targets_in_stock'] = sum(stock.contains(x) for x in multi)
    write_json(output / 'manifest.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'source_sha256'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'data/benchmark')
    parser.add_argument('--stock-index', type=Path)
    args = parser.parse_args()
    build(args.output, Stock(args.stock_index) if args.stock_index else None)
