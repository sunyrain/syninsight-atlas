const PAGE_SIZE = 24;

const state = {
  targets: [],
  summary: null,
  page: 1,
  query: "",
  cohort: "all",
  structure: "all",
  route: "all",
  source: "all",
};

const $ = (selector) => document.querySelector(selector);

function labelForStructure(status) {
  return {
    exact_source_structure_candidate: "exact-source candidate",
    partial_stereo_candidate: "stereo unresolved",
    unresolved: "unresolved",
  }[status] || status || "unresolved";
}

function badgeClass(status) {
  if (status === "exact_source_structure_candidate") return "exact";
  if (status === "partial_stereo_candidate") return "partial";
  return "unresolved";
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function addBadge(container, text, className = "") {
  container.append(element("span", `badge ${className}`.trim(), text));
}

function filteredTargets() {
  const query = state.query.trim().toLocaleLowerCase();
  return state.targets.filter((target) => {
    const haystack = [target.target_name, target.paper_title, target.doi, target.journal]
      .join(" ")
      .toLocaleLowerCase();
    const matchesQuery = !query || haystack.includes(query);
    const matchesCohort = state.cohort === "all" || target.cohort === state.cohort;
    const matchesStructure = state.structure === "all" || target.candidate_structure.status === state.structure;
    const hasRoute = target.route_evidence_lead.passage_count > 0;
    const matchesRoute = state.route === "all" || (state.route === "yes" ? hasRoute : !hasRoute);
    const matchesSource = state.source === "all" || target.source_package.completeness === state.source;
    return matchesQuery && matchesCohort && matchesStructure && matchesRoute && matchesSource;
  });
}

function makeCard(target) {
  const card = element("article", "card");
  const structure = element("div", "structure");
  if (target.candidate_structure.svg) {
    const image = document.createElement("img");
    image.src = target.candidate_structure.svg;
    image.alt = `Candidate structure for ${target.target_name}`;
    image.loading = "lazy";
    structure.append(image);
  } else {
    structure.append(element("span", "unresolved", "Structure unresolved"));
  }
  card.append(structure);

  const body = element("div", "card-body");
  const badges = element("div", "badges");
  addBadge(badges, target.cohort, target.cohort);
  addBadge(badges, labelForStructure(target.candidate_structure.status), badgeClass(target.candidate_structure.status));
  if (target.route_evidence_lead.passage_count > 0) addBadge(badges, "route lead", "exact");
  body.append(badges, element("h3", "", target.target_name), element("p", "paper-title", target.paper_title));

  const meta = element("div", "card-meta");
  meta.append(
    element("span", "", target.journal || "Journal pending"),
    element("span", "", target.publication_date || "Date pending"),
  );
  const button = element("button", "detail-button", "View evidence state");
  button.type = "button";
  button.addEventListener("click", () => showDetail(target));
  body.append(meta, button);
  card.append(body);
  return card;
}

function addDetailRow(container, heading, value) {
  const block = element("div", "detail-block");
  block.append(element("h3", "", heading), element("p", "", value || "Not available"));
  container.append(block);
}

function showDetail(target) {
  const content = $("#dialog-content");
  content.replaceChildren();
  const badges = element("div", "badges");
  addBadge(badges, target.cohort, target.cohort);
  addBadge(badges, labelForStructure(target.candidate_structure.status), badgeClass(target.candidate_structure.status));
  content.append(badges, element("h2", "", target.target_name));
  const grid = element("div", "detail-grid");
  const visual = element("div", "");
  if (target.candidate_structure.svg) {
    const image = document.createElement("img");
    image.src = target.candidate_structure.svg;
    image.alt = `Candidate structure for ${target.target_name}`;
    visual.append(image);
  } else {
    visual.append(element("div", "structure", "Structure unresolved"));
  }
  const facts = element("div", "");
  addDetailRow(facts, "Paper", target.paper_title);
  const citation = element("p", "");
  citation.textContent = `${target.journal || ""} · ${target.publication_date || ""} · `;
  const doi = document.createElement("a");
  doi.href = target.source_url;
  doi.target = "_blank";
  doi.rel = "noopener noreferrer";
  doi.textContent = target.doi;
  citation.append(doi);
  facts.append(citation);
  addDetailRow(facts, "Structure source locator", target.candidate_structure.source_locator);
  addDetailRow(facts, "Source package", target.source_package.completeness);
  addDetailRow(facts, "Human admission", target.formal_benchmark_eligible ? "Admitted and runnable" : "Not admitted; candidate-only");
  grid.append(visual, facts);
  content.append(grid);

  if (target.candidate_structure.isomeric_smiles) {
    const heading = element("h3", "", "Candidate isomeric SMILES");
    const smiles = element("code", "", target.candidate_structure.isomeric_smiles);
    const copy = element("button", "copy", "Copy");
    copy.type = "button";
    copy.addEventListener("click", async () => {
      await navigator.clipboard.writeText(target.candidate_structure.isomeric_smiles);
      copy.textContent = "Copied";
    });
    content.append(heading, smiles, document.createTextNode(" "), copy);
  }
  addDetailRow(content, "Transcription note", target.candidate_structure.transcription_note);
  const routeHeading = element("h3", "", `Route-evidence lead (${target.route_evidence_lead.passage_count} passages)`);
  content.append(routeHeading);
  if (target.route_evidence_lead.source_locators.length) {
    const list = element("ul", "detail-list");
    target.route_evidence_lead.source_locators.slice(0, 12).forEach((locator) => list.append(element("li", "", locator)));
    content.append(list);
  } else {
    content.append(element("p", "", "No target-linked route passage has been located."));
  }
  $("#detail-dialog").showModal();
}

function render() {
  const filtered = filteredTargets();
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  state.page = Math.min(state.page, totalPages);
  const start = (state.page - 1) * PAGE_SIZE;
  const visible = filtered.slice(start, start + PAGE_SIZE);
  const cards = $("#cards");
  cards.replaceChildren(...visible.map(makeCard));
  $("#result-count").textContent = filtered.length.toLocaleString();
  $("#empty").hidden = filtered.length !== 0;
  $("#page-label").textContent = `Page ${state.page} of ${totalPages}`;
  $("#previous").disabled = state.page <= 1;
  $("#next").disabled = state.page >= totalPages;
}

function bindFilters() {
  ["query", "cohort", "structure", "route", "source"].forEach((id) => {
    $("#" + id).addEventListener(id === "query" ? "input" : "change", (event) => {
      state[id] = event.target.value;
      state.page = 1;
      render();
    });
  });
  $("#reset").addEventListener("click", () => {
    $("#filters").reset();
    Object.assign(state, { page: 1, query: "", cohort: "all", structure: "all", route: "all", source: "all" });
    render();
  });
  $("#previous").addEventListener("click", () => { state.page -= 1; render(); window.scrollTo({ top: $("#explore").offsetTop, behavior: "smooth" }); });
  $("#next").addEventListener("click", () => { state.page += 1; render(); window.scrollTo({ top: $("#explore").offsetTop, behavior: "smooth" }); });
  $("#dialog-close").addEventListener("click", () => $("#detail-dialog").close());
  $("#detail-dialog").addEventListener("click", (event) => {
    if (event.target === $("#detail-dialog")) $("#detail-dialog").close();
  });
}

async function start() {
  try {
    const [summaryResponse, targetsResponse] = await Promise.all([
      fetch("data/summary.json"),
      fetch("data/targets.json"),
    ]);
    if (!summaryResponse.ok || !targetsResponse.ok) throw new Error("Dataset files could not be loaded");
    state.summary = await summaryResponse.json();
    state.targets = await targetsResponse.json();
    $("#release-stage").textContent = "Candidate curation release";
    $("#admitted-count").textContent = state.summary.runnable_targets.toLocaleString();
    $("#metric-papers").textContent = state.summary.candidate_papers.toLocaleString();
    $("#metric-targets").textContent = state.summary.candidate_targets.toLocaleString();
    $("#metric-structures").textContent = state.summary.rdkit_valid_structure_candidates.toLocaleString();
    $("#metric-routes").textContent = state.summary.targets_with_route_evidence_leads.toLocaleString();
    $("#metric-sources").textContent = state.summary.source_packages_acquired.toLocaleString();
    bindFilters();
    render();
  } catch (error) {
    $("#cards").replaceChildren(element("p", "notice", `${error.message}. For local viewing, serve the repository with python -m http.server.`));
  }
}

start();
