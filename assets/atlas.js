/* Reads the existing public exports; no duplicated statistics or private sources. */
(() => {
  const labels = {
    extracted_candidate_pending_review: 'Extracted · pending review',
    pending_structure_transcription: 'Pending transcription',
    source_missing_local: 'Local source missing',
    metadata_only: 'Metadata only',
  };
  const select = id => document.getElementById(id);
  const make = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const link = (text, href) => {
    const node = make('a', text); node.href = href; return node;
  };
  function parseCSV(text) {
    const rows = []; let row = [], field = '', quoted = false;
    text = text.replace(/^\uFEFF/, '');
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      if (char === '"') {
        if (quoted && text[i + 1] === '"') { field += '"'; i++; }
        else quoted = !quoted;
      } else if (char === ',' && !quoted) { row.push(field); field = ''; }
      else if ((char === '\n' || char === '\r') && !quoted) {
        if (char === '\r' && text[i + 1] === '\n') i++;
        row.push(field); if (row.some(Boolean)) rows.push(row); row = []; field = '';
      } else field += char;
    }
    if (quoted) throw new Error('Invalid paper export');
    row.push(field); if (row.some(Boolean)) rows.push(row);
    const headings = rows.shift() || [];
    return rows.map(values => Object.fromEntries(headings.map((key, i) => [key, values[i] || ''])));
  }
  let papers = [], page = 1;
  const size = 12;
  function render() {
    const query = select('paper-query').value.trim().toLowerCase();
    const status = select('paper-status').value;
    const filtered = papers.filter(p => (!query || `${p.title} ${p.doi} ${p.paper_id}`.toLowerCase().includes(query)) && (status === 'all' || p.extraction_status === status));
    const pages = Math.max(1, Math.ceil(filtered.length / size));
    page = Math.min(page, pages);
    select('paper-count').textContent = `${filtered.length} of ${papers.length} papers`;
    select('paper-page').textContent = `Page ${page} of ${pages}`;
    select('paper-previous').disabled = page <= 1;
    select('paper-next').disabled = page >= pages;
    select('paper-empty').hidden = filtered.length !== 0;
    const rows = filtered.slice((page - 1) * size, page * size).map(p => {
      const tr = make('tr'), title = make('td');
      title.append(make('div', p.title, 'paper-name'), link(p.doi || p.paper_id, `https://doi.org/${encodeURI(p.doi)}`));
      const statusCell = make('td'); statusCell.append(make('span', labels[p.extraction_status] || p.extraction_status, `paper-state ${p.extraction_status}`));
      tr.append(title, statusCell);
      ['compound_count', 'reaction_event_count', 'route_count'].forEach(k => tr.append(make('td', Number(p[k]).toLocaleString(), 'numeric')));
      const actions = make('td');
      if (p.source_bound_dataset_imported === '1' && /^paper-[a-f0-9]+$/.test(p.paper_id)) {
        actions.append(link('View network', `data/routes/${p.paper_id}/report.html`), link('JSON', `data/routes/${p.paper_id}/dataset.json`));
      } else actions.append(make('span', p.extraction_status === 'metadata_only' ? 'Metadata only' : 'Not extracted', 'unavailable'));
      tr.append(actions); return tr;
    });
    select('paper-rows').replaceChildren(...rows);
  }
  async function load() {
    try {
      const [summaryResponse, papersResponse] = await Promise.all([fetch('data/extraction/batch_summary.json'), fetch('data/database/papers.csv')]);
      if (!summaryResponse.ok || !papersResponse.ok) throw new Error('Paper coverage could not be loaded');
      const summary = await summaryResponse.json();
      papers = parseCSV(await papersResponse.text());
      const db = summary.database, counts = db.counts;
      if (papers.length !== counts.papers) throw new Error('Paper exports are out of sync');
      papers.sort((a, b) => Number(b.source_bound_dataset_imported) - Number(a.source_bound_dataset_imported) || a.title.localeCompare(b.title));
      const metrics = [
        [counts.papers, 'Catalog papers'],
        [db.statuses.extracted_candidate_pending_review || 0, 'Extracted · pending review'],
        [counts.paper_compounds, 'Paper-specific molecules'],
        [counts.reaction_events, 'Preparation events'],
        [counts.routes, 'Paths & branches'],
        [db.complete_route_verified, 'Independently verified routes'],
      ];
      select('atlas-metrics').replaceChildren(...metrics.map(([value, label]) => {
        const article = make('article'); article.append(make('strong', Number(value).toLocaleString()), make('span', label)); return article;
      }));
      const bar = make('div', undefined, 'coverage-bar'), legend = make('div', undefined, 'coverage-legend');
      Object.entries(db.statuses).forEach(([status, count]) => {
        const part = make('div', undefined, status); part.style.flexGrow = count; part.title = `${labels[status] || status}: ${count}`; bar.append(part);
        legend.append(make('span', `${labels[status] || status} · ${count}`, status));
      });
      select('atlas-coverage').replaceChildren(bar, legend);
      select('paper-query').addEventListener('input', () => { page = 1; render(); });
      select('paper-status').addEventListener('change', () => { page = 1; render(); });
      select('paper-filters').addEventListener('submit', event => event.preventDefault());
      select('paper-filters').addEventListener('reset', event => { event.preventDefault(); select('paper-query').value = ''; select('paper-status').value = 'all'; page = 1; render(); });
      ['previous', 'next'].forEach(direction => select(`paper-${direction}`).addEventListener('click', () => { page += direction === 'next' ? 1 : -1; render(); select('paper-filters').scrollIntoView({block:'start',behavior:'instant'}); }));
      render();
    } catch (error) {
      select('paper-count').textContent = 'Coverage unavailable';
      const notice = select('paper-error'); notice.hidden = false;
      notice.replaceChildren(make('span', `${error.message}. `), link('Open database report', 'data/database/report.html'));
    }
  }
  load();
})();
