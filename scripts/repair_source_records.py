"""Apply narrowly sourced corrections and keep existing database exports in sync.

This does not rewrite structures, admit records to a benchmark, or modify historical
model runs. The ledger contains old/new values and evidence, not publisher PDFs.
"""
import csv
import hashlib
import json
import sqlite3
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'data/curation/repairs_20261004.json'


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def apply():
    ledger = json.loads(LEDGER.read_text(encoding='utf-8'))
    datasets = {}
    for change in ledger['changes']:
        pid = change['paper_id']
        path = ROOT / 'data/routes' / pid / 'dataset.json'
        d = datasets.setdefault(pid, json.loads(path.read_text(encoding='utf-8-sig')))
        s = next(s for s in d['steps'] if s['step_id'] == change['step_id'])
        for key, v in change['fields'].items():
            if s.get(key) not in [v['before'], v['after']]:
                raise ValueError(f'Unreviewed concurrent edit: {pid}/{s["step_id"]}/{key}')
            s[key] = v['after']
        s['curation_evidence'] = {
            'revision': ledger['revision'], 'method': change.get('verification_method', 'source_text_and_scheme_crosscheck'),
            'independent_expert_review': False, 'reason': change['reason'],
            'references': change['source_references'],
        }
        for ref in change['source_references']:
            if ref not in s['source_references']:
                s['source_references'].append(ref)
        event = next(e for e in d['reactions'] if e['event_id'] == s['event_id'])
        # Event mirrors are safe only when the source event has exactly this operation.
        if event['step_ids'] == [s['step_id']]:
            mapping = {'agents': 'reagents', 'product_specific_yields': 'reported_yields'}
            for key in change['fields']:
                event[mapping.get(key, key)] = s[key]
            event['curation_evidence'] = s['curation_evidence']
            event['source_references'] = s['source_references']
    for pid, d in datasets.items():
        (ROOT / 'data/routes' / pid / 'dataset.json').write_text(
            json.dumps(d, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    synchronize(datasets)
    from build_absynth import build
    build()
    for pid in datasets:
        refresh_checksums(ROOT / 'data/routes' / pid / 'CHECKSUMS.sha256')
    package = ROOT / 'data/database/datapackage.json'
    p = json.loads(package.read_text(encoding='utf-8'))
    for r in p['resources']:
        if 'sha256' in r:
            r['sha256'] = hashlib.sha256((package.parent / r['path']).read_bytes()).hexdigest()
    package.write_text(json.dumps(p, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    refresh_checksums(ROOT / 'CHECKSUMS.sha256')
    print(dump({'repaired_operations': len(ledger['changes']), 'papers': len(datasets)}))


def synchronize(datasets):
    """Refresh data mirrors already present in the published database, not a reimport."""
    with sqlite3.connect(ROOT / 'data/atlas.sqlite') as db:
        db.execute('PRAGMA foreign_keys=ON')
        for pid, d in datasets.items():
            folder = ROOT / 'data/routes' / pid
            for name in ['steps', 'reactions']:
                (folder / (name + '.json')).write_text(
                    json.dumps(d[name], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                p = folder / (name + '.csv')
                with p.open(encoding='utf-8-sig', newline='') as f:
                    fields = next(csv.reader(f))
                fields += sorted({k for row in d[name] for k in row} - set(fields))
                with p.open('w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
                    writer.writerows({k: dump(v) if isinstance(v, (list, dict)) else v
                                      for k, v in row.items()} for row in d[name])
            report = folder / 'report.html'
            soup = BeautifulSoup(report.read_text(encoding='utf-8'), 'html.parser')
            revised = {e['event_id']: e for e in d['reactions'] if e.get('curation_evidence')}
            for row in soup.select('tr'):
                cells = row.find_all('td', recursive=False)
                if len(cells) == 4 and cells[0].get_text(strip=True) in revised:
                    event = revised[cells[0].get_text(strip=True)]
                    if event.get('yield_scope'):
                        cells[2].string = event['yield_scope']
            note = soup.find(id='source-repair-20261004')
            if note is not None:
                note.decompose()
            note = soup.new_tag('section', id='source-repair-20261004')
            title = soup.new_tag('h2'); title.string = 'Source corrections (2026-10-04)'; note.append(title)
            for e in revised.values():
                paragraph = soup.new_tag('p')
                paragraph.string = e['event_id'] + ': ' + e['curation_evidence']['reason']
                note.append(paragraph)
            (soup.body or soup.html or soup).append(note)
            report.write_text(str(soup), encoding='utf-8')
            for step in d['steps']:
                db.execute('UPDATE operation_steps SET temperature_reported=?, duration_hours=?, '
                           'yield_percent=?, metadata_json=? WHERE paper_id=? AND local_step_id=?',
                           (step.get('temperature_reported'), step.get('duration_hours'),
                            step.get('yield_percent'), dump(step), pid, step['step_id']))
                for ref in step.get('curation_evidence', {}).get('references', []):
                    artifact = db.execute('SELECT artifact_id FROM source_artifacts '
                                          'WHERE paper_id=? AND source_id=?', (pid, ref['source_id'])).fetchone()[0]
                    for page in ref.get('pages') or [None]:
                        eid = 'evidence-' + hashlib.sha256(
                            dump([artifact, page, ref['locator']]).encode()).hexdigest()
                        db.execute('INSERT OR IGNORE INTO evidence_locations VALUES(?,?,?,?,?,?)',
                                   (eid, artifact, page, ref['locator'], ref['sha256'], 'source_bound_reference'))
                        eid = db.execute('SELECT evidence_id FROM evidence_locations WHERE artifact_id=? '
                                         'AND page_number IS ? AND locator=?', (artifact, page, ref['locator'])).fetchone()[0]
                        db.execute('INSERT OR IGNORE INTO operation_evidence VALUES(?,?)',
                                   (f'{pid}:step:{step["step_id"]}', eid))
                        db.execute('INSERT OR IGNORE INTO reaction_evidence VALUES(?,?)',
                                   (f'{pid}:event:{step["event_id"]}', eid))
            for e in d['reactions']:
                db.execute('UPDATE reaction_events SET reported_yields_json=?, metadata_json=? '
                           'WHERE paper_id=? AND local_event_id=?',
                           (dump(e.get('reported_yields', [])), dump(e), pid, e['event_id']))
            # Preserve original extraction hashes: repairs are a later run, not a rewrite of provenance.
            source = ROOT / 'data/routes' / pid / 'dataset.json'
            db.execute('INSERT OR REPLACE INTO extraction_runs VALUES(?,?,?,?,?,?,?,?)',
                       (pid + ':repair:20261004', pid, 'source_text_and_scheme_crosscheck',
                        'repair_source_records.py', str(source.relative_to(ROOT)).replace('\\', '/'),
                        hashlib.sha256(source.read_bytes()).hexdigest(), 'corrected_candidate_pending_review',
                        dump({'independent_expert_review': False, 'structure_changes': False})))
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    path = ROOT / 'data/database/route_steps.csv'
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f); fields = reader.fieldnames; rows = list(reader)
    steps = {(pid, s['step_id']): s for pid, d in datasets.items() for s in d['steps']}
    for r in rows:
        s = steps.get((r['paper_id'], r['local_step_id']))
        if s is not None:
            for key in ['temperature_reported', 'duration_hours', 'yield_percent']:
                r[key] = '' if s.get(key) is None else str(s[key])
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)


def refresh_checksums(path):
    if path.exists():
        lines = []
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            _, rel = line.split(None, 1)
            rel = rel.strip().lstrip('*')
            lines.append(hashlib.sha256((path.parent / rel).read_bytes()).hexdigest() + '  ' + rel)
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    apply()
