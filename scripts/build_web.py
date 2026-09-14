"""Build navigable presentation pages without modifying scientific exports.

Run from the repository: .venv/Scripts/python.exe scripts/build_web.py
The optional --output directory receives only the public website file allowlist.
"""
import argparse, csv, hashlib, html, json, os, re, shutil
from pathlib import Path
from urllib.parse import urlsplit, unquote, quote, parse_qs
from bs4 import BeautifulSoup
import markdown

ROOT = Path(__file__).resolve().parents[1]
TEXT = {'.json', '.csv', '.txt', '.cff', '.sha256', '.sql', '.py'}
BINARY = {'.sqlite', '.sdf', '.zip'}
def rel(path, current):
    return os.path.relpath(path, current.parent).replace('\\', '/')
def view_path(path):
    return ROOT/'pages'/path.relative_to(ROOT).with_suffix('.html')

def diagram_svg(code):
    """Render the repository's small database diagram, retaining its actual edges."""
    positions={'P':(115,205),'S':(335,75),'C':(555,205),'M':(775,365),'E':(775,205),'O':(995,205),'R':(1215,205),'Q':(335,365)}
    labels={};edges=[]
    for line in code.splitlines():
        m=re.fullmatch(r'\s*(\w+)(?:\[([^]]+)\])?\s*-->\s*(\w+)(?:\[([^]]+)\])?\s*',line)
        if not m:continue
        a,al,b,bl=m.groups();edges.append((a,b))
        if al:labels[a]=al
        if bl:labels[b]=bl
    if not edges or set(labels)-positions.keys(): return None
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1340 440" role="img" aria-label="Atlas database relationships"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="#527968"/></marker></defs>']
    for a,b in edges:
        x,y=positions[a];xx,yy=positions[b]
        if x==xx: x1,y1,x2,y2=x,y+36,xx,yy-36
        else:x1,y1,x2,y2=x+91,y,xx-96,yy
        svg.append(f'<path d="M{x1} {y1} C{(x1+x2)/2} {y1} {(x1+x2)/2} {y2} {x2} {y2}" fill="none" stroke="#527968" stroke-width="2" marker-end="url(#arrow)"/>')
    for key,label in labels.items():
        x,y=positions[key];parts=label.split(' ',1)
        svg.append(f'<rect x="{x-91}" y="{y-36}" width="182" height="72" rx="8" fill="#edf4ef" stroke="#95b2a0"/>')
        for i,text in enumerate(parts): svg.append(f'<text x="{x}" y="{y-4+i*22}" text-anchor="middle" fill="#173c2c" font-family="system-ui,sans-serif" font-size="{16 if i==0 else 13}">{html.escape(text)}</text>')
    return ''.join(svg)+'</svg>'

def build(output=None):
    from build_absynth import build as build_absynth
    build_absynth()
    from build_route_figures import build as build_route_figures
    build_route_figures()
    from build_route_overviews import build as build_route_overviews
    build_route_overviews()
    papers = list(csv.DictReader((ROOT/'data/database/papers.csv').open(encoding='utf-8-sig', newline='')))
    imported = {p['paper_id'] for p in papers if p['source_bound_dataset_imported']=='1'}
    eligible = lambda p: 'data/routes' not in p.as_posix() or p.relative_to(ROOT).parts[2] in imported
    docs = list((ROOT/'docs').glob('*.md')) + [ROOT/x for x in ['README.md','CONTRIBUTING.md','LICENSE-CODE','LICENSE-DATA']]
    reports = [ROOT/'data/database/report.html', ROOT/'data/database/native_reactions.html'] + [ROOT/'data/routes'/p/'report.html' for p in sorted(imported)]
    sources = {p.resolve() for p in docs + reports if p.is_file()}
    public = set(sources)
    public.update(p for p in (ROOT/'assets').rglob('*') if p.is_file())
    public.update(p for p in (ROOT/'structures').glob('*.svg'))
    for paper in imported:
        public.update(p for p in (ROOT/'data/routes'/paper).rglob('*') if p.is_file() and p.suffix in TEXT | BINARY | {'.svg','.html','.md'})
    public.update(p for p in (ROOT/'data/database').iterdir() if p.is_file())
    public.update(ROOT/x for x in ['index.html','reader.html','route.html','404.html','.nojekyll','CITATION.cff','CHECKSUMS.sha256','datapackage.json','data/atlas.sqlite','data/papers.json','data/targets.json','data/papers.csv','data/targets.csv','data/summary.json','data/release.json','data/schema.json','data/extraction/batch_summary.json'])
    disabled = []
    externals = set()
    def rewrite(soup, origin, dest):
        for node in soup.find_all(['a','img','script','link']):
            key = 'href' if node.name in ['a','link'] else 'src'
            value = node.get(key)
            if not value or value.startswith(('data:','#','mailto:')): continue
            u = urlsplit(value)
            if u.scheme or u.netloc:
                if node.name=='a':
                    if u.hostname in ('localhost','127.0.0.1'):
                        node.name='code';node.attrs={};continue
                    if u.scheme not in ('https','http'):
                        node.attrs.pop('href',None); continue
                    externals.add(value);node['target']='_blank';node['rel']='noopener noreferrer'
                continue
            target=(origin.parent/unquote(u.path)).resolve()
            if target==ROOT: target=ROOT/'index.html'
            if target==ROOT/'reader.html':
                requested=parse_qs(u.query).get('file',[''])[0]
                if requested.startswith('pages/') and requested.endswith('.html'):
                    target=(ROOT/requested).resolve()
            if target==ROOT/'docs/ASPIDOSPERMA_EXTRACTION_CASE.md' and not target.exists():
                target=ROOT/'data/routes/paper-0ae671ac9a8bbe22/report.html'
                node.string='Aspidosperma case report and source boundaries'
            if target==ROOT/'data/facts':
                node.name='code';node.attrs={};node.string='data/facts/ (curation source directory)';continue
            good=target.is_relative_to(ROOT) and target.is_file() and eligible(target) and not any(x in target.parts for x in ['.local','.venv','tmp'])
            if not good:
                if node.name=='a':
                    disabled.append({'source':str(origin.relative_to(ROOT)),'target':value})
                    node.name='span';node.attrs={'class':'unavailable-resource','title':'Not included in this public website. See the source repository or case scope.'}
                    node.append(' [not in public package]')
                continue
            public.add(target)
            if node.name!='a': node[key]=rel(target,dest);continue
            if target in sources:
                node['href']=rel(view_path(target),dest)+(('#'+u.fragment) if u.fragment else '')
            elif target.name in ['index.html','reader.html','route.html','404.html'] or target.is_relative_to(ROOT/'pages'):
                node['href']=rel(target,dest)+(('?'+u.query) if u.query and target==ROOT/'reader.html' else '')+(('#'+u.fragment) if u.fragment else '')
            elif target.suffix in BINARY or node.has_attr('download'):
                node['href']=rel(target,dest);node['download']=''
            else:
                node['href']=rel(ROOT/'reader.html',dest)+'?file='+quote(target.relative_to(ROOT).as_posix(),safe='')
        for table in list(soup.find_all('table')):
            if not table.parent or 'table-scroll' in table.parent.get('class',[]) or 'table-wrap' in table.parent.get('class',[]):continue
            wrap=soup.new_tag('div',attrs={'class':'table-scroll','tabindex':'0','aria-label':'Scrollable data table'})
            table.wrap(wrap)
        for image in soup.find_all('img'):
            image['loading']='lazy'
            if not image.get('alt'): image['alt']='Molecular structure '+Path(image.get('src','')).stem
        for control in soup.find_all(['input','select']):
            if control.find_parent('label'):
                if control.get('aria-label') in ['Filter records','Filter status',control.get('placeholder')]:
                    control.attrs.pop('aria-label',None)
                continue
            if not control.get('aria-label') and not (control.get('id') and soup.find('label',attrs={'for':control['id']})):
                control['aria-label']=control.get('placeholder') or ('Filter records' if control.name=='input' else 'Filter status')
        if origin != ROOT/'index.html':
            for nested in soup.find_all('main'):
                nested.name='div'
        return soup
    for origin in sorted(sources):
        dest=view_path(origin);dest.parent.mkdir(parents=True,exist_ok=True)
        text=origin.read_text(encoding='utf-8-sig')
        if origin.suffix=='.html':
            soup=BeautifulSoup(text,'html.parser')
            title=soup.title.get_text() if soup.title else origin.stem
            content=''.join(str(n) for n in (soup.body.contents if soup.body else soup.contents) if getattr(n,'name',None) not in ['html','head','meta','title'])
            # Documents without an explicit body still retain all original content.
            if soup.html and not soup.body:content=''.join(str(n) for n in soup.html.contents if getattr(n,'name',None) not in ['head','meta','title'])
            head_styles=''.join(str(x) for x in soup.head.find_all(['style','link'])) if soup.head else ''
        else:
            title=next((l.lstrip('# ').strip() for l in text.splitlines() if l.startswith('# ')),origin.name)
            content=markdown.markdown(text,extensions=['tables','fenced_code','toc','sane_lists']) if origin.suffix=='.md' else '<h1>'+('Data license · CC BY 4.0' if origin.name=='LICENSE-DATA' else 'Code license · MIT')+'</h1><pre>'+html.escape(text)+'</pre>'
            head_styles=''
            if origin.name=='ATLAS_DATABASE.md':
                parsed=BeautifulSoup(content,'html.parser');block=parsed.select_one('code.language-mermaid')
                if block:
                    svg=diagram_svg(block.get_text())
                    if svg:
                        asset=ROOT/'assets/database-model.svg';asset.write_text(svg,encoding='utf8');public.add(asset)
                        figure=parsed.new_tag('figure',attrs={'class':'database-diagram'})
                        picture=parsed.new_tag('img',attrs={'src':'../assets/database-model.svg','alt':'Data relationships: papers link to evidence, paper compounds and candidates; compounds link to molecular identities and reactions; reactions lead to operations and routes.'})
                        figure.append(picture);block.parent.replace_with(figure);content=str(parsed)
        home=rel(ROOT/'index.html',dest)
        page=f'''<!doctype html><html lang="{'zh-CN' if origin.suffix=='.md' else 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | SynInsight Atlas</title>{head_styles}<link rel="stylesheet" href="{rel(ROOT/'assets/report.css',dest)}"><link rel="icon" href="{rel(ROOT/'assets/favicon.svg',dest)}"></head><body class="publication-page"><a class="skip-link" href="#document">Skip to content</a><nav class="publication-nav" aria-label="Atlas navigation"><a class="brand" href="{home}">SI · SynInsight Atlas</a><div><a href="{home}#atlas">Papers & routes</a><a href="{home}#dataset">Reaction dataset</a></div></nav><div class="document-meta">{'Reference document' if origin.suffix!='.html' else 'Source-bound candidate data'} · <a href="{rel(origin,dest)}" download>Download original file</a></div><main id="document" class="document-content">{content}</main><footer class="publication-footer"><a href="{home}">Return to Atlas</a><span>Candidate curation · Data CC BY 4.0 · Code MIT</span></footer><script src="{rel(ROOT/'assets/publication.js',dest)}" defer></script></body></html>'''
        # Rewrite original content before attaching shell, whose links are already relative to dest.
        body=BeautifulSoup(content,'html.parser'); rewrite(body,origin,dest)
        page=page.replace(content,str(body),1)
        dest.write_text(page,encoding='utf8'); public.add(dest)
    index=ROOT/'index.html'
    index_soup=BeautifulSoup(index.read_text(encoding='utf8'),'html.parser')
    # Keep root landmark intact; rewrite only its resource links and tables.
    rewrite(index_soup,index,index)
    index.write_text(str(index_soup),encoding='utf8')
    # Resource mapping lets dynamically created homepage links use the same presentation paths.
    resources={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'view':view_path(p).relative_to(ROOT).as_posix() if p in sources else None} for p in sorted(public) if p.is_file() and p != ROOT/'assets/resources.json'}
    manifest=ROOT/'assets/resources.json';manifest.write_text(json.dumps(resources,ensure_ascii=False,separators=(',',':')),encoding='utf8');public.add(manifest)
    for name in ['assets/site.js','assets/report.css','assets/publication.js','assets/reader.js','assets/favicon.svg']:
        public.add(ROOT/name)
    check={'rendered_pages':len(sources),'candidate_case_pages':len(imported),'unavailable_references':disabled,'external_destinations':sorted(externals)}
    audit=ROOT/'.local/web-build.json';audit.parent.mkdir(exist_ok=True);audit.write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf8')
    if output:
        output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
        for p in public:
            if p.is_file():
                target=output/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        hashes=[]
        for p in sorted(public):
            if p.is_file(): hashes.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix())
        (output/'WEB-CHECKSUMS.sha256').write_text('\n'.join(hashes)+'\n',encoding='utf8')
    print(json.dumps({'rendered_pages':len(sources),'cases':len(imported),'public_files':len(public),'unavailable_references':len(disabled)},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args();build(args.output)
