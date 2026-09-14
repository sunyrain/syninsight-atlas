"""Source-defined reaction schemes with uniform chemical scale and vector typography."""
import csv, hashlib, html, json, math, re, statistics, textwrap
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/route-overviews'
NS = 'http://www.w3.org/2000/svg'
BOND = 28.8  # SVG export: 0.5 pt per viewBox unit, hence a 14.4 pt bond.
FONT = 16

def esc(value):
    return html.escape(str(value))

def txt(value, x, y, size=FONT, bold=False, anchor='middle'):
    return f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="{size}" font-weight="{"bold" if bold else "normal"}">{esc(value)}</text>'

def words(value, width=28):
    return textwrap.wrap(str(value), width=width, break_long_words=True, break_on_hyphens=False) or ['']

def depict(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f'Invalid structure: {smiles}')
    drawer = rdMolDraw2D.MolDraw2DSVG(-1, -1)
    opt = drawer.drawOptions()
    opt.useBWAtomPalette()
    opt.fixedBondLength = BOND
    opt.scalingFactor = BOND / 1.5
    opt.fixedFontSize = FONT
    opt.bondLineWidth = 1.2
    opt.multipleBondOffset = .18
    opt.clearBackground = False
    opt.padding = .12
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    lengths = []
    for bond in mol.GetBonds():
        a, b = drawer.GetDrawCoords(bond.GetBeginAtomIdx()), drawer.GetDrawCoords(bond.GetEndAtomIdx())
        lengths.append(math.hypot(a.x-b.x, a.y-b.y))
    scale = BOND / statistics.median(lengths) if lengths else 1
    svg = drawer.GetDrawingText()
    root = ET.fromstring(svg)
    _, _, w, h = map(float, root.attrib['viewBox'].split())
    body = svg[svg.index('>', svg.index('<svg'))+1:svg.rfind('</svg>')]
    # Normalize the small flexible-canvas rounding error without distorting stereochemistry.
    return {'body': body, 'width': w*scale, 'height': h*scale, 'scale': scale}

def chemical_text(value):
    digits = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
    return re.sub(r'(?<![\w-])(?:[A-Z][a-z]?\d*){2,}(?![\w-])', lambda m:m.group().translate(digits), value)

def condition_lines(step):
    groups = []
    for key in ('agents', 'solvents'):
        value = step.get(key)
        if value:
            groups.append(', '.join(map(str, value)) if isinstance(value, list) else str(value))
    temp = step.get('temperature_reported') or step.get('temperature')
    if temp is not None:
        temp = re.sub(r'(?<=\d)\s*C\b', ' °C', str(temp))
    duration = step.get('time')
    if not duration and step.get('duration_hours') is not None:
        duration = f"{step['duration_hours']} h"
    trailing = ', '.join(str(v) for v in (temp, duration) if v not in (None, ''))
    if trailing:
        groups.append(trailing.replace('room temperature', 'rt'))
    return [line for group in groups for line in words(chemical_text(group))] or ['Conditions not recorded']

def build():
    OUT.mkdir(exist_ok=True, parents=True)
    meta = json.loads((ROOT/'data/database/absynth_metadata.json').read_text(encoding='utf8'))
    with (ROOT/'data/database/SynInsight_ABSynth_Dataset.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    for row in rows:
        groups[row['PathId']].append(row)
    datasets, drawings, manifest = {}, {}, {}
    rdDepictor.SetPreferCoordGen(True)
    for path_id, rr in groups.items():
        info = meta['paths'][path_id]
        pid = info['paper_id']
        if pid not in datasets:
            datasets[pid] = json.loads((ROOT/info['dataset']).read_text(encoding='utf8'))
        dataset = datasets[pid]
        steps = {s['step_id']:s for s in dataset['steps']}
        molecules = {m['label']:m for m in dataset['molecules']}
        nodes, edges, latest, layers = [], [], {}, defaultdict(list)
        def node(kind, rank, **values):
            result = {'id':len(nodes), 'kind':kind, 'rank':rank, **values}
            nodes.append(result)
            layers[rank].append(result)
            return result
        for row in rr:
            step = steps[info['steps'][row['StepId']]['local_step_id']]
            inputs = []
            for label in step['reactant_labels']:
                if label not in latest:
                    latest[label] = node('mol', 0, label=label)
                inputs.append(latest[label])
            rank = max([n['rank'] for n in inputs], default=0)+1
            event = node('event', rank, step=row['StepId'], local=step['step_id'],
                         conditions=row['Conditions'], lines=condition_lines(step),
                         yield_value=info['steps'][row['StepId']]['yield_percent'])
            edges.extend((n['id'], event['id']) for n in inputs)
            for label in step['product_labels']:
                product = node('mol', rank+1, label=label)
                latest[label] = product
                edges.append((event['id'], product['id']))
        target = latest.get(info['target_label'])
        incoming = defaultdict(list)
        for a,b in edges:
            incoming[b].append(a)
        for n in nodes:
            if n['kind'] == 'mol':
                m = molecules.get(n['label'], {})
                smiles = m.get('canonical_isomeric_smiles') or m.get('canonical_smiles')
                if smiles and smiles not in drawings:
                    drawings[smiles] = depict(smiles)
                n['drawing'] = drawings.get(smiles)
                n['width'] = max(110, n['drawing']['width']+24 if n['drawing'] else 210)
                n['height'] = (n['drawing']['height'] if n['drawing'] else 65)+48
            else:
                n['width'] = 240
                n['height'] = 2*max(len(n['lines'])*20+20, 60)
        # Alternate molecular structures and horizontal reaction arrows. Fold after three operations.
        for rank in sorted(layers):
            for n in layers[rank]:
                parents = incoming[n['id']]
                n['lane'] = sum(nodes[p]['lane'] for p in parents)/len(parents) if parents else layers[rank].index(n)
            layers[rank].sort(key=lambda n:n['lane'])
            for previous, n in zip(layers[rank], layers[rank][1:]):
                n['lane'] = max(n['lane'], previous['lane']+1)
        columns = min(6, max(layers)+1)
        widths = [max(n['width'] for n in nodes if n['rank']%6 == c) for c in range(columns)]
        xs = [70]
        for w in widths:
            xs.append(xs[-1]+w+32)
        width = math.ceil(xs[-1]+55)
        header = words(f"Scheme. {rr[0]['TargetName']}", max(35, int(width/11)))
        top = 40+len(header)*28+32
        bands = {}
        for band in range(max(layers)//6+1):
            members = [n for n in nodes if n['rank']//6 == band]
            lane_min = min(n['lane'] for n in members)
            lane_max = max(n['lane'] for n in members)
            row_height = max(n['height'] for n in members)+36
            for n in members:
                n['band'] = band
                n['x'] = xs[n['rank']%6]+widths[n['rank']%6]/2
                n['y'] = top+row_height/2+(n['lane']-lane_min)*row_height
            bottom = top+(lane_max-lane_min+1)*row_height
            bands[band] = {'top':top, 'bottom':bottom}
            top = bottom+100
        height = math.ceil(top+60)
        parts = [f'<svg xmlns="{NS}" width="{width*.5}pt" height="{height*.5}pt" viewBox="0 0 {width} {height}" role="img"><title>{esc(rr[0]["TargetName"])} — complete reaction pathway</title><desc>All {len(rr)} recorded operations. Read each row from left to right, following continuation connectors to the next row. Uniform bond scale, source compound labels and recorded stereochemistry. Chemical review remains pending.</desc><defs><marker id="arrow" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0 0 L9 4 L0 8" fill="none" stroke="#111" stroke-width="1.2"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Arial,Helvetica,sans-serif" fill="#111">']
        for i,line in enumerate(header):
            parts.append(txt(line, 50, 34+i*28, 22, True, 'start'))
        parts.append(txt(f"{rr[0]['DOI']} | {len(rr)} operations", 50, 36+len(header)*28, 16, anchor='start'))
        for a,b in edges:
            u,v = nodes[a],nodes[b]
            x1,y1 = u['x']+u['width']/2,u['y']
            x2,y2 = v['x']-v['width']/2,v['y']
            if u['band'] == v['band']:
                mid = (x1+x2)/2
                route = f'M{x1} {y1} C{mid} {y1} {mid} {y2} {x2} {y2}'
            else:
                # Distinct gutters for long/cross-row links avoid false shared junctions.
                lane = a % 5
                right = width-24-lane*5
                left = 20+lane*5
                bridge = bands[u['band']]['bottom']+24+lane*12
                route = f'M{x1} {y1} H{right} V{bridge} H{left} V{y2} H{x2}'
            marker = ' marker-end="url(#arrow)"' if v['kind']=='mol' else ''
            parts.append(f'<path data-from="{a}" data-to="{b}" d="{route}" fill="none" stroke="#111" stroke-width="1.2"{marker}/>')
        for n in nodes:
            x,y,w,h = n['x'],n['y'],n['width'],n['height']
            parts.append(f'<g data-kind="{n["kind"]}" data-node="{n["id"]}" data-x="{x-w/2}" data-y="{y-h/2}" data-width="{w}" data-height="{h}">')
            if n['kind']=='mol':
                # White knockout protects structures from unrelated continuation lines.
                parts.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" fill="white"/>')
                drawing = n['drawing']
                if drawing:
                    parts.append(f'<g transform="translate({x-drawing["width"]/2},{y-drawing["height"]/2-12}) scale({drawing["scale"]})">{drawing["body"]}</g>')
                else:
                    parts.append(txt('Structure not recorded',x,y))
                label_y = y+h/2-9
                parts.append(txt(n['label'], x, label_y, 17, True))
                if n is target:
                    parts.append(txt('target',x,label_y+20,14))
            else:
                parts.append(f'<title>Step {esc(n["step"])} / {esc(n["local"])}: {esc(n["conditions"])}</title>')
                parts.append(f'<path d="M{x-w/2} {y} H{x+w/2}" stroke="#111" stroke-width="1.2" fill="none"/>')
                for i,line in enumerate(n['lines']):
                    parts.append(txt(line,x,y-14-20*(len(n['lines'])-1-i)))
                value = n['yield_value']
                parts.append(txt(f'{value}%' if value not in ('',None) else 'Yield not recorded',x,y+25))
                parts.append(txt(f'({n["step"]})',x,y+47,14))
            parts.append('</g>')
        caption = 'Source-defined route; compound labels follow the dataset. rt = room temperature. Step numbers in parentheses.'
        for i,line in enumerate(words(caption, int((width-100)/8))):
            parts.append(txt(line,50,height-55+i*20,14,anchor='start'))
        parts.append(txt('SynInsight Atlas | CC BY 4.0 | Candidate data; independent chemical review pending.',50,height-13,14,anchor='start'))
        parts.append('</g></svg>')
        name = hashlib.sha256(path_id.encode()).hexdigest()[:24]+'.svg'
        (OUT/name).write_text(''.join(parts),encoding='utf8')
        manifest[path_id] = {'file':f'assets/route-overviews/{name}', 'width':width, 'height':height,
            'steps':len(rr), 'target':rr[0]['TargetName'], 'paper_id':pid,
            'molecule_nodes':sum(n['kind']=='mol' for n in nodes),'edges':len(edges),
            'style':'journal-scheme-v2','bond_length_pt':14.4,'font_size_pt':8,'rows':len(bands)}
        if len(manifest)%100 == 0:
            print(f'Publication schemes: {len(manifest)}',flush=True)
    (ROOT/'assets/route-overviews.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    print(json.dumps({'connected_routes':len(manifest),'distinct_structures_drawn':len(drawings)}),flush=True)

if __name__ == '__main__':
    build()
