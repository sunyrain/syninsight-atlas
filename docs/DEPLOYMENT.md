# Website maintenance

The generated static website is served from the repository root. No separate frontend
build service is needed. Serve locally with `python -m http.server 8765`.

## Update

1. Edit source HTML, assets or Markdown in the local repository.
2. Install `requirements-web.txt` and `requirements-test.txt`, then run
   `python scripts/build_web.py` to regenerate document pages and the resource manifest.
3. Run `python -m pytest tests/test_release.py tests/test_web.py` and
   `node tests/test_route_tree.cjs`.
4. Review changes in GitHub Desktop, commit and push to the intended fork/branch.

The build preserves the scientific source records. The original
`export_from_autoplanner.py` requires the upstream curation workspace and is not
needed for website updates. `CHECKSUMS.sha256` covers the original discovery snapshot;
website checks additionally validate generated links and route coverage.

## Hosting

The repository includes `.nojekyll` and uses relative URLs. Keep an existing working
GitHub Pages publishing configuration. The published URL belongs to the repository
that deploys it; a fork does not automatically publish at the upstream website URL.
Generated pages in `pages/` should be rebuilt from Markdown, not edited by hand.

## Renderer

See [Route tree renderer](ROUTE_TREE_RENDERER.md) for the interactive desktop tree
and [Reaction figures](REACTION_FIGURES.md) for downloadable SVGs.
