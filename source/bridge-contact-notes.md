# Bridge joinery: local indirect visibility

The bridge now carries a cosine-weighted local visibility field for its assembled wood/bronze joints (22 cm radius, 1.2 mm normal offset, 96 rays at retained samples). Runtime shading affects indirect diffuse and environment specular light only. The existing direct-sun shadow map is untouched.

The initial corner-only bake was rejected after an independent interior audit: sparse faces spread edge occlusion across otherwise open copper surfaces. The shipped mesh instead receives three selective refinement passes, driven by midpoint/centroid visibility error. All new vertices lie on the original triangles before compression. A 32-ray field selects subdivisions; final retained samples use 96 rays. This is an approximation, not a guarantee that every contact boundary is resolved.

Final geometry: 503,219 triangles and 291,107 vertices in the existing four batches, compared with 206,516 triangles previously. Original PBR image payloads are byte-exact. Sequential Draco encoding keeps the asset at 12,592,132 bytes (previously 6,960,424). Maximum additional world-coordinate component error is 0.0268 mm; visibility quantization error <0.000024. No new full-scene frame-rate claim is made; the added geometry and download size are a cost of this detail.

The local editable `精修木桥.blend` and `听秋寺院.blend` retain all 843 bridge parts and their original authored surfaces, normals, UVs and transforms, with a custom corner visibility field. The web export adds shading subdivisions on those same surfaces. Cycles retains its normal physical light transport; the web-only visibility multiplication is not applied again to Blender materials. Pre-change native backups are local.

Validation:
- Native before/after save-reopen audit: 843 standalone bridge meshes and 9,643 meshes in the complete scene are unchanged in geometry, normals, UVs and transforms.
- Independent 1,024-ray sampling: vertex mean absolute visibility error 0.00330, maximum 0.0191. The 384 area-stratified interior probes (96 per material) have mean error 0.0411; individual contact/interpenetration boundaries can still have large error (maximum 0.7435). This is not a per-pixel accuracy bound.
- Refinement area/volume/bounds witness: maximum relative area difference <0.000000321, world bounds difference <0.0000002 m before compression.
- Four rendered camera views with environment/hemisphere disabled: enabling the contact term changes zero direct-light pixels. Four draw calls remain four draw calls.
- Eleven bridge, pond-contact and refraction tests pass. The pond contact atlas is unchanged; its bridge input hash was updated only after verifying unchanged surface bounds and compression deviation below 30 micrometers.
- Browser fixture and complete-scene warnings/errors: none in final runs. Screenshots and reports are local under `evidence/bridge-contact-*`.

Reproduce with the original bridge from commit `c14053cff50803e97d627db6fb84b055b7592887` saved as `evidence/bridge-before-contact.glb`. Run `export_bridge_samples.mjs`, copy its coarse JSON to `bridge-contact-samples.json` before a first native bake, run `bake_bridge_contact.py` in Blender, then `refine_bridge_contact_samples.py`, `verify_bridge_contact.py`, `audit_bridge_subdivision.py`, `compress_bridge_contact.mjs`, `verify_compressed_bridge.mjs`, and `pack_bridge_contact.py`. Finally run `build_browser.py`. The source Blender files remain local and are not uploaded.

The overall commercial AAA fidelity goal remains incomplete. This update improves near-view joint lighting; it does not solve the broader scene's stylization or establish a final performance target.

Publication packaging: the first archive exceeded the hosting expanded-size cap by 736,690 bytes. The unused vendored Rhino runtime was moved from `dist/vendor/three/addons/libs/rhino3dm` to `source/vendor-reference/rhino3dm`. Application modules use GLTF/Draco and do not import the Rhino loader; textures and active dependencies are unchanged.

The hosting limit includes tar metadata/padding: the first trimmed archive had 266,340,553 file bytes but 268,533,248 expanded tar bytes, still 97,792 bytes over the cap. Unused Ammo WASM and Lottie runtimes were also moved into `source/vendor-reference/unused-libs`. Release verification measures the complete gzip-expanded tar stream before upload.
