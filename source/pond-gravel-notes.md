# Water-worn pond gravel

The bridge-side view showed evenly scattered, low-detail dark discs. Two existing bed-stone prototypes now have rounded asymmetric contours and smoother normals. The original 157 cobbles retain XY positions, scales and rotations, with vertical seating recomputed against the actual basin. Another 360 smaller pebbles form 40 sparse groups around existing stones, with open sediment between groups. These are art-directed procedural river stones, not scanned assets.

## Native and browser agreement

`refine_pond_gravel.py` updates `自然池岸.blend` and `听秋寺院.blend`, with local `-before-gravel.blend` backups. The saved main scene now has 9,772 objects. The six bank/toe prototype payloads are byte-exact in the exported GLB; all 100 bank/toe placements are unchanged, including the rocks supporting the moss. The main scene's 5,203 unrelated mesh datablocks and non-bed object transforms were checked unchanged. Source files and backups remain local.

The eight prototypes remain eight browser batches. Bed prototypes increase from 80 to 320 triangles; bed geometry increases from 12,560 to 165,440 triangles before repeated render passes. GLB size increases only from 216,920 to 219,408 bytes, without embedded texture duplication. The fixed water fixture submits 5,731,857 → 6,190,497 triangles at its close-view camera while retaining 176 calls. This adds rendering work; no FPS improvement is claimed.

`verify_pond_gravel.py` independently reopens the saved source. All eight meshes are closed/manifold; all 617 placements match the shipped layout. The 517 bed stones embed 4 mm (new gravel) or 10 mm (existing cobbles) at their support point. New gravel rises at most .070159 m above the local sediment. Every original cobble top is lower than before (smallest reduction .006543 m); the highest stone top is -.858742 m.

## Contact light and verification

The existing 2560 × 1536 finite-distance contact atlas was rebaked against all 517 bed stones, ten piers and retained lotus stems, using the existing 32 Cycles / 64 AO sample settings. `verify_pond_contact.py` now derives its expected count from the shipped layout and includes smallest, median and largest newly added gravel in its independent ray probes. Eighty probes with 2,048 rays each give mean AO-factor error .008261, maximum .116355. Small silhouettes near atlas texel boundaries have larger filtering error; this remains a finite-resolution ambient approximation.

Fourteen geometry/basin/water-visibility tests and four contact-atlas tests pass (18 total). The broad basin-motion test samples its existing parameter set and reports a .068993 m conservative sediment clearance; that is not a continuous collision proof against every individual stone. Actual school trajectories and their previous clearance checks are unchanged by this asset-only revision.

`pond-gravel-fixture.html` compares the previous geometry/layout/contact map with this revision at six fixed views. Evidence: `pond-gravel-before.png`, `pond-gravel-after.png`, `pond-gravel-browser.json`, `gravel-native-audit.json`, `gravel-integrity.json` and `pond-contact-ray-audit.json`. The complete scene was checked beside the bridge using runtime `255f23a45a47`; `pond-gravel-main.png` and `pond-gravel-main.json` record the view and empty warning/error log.

The scene still has stylized geometry, approximate water transport and unvalidated whole-scene performance targets. Commercial AAA fidelity remains incomplete.
