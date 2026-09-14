"""Render source-preserving reaction schemes as standalone, publication-style SVG."""
import csv, hashlib, html, json, math, re, textwrap
from pathlib import Path
from rdkit import Chem, rdBase
from rdkit.Chem import rdDepictor, rdChemReactions
from rdkit.Chem.Draw import rdMolDraw2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/route-figures'
VERSION = '1'

def escape(value): return html.escape(str(value))
def lines(value, width): return textwrap.wrap(str(value), width=width, break_long_words=True, break_on_hyphens=False) or ['']
def label(value, x, y, size=18, weight='normal', fill='#111'):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(value)}</text>'
def readable(value):
    if isinstance(value, list): return ', '.join(readable(x) for x in value)
    if isinstance(value, dict): return '; '.join(f'{k.replace("_", " ")}: {readable(v)}' for k,v in value.items())
    return str(value)

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = json.loads((ROOT/'data/database/absynth_metadata.json').read_text(encoding='utf-8'))
    with (ROOT/'data/database/SynInsight_ABSynth_Dataset.csv').open(encoding='utf-8-sig', newline='') as f: rows = list(csv.DictReader(f))
    groups = {}; datasets = {}; render_cache = {}; manifest = {}; total = 0
    rdDepictor.SetPreferCoordGen(True)
    for r in rows: groups.setdefault(r['PathId'], []).append(r)
    for path_id, path_rows in groups.items():
        path = meta['paths'][path_id]; pid = path['paper_id']
        if pid not in datasets:
            data = json.loads((ROOT/path['dataset']).read_text(encoding='utf-8'))
            datasets[pid] = {s['step_id']:s for s in data['steps']}
        width = 1280
        for r in path_rows:
            mols = [Chem.MolFromSmiles(s) for side in r['RxnSMILES'].split('>>') for s in side.split('.')]
            if any(m is None for m in mols): raise ValueError(f'Invalid structure: {path_id} {r["StepId"]}')
            width = max(width, int(sum(math.sqrt(m.GetNumAtoms()) * 62 for m in mols) + 240))
        width = min(3200, width)
        name = hashlib.sha256(path_id.encode()).hexdigest()[:24] + '.svg'
        content_hash = hashlib.sha256(json.dumps([VERSION, rdBase.rdkitVersion, path_rows, path, datasets[pid]],sort_keys=True).encode()).hexdigest()
        dest = OUT/name
        if dest.exists() and f'<!-- input:{content_hash} -->' in dest.read_text(encoding='utf-8')[:300]:
            manifest[path_id] = {'file':f'assets/route-figures/{name}','steps':len(path_rows),'width':width,'target':path_rows[0]['TargetName'],'paper_id':pid}; continue
        chunks=[]; y=44
        for line in lines(path_rows[0]['TargetName'], max(65,int(width/17))): chunks.append(label(line,40,y,28,'bold')); y+=36
        for line in lines(path['title'], int(width/10)): chunks.append(label(line,40,y,18)); y+=25
        chunks.append(label(f"DOI: {path_rows[0]['DOI']}   |   {len(path_rows)} ordered operation occurrences",40,y,17)); y+=29
        for line in lines(f"{path['route_type'].replace('_',' ')} | {path['coverage_scope'].replace('_',' ')} | Candidate — not independently reviewed", int(width/9)):
            chunks.append(label(line,40,y,16,fill='#555'));y+=24
        chunks.append(label('Source-defined path order; rows may include convergent fragments or control branches.',40,y,16,fill='#555'));y+=40
        for r in path_rows:
            info=path['steps'][r['StepId']]; step=datasets[pid][info['local_step_id']]
            chunks.append(f'<path d="M40 {y-12} H{width-40}" stroke="#ccc" stroke-width="1"/>')
            heading=f"Step {r['StepId']}   ·   {info['local_step_id']}"
            if r['RxnName']: heading += '   |   '+r['RxnName']
            for line in lines(heading,int(width/12)): chunks.append(label(line,40,y+14,21,'bold'));y+=28
            condition_parts=[]
            for key in ['agents','solvents','temperature','temperature_reported','time','duration_hours','pressure','current_mA','operation_stages']:
                if step.get(key) not in (None,'',[]): condition_parts.append(f"{key.replace('_',' ')}: {readable(step[key])}")
            for line in lines('; '.join(condition_parts) or 'Conditions not recorded', int((width-80)/9)):
                chunks.append(label(line,40,y+12,17));y+=24
            reaction = rdChemReactions.ReactionFromSmarts(r['RxnSMILES'], useSmiles=True)
            if reaction is None: raise ValueError(f'Invalid reaction: {path_id}')
            height=400 if max(m.GetNumAtoms() for m in list(reaction.GetReactants())+list(reaction.GetProducts()))>80 else 310
            key=(r['RxnSMILES'],width,height)
            if key not in render_cache:
                drawer=rdMolDraw2D.MolDraw2DSVG(width-80,height)
                opts=drawer.drawOptions();opts.useBWAtomPalette();opts.bondLineWidth=1.6;opts.fixedBondLength=24
                opts.minFontSize=14;opts.maxFontSize=20;opts.padding=.06;opts.clearBackground=False
                drawer.DrawReaction(reaction);drawer.FinishDrawing()
                svg=drawer.GetDrawingText(); inner=svg[svg.index('>',svg.index('<svg'))+1:svg.rfind('</svg>')]
                render_cache[key]=inner
            chunks.append(f'<g transform="translate(40,{y+8})">{render_cache[key]}</g>');y+=height+24
            source_labels=f"Source labels: {', '.join(step.get('reactant_labels',[]))} → {', '.join(step.get('product_labels',[]))}"
            for line in lines(source_labels,int((width-80)/9)): chunks.append(label(line,40,y,17));y+=24
            yield_value=info['yield_percent']; yield_text=f'Reported yield: {yield_value}%' if yield_value not in ('',None) else 'Yield not recorded'
            chunks.append(label(yield_text,40,y,18,'bold'));y+=27
            for ref in info['source_references']:
                reference=f"{ref.get('source_id','Source')}: {ref.get('locator','')}"+(f" · p. {', '.join(map(str,ref['pages']))}" if ref.get('pages') else '')
                for line in lines(reference,int((width-80)/8)): chunks.append(label(line,40,y,15,fill='#555'));y+=21
            y+=28
        for line in lines('Reported yields can refer to grouped operations or mixtures. Repeated structures preserve source-defined step boundaries; missing intermediates are not invented. See the case report for scope, source conflicts and stereochemical uncertainty.',int((width-80)/8)):
            chunks.append(label(line,40,y,15,fill='#555'));y+=22
        chunks.append(label('SynInsight Atlas · CC BY 4.0 · Source-derived candidate data · RDKit vector depiction',40,y+12,14,fill='#555'));y+=42
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}" viewBox="0 0 {width} {y}"><!-- input:{content_hash} --><title>{escape(path_rows[0]["TargetName"])} reaction scheme</title><desc>All {len(path_rows)} ordered operation occurrences with source references. Candidate, not independently reviewed.</desc><rect width="100%" height="100%" fill="white"/><g font-family="Arial, Helvetica, sans-serif">'+''.join(chunks)+'</g></svg>'
        dest.write_text(svg,encoding='utf-8');total+=1
        if total % 100 == 0: print(f'Rendered {total} route figures',flush=True)
        manifest[path_id]={'file':f'assets/route-figures/{name}','steps':len(path_rows),'width':width,'height':y,'target':path_rows[0]['TargetName'],'paper_id':pid}
    (ROOT/'assets/route-figures.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps({'routes':len(manifest),'rendered':total,'cached_reaction_drawings':len(render_cache)},ensure_ascii=False),flush=True)

if __name__=='__main__':build()
