# Real-time scene motion with bounded physics steps

The application previously clamped every frame's simulation time to 45 ms. At 8 fps, one minute of viewing advanced wind, koi, falling/swept leaves, walking and the bell schedule by only 21.6 seconds. Incense used a separate 250 ms limit, so different parts of the same scene ran at different speeds.

`simulationFrame` now retains up to 250 ms of elapsed time per displayed frame. Analytic animation and ritual updates use that time once; walking and leaf physics divide it into steps no longer than 45 ms. This preserves the former collision-step limit while retaining normal speed at 4 fps and above. Leaf transforms/counts are published only on the final substep, so extra physics steps do not multiply matrix uploads or draw calls. Hidden-page suspension resets the previous timestamp both on hiding and return, avoiding a burst of catch-up motion.

The existing 250 ms long-stall limit remains intentional: a frozen tab or severe stall cannot demand an unlimited simulation backlog. This is a timing correction, not a frame-rate improvement. Rendering is still too slow for the full commercial AAA objective. No model, texture, water optical shader or lighting setting changed.

223 tests pass. New tests cover one minute at 4, 8, 15, 24, 60 and 144 fps; irregular frames; bounded long stalls; the actual visibility-change callback; and the actual leaf update with eight displayed frames and three physics substeps per frame. A leaf descends 0.44 m in one second at both 8 and 60 fps, while its instance buffers update eight times for the eight-frame case. Existing support/collision and koi separation tests remain in force.

Integrated runtime `04082fbf92ba`: two public diagnostic snapshots span 85.1274 seconds of wall time and 84.3485 seconds of simulation (99.09%; long-stall protection accounts for lost time). Automatic bell count increased from two to five, 49 leaves were swept, and the broom returned to its parked state. No browser warning/error logs were recorded. The later frame average remained 119.3 ms, so this change does not resolve the FPS deficit. Evidence: `evidence/simulation-time-browser.json` and `simulation-time-pond.png`.

## Rejected performance experiments

Two measured alternatives were kept outside the production build:

- Adaptive Snell solve (`water-refraction-adaptive-experiment.js` and fixtures): early termination under the existing residual criterion plus reciprocal-square-root reuse. 8,192 real-GPU optical tests had no invalid results and a maximum exit-position error of 0.0415 mm; six actual views had small raster differences. But two alternating 36-sample timing runs did not establish stable benefit: first medians 12.108/11.272 ms with nearly equal means 11.856/11.788 ms; second medians 11.817/11.705 ms and means 12.192/11.654 ms. The published fixed-five-step implementation remains unchanged. The independent 8,192-case optical-path test was retained for the original CPU solver, allowing 1e-12 m endpoint roundoff and retaining a 0.5 mm maximum error gate.
- Drawing alpha-one water first as an opaque depth occluder (`water-depth-first-fixture.html`): six views were almost identical, but the tested whole-draw GPU median increased from 26.668 to 33.746 ms (36 samples each), so the original draw order remains unchanged.

Fixtures use actual pond/bridge/koi assets and asynchronous GPU queries; they are not full-app frame-rate proofs. Local evidence is saved in `evidence/refraction-perf-baseline.json`, `refraction-early-exit-initial.json`, `refraction-adaptive-final.json`, `refraction-adaptive-numeric.json` and `water-depth-first-rejected.json`. Both rejected shaders/orderings are test-page-only and are not imported by the production app.
