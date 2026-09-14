(() => {
  const toast=document.createElement('div'); toast.className='atlas-toast'; toast.setAttribute('role','status'); toast.setAttribute('aria-live','polite'); document.body.append(toast); let timer;
  const notify=text=>{ clearTimeout(timer); toast.textContent=text; toast.classList.add('visible'); timer=setTimeout(()=>toast.classList.remove('visible'),3200); };
  const copy=async(text,success='Copied to clipboard')=>{ try{await navigator.clipboard.writeText(text);notify(success);return true;}catch{notify('Clipboard unavailable. Select and copy the text manually.');return false;} };
  window.AtlasUI={notify,copy,reduced:()=>matchMedia('(prefers-reduced-motion: reduce)').matches};
})();
