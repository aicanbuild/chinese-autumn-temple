# Fine honed granite revision

The pondside lantern and original granite paving were dominated by large high-contrast dark grains in close views. The deterministic stone generator now uses 230 mineral cells across the same 0.77 m tile, giving a typical 3.35 mm scale rather than 4.97 mm. The realized dark mica area is 4.564%, with a lighter grey-green pigment and smaller intra-grain contrast. Surface relief, tiny pits and roughness variation remain, but their amplitudes are reduced to suit a honed surface. Texture resolution remains 1024; no mesh, material or draw call is added.

`granite_finish.py` updates the three JPEG maps and their embedded copies in the original temple and lantern GLBs. `verify_granite_finish.py` compares those exports with the saved pre-change assets: all 37 unrelated temple buffers and all four lantern mesh buffers are byte-identical, as are all mesh/accessor/node/material descriptors. Only the three granite images change in each GLB. The compressed lantern contact attribute remains unchanged.

`sync_granite_finish.py` backs up, updates, saves and reopens the editable lantern and full temple files. Signatures preserve the world transforms, positions, topology, UVs, scalar attributes (including baked contact visibility) and material assignments of 46 lantern objects and 9,963 full-scene objects. Used packed stone images are verified against the current JPEG bytes after reopening.

The contact atlas test run exposed a pre-existing stale sanctuary binding from the prior mineral-paint change. Comparing its recorded original GLB confirmed exact geometry and image payloads, and only the known azurite/malachite roughness, metalness and normal-map settings changed. Both contact atlas binding records were refreshed only after that check; atlas pixels and all other input hashes remain unchanged. Lantern, floor contact, mural contact and browser build suites now pass all eleven tests.

The full scene was inspected with a local old/new image toggle at the same pondside camera. The revised grains no longer dominate the carved edges, and the roof and window frame still show material variation and tree shadows. Browser logs showed no warnings or errors. Accepted image: `evidence/granite-fine-main.png`; diagnostic fixture generation: `build_granite_audit.py`.

Runtime `53ac8d3a2c72` retains the last published `c81b1efe744a` rollback. This revision remains local; upload permission from the earlier automatic approval rejection is still pending. No publication was retried.
