# Local reaction-image recognition calibration

The local CPU environment runs the authors' [RxnScribe](https://github.com/thomas0809/RxnScribe)
and [MolScribe](https://github.com/thomas0809/MolScribe) implementations. This is a
diagnostic tool, not an unattended route-completion pipeline.

The source-bound trial uses Glabridin, `paper-0bac8bc7088bc164`, article page 3,
Scheme 3, rendered with Poppler at 150 and 300 dpi. The article SHA256 is
`3c267ab99b5e43d52366b3df41d8c12d323121763bc94b18bd496dc9a790dd87`.
The input is regenerated from this exact PDF on every run.

Both resolutions located the three reaction connections. Only two of the four
numbered structures matched the existing curated molecular graphs: a1 and a.
THP-protected a2 and a3 were misread or remained unresolved. In particular,
some erroneous outputs contained thallium/phosphorus fragments while still
passing RDKit syntax and canonical roundtrip checks. Every reaction in this
small trial had at least one incorrect or unresolved route endpoint.

These observations do not estimate performance on all 133 papers. They show that
canonical validity and detected arrows cannot justify automatic admission of
full routes. No trial prediction was imported into the curated database tables.
Source-aware abbreviation transcription and stereochemical review remain necessary.
The [machine-readable trial record](../data/extraction/ocsr_calibration.json)
contains source/model hashes, checkpoint-load checks and both resolution runs.

## Reproduction

The current workspace already has an isolated Python 3.11 environment under
`.local/ocsr-venv`, private upstream checkouts, and hash-verified model files.
From the repository root:

```powershell
.local/ocsr-venv/Scripts/python.exe scripts/evaluate_local_ocsr.py 150
.local/ocsr-venv/Scripts/python.exe scripts/evaluate_local_ocsr.py 300
```

For another workspace, install `requirements-ocsr.txt` in an isolated Python 3.11
environment, provide Poppler's `pdftoppm`, and place upstream checkouts at:

| Checkout | Exact commit |
|---|---|
| `.local/tools/RxnScribe` | `ad6b1c75d40e563e68deca0491918885948d69c7` |
| `.local/tools/MolScribe` | `7296a30413eb55436702011efdff78131f66d162` |

Place these author-published model files in `.local/models`:

| Hugging Face repository / revision | File | SHA256 |
|---|---|---|
| `yujieq/RxnScribe` / `034bcfeaa6780624b2897f7955853271de1d1f65` | `pix2seq_reaction_full.ckpt` | `b0020634f13fb3e1f588bddca97f68fd6483f0cdecd83e2ca31c2434ea4340fe` |
| `yujieq/MolScribe` / `a0189776b7415b82795c7ee81eed311bf5c8724b` | `swin_base_char_aux_1m.pth` | `6f0df56fa32b5ffc21f8c7f311ef333da522f590bf5622e966c6bcb1f2d9ea1d` |

The evaluator verifies the source, model hashes, checkout commits and clean tracked
code before inference. All checkpoint keys must load strictly, with no missing or
unexpected parameters. Initial ImageNet downloads are disabled because the verified
reaction checkpoint supplies the full backbone. Condition-text OCR is disabled;
the trial evaluates molecular structures and connections only.

Raw predictions, model-generated molfiles, source renders and logs remain private
under `.local/ocsr-pilot`. The public calibration record contains provenance,
comparison results and limitations, without redistributing source images.
