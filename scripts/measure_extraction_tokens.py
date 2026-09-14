"""Collect numeric usage records for an explicitly selected local Codex turn only.

No messages, prompts, reasoning content, credentials or unrelated turn usage are exported.
"""
import argparse,json,time
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.local/two-paper-token-run.json'
OUT=ROOT/'data/extraction/two-paper-token-usage.json'
FIELDS=['input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens','total_tokens']

def now():return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

def save(state):STATE.parent.mkdir(parents=True,exist_ok=True);STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')

def scan(state):
    path=Path(state['log'])
    with path.open('rb') as f:
        f.seek(state.get('offset',0))
        while True:
            offset=f.tell();line=f.readline()
            if not line or not line.endswith(b'\n'):
                state['offset']=offset;break
            # Do not parse message or reasoning records.
            if b'token_usage_record' not in line and b'task_complete' not in line:continue
            try:r=json.loads(line)
            except ValueError:continue
            p=r.get('payload',{})
            if p.get('turn_id')!=state['turn_id']:continue
            if r.get('type')=='token_usage_record':
                identifier=p.get('response_id')
                if not identifier:continue
                state['records'][identifier]={'timestamp':r['timestamp'],'usage':{k:int(p.get('usage',{}).get(k,0)) for k in FIELDS},
                    'turn_total':{k:int(p.get('turn_token_usage',{}).get(k,0)) for k in FIELDS}}
            elif p.get('type')=='task_complete':
                state['turn_completed']=True;state['completed_at']=r['timestamp']
    save(state)
    records=sorted(state['records'].values(),key=lambda r:r['timestamp'])
    total=records[-1]['turn_total'] if records else {k:0 for k in FIELDS}
    stages={s['name']:{k:0 for k in FIELDS} for s in state['stages']}
    for r in records:
        eligible=[s for s in state['stages'] if s['at']<=r['timestamp']]
        stage=eligible[-1]['name'] if eligible else state['stages'][0]['name']
        for k in FIELDS:stages[stage][k]+=r['usage'][k]
    summed={k:sum(r['usage'][k] for r in records) for k in FIELDS}
    report={'run_id':state.get('run_id','two-new-papers-20260909'),'papers':state['papers'],'measurement':'actual_local_codex_token_usage_record',
        'captured_at':now(),'last_usage_at':records[-1]['timestamp'] if records else None,
        'started_at':state.get('started_at'),'completed_at':state.get('completed_at'),
        'measurement_finalized':state.get('measurement_finalized',False),
        'turn_completed':state.get('turn_completed',False),'response_records':len(records),'total':total,
        'uncached_input_tokens':total['input_tokens']-total['cached_input_tokens'],
        'per_response_sum_matches_turn_total':summed==total,'stages':stages,
        'responses':[{'index':i+1,'timestamp':r['timestamp'],**r['usage']} for i,r in enumerate(records)],
        'scope_notes':['Includes selection, measurement setup, extraction, verification and reporting within this turn.',
            'Input totals include cached input. Reasoning output is a subset of output; do not add these subsets again.',
            'Stages use usage-record timestamps and may straddle tool/model boundaries; per-paper stages are not isolated benchmark runs.',
            'This is runtime token telemetry, not a billing statement. Local deterministic programs themselves make no LLM calls.',
            'Final assistant response is included only after its usage record is persisted; watch mode updates automatically.']}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['init','stage','snapshot','watch']);p.add_argument('--log',type=Path);p.add_argument('--turn');p.add_argument('--papers',nargs='+');p.add_argument('--name');p.add_argument('--run-id');a=p.parse_args()
    if a.run_id:
        import re
        if not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}',a.run_id):p.error('Invalid run ID')
        STATE=ROOT/'.local'/(a.run_id+'-token-run.json');OUT=ROOT/'data/extraction'/(a.run_id+'-token-usage.json')
    if a.action=='init':
        if not a.log or not a.turn or not a.papers:p.error('init requires --log, --turn, --papers')
        if STATE.exists():raise ValueError('Measurement already exists; do not overwrite an active or completed run')
        state={'run_id':a.run_id or 'two-new-papers-20260909','started_at':now(),'log':str(a.log),'turn_id':a.turn,'papers':a.papers,'offset':0,'records':{},'stages':[{'name':'shared_selection_and_meter_setup','at':'1970-01-01T00:00:00Z'}]};save(state)
    state=json.loads(STATE.read_text(encoding='utf8'))
    if a.action=='stage':
        if not a.name:p.error('stage requires --name')
        scan(state);state['stages'].append({'name':a.name,'at':now()});save(state)
    if a.action=='watch':
        deadline=time.monotonic()+8*3600
        completed_seen=None;last_count=None;last_change=time.monotonic()
        while time.monotonic()<deadline:
            state=json.loads(STATE.read_text(encoding='utf8'));report=scan(state)
            if report['response_records']!=last_count:
                last_count=report['response_records'];last_change=time.monotonic()
            if report['turn_completed']:
                if completed_seen is None:completed_seen=time.monotonic()
                if time.monotonic()-completed_seen>=30 and time.monotonic()-last_change>=15:
                    state['measurement_finalized']=True;scan(state);break
            time.sleep(3)
    else:
        r=scan(state);print(json.dumps({k:r[k] for k in ['response_records','total','uncached_input_tokens','per_response_sum_matches_turn_total','turn_completed']},indent=2))
