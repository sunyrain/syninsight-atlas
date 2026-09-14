(() => {
  for (const table of document.querySelectorAll('table')) {
    if (!table.closest('.table-scroll,.table-wrap')) {
      const wrap=document.createElement('div');wrap.className='table-scroll';wrap.tabIndex=0;wrap.setAttribute('aria-label','Scrollable data table');table.before(wrap);wrap.append(table);
    }
  }
  for (const image of document.images) image.addEventListener('error',()=>{
    const note=document.createElement('span');note.className='image-unavailable';note.textContent='Structure image unavailable';image.replaceWith(note);
  });
  for (const code of document.querySelectorAll('code')) {
    if (code.textContent.length<45 || code.closest('pre') || !code.closest('td,article')) continue;
    const copy=document.createElement('button');copy.type='button';copy.className='copy-code';copy.textContent='Copy';copy.setAttribute('aria-label','Copy molecular or reaction notation');
    copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(code.textContent);copy.textContent='Copied';}catch{copy.textContent='Select text to copy';}});code.after(copy);
  }
})();
