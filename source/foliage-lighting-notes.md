# Thin foliage lighting

Adds local, shadowed diffuse transmission to 620 woodland trees, 127 established shrubs, 265 forest-edge shrubs, 743 forest-edge ferns and 96 pond-edge ferns. Twigs/trunks are excluded. Existing individual garden leaves retain their separate vein-aware shader.

- Diffuse fractions: evergreen woodland .20, autumn woodland .25, shrub .16, fern .27. Existing pigment, vertex color, normals and cutout alpha remain authoritative.
- Splits direct diffuse reflection/transmission; no emissive boost, transparent pass, extra texture, geometry, or shadow-map lookup. Specular and environment response stay as before in the browser.
- Corrects normal bias to the light-facing side of a thin sheet. Directional/spot projection-depth derivative determines the side; point lights use radial distance. This fixes false self-shadowing under backlighting without ignoring other occluders. Inner scopes survive Three's light-loop unrolling with multiple lights.
- Shader hooks compose with existing woodland wind; depth/distance silhouette shaders remain unchanged. InstancedMesh and BatchedMesh both tested.

## Verification

`node --test source/foliage-lighting.test.mjs source/foliage-wind.test.mjs source/forest-edge.test.mjs source/understory.test.mjs source/landscape.test.mjs`: 16 passed.

`source/foliage-lighting-fixture.html` renders real fern/shrub/tree assets and a separate float-target radiometric check. Directional, point and spot lights independently produced backlit luminance .0623/.0621/.0621 vs zero for opaque, zero with blocker, and zero with light off. Front diffuse dimmed as the transport budget was split. Repeated directional lights together with point/spot lights compiled and rendered (mixed backlit .0744). These are controlled fixture values, not measurements of the whole garden or proof of physical accuracy.

Full app runtime 54dc2b9cb2f2 rendered in bridge and woodland-side views; no new warnings/errors after final shader correction. Saved proof and screenshots in `evidence/foliage-lighting-*` (local only). The earlier trial's shader compile failure from unrolled variable redeclaration was fixed before the final build. Fixture comparison buttons toggle diffuse transport with the corrected receiver bias retained in both modes.

`source/refine_foliage_light.py` updated the main native file plus 山林地形 / 山林地被 / 林下灌木 / 池岸蕨类, using a pigmented Translucent BSDF mixed with the existing shader. Alpha masks and normal maps remain connected. Native objects and transforms were checked unchanged; main file has 9,412 objects and 12 matching material datablocks. Backups end in `-before-foliage-light.blend`. The script is idempotent and should run after regenerating plant sources. GLB assets were deliberately not re-exported through Blender's unsupported arbitrary shader mix; browser material extension is supplied by JS.

## Limits

This is a thin diffuse approximation, not measured species-specific scattering or multi-layer canopy transport. Browser environment diffuse is unchanged; Cycles also transports environment lighting through the native translucent lobe, so the two renderers are not pixel-identical. No frame-rate improvement is claimed. Overall AAA fidelity remains incomplete.
