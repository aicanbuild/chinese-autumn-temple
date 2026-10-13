# Continuous garden water current — 2026-10-10

The pond now has broad travelling ripple slopes as well as its advected normal maps. Normal flow speed increases from .008 to .055 texture units/second, with smaller world-space features. Reflection distortion increases separately from refraction distortion, preserving visibility of the bed and fish. Floating leaves travel east at approximately .10 metres/second, with a mild southward component and bank/bridge collision checks.

Creek normal advection is 1.65 times the authored velocity field. Broken highlights move downstream through rock wakes; the wake envelope stays attached to each rock while the individual crests travel through it. The shallow creek remains predominantly transparent, with very sparse crests outside the wake zones. Bed caustics travel with the current in both regions.

Shader composition applies creek normals, impact ripples, then broad current slopes. This also fixes creek normals overwriting impact ripples. There are no new scene captures or meshes, and no native Blender geometry changed.

Validation: 18 pond motion, creek, optics, and surface visibility checks passed, including ten-minute bank/bridge collision simulation and 30/60 FPS agreement. The actual composed Water2 vertex/fragment shaders compiled and linked with the Apple M5 OpenGL driver. Browser visual verification was unavailable because the browser tool rejected access to the local URL earlier in this session. The shader is an animated visual approximation, not a fluid dynamics solver.


## Surface-integrated click ripples — 2026-10-10

Replaced the opaque-looking cylinder crown and 72-drop burst with twelve small, low droplets. The pond itself now uses a 192 × 112 indexed ellipse grid. A shared analytic height field produces an initial depression, rebound, and a broadening wave train travelling at 1.4 m/s for 6.8 seconds. Its derivative changes the existing water reflection, refraction and sun lobe; there are no painted rings or extra water shells. Floating leaves sample the same height profile. Repeated impacts are smoothly height-limited to 14 cm. Eight click slots are reserved separately from four leaf-impact slots, so falling leaves cannot erase a click's wave train. The creek retains its separate fast-flow treatment.

Wave propagation, amplitude decay, leaf attachment, bounded particle lifetime, koi retreat, pond geometry, water visibility, optics, sun binding and AO checks pass. The final composed vertex and fragment shaders compile and link on the Apple M5 native OpenGL driver. Live browser visual verification remains unavailable under the browser tool restriction; this is an analytic surface animation, not a fluid simulation.


## Recording-based timing review — 2026-10-11

Reviewed the full recording at five-second intervals, then extracted 30 Hz frames from 2–5 s and 6–8 s of `ScreenRecording_10-09-2026 19-41-11_1.MP4` using AVFoundation with zero seek tolerance. The first interval includes camera motion. The 6.0–6.3 s interval holds the foreground rock essentially stationary: normalized correlation of its crop remains above .999. In the water crop beside it, correlation drops to .491 after .1 s and -.015 after .3 s. These measurements establish a fast changing fine highlight pattern, not a real-world metres-per-second measurement; the recording has no spatial calibration.

Adjusted the creek advection from a nominal 4.725 to 6.3 scene metres/second (about +33%). Broadened the visible moving normal features from scale 1.65 to 1.05 so speed reads as travel rather than only subpixel sparkle. The rock-aware normal maps, broken crests and hillside continuation all use the same speed. Shortened the phase crossfade window to 1.25 s to limit distortion through changing flow directions. Removed the independent slow cross-wave in the creek and slightly increased sparse moving crest visibility (.045 to .075 outside wakes); the pond retains its own current. The extended narrowing hillside geometry is unchanged.

Validation: 19 creek, pond, visibility and frame-time tests pass. Final composed Water2 shaders compile/link on the Apple M5 driver. Browser inspection is still unavailable under the existing tool restriction, so exact perceptual equivalence to the video has not been established in the live scene.


## Actual rapid relief and stone overflow — 2026-10-11

The speed-only approach was rejected: the author-exported water had only two vertices across the channel, so all prior creek motion remained shading on a flat surface. Added `creek-rapids.js`: subdivides the authored river bank cross-sections into 761 × 37 vertices, then displaces the actual water through a rock-registered relief atlas. The same height field changes the reflection/refraction/sun normal. Rollers reach approximately 18 cm above the local mean; low-rock relief reaches 23 cm. The bank fade and unchanged authored perimeter keep the water within the existing channel.

Read all 22 stone heights from the actual native Blender assembly; 9 lower stones feed transparent, narrowing overflow sheets with forward motion and 108 short ballistic drops. Downstream crests carry broken foam directly in the water shader. This adds two draw calls and no reflection/refraction captures. Pond interactions, hallway, controls and the long tapering headwater are unchanged. Native original stone/terrain geometry was not modified. The Blender inspection file in evidence contains the corresponding offline water shapes.

Validated river-bank alignment/upward winding, sheet launch/landing, animated geometry, bounded droplet counts, data-texture encoding, existing creek/pond/visibility/frame-time behavior (23 tests). Complete Water2 shader compiled/linked on Apple M5. Two offline Blender frames inspected; initially broad rectangular sheets were narrowed with irregular edges. This is an animated procedural rapid, not a fluid solver; the offline preview uses a different material and is only a geometry inspection. Live browser visual QA remains unavailable under the existing browser tool restriction.


## Clear irregular rapids instead of white periodic bands — 2026-10-11

Removed the crest-color blend altogether. The earlier large cosine/power wave and foreground sine-slope train were visibly regular; replaced creek relief with two scales of quintic-continuous spatial noise advected downstream, using analytic gradients for the optical normal. This gives spatially different, temporally continuous disturbances without per-frame jitter or a short repeating wave train. Wake activation now ramps smoothly rather than switching at a straight boundary. Pond ripple behavior is unchanged.

The overflowing sheets now reuse the actual pond/creek Water2 shader and share its reflection, refraction, sunlight and time uniforms. Removed the separate pale diffuse material and its white aeration tint; independent smooth irregular variation shapes each sheet. Sheets draw after the main water and are excluded from both water capture passes to avoid render-target texture feedback. Droplets are less opaque.

18 creek/pond/geometry/material-sharing checks passed. Both the complete river shader and the overflowing-sheet variant compile/link on Apple M5. Browser visual inspection remains unavailable. Prior native preview images document the previous geometry, not this revision's material; do not use them as a final visual comparison.


## Stronger natural relief and capture envelope — 2026-10-11

Increased the shared dynamic displacement/analytic-gradient amplitude by 35%, with the same nonperiodic flow field and clear optical shader. Small sheet deformation also increases from .020 to .027. Static stone registration and pond ripple amplitudes are unchanged. The existing .55 m conservative displacement bound covers the increased relief.

Investigating the reported angle-dependent dark patches found a definite capture-coverage issue: the reflection/refraction crop used undeformed vertices only. Capture bounds now enclose each region's full animated height range, and reserve .03 UV for the .018 reflection distortion plus filtering. Eight box corners per region replace tens of thousands of projected vertices. A new regression exercises 48 grazing/raised camera positions and both extrema of the displacement envelope, verifying every visible crest sample plus distortion margin is covered. This is a concrete coverage fix, not a confirmed reproduction of the screenshot's full dark-patch cause. Live browser visual reproduction remains unavailable.
