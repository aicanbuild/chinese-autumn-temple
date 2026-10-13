# Near woodland skeleton refinement

The original woodland used disconnected straight trunk segments and almost straight side branches, with bark UVs restarting on each segment. `refine_woodland_branches.py` replaces the three near prototypes with continuous curved stems, flared root collars, curved tapering branches and small terminal forks. It replays the original deterministic center paths so the existing crowns remain attached to the same branch tips. Branch bark follows path length with circumferential scale adjusted to stem diameter.

105 trees inside the near ring use the new skeletons; 515 distant trees retain the existing light geometry. Original placement data is unchanged. The branch model grows from 638 to 6,252 triangles per near tree, an additional 589,470 triangles if every near tree is submitted. Spatial and per-tree culling remain in place. This is an explicit geometry cost, not a frame-rate improvement.

The native installer updates `山林地形.blend` and `听秋寺院.blend`, preserving unrelated mesh geometry and UVs. Backups remain local. Inspection discovered stale lower-resolution leaf textures packed in the native sources; these were synchronized to the current browser textures. The exported GLB preserves the exact original eight texture payloads. All six decoded crown meshes retain identical positions, normals, UVs, colors and indices. Far branches remain unchanged. The GLB increases by 61,824 bytes, with all original texture payloads intact. The ground-check pass raycasts the actual sculpted terrain under every near tree's root bottom ring; buried lower stems prevent open undersides on sloping ground. The least-buried tested bottom vertex is 0.236 m below the actual terrain.

Validation: five existing landscape tests pass, covering placements, instancing, spatial sharing, wind bounds and shadow membership. `woodland-branches-fixture.html` provides identical-camera before/after views, with optional crown visibility. Evidence under `evidence/woodland-branches-*` records the crown comparison, native update and close-view captures. The fixture uses a flat ground solely for prototype inspection; native slope checks verify planting.

The full courtyard loaded and rendered without browser warnings/errors; `woodland-branches-main.png` shows the actual slope beside the bridge.

The trees remain procedural and the branch junctions use intersecting closed surfaces rather than a fully fused scanned tree. Existing foliage density and far silhouettes are retained. This refinement does not complete the commercial AAA goal.
