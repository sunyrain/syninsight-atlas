"""Deterministic diagnostics; no chemical-feasibility or expert-quality claims.

Missing predictions remain in the denominator. Ranking must be supplied by the
planner, before reference access. Accept at most three candidates per target.
"""
import argparse
import collections
import json
from pathlib import Path
from benchmark_common import (ROOT, Stock, canonical, components, reaction_key,
                              read_jsonl, write_json)


def precursor_key(values, stereo=True):
    return tuple(sorted(fragment for value in values for fragment in components(value, stereo)))


def score_single(candidates, references):
    expected = {precursor_key(r['precursor_smiles']) for r in references}
    relaxed = {precursor_key(r['precursor_smiles'], False) for r in references}
    rows = []
    for c in candidates:
        try:
            values = c['precursor_smiles']
            if not isinstance(values, list) or not values:
                raise ValueError('precursor_smiles must be a nonempty list')
            key = precursor_key(values)
            rows.append({'valid': True, 'exact': key in expected,
                         'connectivity_only': precursor_key(values, False) in relaxed})
        except (ValueError, KeyError, TypeError) as exc:
            rows.append({'valid': False, 'exact': False, 'connectivity_only': False, 'error': str(exc)})
    return rows


def assess_route(candidate, target, stock):
    steps = candidate.get('steps', [])
    if not isinstance(steps, list):
        return {'valid': False, 'stock_closed': False, 'error': 'steps must be a list'}
    if not steps:
        return {'valid': False, 'stock_closed': False, 'error': 'no reaction steps; target-in-stock is a separate triviality diagnostic'}
    try:
        if candidate.get('target_smiles') and canonical(candidate['target_smiles']) != canonical(target):
            raise ValueError('candidate target differs from the question')
        latest, dependencies, leaves, keys = {}, {}, set(), []
        condition_presence = []
        for i, step in enumerate(steps):
            left, right = step['reactants'], step['products']
            if not isinstance(left, list) or not isinstance(right, list) or not left or not right:
                raise ValueError('each forward operation needs nonempty reactants and products lists')
            left = [canonical(x) for x in left]; right = [canonical(x) for x in right]
            if precursor_key(left) == precursor_key(right):
                raise ValueError('identity operation has no net molecular change')
            dependencies[i] = set()
            for x in left:
                if x in latest:
                    dependencies[i].add(latest[x])
                else:
                    leaves.add(x)
            for x in right:
                latest[x] = i
            keys.append(reaction_key('.'.join(left) + '>>' + '.'.join(right)))
            conditions = step.get('conditions')
            condition_presence.append(isinstance(conditions, dict) and
                                      any(v not in (None, '', [], {}) for v in conditions.values()))
        target = canonical(target)
        ancestry = set()
        def visit(i):
            if i in ancestry:
                return
            ancestry.add(i)
            for earlier in dependencies[i]:
                visit(earlier)
        if target in latest:
            visit(latest[target])
        connected = bool(ancestry) and len(ancestry) == len(steps)
        unresolved = sorted(x for x in leaves if not stock.contains(x))
        return {'valid': True, 'target_produced': target in latest, 'connected': connected,
                'stock_closed': connected and not unresolved, 'unresolved_leaves': unresolved,
                'external_start_count': len(leaves), 'steps': len(steps),
                'off_target_operations': sorted(set(range(len(steps))) - ancestry),
                'condition_field_coverage': sum(condition_presence) / len(steps),
                'all_condition_fields_present': all(condition_presence),
                'chemical_plausibility': 'not_assessed', '_reaction_keys': keys}
    except (KeyError, TypeError, ValueError) as exc:
        return {'valid': False, 'stock_closed': False, 'error': str(exc)}


def reference_recovery(keys, references, operation_lookup):
    generated = collections.Counter(keys)
    best = {'reference_operation_recall': 0.0, 'reference_operation_precision': 0.0,
            'reference_operation_multiset_match': False}
    for ref in references:
        expected = collections.Counter(reaction_key(operation_lookup[(ref['paper_id'], sid)]['reaction_smiles'])
                                       for sid in ref['target_ancestry_step_ids'])
        overlap = sum((expected & generated).values())
        rec = overlap / sum(expected.values()) if expected else 0.0
        prec = overlap / sum(generated.values()) if generated else 0.0
        if (rec, prec) > (best['reference_operation_recall'], best['reference_operation_precision']):
            best.update(reference_operation_recall=rec, reference_operation_precision=prec)
        best['reference_operation_multiset_match'] |= bool(expected) and expected == generated
    return best


def score(root, predictions, track, split, stock=None):
    questions = {q['task_id']: q for q in read_jsonl(root / 'inputs' / (track + '.jsonl'))}
    answers = {a['task_id']: a for a in read_jsonl(root / 'evaluation_only' / (track + '.jsonl'))}
    if split != 'all':
        questions = {k: v for k, v in questions.items() if answers[k]['split'] == split}
    supplied = {}
    for p in predictions:
        if p['task_id'] not in questions:
            raise ValueError('Unknown or out-of-split task: ' + p['task_id'])
        if p['task_id'] in supplied:
            raise ValueError('Duplicate task prediction: ' + p['task_id'])
        candidates = p.get('candidates', [])
        if not isinstance(candidates, list) or len(candidates) > 3:
            raise ValueError('Submit at most three ranked candidates per task')
        if any(not isinstance(c, dict) for c in candidates):
            raise ValueError('Every candidate must be an object')
        supplied[p['task_id']] = candidates
    operations = {(o['paper_id'], o['step_id']): o for o in read_jsonl(root / 'evaluation_only/operation_bank.jsonl')}
    outcomes = []
    for tid, question in questions.items():
        candidates = supplied.get(tid, [])
        references = answers[tid]['references']
        if track == 'single_step':
            rows = score_single(candidates, references)
        else:
            if stock is None:
                raise ValueError('The frozen inventory is required for multistep scoring')
            rows = [assess_route(c, question['target_smiles'], stock) for c in candidates]
            for r in rows:
                r.update(reference_recovery(r.pop('_reaction_keys', []), references, operations))
        outcome = {'task_id': tid, 'submitted_candidates': len(candidates), 'candidates': rows}
        if track == 'multistep':
            outcome['target_in_stock'] = stock.contains(question['target_smiles'])
        outcomes.append(outcome)
    metrics = ['exact', 'connectivity_only'] if track == 'single_step' else ['stock_closed', 'reference_operation_multiset_match']
    summary = {'status': 'candidate_reference_diagnostics_not_chemical_validation', 'track': track,
               'split': split, 'tasks': len(questions), 'missing_task_predictions': len(questions) - len(supplied)}
    for metric in metrics:
        for k in (1, 3):
            numerator = sum(any(c.get(metric, False) for c in o['candidates'][:k]) for o in outcomes)
            summary[metric + '@' + str(k)] = {'numerator': numerator, 'denominator': len(outcomes),
                                            'fraction': numerator / len(outcomes) if outcomes else None}
    if track == 'multistep':
        subset = [o for o in outcomes if not o['target_in_stock']]
        summary['trivial_target_in_stock_tasks'] = len(outcomes) - len(subset)
        summary['stock_closed_nontrivial@3'] = {
            'numerator': sum(any(c['stock_closed'] for c in o['candidates']) for o in subset),
            'denominator': len(subset)}
    return {'summary': summary, 'outcomes': outcomes}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--benchmark', type=Path, default=ROOT / 'data/benchmark')
    p.add_argument('--predictions', type=Path, required=True)
    p.add_argument('--track', choices=['single_step', 'multistep'], required=True)
    p.add_argument('--split', choices=['all', 'development', 'validation', 'test'], default='test')
    p.add_argument('--stock-index', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = score(a.benchmark, read_jsonl(a.predictions), a.track, a.split,
                   Stock(a.stock_index) if a.stock_index else None)
    write_json(a.output, result)
    print(json.dumps(result['summary'], indent=2))
