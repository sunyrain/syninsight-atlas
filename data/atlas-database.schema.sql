PRAGMA foreign_keys = ON;

CREATE TABLE database_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE papers (
    paper_id TEXT PRIMARY KEY,
    doi TEXT,
    title TEXT NOT NULL,
    journal TEXT,
    publication_date TEXT,
    article_family_id TEXT,
    source_url TEXT,
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE INDEX papers_doi_idx ON papers(doi);
CREATE INDEX papers_family_idx ON papers(article_family_id);
CREATE TABLE paper_status (
    paper_id TEXT PRIMARY KEY REFERENCES papers(paper_id),
    extraction_status TEXT NOT NULL,
    detail_policy TEXT NOT NULL CHECK(detail_policy IN ('allowed', 'metadata_only')),
    review_status TEXT NOT NULL,
    reason TEXT,
    source_bound_dataset_imported INTEGER NOT NULL DEFAULT 0 CHECK(source_bound_dataset_imported IN (0,1)),
    provisional_candidates_imported INTEGER NOT NULL DEFAULT 0 CHECK(provisional_candidates_imported IN (0,1)),
    complete_route_verified INTEGER NOT NULL DEFAULT 0 CHECK(complete_route_verified = 0),
    inventory_json TEXT NOT NULL CHECK(json_valid(inventory_json))
);
CREATE INDEX paper_status_state_idx ON paper_status(extraction_status, detail_policy);
CREATE TABLE extraction_runs (
    run_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    method TEXT NOT NULL,
    software_version TEXT NOT NULL,
    dataset_path TEXT,
    dataset_sha256 TEXT,
    status TEXT NOT NULL,
    validation_json TEXT NOT NULL CHECK(json_valid(validation_json))
);
CREATE INDEX extraction_runs_paper_idx ON extraction_runs(paper_id);
CREATE TABLE source_artifacts (
    artifact_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    source_id TEXT NOT NULL,
    role TEXT,
    local_path TEXT,
    source_url TEXT,
    sha256 TEXT,
    page_count INTEGER CHECK(page_count IS NULL OR page_count > 0),
    byte_size INTEGER CHECK(byte_size IS NULL OR byte_size >= 0),
    source_bytes_verified INTEGER NOT NULL DEFAULT 0 CHECK(source_bytes_verified IN (0,1)),
    redistribute_source INTEGER NOT NULL DEFAULT 0 CHECK(redistribute_source = 0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id, source_id)
);
CREATE INDEX source_artifacts_paper_idx ON source_artifacts(paper_id);
CREATE INDEX source_artifacts_hash_idx ON source_artifacts(sha256);
CREATE TABLE evidence_locations (
    evidence_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL REFERENCES source_artifacts(artifact_id),
    page_number INTEGER CHECK(page_number IS NULL OR page_number > 0),
    locator TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    evidence_type TEXT NOT NULL DEFAULT 'source_bound_reference',
    UNIQUE(artifact_id, page_number, locator)
);
CREATE INDEX evidence_artifact_idx ON evidence_locations(artifact_id);
CREATE UNIQUE INDEX evidence_unpaginated_unique_idx ON evidence_locations(artifact_id,locator) WHERE page_number IS NULL;
CREATE TABLE molecules (
    molecule_id TEXT PRIMARY KEY,
    canonical_smiles TEXT NOT NULL UNIQUE,
    molecular_formula TEXT NOT NULL,
    exact_mass REAL NOT NULL,
    inchikey TEXT,
    rdkit_version TEXT NOT NULL,
    normalization_policy TEXT NOT NULL
);
CREATE INDEX molecules_inchikey_idx ON molecules(inchikey);
CREATE TABLE targets (
    target_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    target_name TEXT NOT NULL,
    cohort TEXT,
    review_status TEXT,
    formal_benchmark_eligible INTEGER NOT NULL DEFAULT 0 CHECK(formal_benchmark_eligible = 0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE INDEX targets_paper_idx ON targets(paper_id);
CREATE TABLE target_structure_candidates (
    target_id TEXT PRIMARY KEY REFERENCES targets(target_id),
    molecule_id TEXT NOT NULL REFERENCES molecules(molecule_id),
    original_smiles TEXT NOT NULL,
    original_atom_mapping_json TEXT NOT NULL CHECK(json_valid(original_atom_mapping_json)),
    candidate_status TEXT NOT NULL,
    source_artifact_sha256 TEXT,
    source_locator TEXT,
    admission_authority INTEGER NOT NULL DEFAULT 0 CHECK(admission_authority = 0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE INDEX target_candidates_molecule_idx ON target_structure_candidates(molecule_id);
CREATE TABLE provisional_compounds (
    provisional_compound_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    source_id TEXT NOT NULL,
    paper_label TEXT NOT NULL,
    original_molecule_id TEXT,
    molecule_id TEXT NOT NULL REFERENCES molecules(molecule_id),
    source_name TEXT NOT NULL,
    structure_basis TEXT NOT NULL,
    drawing_agreement_status TEXT NOT NULL,
    stereo_status TEXT,
    review_status TEXT NOT NULL CHECK(review_status='provisional'),
    original_smiles TEXT NOT NULL,
    original_atom_mapping_json TEXT NOT NULL CHECK(json_valid(original_atom_mapping_json)),
    formal_benchmark_eligible INTEGER NOT NULL DEFAULT 0 CHECK(formal_benchmark_eligible=0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id,source_id,paper_label),
    FOREIGN KEY(paper_id,source_id) REFERENCES source_artifacts(paper_id,source_id)
);
CREATE INDEX provisional_compounds_paper_idx ON provisional_compounds(paper_id);
CREATE INDEX provisional_compounds_molecule_idx ON provisional_compounds(molecule_id);
CREATE TABLE provisional_compound_evidence (
    provisional_compound_id TEXT NOT NULL REFERENCES provisional_compounds(provisional_compound_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_locations(evidence_id),
    PRIMARY KEY(provisional_compound_id,evidence_id)
);
CREATE INDEX provisional_compound_evidence_location_idx ON provisional_compound_evidence(evidence_id);
CREATE TABLE provisional_reaction_endpoints (
    provisional_endpoint_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    source_id TEXT NOT NULL,
    original_candidate_id TEXT,
    product_label TEXT NOT NULL,
    candidate_kind TEXT NOT NULL,
    canonical_reaction_smiles TEXT NOT NULL,
    smiles_scope TEXT NOT NULL,
    all_reaction_participants_resolved INTEGER NOT NULL DEFAULT 0 CHECK(all_reaction_participants_resolved=0),
    step_segmentation_status TEXT NOT NULL,
    atom_mapping_status TEXT NOT NULL,
    review_status TEXT NOT NULL CHECK(review_status='provisional'),
    formal_benchmark_eligible INTEGER NOT NULL DEFAULT 0 CHECK(formal_benchmark_eligible=0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id,original_candidate_id),
    FOREIGN KEY(paper_id,source_id) REFERENCES source_artifacts(paper_id,source_id)
);
CREATE INDEX provisional_endpoints_paper_idx ON provisional_reaction_endpoints(paper_id);
CREATE TABLE provisional_endpoint_components (
    provisional_endpoint_id TEXT NOT NULL REFERENCES provisional_reaction_endpoints(provisional_endpoint_id),
    role TEXT NOT NULL CHECK(role IN ('reactant','product')),
    component_index INTEGER NOT NULL CHECK(component_index > 0),
    provisional_compound_id TEXT NOT NULL REFERENCES provisional_compounds(provisional_compound_id),
    PRIMARY KEY(provisional_endpoint_id,role,component_index)
);
CREATE INDEX provisional_endpoint_components_compound_idx ON provisional_endpoint_components(provisional_compound_id);
CREATE TABLE provisional_unresolved_labels (
    provisional_endpoint_id TEXT NOT NULL REFERENCES provisional_reaction_endpoints(provisional_endpoint_id),
    paper_label TEXT NOT NULL,
    resolution_status TEXT NOT NULL DEFAULT 'unresolved_source_reference',
    PRIMARY KEY(provisional_endpoint_id,paper_label)
);
CREATE TABLE provisional_endpoint_evidence (
    provisional_endpoint_id TEXT NOT NULL REFERENCES provisional_reaction_endpoints(provisional_endpoint_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_locations(evidence_id),
    PRIMARY KEY(provisional_endpoint_id,evidence_id)
);
CREATE INDEX provisional_endpoint_evidence_location_idx ON provisional_endpoint_evidence(evidence_id);
CREATE TABLE embedded_structure_candidates (
    embedded_candidate_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    original_candidate_id TEXT NOT NULL,
    molecule_id TEXT NOT NULL REFERENCES molecules(molecule_id),
    native_molecule_index_1based INTEGER NOT NULL CHECK(native_molecule_index_1based > 0),
    paper_label TEXT CHECK(paper_label IS NULL),
    reaction_role TEXT CHECK(reaction_role IS NULL),
    reaction_id TEXT CHECK(reaction_id IS NULL),
    structure_basis TEXT NOT NULL,
    stereo_basis TEXT,
    unassigned_stereocenter_count INTEGER CHECK(unassigned_stereocenter_count IS NULL OR unassigned_stereocenter_count >= 0),
    review_status TEXT NOT NULL,
    original_smiles TEXT NOT NULL,
    original_atom_mapping_json TEXT NOT NULL CHECK(json_valid(original_atom_mapping_json)),
    formal_benchmark_eligible INTEGER NOT NULL DEFAULT 0 CHECK(formal_benchmark_eligible=0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id,original_candidate_id)
);
CREATE INDEX embedded_candidates_paper_idx ON embedded_structure_candidates(paper_id);
CREATE INDEX embedded_candidates_molecule_idx ON embedded_structure_candidates(molecule_id);
CREATE TABLE embedded_structure_evidence (
    embedded_candidate_id TEXT NOT NULL REFERENCES embedded_structure_candidates(embedded_candidate_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_locations(evidence_id),
    source_member TEXT NOT NULL,
    embedded_object_sha256 TEXT NOT NULL,
    cdx_sha256 TEXT NOT NULL,
    ole_stream TEXT NOT NULL,
    signature_offset_in_stream INTEGER NOT NULL CHECK(signature_offset_in_stream >= 0),
    document_contexts_json TEXT NOT NULL CHECK(json_valid(document_contexts_json)),
    PRIMARY KEY(embedded_candidate_id,evidence_id)
);
CREATE INDEX embedded_evidence_location_idx ON embedded_structure_evidence(evidence_id);
CREATE TABLE paper_compounds (
    paper_compound_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    local_label TEXT NOT NULL,
    paper_label TEXT,
    molecule_id TEXT NOT NULL REFERENCES molecules(molecule_id),
    compound_name TEXT,
    compound_role TEXT,
    structure_basis TEXT NOT NULL,
    stereo_status TEXT,
    review_status TEXT NOT NULL,
    original_smiles TEXT NOT NULL,
    original_atom_mapping_json TEXT NOT NULL CHECK(json_valid(original_atom_mapping_json)),
    formal_benchmark_eligible INTEGER NOT NULL DEFAULT 0 CHECK(formal_benchmark_eligible = 0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id, local_label)
);
CREATE INDEX compounds_molecule_idx ON paper_compounds(molecule_id);
CREATE INDEX compounds_paper_idx ON paper_compounds(paper_id);
CREATE TABLE compound_evidence (
    paper_compound_id TEXT NOT NULL REFERENCES paper_compounds(paper_compound_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_locations(evidence_id),
    PRIMARY KEY(paper_compound_id, evidence_id)
);
CREATE TABLE reaction_events (
    reaction_event_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    local_event_id TEXT NOT NULL,
    category TEXT,
    canonical_reaction_smiles TEXT NOT NULL,
    smiles_scope TEXT NOT NULL,
    atom_mapping_status TEXT NOT NULL,
    reported_yields_json TEXT NOT NULL CHECK(json_valid(reported_yields_json)),
    review_status TEXT NOT NULL,
    formal_benchmark_eligible INTEGER NOT NULL DEFAULT 0 CHECK(formal_benchmark_eligible = 0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id, local_event_id)
);
CREATE INDEX compound_evidence_location_idx ON compound_evidence(evidence_id);
CREATE INDEX events_paper_idx ON reaction_events(paper_id);
CREATE TABLE reaction_components (
    reaction_event_id TEXT NOT NULL REFERENCES reaction_events(reaction_event_id),
    role TEXT NOT NULL CHECK(role IN ('reactant','product')),
    component_index INTEGER NOT NULL CHECK(component_index > 0),
    paper_compound_id TEXT NOT NULL REFERENCES paper_compounds(paper_compound_id),
    PRIMARY KEY(reaction_event_id, role, component_index)
);
CREATE INDEX reaction_components_compound_idx ON reaction_components(paper_compound_id);
CREATE TABLE reaction_evidence (
    reaction_event_id TEXT NOT NULL REFERENCES reaction_events(reaction_event_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_locations(evidence_id),
    PRIMARY KEY(reaction_event_id, evidence_id)
);
CREATE TABLE participants (
    participant_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    local_participant_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    molecule_id TEXT REFERENCES molecules(molecule_id),
    original_smiles TEXT,
    original_atom_mapping_json TEXT NOT NULL CHECK(json_valid(original_atom_mapping_json)),
    structure_basis TEXT NOT NULL,
    note TEXT,
    UNIQUE(paper_id, local_participant_id)
);
CREATE INDEX reaction_evidence_location_idx ON reaction_evidence(evidence_id);
CREATE INDEX participants_paper_idx ON participants(paper_id);
CREATE INDEX participants_molecule_idx ON participants(molecule_id);
CREATE TABLE operation_steps (
    operation_step_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    reaction_event_id TEXT NOT NULL REFERENCES reaction_events(reaction_event_id),
    local_step_id TEXT NOT NULL,
    step_index INTEGER NOT NULL CHECK(step_index > 0),
    transformation TEXT,
    structure_basis TEXT NOT NULL,
    canonical_reaction_smiles TEXT NOT NULL,
    temperature_reported TEXT,
    duration_hours REAL,
    yield_percent REAL CHECK(yield_percent IS NULL OR (yield_percent >= 0 AND yield_percent <= 100)),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(reaction_event_id, step_index),
    UNIQUE(paper_id, local_step_id)
);
CREATE INDEX steps_paper_idx ON operation_steps(paper_id);
CREATE INDEX steps_event_idx ON operation_steps(reaction_event_id);
CREATE TABLE operation_components (
    operation_step_id TEXT NOT NULL REFERENCES operation_steps(operation_step_id),
    role TEXT NOT NULL CHECK(role IN ('reactant','product')),
    component_index INTEGER NOT NULL CHECK(component_index > 0),
    paper_compound_id TEXT NOT NULL REFERENCES paper_compounds(paper_compound_id),
    PRIMARY KEY(operation_step_id, role, component_index)
);
CREATE INDEX operation_components_compound_idx ON operation_components(paper_compound_id);
CREATE TABLE operation_participants (
    operation_step_id TEXT NOT NULL REFERENCES operation_steps(operation_step_id),
    role TEXT NOT NULL CHECK(role IN ('agent','solvent')),
    component_index INTEGER NOT NULL CHECK(component_index > 0),
    participant_id TEXT NOT NULL REFERENCES participants(participant_id),
    PRIMARY KEY(operation_step_id, role, component_index)
);
CREATE INDEX operation_participants_participant_idx ON operation_participants(participant_id);
CREATE TABLE operation_evidence (
    operation_step_id TEXT NOT NULL REFERENCES operation_steps(operation_step_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_locations(evidence_id),
    PRIMARY KEY(operation_step_id, evidence_id)
);
CREATE TABLE routes (
    route_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    local_route_id TEXT NOT NULL,
    start_compound_id TEXT NOT NULL REFERENCES paper_compounds(paper_compound_id),
    target_compound_id TEXT NOT NULL REFERENCES paper_compounds(paper_compound_id),
    claimed_natural_product_label TEXT,
    route_type TEXT NOT NULL,
    topology_kind TEXT NOT NULL DEFAULT 'linear',
    coverage_scope TEXT NOT NULL,
    upstream_boundary TEXT,
    downstream_boundary TEXT,
    from_commercial_starting_materials_complete INTEGER NOT NULL DEFAULT 0 CHECK(from_commercial_starting_materials_complete IN (0,1)),
    formal_benchmark_eligible INTEGER NOT NULL DEFAULT 0 CHECK(formal_benchmark_eligible = 0),
    split_group TEXT NOT NULL,
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id, local_route_id)
);
CREATE INDEX operation_evidence_location_idx ON operation_evidence(evidence_id);
CREATE INDEX routes_paper_idx ON routes(paper_id);
CREATE INDEX routes_split_idx ON routes(split_group);
CREATE INDEX routes_target_idx ON routes(target_compound_id);
CREATE TABLE route_start_compounds (
    route_id TEXT NOT NULL REFERENCES routes(route_id),
    start_index INTEGER NOT NULL CHECK(start_index > 0),
    paper_compound_id TEXT NOT NULL REFERENCES paper_compounds(paper_compound_id),
    PRIMARY KEY(route_id, start_index)
);
CREATE INDEX route_starts_compound_idx ON route_start_compounds(paper_compound_id);
CREATE TABLE route_steps (
    route_id TEXT NOT NULL REFERENCES routes(route_id),
    step_index INTEGER NOT NULL CHECK(step_index > 0),
    operation_step_id TEXT NOT NULL REFERENCES operation_steps(operation_step_id),
    reaction_event_id TEXT NOT NULL REFERENCES reaction_events(reaction_event_id),
    event_index INTEGER NOT NULL CHECK(event_index > 0),
    PRIMARY KEY(route_id, step_index)
);
CREATE INDEX route_steps_operation_idx ON route_steps(operation_step_id);
CREATE INDEX route_steps_event_idx ON route_steps(reaction_event_id);
CREATE TABLE route_molecules (
    route_id TEXT NOT NULL REFERENCES routes(route_id),
    molecule_index INTEGER NOT NULL CHECK(molecule_index > 0),
    paper_compound_id TEXT NOT NULL REFERENCES paper_compounds(paper_compound_id),
    PRIMARY KEY(route_id, molecule_index)
);
CREATE INDEX route_molecules_compound_idx ON route_molecules(paper_compound_id);
CREATE TABLE issues (
    issue_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    severity TEXT NOT NULL,
    subject TEXT,
    detail TEXT NOT NULL,
    provenance TEXT NOT NULL
);
CREATE INDEX issues_paper_idx ON issues(paper_id, severity);

CREATE TABLE native_reaction_fragments (
    native_fragment_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    cdx_sha256 TEXT NOT NULL,
    fragment_object_id INTEGER NOT NULL,
    fragment_sha256 TEXT NOT NULL,
    molecule_id TEXT REFERENCES molecules(molecule_id),
    paper_label TEXT,
    status TEXT NOT NULL,
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id,cdx_sha256,fragment_object_id)
);
CREATE TABLE native_reaction_steps (
    native_step_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    cdx_sha256 TEXT NOT NULL,
    step_object_id INTEGER NOT NULL,
    endpoint_status TEXT NOT NULL,
    canonical_reaction_smiles TEXT,
    full_article_route_coverage INTEGER NOT NULL DEFAULT 0 CHECK(full_article_route_coverage=0),
    formal_benchmark_eligible INTEGER NOT NULL DEFAULT 0 CHECK(formal_benchmark_eligible=0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    UNIQUE(paper_id,cdx_sha256,step_object_id)
);
CREATE TABLE native_reaction_components (
    native_step_id TEXT NOT NULL REFERENCES native_reaction_steps(native_step_id),
    role TEXT NOT NULL CHECK(role IN ('reactant','product')),
    component_index INTEGER NOT NULL CHECK(component_index>0),
    native_fragment_id TEXT NOT NULL REFERENCES native_reaction_fragments(native_fragment_id),
    PRIMARY KEY(native_step_id,role,component_index)
);
CREATE TABLE native_reaction_evidence (
    native_step_id TEXT NOT NULL REFERENCES native_reaction_steps(native_step_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_locations(evidence_id),
    PRIMARY KEY(native_step_id,evidence_id)
);
CREATE TABLE native_fragment_evidence (
    native_fragment_id TEXT NOT NULL REFERENCES native_reaction_fragments(native_fragment_id),
    evidence_id TEXT NOT NULL REFERENCES evidence_locations(evidence_id),
    PRIMARY KEY(native_fragment_id,evidence_id)
);
CREATE TABLE native_scheme_routes (
    native_route_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    coverage_scope TEXT NOT NULL,
    full_article_route_coverage INTEGER NOT NULL DEFAULT 0 CHECK(full_article_route_coverage=0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE TABLE native_scheme_route_steps (
    native_route_id TEXT NOT NULL REFERENCES native_scheme_routes(native_route_id),
    step_index INTEGER NOT NULL CHECK(step_index>0),
    native_step_id TEXT NOT NULL REFERENCES native_reaction_steps(native_step_id),
    PRIMARY KEY(native_route_id,step_index)
);
CREATE INDEX native_steps_paper_idx ON native_reaction_steps(paper_id);
CREATE INDEX native_fragments_paper_idx ON native_reaction_fragments(paper_id);
CREATE TRIGGER metadata_only_native_fragment_guard BEFORE INSERT ON native_reaction_fragments
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain native reaction fragments'); END;
CREATE TRIGGER metadata_only_native_step_guard BEFORE INSERT ON native_reaction_steps
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain native reaction steps'); END;
CREATE TRIGGER metadata_only_native_route_guard BEFORE INSERT ON native_scheme_routes
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain native scheme routes'); END;

CREATE TRIGGER metadata_only_compound_guard BEFORE INSERT ON paper_compounds
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain detailed compounds'); END;
CREATE TRIGGER metadata_only_event_guard BEFORE INSERT ON reaction_events
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain reaction events'); END;
CREATE TRIGGER metadata_only_participant_guard BEFORE INSERT ON participants
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain participants'); END;
CREATE TRIGGER metadata_only_candidate_guard BEFORE INSERT ON target_structure_candidates
WHEN (SELECT detail_policy FROM paper_status JOIN targets USING(paper_id) WHERE target_id=NEW.target_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain target structures'); END;
CREATE TRIGGER metadata_only_provisional_compound_guard BEFORE INSERT ON provisional_compounds
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain provisional compounds'); END;
CREATE TRIGGER metadata_only_provisional_endpoint_guard BEFORE INSERT ON provisional_reaction_endpoints
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain provisional endpoints'); END;
CREATE TRIGGER metadata_only_embedded_candidate_guard BEFORE INSERT ON embedded_structure_candidates
WHEN (SELECT detail_policy FROM paper_status WHERE paper_id=NEW.paper_id)='metadata_only'
BEGIN SELECT RAISE(ABORT, 'metadata_only paper cannot contain native structure candidates'); END;

CREATE VIEW v_paper_coverage AS
SELECT p.paper_id,p.doi,p.title,s.extraction_status,s.detail_policy,s.review_status,
       s.source_bound_dataset_imported,s.provisional_candidates_imported,s.complete_route_verified,s.reason,
       (SELECT count(*) FROM targets t WHERE t.paper_id=p.paper_id) AS target_count,
       (SELECT count(*) FROM target_structure_candidates c JOIN targets t USING(target_id) WHERE t.paper_id=p.paper_id) AS target_candidate_count,
       (SELECT count(*) FROM provisional_compounds c WHERE c.paper_id=p.paper_id) AS provisional_compound_count,
       (SELECT count(*) FROM provisional_reaction_endpoints e WHERE e.paper_id=p.paper_id) AS provisional_endpoint_count,
       (SELECT count(*) FROM embedded_structure_candidates e WHERE e.paper_id=p.paper_id) AS embedded_candidate_count,
       (SELECT count(*) FROM native_reaction_steps n WHERE n.paper_id=p.paper_id) AS native_step_count,
       (SELECT count(*) FROM native_reaction_steps n WHERE n.paper_id=p.paper_id AND n.canonical_reaction_smiles IS NOT NULL) AS native_resolved_step_count,
       (SELECT count(*) FROM native_scheme_routes n WHERE n.paper_id=p.paper_id) AS native_scoped_route_count,
       (SELECT count(*) FROM source_artifacts a WHERE a.paper_id=p.paper_id) AS source_artifact_count,
       (SELECT count(*) FROM paper_compounds c WHERE c.paper_id=p.paper_id) AS compound_count,
       (SELECT count(*) FROM reaction_events e WHERE e.paper_id=p.paper_id) AS reaction_event_count,
       (SELECT count(*) FROM operation_steps o WHERE o.paper_id=p.paper_id) AS operation_step_count,
       (SELECT count(*) FROM routes r WHERE r.paper_id=p.paper_id) AS route_count,
       (SELECT count(*) FROM issues i WHERE i.paper_id=p.paper_id) AS issue_count
FROM papers p JOIN paper_status s USING(paper_id);
CREATE VIEW v_native_reaction_endpoints AS
SELECT s.paper_id,s.native_step_id,s.endpoint_status,s.canonical_reaction_smiles,
       s.cdx_sha256,s.step_object_id,s.full_article_route_coverage,s.formal_benchmark_eligible,
       (SELECT count(*) FROM native_reaction_components c WHERE c.native_step_id=s.native_step_id AND role='reactant') AS reactant_count,
       (SELECT count(*) FROM native_reaction_components c WHERE c.native_step_id=s.native_step_id AND role='product') AS product_count
FROM native_reaction_steps s;
CREATE VIEW v_native_reaction_components AS
SELECT s.paper_id,s.native_step_id,c.role,c.component_index,f.native_fragment_id,f.paper_label,
       f.status,m.canonical_smiles,m.molecular_formula,f.cdx_sha256,f.fragment_object_id
FROM native_reaction_components c JOIN native_reaction_steps s USING(native_step_id)
JOIN native_reaction_fragments f USING(native_fragment_id) LEFT JOIN molecules m USING(molecule_id);
CREATE VIEW v_native_reaction_provenance AS
SELECT s.paper_id,s.native_step_id,a.local_path,a.sha256,e.locator,e.page_number
FROM native_reaction_steps s JOIN native_reaction_evidence n USING(native_step_id)
JOIN evidence_locations e USING(evidence_id) JOIN source_artifacts a USING(artifact_id);
CREATE VIEW v_native_scheme_sequence AS
SELECT r.paper_id,r.native_route_id,r.coverage_scope,o.step_index,s.native_step_id,s.canonical_reaction_smiles,
       r.full_article_route_coverage
FROM native_scheme_routes r JOIN native_scheme_route_steps o USING(native_route_id)
JOIN native_reaction_steps s USING(native_step_id);
CREATE VIEW v_route_smiles_sequence AS
SELECT r.paper_id,r.route_id,r.route_type,r.coverage_scope,rm.molecule_index,
       c.local_label,c.paper_label,c.structure_basis,c.stereo_status,c.molecule_id,m.canonical_smiles
FROM routes r JOIN route_molecules rm USING(route_id)
JOIN paper_compounds c USING(paper_compound_id) JOIN molecules m USING(molecule_id);
CREATE VIEW v_route_step_sequence AS
SELECT r.paper_id,r.route_id,rs.step_index,rs.event_index,o.local_step_id,e.local_event_id,
       o.canonical_reaction_smiles,o.structure_basis,o.transformation,o.temperature_reported,
       o.duration_hours,o.yield_percent,r.split_group,r.formal_benchmark_eligible
FROM routes r JOIN route_steps rs USING(route_id)
JOIN operation_steps o USING(operation_step_id)
JOIN reaction_events e ON e.reaction_event_id=rs.reaction_event_id;
CREATE VIEW v_source_drawn_reactions AS
SELECT e.* FROM reaction_events e
WHERE NOT EXISTS (
    SELECT 1 FROM reaction_components rc JOIN paper_compounds c USING(paper_compound_id)
    WHERE rc.reaction_event_id=e.reaction_event_id AND c.structure_basis!='source_drawing_transcription'
);
CREATE VIEW v_target_candidate_structures AS
SELECT t.paper_id,t.target_id,t.target_name,c.candidate_status,m.canonical_smiles,
       c.source_artifact_sha256,c.source_locator,c.admission_authority
FROM targets t JOIN target_structure_candidates c USING(target_id) JOIN molecules m USING(molecule_id);
CREATE VIEW v_compound_provenance AS
SELECT c.paper_id,c.local_label,c.paper_label,c.structure_basis,c.review_status,m.canonical_smiles,
       a.source_id,a.local_path,e.page_number,e.locator,e.sha256,a.source_bytes_verified
FROM paper_compounds c JOIN molecules m USING(molecule_id)
JOIN compound_evidence ce USING(paper_compound_id)
JOIN evidence_locations e USING(evidence_id) JOIN source_artifacts a USING(artifact_id);
CREATE VIEW v_provisional_compound_provenance AS
SELECT c.paper_id,c.paper_label,c.source_name,c.structure_basis,c.drawing_agreement_status,
       c.review_status,m.canonical_smiles,a.source_id,a.local_path,e.page_number,e.locator,e.sha256
FROM provisional_compounds c JOIN molecules m USING(molecule_id)
JOIN provisional_compound_evidence ce USING(provisional_compound_id)
JOIN evidence_locations e USING(evidence_id) JOIN source_artifacts a USING(artifact_id);
CREATE VIEW v_provisional_endpoint_summary AS
SELECT e.provisional_endpoint_id,e.paper_id,e.source_id,e.product_label,e.canonical_reaction_smiles,
       e.smiles_scope,e.review_status,e.all_reaction_participants_resolved,e.step_segmentation_status,
       (SELECT count(*) FROM provisional_unresolved_labels u WHERE u.provisional_endpoint_id=e.provisional_endpoint_id) AS unresolved_label_count
FROM provisional_reaction_endpoints e;
CREATE VIEW v_embedded_structure_provenance AS
SELECT c.paper_id,c.embedded_candidate_id,c.molecule_id,m.canonical_smiles,c.paper_label,
       c.reaction_role,c.reaction_id,c.structure_basis,c.stereo_basis,c.review_status,
       c.native_molecule_index_1based,a.source_id,a.local_path,a.sha256 AS source_sha256,
       e.page_number,e.locator,x.source_member,x.embedded_object_sha256,x.cdx_sha256,
       x.ole_stream,x.signature_offset_in_stream,x.document_contexts_json
FROM embedded_structure_candidates c JOIN molecules m USING(molecule_id)
JOIN embedded_structure_evidence x USING(embedded_candidate_id)
JOIN evidence_locations e USING(evidence_id) JOIN source_artifacts a USING(artifact_id);
