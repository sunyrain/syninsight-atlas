(() => {
  const get=id=>document.getElementById(id);
  const make=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
  let rows=[],columns=[],page=1; const size=25;
  function parseCSV(text){const out=[];let row=[],field='',quoted=false;for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}else if(c===','&&!quoted){row.push(field);field='';}else if((c==='\r'||c==='\n')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(field);if(row.some(Boolean))out.push(row);row=[];field='';}else field+=c;}row.push(field);if(row.some(Boolean))out.push(row);if(quoted)throw Error('The CSV file could not be parsed. Download the original file to inspect it.');return out;}
  function tree(value,label='Record'){
    if(value===null||typeof value!=='object')return make('div',`${label}: ${value===null?'null':String(value)}`,'json-value');
    const d=make('details',undefined,'json-node'),entries=Object.entries(value);
    d.append(make('summary',`${label} · ${entries.length} ${Array.isArray(value)?'items':'fields'}`));
    let loaded=false;d.addEventListener('toggle',()=>{if(!d.open||loaded)return;loaded=true;const body=make('div',undefined,'json-children');d.append(body);let offset=0;
      const more=make('button','Show more');more.type='button';
      function batch(){const end=Math.min(offset+40,entries.length);for(;offset<end;offset++){const [k,v]=entries[offset];body.append(tree(v,k));}if(offset<entries.length){more.textContent=`Show next ${Math.min(40,entries.length-offset)} (${entries.length-offset} remaining)`;body.append(more);}else more.remove();}
      more.addEventListener('click',()=>{more.remove();batch();});batch();
    });return d;
  }
  function renderRows(){const q=get('reader-query').value.toLowerCase().trim();const filtered=rows.filter(r=>!q||r.some(v=>String(v).toLowerCase().includes(q)));const pages=Math.max(1,Math.ceil(filtered.length/size));page=Math.min(page,pages);
    const wrap=make('div',undefined,'table-scroll');wrap.tabIndex=0;wrap.setAttribute('aria-label','Scrollable data table');const table=make('table'),head=make('thead'),tr=make('tr');columns.forEach(c=>{const th=make('th',c);th.scope='col';if(/title|description|detail|smiles|json|sequence|reason|conditions/i.test(c))th.className='wide-field';tr.append(th);});head.append(tr);table.append(head);const body=make('tbody');
    for(const row of filtered.slice((page-1)*size,page*size)){const tr=make('tr');columns.forEach((name,i)=>tr.append(make('td',row[i]??'',/title|description|detail|smiles|json|sequence|reason|conditions/i.test(name)?'wide-field':'')));body.append(tr);}table.append(body);wrap.append(table);get('file-content').replaceChildren(filtered.length?wrap:make('p','No rows match your search.'));
    get('row-count').textContent=`${filtered.length.toLocaleString()} of ${rows.length.toLocaleString()} rows`;get('reader-page').textContent=`Page ${page} of ${pages}`;get('reader-prev').disabled=page===1;get('reader-next').disabled=page===pages;
  }
  async function start(){try{
    const path=new URLSearchParams(location.search).get('file');if(!path)throw Error('Choose a file from the Atlas download list.');
    const mr=await fetch('assets/resources.json');if(!mr.ok)throw Error('The file catalog is unavailable. Please reload.');const manifest=await mr.json();
    if(!Object.hasOwn(manifest,path)||path.startsWith('/')||path.split('/').includes('..'))throw Error('This file is not included in the public website.');
    const info=manifest[path];if(info.view){location.replace(info.view);return;}
    get('file-title').textContent=path.split('/').pop();document.title=`${path.split('/').pop()} | SynInsight Atlas`;
    get('file-meta').textContent=`${path} · ${info.bytes.toLocaleString()} bytes`;
    get('file-download').href=path;get('file-download').hidden=false;
    const match=path.match(/^data\/routes\/(paper-[a-f0-9]+)\//);if(match){get('file-parent').href=`pages/data/routes/${match[1]}/report.html`;get('file-parent').textContent='Back to case report';}
    if(/\.(sqlite|sdf|zip)$/i.test(path)){get('file-content').append(make('p','This scientific file is available as an original download. Open it with a compatible database or chemistry application.'));return;}
    if(path.endsWith('.svg')){const img=make('img');img.src=path;img.alt='Molecular structure';get('file-content').append(img);return;}
    const response=await fetch(path);if(!response.ok)throw Error('This file could not be loaded. Return to the file list or reload.');const text=(await response.text()).replace(/^\uFEFF/,'');
    if(path.endsWith('.csv')){const parsed=parseCSV(text);columns=parsed.shift()||[];rows=parsed;get('reader-tools').hidden=false;get('reader-pages').hidden=false;get('reader-query').addEventListener('input',()=>{page=1;renderRows();});get('reader-prev').addEventListener('click',()=>{page--;renderRows();get('reader-tools').scrollIntoView({block:'start'});});get('reader-next').addEventListener('click',()=>{page++;renderRows();get('reader-tools').scrollIntoView({block:'start'});});renderRows();}
    else if(path.endsWith('.json')){const data=JSON.parse(text);const t=tree(data,'Contents');get('file-content').append(t);t.open=true;}
    else get('file-content').append(make('pre',text));
  }catch(error){get('file-title').textContent='File unavailable';get('file-error').hidden=false;get('file-error').textContent=error.message;}
  finally{get('file-content').setAttribute('aria-busy','false');}}
  start();
})();
