"""Molecular identity and inventory policy shared by compiler and scorer."""
import functools
import hashlib
import json
import sqlite3
from pathlib import Path
from rdkit import Chem, rdBase

ROOT = Path(__file__).resolve().parents[1]
CONDITION_KEYS = ('agents', 'solvents', 'temperature', 'temperature_reported', 'time',
                  'duration_hours', 'pressure', 'current_mA', 'operation_stages')
STOCK = {
    'name': 'ChemEnzy Repaired ZINC (full list)',
    'raw_rows': 10320697, 'canonical_unique_entries': 10320664,
    'source_csv_sha256': '3bd4ed65bde4f0bac839cb146977d5601a198ef99c04c09170e07f53ebbc1cdb',
    'canonical_index_sha256': 'c64abe5faf9b0e2ee8ef726ed536a5367fc9a9b757c9c4d1ecab247d82f7f1ad',
    'rdkit_version': '2023.09.6', 'matching': 'canonical_isomeric_smiles',
    'supplementary_stock': [], 'target_dependent_filter': False,
}


def stable_id(prefix, value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'))
    return prefix + '-' + hashlib.sha256(payload.encode()).hexdigest()[:20]


@functools.lru_cache(maxsize=50000)
def canonical(smiles, stereo=True):
    m = Chem.MolFromSmiles(smiles)
    if m is None or not m.GetNumAtoms():
        raise ValueError('Invalid or empty SMILES: ' + str(smiles))
    for atom in m.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(m, isomericSmiles=stereo)


def components(smiles, stereo=True):
    # Order-independent multiset: ignore mapping and component order, preserve salts,
    # isotopes (strict mode), charge, tautomer and stereochemistry. No largest-fragment rule.
    return tuple(sorted(canonical(part, stereo) for part in smiles.split('.')))


def reaction_key(smiles, stereo=True):
    left, _, right = smiles.split('>')
    return components(left, stereo), components(right, stereo)


def read_jsonl(path):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_jsonl(path, rows):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rows), encoding='utf-8')


class Stock:
    def __init__(self, path):
        if rdBase.rdkitVersion != STOCK['rdkit_version']:
            raise ValueError('Inventory canonicalization requires RDKit ' + STOCK['rdkit_version'])
        self.path = Path(path).resolve()
        digest = hashlib.file_digest(self.path.open('rb'), 'sha256').hexdigest()
        if digest != STOCK['canonical_index_sha256']:
            raise ValueError('The supplied inventory is not the frozen Repaired ZINC index')
        self.db = sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True)

    @functools.lru_cache(maxsize=50000)
    def contains(self, smiles):
        # Whole molecule/ion-pair identity is looked up; do not require individual salt
        # fragments to exist as separate purchasable entries.
        return self.db.execute('SELECT 1 FROM stock WHERE canonical_smiles=?',
                               (canonical(smiles),)).fetchone() is not None
