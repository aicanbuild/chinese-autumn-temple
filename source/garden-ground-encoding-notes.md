# Moss delivery texture encoding

The original three 2K JPEGs total 21,113,299 bytes and use all-one quantization tables. Lossless WebP trials saved almost nothing overall; the normal map grew. Those trial files were not shipped.

The browser now uses a quality-97, 4:4:4 JPEG derivative for color and a quality-95 grayscale derivative for roughness. Resolution remains 2048 × 2048. The OpenGL normal map is the unchanged original. `encode_garden_moss.py` reproduces the two derivatives and records decoded image differences. The original downloaded maps remain available to the retained previous runtime and in the editable Blender materials.

The selected three runtime textures total 17,423,349 bytes, a 3,689,950-byte reduction (17.5%). This is a transfer-size reduction for these textures, not a measured page-load-time or frame-rate improvement. GPU texture dimensions and memory allocation remain unchanged. The JPEG derivatives are lossy; there is no pixel-identity claim.

`garden-ground-encoding-fixture.html` renders the actual terrain material with each encoding at three fixed viewpoints. It compares the final tone-mapped default framebuffer immediately after rendering, with the same lighting, camera and antialiasing:

| View | Mean RGB channel difference / 255 | Maximum difference / 255 | Channels differing by more than 2 |
| --- | ---: | ---: | ---: |
| Eye height | 0.132 | 2 | 0 |
| Near ground | 0.345 | 7 | 7,583 of 1,950,000 |
| Wide transition | 0.039 | 2 | 0 |

Visual toggling showed no obvious change in moss structure or highlights. No browser warnings/errors were recorded. Evidence is saved under `evidence/garden-ground-encoding-*`. Geometry, collision, sweep behavior and the native Blender material are unchanged.
