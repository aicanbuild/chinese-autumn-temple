# Calm surface slopes and continuous sediment

Close pond views had two separate problems: strong intersecting caustic ribbons and large rectangular sediment boundaries. Disabling the water surface in the fixture left the boundaries visible, isolating the second problem to the repeating sediment material.

## Surface and photon density

The ripple atlas encodes .65 of the analytical XY slopes and the surface shader applies another .42. The photon bake previously used the unscaled wave field. `caustic_transport.py` now scales wave heights and derivatives by their product, .273, before tracing its existing 4,194,304 rays per depth layer. The three depths, two seeds, mean-one energy convention and .48 runtime contrast remain unchanged. This changes focusing to suit the calm surface rather than applying a uniform darkening multiplier.

`water-optics.js` also decodes normal-map Z from [0,1] to [-1,1], as it already did for X/Y. The former unsigned Z made the nominal slope slightly flatter and dependent on wave steepness. Ripple images themselves are unchanged. Shared caustic sampler uniforms allow the source comparison to swap before/after maps without rebuilding materials.

`audit_calm_water.py` compares the shipped, quantized ripple atlases with the analytical nominal slope used for the bake. Maximum normal-angle errors are .155920° and .149520°; mean density at every stored depth remains within .000029 of 1.0. The two maps and their flow/phase blends still approximate evolving wave transport; this is not frame-by-frame physical caustic simulation or exact phase synchronization.

## Sediment continuity

`pond_sediment_finish.py` generates original Fourier-periodic color, normal and roughness maps at the existing 4.2857 × 2.5714 m UV pitch. Color means remain within .30/255 per channel of the old maps. Mean first/last-edge differences in the color atlas decrease from 10.12/10.47 to .78/.80 byte values, comparable to local fine-grain variation. Fine relief is defined in physical units and differentiated with periodic neighbors.

Only three opaque sediment images were replaced in `temple.glb`; every other buffer payload, including all compressed geometry and other images, was verified byte-exact. The resulting GLB is 21,100,112 bytes. Hall/mural contact metadata hashes were advanced after that image-only proof; their baked factors and geometry were not changed or rebaked. Pond contact inputs remain unchanged.

`refine_calm_water.py` and `sync_pond_sediment.py` apply the matching nominal normal strength and packed sediment maps to the existing `听秋寺院.blend`, retaining all 9,772 objects and their transforms. Local backups are `-before-calm-water.blend` and `-before-continuous-sediment.blend`. The older native water rebuild script was also updated so a later rebuild retains the corrected decoder and current stone count.

## Validation

- Twelve water/pond optics, motion and sun-shadow tests pass, including evaluating the generated normal-decode expression against known analytical slopes.
- Ten pond, hall and mural contact tests pass; image-only temple changes preserve the geometry dependencies of the saved atlases.
- `calm-wave-fixture.html` compares the old decoder, caustic maps and sediment finish against the final revision at fixed time/cameras. Both variants retain 43 calls and 1,032,617 triangles in the renderer's recorded final pass. This is not a whole-frame performance measurement.
- Two close views show continuous sediment and softer light patterns. The final fresh fixture reports no warnings/errors. An earlier development load hit a stale unversioned helper; explicit fixture module versions corrected it before validation.
- Evidence: `calm-wave-before.png`, `calm-wave-after.png`, `calm-wave-browser.json`, `calm-water-audit.json`, `pond-sediment-finish.json`, and the full-scene `calm-water-main.png` / `calm-water-main.json`.

Runtime: `a1f99f43f059`. This revision adds no geometry, texture dimensions, light or capture pass. Baked transport, finite reflection/refraction resolution and overall stylized content still limit realism. Commercial AAA fidelity remains incomplete.
