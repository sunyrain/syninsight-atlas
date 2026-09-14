# Interactive route-tree renderer

The desktop route workspace adapts the HTML/CSS route-tree presentation and interaction approach from [AutoPlanner Case 02](https://sunyrain.github.io/AutoPlanner/case-2.html), inspected on 2026-09-14. The source page embeds its renderer; it does not rely on a separately loaded graph library.

`assets/autoplanner-tree.css` carries the adapted route-tree styles. `assets/autoplanner-tree.js` adapts the recursive molecule/precursor tree and compact reaction connectors. `assets/route-network.js` maps the existing source compound IDs and ordered operations to that renderer. Molecule images come from each case's existing structure depictions.

The interactive tree reads from the target toward its recorded precursors (retrosynthetic display direction). It does not change the recorded forward reaction, step numbering, yields or stereochemistry. Repeated shared intermediates are labeled; operations without a recorded connection to the target appear as additional modules. Each operation is rendered once. Other products of a multi-product operation remain listed in the inspector.

The reference page's replay history, model activity, strategy judgments and example molecule dataset are not imported. The right rail instead shows actual recorded operations and source locators. Printable forward-reaction SVG schemes remain available as a separate download.

Controls include compact/full reaction detail, horizontal/vertical layout, readable view, fit-all, mouse pan/zoom, step selection and an expandable workspace. Run `node tests/test_route_tree.cjs` to check that every operation in all 635 exported paths is represented exactly once in both detail modes, including shared branches and additional modules.
