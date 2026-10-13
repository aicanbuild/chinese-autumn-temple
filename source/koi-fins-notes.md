# Koi fin refinement

Close views showed angular fin silhouettes, broad white rays and single-point dorsal/anal attachment. Seven shared fin meshes now have curved outlines, slightly bowed membranes and shallow inward scallops. Dorsal and anal roots follow the existing body profile, just inside the surface. Seventeen finer rays branch toward the outer membrane; opacity and pigmentation vary gently instead of forming uniformly white spokes.

`koi_fin_surfaces.py` generates the original 1024 × 1024 RGBA membrane and normal map. Root/edge UV orientation is explicit. The modeled ray relief is .065 mm; normal strength .65 matches native and browser materials. Fin roughness is .5, coat .10, coat roughness .28. This is artistic procedural modeling, not scanned anatomy.

`refine_koi_fins.py` updates `锦鲤.blend` and `听秋寺院.blend`, with local backups ending in `-before-koi-fins.blend`. All 84 standalone and 9,412 main-scene object transforms are preserved. Unrelated mesh fingerprints remain unchanged: 16 standalone and 5,198 main-scene meshes. Native files and backups remain local.

## Validation and cost

- Final GLB: 2,712,668 bytes, SHA256 `4259f146fb57bd5c90f0452ecd25cde77fefec693df7ac52894e30d5b5b21f32`.
- All 16 non-fin compressed mesh payloads and all six body image payloads are byte-exact against the previous published model; see `evidence/koi-fins-integrity.json`.
- Seven fin meshes increase from 1,680 to 4,390 triangles. One visible fish increases from 14,272 to 16,982 triangles, with the fixture still at 20 draw calls. Sixteen fish add 43,360 raw triangles before culling. The new maps also increase texture memory; no FPS improvement is claimed.
- `node --test source/koi-finish.test.mjs source/koi.test.mjs source/koi-motion.test.mjs source/koi-school.test.mjs`: 11 passed. One hour sampled every .2 s at maximum size retains envelope gaps of .0848762 m between fish, .2748482 m from piers and .1124504 m above the bed. One day sampled every 3.17 s also passes (.0867054, .2744543 and .1112313 m respectively). These sampled checks are not continuous collision proofs.
- `koi-fins-fixture.html` provides four variants and four views. Matching close-view captures: `evidence/koi-fins-before.png` and `koi-fins-after.png`. Actual pond view: `koi-fins-main.png`. Main runtime `b56bc2aad73d` and the fixture reported no browser warnings/errors; `koi-fins-browser.json` records this check.

The fin membranes, gill seams and underwater optics remain approximations. This increment does not establish commercial AAA fidelity for the whole temple.
