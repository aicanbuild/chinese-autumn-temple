# Koi contour and surface refinement

The close view showed segmented body contours, uniform plastic-looking highlights, oversized round eyes and largely buried gill seams. This revision refines the existing four koi prototypes while retaining the sixteen-fish school, motion code, original pigment patterns, fins and barbels.

## Changes

- Shape-preserving cubic interpolation replaces a separate zero-slope smoothstep at every body landmark. All original landmark radii are retained, with no overshoot beyond .166 m. Maximum analytic radius change from the old curve is .009242 m; position-row and side counts remain 73 × 49.
- Eyes scale to 65% of the old dimensions, with their centers placed against the new head surface instead of shrinking in place.
- Gill seams follow the revised surface, use a narrower section and a darker matte finish. The shared mouth-cavity material also receives the darker finish. Seams remain separate geometry, not actual operculum topology.
- A shared 2048 × 1024 normal map uses a .14 mm scale crest and body-space derivative conversion. Roughness varies approximately .33–.479 across smooth skin, scale faces and overlapping rims. Runtime normal strength now matches the native map at 1.0. Clearcoat .18, clearcoat roughness .25.
- Four existing pigment atlases and the fin-membrane payload are byte-exact against the pre-change GLB. No new skin pattern or downloaded texture is used. Packed roughness uses the green channel; metallicFactor remains zero, so the grayscale JPEG is safe for the unused metallic channel.
- GLB 1,878,996 → 2,296,856 bytes (see final integrity file/stat for exact size). Four prototypes still render 14,272 triangles each; the standalone fixture uses 20 calls before and after. The runtime keeps its existing instancing and shader-deformation path. No FPS improvement is claimed.

## Files and reproducibility

`koi_surface_finish.py` creates the surface maps and defines the continuous contour. `refine_koi_finish.py` applies the finish to `锦鲤.blend` and `听秋寺院.blend`, exports `dist/assets/koi/koi.glb`, and checks all untouched geometry and all object transforms before saving. Native backups end in `-before-koi-finish.blend`; original gill coordinates come from that local backup for repeatability. The main scene's 9,412 objects remain in place; 5,195 unrelated mesh datablocks were checked unchanged in the final run. Native files/backups remain local.

The final run is idempotent for already-refined bodies, so its `maximumVertexChangeMeters: 0` describes that run, not the total difference from the initial model. Original body change was .009237 m at sampled mesh vertices. Analytic profile evidence is separately stored in `evidence/koi-finish-integrity.json`.

## Validation

`node --test source/koi-finish.test.mjs source/koi.test.mjs source/koi-motion.test.mjs source/koi-school.test.mjs`: 11 passed. An hour sampled every .2 s at maximum fish size retained minimum envelope gaps of .0849 m between fish, .2736 m from piers, and .1122 m above the bed. A day sampled every 3.17 s also passed; these sampled results do not prove every possible continuous instant or parameter choice.

`source/koi-finish-fixture.html`: four original/refined skin variants, side and head close views. `evidence/koi-finish-before.png` and `...-after.png` show the same close-view camera. Main runtime `047ee32c5aa5` was checked beside the bridge, with fish visible through the water and no browser warnings/errors. Evidence: `koi-finish-main.png`, `koi-finish-browser.json`, `koi-finish-native.json` and `koi-finish-integrity.json`.

Visual references consulted: [Zoo Leipzig domestic koi photographs](https://www.zoo-leipzig.de/en/animal/koi-farbkarpfen/) and [Connecticut DEEP carp identification/photos](https://portal.ct.gov/deep/fishing/freshwater/freshwater-fishes-of-connecticut/common-carp). These informed inspection of body/fins/eyes; proportions here are art direction, not a measured anatomical reconstruction. No reference photos are included in the distributed assets.

## Remaining limitations

Procedural body and fins remain stylized at macro scale. The gill seam is an approximation, fins use alpha membranes, and underwater reflections/scattering are real-time approximations. This increment does not establish commercial AAA fidelity for the overall temple.
