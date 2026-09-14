(() => {
  const $=id=>document.getElementById(id),ui=window.AtlasUI,ns='http://www.w3.org/2000/svg';
  const params=new URLSearchParams(location.search),path=params.get('path'),canvas=$('route-canvas'),stage=$('route-stage'),workspace=document.querySelector('.workspace');
  let graph,info,dataset,figures,metadata,figure,scale=.7,tx=0,ty=0,vertical=false,compact=true,selected='',drag,lastFocus,fitMode=false;
  const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!=null)n.textContent=text;if(cls)n.className=cls;return n;};
  const pretty=s=>String(s||'Not recorded').replaceAll('_',' ');
  const depiction=m=>m?.depiction?new URL(m.depiction,new URL(info.dataset,location.href)).href:'';
  function image(m){const n=el('img');n.src=depiction(m);n.alt=m?.name||`Compound ${m?.label||''}`;n.draggable=false;n.onerror=()=>{n.replaceWith(el('p','Structure unavailable'));};return n;}
  function transform(){stage.style.transform=`translate(${tx}px,${ty}px) scale(${scale})`;$('route-scale').textContent=`${Math.round(scale*100)}%`;$('route-plus').disabled=scale>=1.8;$('route-minus').disabled=scale<=.08;}
  function fit(){if(!graph)return;fitMode=true;scale=Math.max(.04,Math.min(1,(canvas.clientWidth-50)/graph.width,(canvas.clientHeight-50)/graph.height));tx=(canvas.clientWidth-graph.width*scale)/2;ty=(canvas.clientHeight-graph.height*scale)/2;transform();}
  function zoom(factor,x=canvas.clientWidth/2,y=canvas.clientHeight/2){if(!graph)return;fitMode=false;const next=Math.max(.04,Math.min(1.8,scale*factor)),ratio=next/scale;tx=x-(x-tx)*ratio;ty=y-(y-ty)*ratio;scale=next;transform();}
  function center(n){const card=$('routeTree').querySelector(`[data-node="${n.id}"]`);if(!card)return;const rect=card.getBoundingClientRect(),base=stage.getBoundingClientRect(),x=(rect.left-base.left+rect.width/2)/scale,y=(rect.top-base.top+rect.height/2)/scale;fitMode=false;scale=Math.max(scale,.8);tx=canvas.clientWidth/2-x*scale;ty=canvas.clientHeight/2-y*scale;transform();}
  function readable(){if(!graph)return;fitMode=false;const width=stage.scrollWidth,height=stage.scrollHeight;scale=vertical?Math.max(.35,Math.min(1,(canvas.clientWidth-48)/width)):Math.max(.68,Math.min(1,(canvas.clientHeight-48)/height));tx=vertical?(canvas.clientWidth-width*scale)/2:24;ty=vertical?24:Math.max(24,(canvas.clientHeight-height*scale)/2);transform();}
  function highlight(n){
    selected=n?.id||'';
    for(const button of $('routeTree').querySelectorAll('[data-node]'))button.classList.toggle('selected',button.dataset.node===selected);

    const stepId=n?.kind==='event'?n.stepId:n?.producedBy||'';
    $('route-step').value=stepId;
    for(const b of $('step-timeline').children){b.classList.toggle('selected',b.dataset.step===stepId);if(b.dataset.step===stepId)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');}
    const index=graph.events.findIndex(e=>e.stepId===stepId);$('route-step-prev').disabled=index<=0;$('route-step-next').disabled=index===graph.events.length-1;
    const url=new URL(location.href);stepId?url.searchParams.set('step',stepId):url.searchParams.delete('step');history.replaceState(null,'',url);
  }
  function fieldList(values){const dl=el('dl');for(const [k,v] of values)dl.append(el('dt',k),el('dd',v));return dl;}
  function reportLink(){const a=el('a','Open source case report ↗');a.href=info.report;return a;}
  function overview(){highlight(null);const box=$('inspector');box.replaceChildren(el('span','PATHWAY OVERVIEW','eyebrow'),el('h2',figure.target),el('p',info.title),fieldList([['Path type',pretty(info.route_type)],['Coverage',pretty(info.coverage_scope)],['Review',pretty(info.review_status)]]),reportLink(),el('p','Select any molecule or numbered step on the canvas to inspect its recorded details.'));}
  function select(n,move=false){
    highlight(n);if(move)center(n);const box=$('inspector');box.replaceChildren();
    if(n.kind==='mol'){
      const m=n.molecule||{};box.append(el('span',n.target?'TARGET COMPOUND':n.initial?'STARTING MATERIAL':'INTERMEDIATE','eyebrow'),el('h2',m.name||`Compound ${n.label}`),image(m),fieldList([['Label',n.label],['Formula',m.molecular_formula||'Not recorded'],['Stereo',pretty(m.stereo_status)],['Review',pretty(m.review_status)]]));
      const smiles=m.canonical_isomeric_smiles||m.canonical_smiles||'';box.append(el('code',smiles||'Structure not recorded'));
      if(smiles){const copy=el('button','Copy SMILES');copy.onclick=()=>ui.copy(smiles,'Compound SMILES copied');box.append(copy);}
      if(n.producedBy){const b=el('button',`Inspect producing step ${n.producedBy}`);b.style.marginTop='12px';b.onclick=()=>select(graph.events.find(e=>e.stepId===n.producedBy),true);box.append(b);}
      box.append(reportLink());
    }else{
      const s=n.step,m=n.meta;box.append(el('span',`RECORDED STEP ${n.stepId}`,'eyebrow'),el('h2',s.transformation||`${s.reactant_labels.join(' + ')} → ${s.product_labels.join(' + ')}`));
      const conditions=[];for(const k of ['agents','solvents','temperature_reported','temperature','time','duration_hours','pressure','current_mA']){const v=s[k];if(v!=null&&v!==''&&(!Array.isArray(v)||v.length))conditions.push(`${k==='duration_hours'?'Time':pretty(k)}: ${Array.isArray(v)?v.join(', '):v}${k==='duration_hours'?' h':''}`);}
      box.append(el('p',conditions.join('\n')||'Conditions not recorded','condition-box'),fieldList([['Yield',m.yield_percent==null||m.yield_percent===''?'Not recorded':`${m.yield_percent}%`],['Operation',m.local_step_id],['Inputs',s.reactant_labels.join(' + ')],['Products',s.product_labels.join(' + ')],['Basis',pretty(m.structure_basis)]]));
      box.append(el('h3','Source evidence'));const refs=el('ul');for(const r of m.source_references||[])refs.append(el('li',`${r.locator||r.source_id}${r.pages?.length?` · p. ${r.pages.join(', ')}`:''}`));box.append(refs,reportLink());if(s.notes)box.append(el('p',s.notes));
    }
  }
  function render(){
    graph=window.RouteNetwork.build(dataset,info,vertical);canvas.classList.toggle('horizontalRoute',!vertical);
    const outcome=window.AutoPlannerTree.mount($('routeTree'),graph,{compact,depiction,select:n=>{if(!drag?.moved)select(n);}});
    if(outcome.renderedSteps!==graph.events.length)throw Error('Route tree omitted a recorded operation.');
    stage.style.width='max-content';stage.style.height='auto';
    graph.width=stage.scrollWidth;graph.height=stage.scrollHeight;
    $('stat-steps').textContent=graph.events.length;$('stat-molecules').textContent=graph.nodes.filter(n=>n.kind==='mol').length;
    $('route-step').replaceChildren(new Option('Full route',''),...graph.events.map(n=>new Option(`Step ${n.stepId} · ${n.meta.local_step_id}`,n.stepId)));
    $('step-timeline').replaceChildren(...graph.events.map(n=>{const b=el('button',null,'timeline-step');b.dataset.step=n.stepId;const text=el('span');text.append(el('strong',n.step.transformation||`${n.step.reactant_labels.join(' + ')} → ${n.step.product_labels.join(' + ')}`),el('small',`${n.meta.local_step_id} · ${n.meta.yield_percent==null||n.meta.yield_percent===''?'Yield not recorded':n.meta.yield_percent+'% yield'}`));b.append(el('span',n.stepId),text);b.onclick=()=>select(n,true);return b;}));
    $('sequence-count').textContent=`${graph.events.length} steps`;
    overview();readable();
  }
  canvas.addEventListener('wheel',e=>{if(!graph)return;e.preventDefault();const r=canvas.getBoundingClientRect();zoom(Math.exp(-e.deltaY*.0018),e.clientX-r.left,e.clientY-r.top);},{passive:false});
  canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,tx,ty,moved:false,id:e.pointerId};});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>4){drag.moved=true;canvas.setPointerCapture(e.pointerId);canvas.classList.add('dragging');fitMode=false;tx=drag.tx+dx;ty=drag.ty+dy;transform();}});
  function release(){canvas.classList.remove('dragging');setTimeout(()=>drag=null,0);}
  canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);
  canvas.addEventListener('dblclick',e=>{if(e.target.closest('button'))return;const r=canvas.getBoundingClientRect();zoom(1.5,e.clientX-r.left,e.clientY-r.top);});
  $('route-plus').onclick=()=>zoom(1.25);$('route-minus').onclick=()=>zoom(.8);$('route-fit').onclick=()=>{overview();fit();};
  $('route-compact').onclick=()=>{compact=!compact;$('route-compact').textContent=compact?'Full detail':'Compact';$('route-compact').setAttribute('aria-pressed',String(compact));render();};
  $('route-readable').onclick=readable;
  $('route-layout').onclick=()=>{vertical=!vertical;$('route-layout').textContent=vertical?'Horizontal layout':'Vertical layout';render();};
  $('route-step').onchange=()=>{const n=graph.events.find(n=>n.stepId===$('route-step').value);n?select(n,true):(overview(),fit());};
  for(const [id,delta] of [['route-step-prev',-1],['route-step-next',1]])$(id).onclick=()=>{const i=graph.events.findIndex(n=>n.stepId===$('route-step').value);select(graph.events[Math.max(0,Math.min(graph.events.length-1,i+delta))],true);};
  $('toggle-details').onclick=()=>{const hidden=workspace.classList.toggle('hide-details');$('toggle-details').textContent=hidden?'Show details':'Hide details';$('toggle-details').setAttribute('aria-pressed',String(hidden));if(fitMode)fit();};
  function expand(){const open=workspace.classList.toggle('expanded');$('route-fullscreen').textContent=open?'Exit expanded':'Expand';if(open){lastFocus=document.activeElement;$('route-fullscreen').focus();}else lastFocus?.focus();if(fitMode)fit();}
  $('route-fullscreen').onclick=expand;
  $('route-share').onclick=()=>ui.copy(location.href,'Pathway link copied');
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&workspace.classList.contains('expanded')){expand();return;}if(e.ctrlKey||e.metaKey||e.altKey||/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)||!graph)return;if(!document.querySelector('.canvas-panel').contains(document.activeElement))return;if(e.key==='0'){e.preventDefault();fit();}if(e.key==='+'||e.key==='='){e.preventDefault();zoom(1.25);}if(e.key==='-'){e.preventDefault();zoom(.8);}});
  new ResizeObserver(()=>{if(graph&&fitMode)fit();}).observe(canvas);
  function related(){const entries=Object.entries(metadata.paths).filter(([id,p])=>p.paper_id===info.paper_id&&(!$('route-search').value||figures[id].target.toLowerCase().includes($('route-search').value.toLowerCase())));$('related-routes').replaceChildren(...entries.map(([id,p],i)=>{const a=el('a',null,`route-option${id===path?' active':''}`);a.href=`route.html?path=${encodeURIComponent(id)}`;if(id===path)a.setAttribute('aria-current','page');a.append(el('span',`ROUTE ${String(i+1).padStart(2,'0')}`,'route-index'),el('strong',figures[id].target),el('small',`${Object.keys(p.steps).length} steps · ${pretty(p.route_type)}`));return a;}));if(!entries.length)$('related-routes').append(el('p','No matching routes.','sidebar-note'));}
  $('route-search').oninput=related;
  async function load(){try{$('route-status').textContent='Loading the recorded network…';$('route-retry').hidden=true;const fetchJSON=async url=>{const r=await fetch(url);if(!r.ok)throw Error('Unable to load route data.');return r.json();};[figures,metadata]=await Promise.all([fetchJSON('assets/route-overviews.json'),fetchJSON('data/database/absynth_metadata.json')]);figure=figures[path];info=metadata.paths[path];if(!figure||!info)throw Error('Route not found. Return to the dataset to select a product.');dataset=await fetchJSON(info.dataset);$('route-title').textContent=figure.target;$('route-description').textContent=info.title;document.title=`${figure.target} · Route workspace | SynInsight Atlas`;$('route-download').href=figure.file;$('route-total').textContent=Object.values(metadata.paths).filter(p=>p.paper_id===info.paper_id).length+' routes';related();render();
    const target=graph.target?.molecule;if(target)$('target-card').replaceChildren(image(target),el('strong',target.name||`Target ${target.label}`),el('small',target.molecular_formula||target.label));
    $('route-status').textContent='';const step=graph.events.find(n=>n.stepId===params.get('step'));if(step)select(step,true);
  }catch(e){$('route-status').textContent=e.message;$('route-retry').hidden=false;}}
  $('route-retry').onclick=load;load();
})();
