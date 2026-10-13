# Pond-side pruned pine refinement

The twig-heavy forms in the foreground are the six existing pruned pines, not the woodland understory. Their short, dark needles exposed too much branch structure at normal courtyard viewing distances.

- Retained all 36 crown attachment positions and the existing trunk silhouettes.
- Changed paired needle length from 10–17 cm to 14–22 cm before tip taper; slightly broadened the triangular needle cross-section and lifted green pigment values.
- Reduced the fan twig base radius from 18 mm to 12 mm, with a 3 mm terminal radius.
- Kept 84,672 near needles, 28,224 distant needles and 12 batches per asset. Both LODs receive the same source change.
- Rebuilt `庭院立体松针.blend` and synchronized the pine-crown objects in `听秋寺院.blend`; other tagged temple objects were checked for preservation by the builder. Native files remain local.

Validation: all three `pine-crowns.test.mjs` checks passed, including LOD extent and attachment tests. The fixed-camera fixture used the previous GLB saved locally under ignored `evidence/`; it showed exactly 4 color draw calls and 144,734 triangles for either variant. That fixture uses a simple trunk material and ground, so the final visual check was also performed in the full courtyard. No browser warning/error was recorded in either view. Evidence: `pine-refinement-before.png`, `pine-refinement-after.png`, `pine-refinement-main.png`.

This is a foliage proportion and material improvement, not a measured frame-rate improvement or a claim of AAA completion. GLB payload increased by approximately 115 KB across the two LOD assets while mesh counts stayed unchanged.
