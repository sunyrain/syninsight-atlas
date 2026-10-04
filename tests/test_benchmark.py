import json
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from benchmark_common import canonical, read_jsonl
from build_benchmark import operation_kind, route_trace
from score_benchmark import assess_route, score, score_single


class TinyStock:
    def __init__(self, *smiles):
        self.entries = {canonical(s) for s in smiles}
    def contains(self, smiles):
        return canonical(smiles) in self.entries


class BenchmarkTests(unittest.TestCase):
    def test_order_mapping_and_stereo(self):
        refs = [{'precursor_smiles': ['C[C@H](O)C(=O)O', '[Na+].[Cl-]']}]
        rows = score_single([
            {'precursor_smiles': ['[Cl-].[Na+]', '[CH3:1][C@H:2](O)C(=O)O']},
            {'precursor_smiles': ['[Na+].[Cl-]', 'C[C@@H](O)C(=O)O']},
        ], refs)
        self.assertTrue(rows[0]['exact'])
        self.assertFalse(rows[1]['exact'])
        self.assertTrue(rows[1]['connectivity_only'])

    def test_unclosed_and_disconnected_routes_cannot_pass(self):
        stock = TinyStock('CCO')
        route = {'steps': [{'reactants': ['CCO'], 'products': ['CC=O'],
                            'conditions': {'agents': ['oxidant unspecified']}}]}
        self.assertTrue(assess_route(route, 'CC=O', stock)['stock_closed'])
        self.assertEqual(assess_route(route, 'CC=O', stock)['chemical_plausibility'], 'not_assessed')
        self.assertFalse(assess_route(route, 'CC=O', TinyStock())['stock_closed'])
        route['steps'].append({'reactants': ['CCO'], 'products': ['C=C']})
        self.assertFalse(assess_route(route, 'CC=O', stock)['stock_closed'])
        self.assertFalse(assess_route({'steps': []}, 'CCO', stock)['stock_closed'])

    def test_conditions_presence_does_not_certify_conditions(self):
        route = {'steps': [{'reactants': ['CCO'], 'products': ['CC=O']}]}
        row = assess_route(route, 'CC=O', TinyStock('CCO'))
        self.assertTrue(row['stock_closed'])
        self.assertFalse(row['all_condition_fields_present'])
        self.assertEqual(row['chemical_plausibility'], 'not_assessed')

    def test_reference_trace_handles_branching_and_time(self):
        molecules = {x: {'canonical_smiles': s} for x, s in [('a', 'CCO'), ('b', 'CC=O'), ('c', 'CC(O)C')]}
        steps = {'s1': {'reactant_labels': ['a'], 'product_labels': ['b', 'c']},
                 's2': {'reactant_labels': ['b'], 'product_labels': ['a']}}
        row = route_trace({'ordered_step_ids': ['s1', 's2'], 'target_label': 'a',
                           'start_labels': ['a']}, steps, molecules)
        self.assertFalse(row['errors'])
        self.assertEqual(row['target_ancestry_step_ids'], ['s1', 's2'])
        self.assertEqual(row['external_start_labels'], ['a'])

    def test_actual_source_repairs_and_mirrors(self):
        ledger = json.loads((ROOT / 'data/curation/repairs_20261004.json').read_text())
        with sqlite3.connect(ROOT / 'data/atlas.sqlite') as db:
            for change in ledger['changes']:
                folder = ROOT / 'data/routes' / change['paper_id']
                dataset = json.loads((folder / 'dataset.json').read_text(encoding='utf-8'))
                step = next(x for x in dataset['steps'] if x['step_id'] == change['step_id'])
                mirrors = json.loads((folder / 'steps.json').read_text(encoding='utf-8'))
                self.assertEqual(step, next(x for x in mirrors if x['step_id'] == step['step_id']))
                stored = json.loads(db.execute('SELECT metadata_json FROM operation_steps WHERE paper_id=? '
                                              'AND local_step_id=?', (change['paper_id'], step['step_id'])).fetchone()[0])
                self.assertEqual(step, stored)
                for k, v in change['fields'].items():
                    self.assertEqual(step[k], v['after'])
                self.assertFalse(step['formal_benchmark_eligible'])
                if change['paper_id'] == 'paper-c68b92dcce0b5753':
                    self.assertEqual(operation_kind(step, {}), 'referenced_multistep_sequence')
                    self.assertIsNone(step['yield_percent'])

    def test_inputs_are_answer_free_and_splits_keep_shared_products_together(self):
        root = ROOT / 'data/benchmark'
        operations = read_jsonl(root / 'evaluation_only/operation_bank.jsonl')
        product_splits = {}
        for row in operations:
            for product in row.get('product_smiles', []):
                key = canonical(product, False)
                self.assertEqual(product_splits.setdefault(key, row['split']), row['split'])
        for track in ['single_step', 'multistep']:
            questions = read_jsonl(root / 'inputs' / (track + '.jsonl'))
            self.assertEqual(len(questions), len({q['task_id'] for q in questions}))
            for q in questions:
                self.assertEqual(set(q), {'task_id', 'target_smiles', 'task_type', 'max_candidates', 'stock_id'})

    def test_reference_self_recovery_and_missing_denominators(self):
        root = ROOT / 'data/benchmark'
        answers = read_jsonl(root / 'evaluation_only/single_step.jsonl')
        predictions = [{'task_id': a['task_id'], 'candidates': [
            {'precursor_smiles': a['references'][0]['precursor_smiles']}]} for a in answers]
        result = score(root, predictions, 'single_step', 'all')['summary']
        self.assertEqual(result['exact@1']['fraction'], 1.0)
        result = score(root, [], 'single_step', 'all')['summary']
        self.assertEqual(result['exact@3']['denominator'], len(answers))
        self.assertEqual(result['exact@3']['numerator'], 0)
        self.assertEqual(result['missing_task_predictions'], len(answers))
        predictions[0]['candidates'] *= 4
        with self.assertRaises(ValueError):
            score(root, predictions, 'single_step', 'all')


if __name__ == '__main__':
    unittest.main()
