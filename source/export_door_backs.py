"""Export installed door linings without modifying the native file."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/庄严内殿.blend'))
layout_path=R/'dist/assets/sanctuary.json';layout=json.loads(layout_path.read_text());layout['components']=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects);layout['doorBacks']={'leaves':4,'parts':sum(bool(o.get('door_back')) for o in bpy.data.objects),'asset':'door-backs.glb'};layout_path.write_text(json.dumps(layout,indent=2))
parts=[o for o in bpy.data.objects if o.get('door_back')];materials=set(o.data.materials[0] for o in parts)
for m in materials:
 bpy.ops.object.select_all(action='DESELECT');selected=[o for o in bpy.data.objects if o.get('door_back') and o.data.materials[0]==m]
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=m.name;bpy.context.object['sourceMaterial']=m.name
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.get('door_back'):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/door-backs.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='NONE',export_extras=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
