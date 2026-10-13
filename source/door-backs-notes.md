# Interior door linings

The existing four door leaves at native x = −4.35, −2.88, 2.88 and 4.35 m had detailed exterior lattices but plain opaque backs. This addition keeps the original leaf thickness, exterior face and central entry. It adds a 2 mm embedded inner lining, softened timber frames, a recessed diamond lattice field, narrow gilt beads and lotus relief skirt panels. The relief is adapted from this project's original altar carving to keep the decorative vocabulary consistent.

The Palace Museum's [槅扇 description](https://www.dpm.org.cn/lemmas/243812.html?hl=%E6%89%87) and [储秀宫 account](https://www.dpm.org.cn/explore/building/236486.html) informed the separation of frame, lattice field and carved skirt panel. This is an original composite design, not a replica or a claim of historically exact temple construction. No museum imagery is included in the asset.

`door_backs.py` defines the editable geometry. `install_door_backs.py` backs up and updates both native Blender scenes, checks closed positive-volume meshes and retained object geometry/UV/transforms, then exports four geometry-only batches. The browser assigns the existing finished sanctuary materials, sharing textures and indoor reflection capture. The leaves remain opaque and static; the lattice is a relief lining, with no new opening interaction or light transmission.

After a complete rebuild of the base sanctuary, rerun `install_door_backs.py` and `build_hall_navigation.py`. The latter reads the full native scene without changing it and includes four door leaves in the camera collision bounds. Original Blender scenes and backups remain local; only the web geometry and reproducible source are published.
