"""Validate presentation links/assets, reader inputs and export identity."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, unquote, parse_qs
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]

def validate(root=ROOT):
    root=Path(root);manifest=json.loads((root/'assets/resources.json').read_text(encoding='utf8'))
    pages=[root/'index.html',root/'reader.html',root/'route.html',root/'404.html',*sorted((root/'pages').rglob('*.html'))]
    errors=[];links=0;assets=0;external=set();soups={}
    for path in pages:
        soup=BeautifulSoup(path.read_text(encoding='utf8'),'html.parser');soups[path]=soup
        if not soup.title or not soup.title.get_text(strip=True):errors.append(f'missing_title:{path}')
        if not soup.find('meta',attrs={'name':'viewport'}):errors.append(f'missing_viewport:{path}')
        ids=[n['id'] for n in soup.select('[id]')]
        if len(ids)!=len(set(ids)):errors.append(f'duplicate_id:{path}')
        for n in soup.find_all(['a','img','link','script']):
            attr='href' if n.name in ['a','link'] else 'src';value=n.get(attr)
            if not value:continue
            if n.name=='a':links+=1
            else:assets+=1
            u=urlsplit(value)
            if u.scheme or u.netloc:
                if u.scheme in ['http','https']:external.add(value)
                continue
            target=(path.parent/unquote(u.path)).resolve() if u.path else path
            if target==root:target=root/'index.html'
            if not target.is_relative_to(root) or not target.is_file():errors.append(f'missing:{path.relative_to(root)}:{value}');continue
            if target.name=='reader.html' and u.query:
                resource=parse_qs(u.query).get('file',[''])[0]
                if resource not in manifest or not (root/resource).is_file():errors.append(f'reader_missing:{resource}')
            if u.fragment and target.suffix=='.html':
                other=soups.get(target) or BeautifulSoup(target.read_text(encoding='utf8'),'html.parser')
                if not other.find(id=unquote(u.fragment)):errors.append(f'anchor_missing:{path.relative_to(root)}:{value}')
    paths=json.loads((root/'data/database/absynth_metadata.json').read_text(encoding='utf8'))['paths']
    overviews=json.loads((root/'assets/route-overviews.json').read_text(encoding='utf8'))
    if set(overviews)!=set(paths):errors.append('connected_route_coverage_mismatch')
    for key,figure in overviews.items():
        try:
            svg=ET.parse(root/figure['file']).getroot()
            events=svg.findall('.//{http://www.w3.org/2000/svg}g[@data-kind="event"]')
            if len(events)!=len(paths[key]['steps']):errors.append(f'connected_route_step_count:{key}')
            if figure['file'] not in manifest:errors.append(f'connected_route_not_packaged:{key}')
            nodes={n.get('data-node'):n for n in svg.iter() if n.get('data-node') is not None}
            edges=[n for n in svg.iter() if n.get('data-from') is not None]
            if len(edges)!=figure['edges']:errors.append(f'connected_edge_count:{key}')
            if any(n.get('data-from') not in nodes or n.get('data-to') not in nodes for n in edges):errors.append(f'connected_edge_endpoint:{key}')
            boxes=[]
            for n in nodes.values():
                x,y,w,h=[float(n.get('data-'+attr)) for attr in ('x','y','width','height')]
                if x<0 or y<0 or x+w>figure['width'] or y+h>figure['height']:errors.append(f'figure_bounds:{key}:{n.get("data-node")}')
                for bx,by,bw,bh in boxes:
                    if min(x+w,bx+bw)-max(x,bx)>.1 and min(y+h,by+bh)-max(y,by)>.1:errors.append(f'figure_overlap:{key}:{n.get("data-node")}')
                boxes.append((x,y,w,h))

        except (OSError,ET.ParseError) as exc:errors.append(f'connected_route_svg:{key}:{exc}')
    result={'passed':not errors,'pages':len(pages),'links':links,'assets':assets,'connected_routes':len(overviews),'external_urls':len(external),'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':raise SystemExit(0 if validate()['passed'] else 1)
