# Maintained courtyard ground

The forest-floor photograph previously repeated across the courtyard at 7 m per tile. Its baked autumn leaves remained visible after sweeping independent leaf meshes. The maintained clearing now blends in a separate moss PBR surface, keeping distant woodland leaf litter beyond the garden.

`garden-ground.js` now blends color, OpenGL normal and roughness maps using interpolated world XZ coordinates, converted to native XY. The initial terrain-UV mapping was superseded because compressed UVs introduced near-view stretching (see `bank-moss-notes.md`). The 18–28 m radial transition remains centered at native `(0,-2)`. A small irregular edge and broad tone modulation soften repetition. The 2K moss repeats every 1.2 m. Color data is sRGB; normal/roughness are linear. Three texture samples are added; terrain vertices, triangle count, collision and leaf landing geometry are unchanged.

The source maps are unmodified JPGs from [ambientCG Moss002](https://ambientcg.com/view?id=Moss002), distributed under [CC0](https://docs.ambientcg.com/license/). See `garden-moss-source.json` and `fetch_garden_moss.py`. `sync_garden_moss.py` installs equivalent material nodes and packed maps in `山林地形.blend` and `听秋寺院.blend`. These editable native files remain local. The original forest terrain GLB remains unchanged; runtime blending is installed separately.

Validation:

- Twelve existing landscape, ground surface and leaf-ground tests passed.
- Real terrain comparison fixture compiled cleanly and rendered both variants in one draw with 102,400 triangles. The first visual check exposed glTF's reversed V in the region mask; fixed before the final capture.
- Saved same-camera before/after views and a wide transition view under `evidence/garden-ground-*.png`.
- Checked the complete courtyard overview and the bridge-side first-person view, including stone, fern, water-reflection and moss junctions. Browser errors/warnings were empty. Public canvas diagnostics reported one modified material.

The transition intentionally retains baked leaf litter in the distant forest. This material layer alone does not establish a target frame rate or complete the overall AAA fidelity goal. Separate geometric moss tufts were subsequently added at the bank; see `bank-moss-notes.md`. Runtime color/roughness encoding is documented in `garden-ground-encoding-notes.md`.
