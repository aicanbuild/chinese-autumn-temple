"""Build a distant-view sculpture from the full original, never overwrite the sculpt."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.wm.open_mainfile(filepath=str(R/'source/主殿佛像.blend'))
materials=list({o.data.materials[0] for o in bpy.data.objects if o.type=='MESH' and o.data.materials})
for material in materials:
 parts=[o for o in bpy.data.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==material]
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=material.name+' | distant'
 mod=o.modifiers.new('Distant silhouette topology','DECIMATE');mod.ratio=.075;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.validate(clean_customdata=False);o.data.update()
 for p in o.data.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(A/'sculpture-distant.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/主殿佛像-远景.blend'))
print('DISTANT SCULPTURE',sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH'),'polygons')
