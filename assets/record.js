(() => {
  const get = id => document.getElementById(id);
  const scalar = (text, key) => {
    const match = text.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'));
    return match ? match[1].trim().replace(/^["']|["']$/g, '') : '';
  };
  async function loadCitation() {
    try {
      const response = await fetch('CITATION.cff');
      if (!response.ok) throw new Error('Citation metadata unavailable');
      const cff = await response.text();
      // Current CFF uses an organisational author. Do not guess personal names.
      const authorBlock = cff.match(/^authors:\s*\n([\s\S]*?)(?=^\S|$)/m)?.[1] || '';
      const creators = [...authorBlock.matchAll(/^\s*-\s*name:\s*["']?(.+?)["']?\s*$/gm)].map(m => m[1]);
      const creator = creators.join('; ') || 'See CITATION.cff for creator names';
      const version = scalar(cff, 'version');
      const date = scalar(cff, 'date-released');
      const title = scalar(cff, 'title');
      const url = scalar(cff, 'url');
      const doi = scalar(cff, 'doi');
      get('record-creator').textContent = creator;
      get('record-version').textContent = version || 'Version not specified';
      get('record-date').textContent = date ? `Catalog release date: ${date}` : 'Release date not specified';
      const citation = `${creator}. ${date ? `(${date.slice(0, 4)}). ` : ''}${title}. ${version ? `Version ${version}. ` : ''}[Data set]. ${doi ? `https://doi.org/${doi}` : url}`;
      get('record-citation').textContent = citation;
      if (doi) {
        const dd = document.querySelector('.citation-panel dl dd:last-child');
        dd.textContent = `DOI recorded in citation metadata: ${doi}`;
      }
      get('copy-citation').disabled = false;
      get('copy-citation').addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(citation); get('citation-feedback').textContent = 'Citation copied.'; }
        catch { get('citation-feedback').textContent = 'Select the citation text to copy it, or download CITATION.cff.'; }
      });
    } catch {
      get('record-version').textContent = 'Citation metadata unavailable';
      get('record-creator').textContent = 'See CITATION.cff';
      get('record-citation').textContent = 'Download CITATION.cff to view the original catalog citation.';
    }
  }
  async function loadWorkingSummary() {
    try {
      const response = await fetch('data/extraction/batch_summary.json');
      if (!response.ok) return;
      const { database: db } = await response.json();
      get('working-summary').textContent = `${db.counts.papers.toLocaleString()} papers · ${db.statuses.extracted_candidate_pending_review.toLocaleString()} candidate extractions awaiting review · ${db.counts.paper_compounds.toLocaleString()} paper-specific molecules · ${db.counts.routes.toLocaleString()} paths.`;
    } catch { /* Keep the link to the primary coverage view available. */ }
  }
  loadCitation();
  loadWorkingSummary();
})();
