/* The downloadable CSV is the single source of rows shown in the main browser. */
(() => {
  const $ = id => document.getElementById(id);
  const el = (tag, value, cls) => { const n = document.createElement(tag); if (value !== undefined) n.textContent = value; if (cls) n.className = cls; return n; };
  const a = (label, href) => { const n = el('a', label); n.href = href; return n; };
  function parse(text) {
    const rows = []; let row = [], value = '', quoted = false;
    text = text.replace(/^\uFEFF/, '');
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (c === '"') { if (quoted && text[i + 1] === '"') { value += '"'; i++; } else quoted = !quoted; }
      else if (c === ',' && !quoted) { row.push(value); value = ''; }
      else if ((c === '\n' || c === '\r') && !quoted) { if (c === '\r' && text[i + 1] === '\n') i++; row.push(value); if (row.some(Boolean)) rows.push(row); row = []; value = ''; }
      else value += c;
    }
    if (quoted) throw new Error('Incomplete CSV');
    row.push(value); if (row.some(Boolean)) rows.push(row);
    const fields = rows.shift();
    return rows.map(r => Object.fromEntries(fields.map((f, i) => [f, r[i] || ''])));
  }
  let rows = [], meta, page = 1, filtered = [];
  const size = 20;
  const ui=window.AtlasUI, stateKey='atlas-dataset-view-v2';
  let searchIndex=[], searchTimer, composing=false, selectedKey='';
  function saveState(){
    const state={q:$('ds-query').value,path:$('ds-path').value,kind:$('ds-kind').value,page};
    try{sessionStorage.setItem(stateKey,JSON.stringify(state));}catch{}
    const url=new URL(location.href);
    for(const [key,value] of Object.entries(state)){const name='ds_'+key;if(value && !(key==='page'&&value===1))url.searchParams.set(name,value);else url.searchParams.delete(name);}
    history.replaceState(null,'',url);
  }
  function restoreState(){
    const params=new URLSearchParams(location.search);let state={};
    if([...params.keys()].some(k=>k.startsWith('ds_'))){for(const key of ['q','path','kind','page'])state[key]=params.get('ds_'+key)||'';}
    else try{state=JSON.parse(sessionStorage.getItem(stateKey)||'{}');}catch{}
    $('ds-query').value=state.q||'';$('ds-path').value=meta.paths[state.path]?state.path:'';
    $('ds-kind').value=[...$('ds-kind').options].some(o=>o.value===state.kind)?state.kind:'';
    page=Math.max(1,Math.floor(Number(state.page)||1));
  }
  function chips(){
    const box=$('ds-active-filters');box.replaceChildren();
    for(const [id,label] of [['ds-query','Search'],['ds-path','Path'],['ds-kind','Type']]){
      if(!$(id).value)continue;
      const value=id==='ds-query'?$(id).value:$(id).selectedOptions[0].textContent;
      const button=el('button',`${label}: ${value} ×`,'ds-filter-chip');button.type='button';button.title=`Remove ${label.toLowerCase()} filter`;button.onclick=()=>{$(id).value='';page=1;draw();$(id).focus();};box.append(button);
    }
    box.hidden=!box.childElementCount;
  }
  const readable = value => (value || 'Not recorded').replaceAll('_', ' ');
  function preview(r, scroll = false) {
    const panel = $('ds-preview'); panel.hidden = !r;
    selectedKey=r?`${r.PathId}:${r.StepId}`:'';
    for(const row of $('ds-rows').children)row.classList.toggle('is-selected',row.dataset.key===selectedKey);
    if (!r) return;
    const path = meta.paths[r.PathId], step = path.steps[r.StepId];
    const heading = el('div', undefined, 'ds-preview-heading');
    const title = el('div'); title.append(el('p', 'Step preview · source-bound candidate', 'eyebrow'), el('h3', `${r.TargetName} · Step ${r.StepId}`));
    const full = el('button', 'All step details'); full.type = 'button'; full.onclick = () => show(r); heading.append(title, full);
    const facts = el('dl', undefined, 'ds-step-facts');
    for (const [key, value] of [['Reported yield', step.yield_percent === '' || step.yield_percent == null ? 'Not recorded' : `${step.yield_percent}%`], ['Operation / event', `${step.local_step_id} / ${step.local_event_id}`], ['Reaction name', r.RxnName || 'Not recorded'], ['Review status', readable(path.review_status)]]) {
      const fact = el('div'); fact.append(el('dt', key), el('dd', value)); facts.append(fact);
    }
    const grid = el('div', undefined, 'ds-preview-grid');
    const conditions = el('section'); conditions.append(el('h4', 'Conditions & route scope'), el('p', r.Conditions || 'Conditions not recorded.', 'ds-condition-text'), el('p', `Path type: ${readable(path.route_type)}`), el('p', `Coverage: ${readable(path.coverage_scope)}`), el('p', `Structure basis: ${readable(step.structure_basis)}`));
    const source = el('section'); source.append(el('h4', 'Source evidence'), el('p', path.title), a(r.DOI, `https://doi.org/${encodeURI(r.DOI)}`));
    const refs = el('ul');
    for (const ref of step.source_references) refs.append(el('li', `${ref.source_id || 'Source'} · ${ref.locator || 'Locator not recorded'}${ref.pages?.length ? ` · p. ${ref.pages.join(', ')}` : ''}`));
    source.append(refs, a('Open case report ↗', path.report)); grid.append(conditions, source);
    const more = el('details', undefined, 'ds-preview-smiles'); more.append(el('summary', 'Show reaction SMILES'));
    const code = el('code', r.RxnSMILES); more.append(code);
    panel.replaceChildren(heading, a('View full reaction pathway ↗', `route.html?path=${encodeURIComponent(r.PathId)}`), facts, grid, more, el('p', 'Reported yield may apply to a combined preparation or mixture. Consult the case report for yield scope and source conflicts.', 'ds-help'));
    if (scroll) { panel.scrollIntoView({block:'start',behavior:ui.reduced()?'auto':'smooth'}); panel.focus({preventScroll:true}); }
  }
  function draw() {
    const q = $('ds-query').value.trim().toLowerCase(), path = $('ds-path').value, kind = $('ds-kind').value;
    const terms=q.split(/\s+/).filter(Boolean);
    filtered = rows.filter((r,i) => (!path || r.PathId === path) && (!kind || meta.paths[r.PathId].route_type === kind) && terms.every(term=>searchIndex[i].includes(term)));
    const pages = Math.max(1, Math.ceil(filtered.length / size)); page = Math.min(page, pages);
    const pathCount = new Set(filtered.map(r => r.PathId)).size;
    $('ds-count').textContent = `${filtered.length.toLocaleString()} / ${rows.length.toLocaleString()} step occurrences · ${pathCount} ${pathCount === 1 ? 'path' : 'paths'}`;
    $('ds-page').textContent = `Page ${page} of ${pages}`;
    for (const suffix of ['top', 'bottom']) {
      const input = $(`ds-jump-${suffix}`);
      input.max = pages; input.value = page; input.disabled = !filtered.length;
      $(`ds-jump-total-${suffix}`).textContent = `/ ${pages}`;
      $(`ds-jump-form-${suffix}`).querySelector('button').disabled = !filtered.length;
    }
    for(const suffix of ['', '-top']){$('ds-prev'+suffix).disabled=page===1;$('ds-next'+suffix).disabled=page===pages;}
    $('ds-export').disabled = !filtered.length;saveState();chips();
    $('ds-empty').hidden = !!filtered.length;
    preview(filtered[(page - 1) * size]);
    $('ds-rows').replaceChildren(...filtered.slice((page - 1) * size, page * size).map(r => {
      const tr = el('tr'), path = meta.paths[r.PathId], target = el('td');
      tr.dataset.key=`${r.PathId}:${r.StepId}`;tr.classList.toggle('is-selected',tr.dataset.key===selectedKey);
      const routeLink = a(r.TargetName, `route.html?path=${encodeURIComponent(r.PathId)}`); routeLink.className='ds-target';
      routeLink.title = `Open reaction pathway for ${r.TargetName}`;
      const filter = el('button', 'Filter this path', 'ds-copy'); filter.type='button';
      filter.onclick = () => { $('ds-path').value = r.PathId; $('ds-query').value = ''; $('ds-kind').value = ''; page = 1; draw(); };
      target.append(routeLink, el('small', r.PathId, 'ds-id'), filter);
      const source = el('td'); source.append(a(r.DOI, `https://doi.org/${encodeURI(r.DOI)}`), el('small', `${r.Year} · ${r.Author}`));
      const rxn = el('td'); rxn.append(el('code', r.RxnSMILES));
      const copy = el('button', 'Copy SMILES', 'ds-copy'); copy.type = 'button'; copy.onclick = async () => { if(await ui.copy(r.RxnSMILES,'Reaction SMILES copied')){copy.textContent='Copied ✓';setTimeout(()=>copy.textContent='Copy SMILES',1800);} }; rxn.append(copy);
      const action = el('td'), detail = el('button', 'Preview step ↑'); detail.type = 'button'; detail.onclick = () => preview(r, true); action.append(detail, a('Case report ↗', path.report));
      const step = path.steps[r.StepId], stepCell = el('td', r.StepId, 'numeric');
      stepCell.append(el('small', step.local_step_id), el('small', step.yield_percent === '' || step.yield_percent == null ? 'Yield not recorded' : `Yield ${step.yield_percent}%`));
      tr.append(target, source, stepCell, rxn, el('td', r.RxnName || 'Not recorded'), el('td', r.Conditions || 'Not recorded'), action);
      ['Target / path','Source','Step','Reaction SMILES','Reaction name','Conditions','Explore'].forEach((label,i)=>tr.children[i].dataset.label=label);return tr;
    }));
  }
  function show(r) {
    const path = meta.paths[r.PathId], step = path.steps[r.StepId], content = $('ds-detail');
    content.replaceChildren(el('p', `Step ${r.StepId} · ${step.local_step_id}`, 'eyebrow'), el('h2', r.TargetName), el('p', path.title));
    const dl = el('dl');
    for (const [key, value] of Object.entries({...r, RouteType: path.route_type, Coverage: path.coverage_scope, Review: path.review_status, YieldPercent: step.yield_percent, StructureBasis: step.structure_basis})) { dl.append(el('dt', key), el('dd', value == null || value === '' ? 'Not recorded' : value)); }
    content.append(dl, el('h3', 'Source locators'));
    for (const ref of step.source_references) content.append(el('p', `${ref.source_id || ''} · ${ref.locator || ''} · pages ${(ref.pages || []).join(', ')}`));
    content.append(a('Open case report ↗', path.report), document.createTextNode(' · '), a('Source dataset', `reader.html?file=${encodeURIComponent(path.dataset)}`));
    content.append(document.createTextNode(' · '),a('View full pathway',`route.html?path=${encodeURIComponent(r.PathId)}&step=${encodeURIComponent(r.StepId)}`));
    $('ds-dialog').showModal();
  }
  $('ds-close').onclick = () => $('ds-dialog').close();
  $('ds-dialog').onclick = e => { const b = $('ds-dialog').getBoundingClientRect(); if (e.target === $('ds-dialog') && (e.clientX < b.left || e.clientX > b.right || e.clientY < b.top || e.clientY > b.bottom)) $('ds-dialog').close(); };
  $('ds-filters').onsubmit = e => {e.preventDefault();clearTimeout(searchTimer);page=1;if(meta)draw();};
  $('ds-filters').onreset = e => { e.preventDefault(); $('ds-query').value = ''; $('ds-path').value = ''; $('ds-kind').value = ''; $('ds-rows').closest('.table-scroll').scrollLeft = 0; page = 1; if (meta) draw(); };
  for (const id of ['ds-query', 'ds-path', 'ds-kind']) $(id).addEventListener(id === 'ds-query' ? 'input' : 'change', () => { clearTimeout(searchTimer);if(composing)return;page=1;if(meta){if(id==='ds-query')searchTimer=setTimeout(draw,180);else draw();} });
  $('ds-query').addEventListener('compositionstart',()=>composing=true);$('ds-query').addEventListener('compositionend',()=>{composing=false;page=1;if(meta)draw();});
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)&&!$('ds-dialog').open){e.preventDefault();$('ds-query').focus();}if(e.key==='Escape'&&document.activeElement===$('ds-query')){$('ds-query').value='';page=1;if(meta)draw();}});
  $('ds-share').onclick=()=>{clearTimeout(searchTimer);if(meta)draw();const link=new URL(location.href);link.searchParams.set('ds_page',String(page));ui.copy(link.href,'Search link copied');};
  $('ds-empty-reset').onclick=()=>$('ds-filters').reset();
  for (const [id, delta] of [['ds-prev', -1], ['ds-next', 1],['ds-prev-top',-1],['ds-next-top',1]]) $(id).onclick = () => { page += delta; draw(); $('ds-filters').scrollIntoView({block: 'start'}); };
  for (const suffix of ['top', 'bottom']) {
    $(`ds-jump-form-${suffix}`).onsubmit = e => {
      e.preventDefault();
      const input = $(`ds-jump-${suffix}`), requested = Number(input.value);
      if (!meta || !Number.isInteger(requested) || requested < 1 || requested > Number(input.max)) { input.reportValidity(); return; }
      page = requested; draw(); $('ds-filters').scrollIntoView({block: 'start'});
    };
  }
  $('ds-export').onclick = () => {
    const fields = meta.fields, quote = v => `"${v.replace(/"/g, '""')}"`;
    const csv = '\uFEFF' + [fields, ...filtered.map(r => fields.map(k => r[k]))].map(r => r.map(quote).join(',')).join('\r\n') + '\r\n';
    const url = URL.createObjectURL(new Blob([csv], {type: 'text/csv;charset=utf-8'})); const link = a('', url); link.download = 'SynInsight_ABSynth_filtered.csv'; link.click(); ui.notify(`Exported ${filtered.length.toLocaleString()} step occurrences`); setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  Promise.all([fetch('data/database/SynInsight_ABSynth_Dataset.csv'), fetch('data/database/absynth_metadata.json')]).then(async responses => {
    if (responses.some(r => !r.ok)) throw new Error('Dataset unavailable');
    rows = parse(await responses[0].text()); meta = await responses[1].json();
    if (rows.length !== meta.rows) throw new Error('Dataset and metadata do not match');
    $('ds-metrics').replaceChildren(...[[meta.rows.toLocaleString(), 'Step occurrences'], [meta.paths_count, 'Paths & branches'], [meta.papers_count, 'Source papers'], [meta.unique_operations.toLocaleString(), 'Distinct operations in paths']].map(([v, label]) => { const n = el('article'); n.append(el('strong', v), el('span', label)); return n; }));
    const first = new Map(rows.map(r => [r.PathId, r]));
    for (const [id, r] of [...first].sort((a, b) => a[1].TargetName.localeCompare(b[1].TargetName))) { const option = el('option', `${r.TargetName} · ${r.DOI}`); option.value = id; $('ds-path').append(option); }
    for (const kind of [...new Set(Object.values(meta.paths).map(p => p.route_type))].sort()) { const option = el('option', kind.replaceAll('_', ' ')); option.value = kind; $('ds-kind').append(option); }
    $('ds-quality').textContent = `RxnName is absent in ${meta.blank_counts.RxnName.toLocaleString()} rows; Conditions is absent in ${meta.blank_counts.Conditions} rows. Blank values mean not recorded. TargetName preserves the existing route label, including numbered endpoints and control branches.`;
    searchIndex=rows.map(r=>(Object.values(r).join(' ')+' '+meta.paths[r.PathId].title).toLowerCase());
    restoreState();draw();
  }).catch(() => { $('ds-error').hidden = false; $('ds-error').textContent = 'Unable to load the dataset. Reload this page or download the CSV directly.'; $('ds-count').textContent = 'Dataset unavailable'; });
})();
