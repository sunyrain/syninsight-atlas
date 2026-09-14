(() => {
  const $=id=>document.getElementById(id), ui=window.AtlasUI;
  const params=new URLSearchParams(location.search), path=params.get('path');
  const canvas=$('route-canvas'), img=$('route-image'), stage=$('route-stage'), viewer=document.querySelector('.route-viewer');
  let figure, info, scale=1, mode='whole', boxes=new Map(), selected='', drag, lastFocus, loading=false;
  const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));
  const steps=()=>Object.keys(info?.steps||{});
  function highlight(){
    const box=boxes.get(selected), mark=$('route-highlight'); mark.hidden=!box;
    if(box)Object.assign(mark.style,{left:`${box.x*scale}px`,top:`${box.y*scale}px`,width:`${box.w*scale}px`,height:`${box.h*scale}px`});
  }
  function setScale(next,anchor){
    if(!figure)return;
    const before=img.getBoundingClientRect(), cr=canvas.getBoundingClientRect();
    const point=anchor||{x:cr.left+canvas.clientWidth/2,y:cr.top+canvas.clientHeight/2};
    const fx=(point.x-before.left)/(before.width||1),fy=(point.y-before.top)/(before.height||1);
    scale=clamp(next,.04,4);
    stage.style.width=`${figure.width*scale}px`; img.style.width='100%';
    const after=img.getBoundingClientRect();
    canvas.scrollLeft+=after.left+fx*after.width-point.x; canvas.scrollTop+=after.top+fy*after.height-point.y;
    $('route-scale').textContent=`${Math.round(scale*100)}%`;
    $('route-minus').disabled=scale<=.0401; $('route-plus').disabled=scale>=3.999;
    highlight();
  }
  function fit(){
    if(!figure)return;
    const width=canvas.clientWidth-32;
    setScale(mode==='whole'?Math.min(width/figure.width,(canvas.clientHeight-32)/figure.height):width/figure.width);
    canvas.scrollTop=0;canvas.scrollLeft=0;
  }
  function manual(factor,anchor){mode='custom';$('route-zoom').value='custom';setScale(scale*factor,anchor);}
  function reset(){mode='whole';$('route-zoom').value=mode;fit();}
  $('route-zoom').onchange=()=>{mode=$('route-zoom').value;if(mode==='whole'||mode==='fit')fit();else if(mode!=='custom')setScale(Number(mode)/100);};
  $('route-plus').onclick=()=>manual(1.25); $('route-minus').onclick=()=>manual(.8);
  canvas.addEventListener('wheel',e=>{if(!figure||(!e.ctrlKey&&!e.metaKey))return;e.preventDefault();manual(Math.exp(-e.deltaY*.004),{x:e.clientX,y:e.clientY});},{passive:false});
  canvas.addEventListener('dblclick',e=>{if(figure)manual(e.shiftKey ? 0.5 : 2,{x:e.clientX,y:e.clientY});});
  canvas.addEventListener('pointerdown',e=>{
    if(e.pointerType!=='mouse'||e.button!==0||!figure)return;
    drag={x:e.clientX,y:e.clientY,left:canvas.scrollLeft,top:canvas.scrollTop};canvas.setPointerCapture(e.pointerId);canvas.classList.add('dragging');canvas.focus({preventScroll:true});
  });
  canvas.addEventListener('pointermove',e=>{if(!drag)return;canvas.scrollLeft=drag.left-(e.clientX-drag.x);canvas.scrollTop=drag.top-(e.clientY-drag.y);});
  const release=()=>{drag=null;canvas.classList.remove('dragging');};
  canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);canvas.addEventListener('lostpointercapture',release);
  function closeFull(){
    viewer.classList.remove('expanded');document.body.style.overflow='';viewer.removeAttribute('role');viewer.removeAttribute('aria-modal');
    (lastFocus||$('route-fullscreen')).focus({preventScroll:true});if(mode==='whole'||mode==='fit')fit();
  }
  $('route-fullscreen').onclick=()=>{lastFocus=document.activeElement;viewer.classList.add('expanded');document.body.style.overflow='hidden';viewer.setAttribute('role','dialog');viewer.setAttribute('aria-modal','true');$('route-close-fullscreen').focus();if(mode==='whole'||mode==='fit')fit();};
  $('route-close-fullscreen').onclick=closeFull;
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'&&viewer.classList.contains('expanded')){e.preventDefault();closeFull();return;}
    if(e.key==='Tab'&&viewer.classList.contains('expanded')){
      const focusables=[...viewer.querySelectorAll('button:not(:disabled),select,a[href],[tabindex="0"]')].filter(n=>n.getClientRects().length);
      const first=focusables[0],last=focusables.at(-1);
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
    }
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    if(!viewer.contains(document.activeElement)||/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName))return;
    if(e.key==='+'||e.key==='='){e.preventDefault();manual(1.25);}else if(e.key==='-'){e.preventDefault();manual(.8);}else if(e.key==='0'){e.preventDefault();reset();}else if(e.key.toLowerCase()==='f'){e.preventDefault();viewer.classList.contains('expanded')?closeFull():$('route-fullscreen').click();}
  });
  function selectStep(value,focus=true){
    selected=value; $('route-step').value=value;
    const list=steps(), index=list.indexOf(value), detail=$('route-step-detail');
    $('route-step-prev').disabled=index<=0; $('route-step-next').disabled=index>=list.length-1;
    const url=new URL(location.href);value?url.searchParams.set('step',value):url.searchParams.delete('step');history.replaceState(null,'',url);
    detail.replaceChildren();detail.hidden=!value;
    if(!value){$('route-position').textContent='Whole pathway';highlight();reset();return;}
    const step=info.steps[value];
    const title=document.createElement('strong');title.textContent=`Step ${value} · ${step.local_step_id}`;
    const yieldText=document.createElement('span');yieldText.textContent=step.yield_percent==null||step.yield_percent===''?'Yield not recorded':`Reported yield: ${step.yield_percent}%`;
    const evidence=document.createElement('span');evidence.textContent=(step.source_references||[]).map(r=>`${r.locator||r.source_id||'Source'}${r.pages?.length?` · p. ${r.pages.join(', ')}`:''}`).join(' / ');
    detail.append(title,yieldText,evidence);$('route-position').textContent=`Step ${index+1} / ${list.length}`;
    const box=boxes.get(value);
    if(box&&focus){mode='custom';$('route-zoom').value=mode;setScale(Math.max(scale,Math.min(1.25,(canvas.clientWidth-48)/(box.w+320))));const r=img.getBoundingClientRect(),c=canvas.getBoundingClientRect();canvas.scrollLeft+=r.left+(box.x+box.w/2)*scale-c.left-canvas.clientWidth/2;canvas.scrollTop+=r.top+(box.y+box.h/2)*scale-c.top-canvas.clientHeight/2;}
    highlight();
  }
  $('route-step').onchange=()=>selectStep($('route-step').value);
  $('route-step-prev').onclick=()=>{const list=steps();selectStep(list[Math.max(0,list.indexOf(selected)-1)]);};
  $('route-step-next').onclick=()=>{const list=steps();selectStep(list[Math.min(list.length-1,list.indexOf(selected)+1)]);};
  $('route-share').onclick=()=>ui.copy(location.href,'Link copied — includes the selected step');
  $('route-download').onclick=()=>ui.notify('Downloading vector SVG');
  window.addEventListener('resize',()=>{if(figure&&(mode==='whole'||mode==='fit'))fit();});
  async function load(){
    if(loading)return;loading=true;viewer.setAttribute('aria-busy','true');$('route-retry').hidden=true;$('route-status').textContent='Preparing vector diagram…';
    try{
      const responses=await Promise.all([fetch('assets/route-overviews.json'),fetch('data/database/absynth_metadata.json')]);
      if(responses.some(r=>!r.ok))throw Error('The pathway files could not be loaded.');
      const [figures,metadata]=await Promise.all(responses.map(r=>r.json()));figure=figures[path];info=metadata.paths[path];
      if(!figure||!info)throw Error('This route is not in the current dataset. Return to the dataset and select a product.');
      document.title=`${figure.target} · Reaction pathway | SynInsight Atlas`;
      $('route-title').textContent=figure.target;$('route-description').textContent=`Complete connected pathway · ${figure.steps} operations · ${info.title}`;
      $('route-download').href=figure.file;$('route-report').href=info.report;
      img.alt=`Full reaction pathway for ${figure.target}, ${figure.steps} operations, with structures, conditions and yields`;
      const svgResponse=await fetch(figure.file);if(!svgResponse.ok)throw Error('The vector diagram could not load.');
      const xml=new DOMParser().parseFromString(await svgResponse.text(),'image/svg+xml');
      if(xml.querySelector('parsererror'))throw Error('The vector diagram is invalid.');
      boxes=new Map([...xml.querySelectorAll('g[data-kind="event"]')].map(n=>{const id=n.querySelector('title')?.textContent.match(/^Step (\S+)/)?.[1];return[id,{x:Number(n.getAttribute('data-x')),y:Number(n.getAttribute('data-y')),w:Number(n.getAttribute('data-width')),h:Number(n.getAttribute('data-height'))}];}));
      $('route-step').replaceChildren(new Option('All steps',''),...steps().map(id=>new Option(`Step ${id} · ${info.steps[id].local_step_id}`,id)));
      await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(Error('The vector diagram could not load.'));img.src=figure.file;});
      img.hidden=false;$('route-tools').hidden=false;$('route-status').textContent='';fit();selectStep(steps().includes(params.get('step'))?params.get('step'):'',true);
    }catch(error){$('route-status').textContent=error.message;$('route-retry').hidden=false;if(!figure)$('route-title').textContent='Pathway unavailable';}
    finally{loading=false;viewer.setAttribute('aria-busy','false');}
  }
  $('route-retry').onclick=load;load();
})();
