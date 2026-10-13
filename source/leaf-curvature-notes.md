# Fallen leaf curvature refinement

The six fallen-leaf meshes now use normals sampled from their authored continuous height fields, instead of averaging a sparse triangle fan. Shared edges with midpoint curl error greater than 0.002 normalized units receive one additional split. This is a refinement selection threshold, not a guaranteed bound on every point of the final surface.

Runtime batch triangle counts: 66, 124, 71, 146, 109, 176 (previously 60, 108, 60, 108, 60, 108). At the full 3900-leaf pool this adds 122,200 triangles before shadow/reflection passes. The six instanced batches, 11.5–20.5 cm leaf sizes, textures, spawning and broad broom interaction are preserved. Canopy geometry is unchanged.

`export_leaf_specimens.mjs` exports positions, UVs, normals and indices into `leaf-specimens.json`. `build_leaf_specimens.py` creates the local editable `落叶标本.blend`, preserves the six exact runtime surfaces and installs custom split normals. Save/reopen checks passed for all vertex positions, triangle counts and normals (dot product > 0.99999). A local pre-change backup is retained. This standalone leaf source is the native counterpart of runtime-created leaves; the main temple model did not need modification.

Validation:

- 12 leaf surface, topology, support-contact and motion tests passed. The selective mesh remains one connected disk, with opposing shared-edge winding, one boundary loop, no degenerate faces, orphaned vertices or T-junctions.
- Matched close-view comparisons in `leaf-curvature-fixture.html` show more continuous highlights, particularly across the ginkgo curl. Baseline geometry is retained in `leaf-curvature-baseline.js` for reproduction.
- Complete scene: entered the courtyard, looked down at the bridge, clicked the physical broom, cleared the foreground with a broad drag, and returned it. No browser errors or warnings were captured. An initial page-control timeout cleared after closing the separate comparison render tab.
- Evidence is local under `evidence/leaf-curvature-*`; native report is `evidence/leaf-specimens-native.json`.

The project remains stylized and below the overall commercial AAA target. Leaves are still thin procedural surfaces and do not form physically stacked piles. No new full-scene frame-rate claim is made.
