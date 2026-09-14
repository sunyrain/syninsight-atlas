(() => {
  const root = new URL('../', document.currentScript.src);
  let resources;
  const readable = /\.(json|csv|txt|cff|sha256|sql|md|py|svg)$/i;
  function decorate(container = document) {
    if (!resources) return;
    for (const a of container.querySelectorAll('a[href]')) {
      if (a.dataset.routed) continue;
      a.dataset.routed = 'true';
      let url; try { url = new URL(a.href); } catch { continue; }
      if (!['http:', 'https:'].includes(url.protocol)) { a.removeAttribute('href'); continue; }
      if (url.origin !== root.origin) { a.target='_blank'; a.rel='noopener noreferrer'; continue; }
      if (!url.pathname.startsWith(root.pathname)) continue;
      const path=decodeURIComponent(url.pathname.slice(root.pathname.length));
      const resource=resources[path];
      if (!resource) continue;
      if (/\.(sqlite|sdf|zip)$/i.test(path)) { a.download=''; a.title='Download file'; }
      else if (!a.hasAttribute('download')) {
        if (resource.view) a.href=new URL(resource.view+url.hash,root).href;
        else if (readable.test(path) || /^LICENSE-/.test(path)) a.href=new URL('reader.html?file='+encodeURIComponent(path),root).href;
      }
      if (a.hasAttribute('download')) a.title=`Download · ${formatBytes(resource.bytes)}`;
    }
  }
  function formatBytes(n) { return n<1024?`${n} B`:n<1048576?`${(n/1024).toFixed(1)} KB`:`${(n/1048576).toFixed(1)} MB`; }
  fetch(new URL('assets/resources.json',root)).then(r=>{if(!r.ok)throw Error();return r.json()}).then(r=>{
    resources=r;decorate();
    new MutationObserver(records=>{if(records.some(r=>r.addedNodes.length))decorate();}).observe(document.body,{childList:true,subtree:true});
  }).catch(()=>{
    const note=document.getElementById('site-status');
    if(note){note.hidden=false;note.textContent='Document previews could not load. Original file links remain available. Reload to retry.';}
  });
})();
