"""Derive distant branch meshes while leaving the full native trees untouched."""
import bpy,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.wm.open_mainfile(filepath=str(R/'source/庭院曲枝树木.blend'))
shell=bpy.data.materials.new('Specimen bark | shared runtime maps');shell.use_nodes=True
for o in bpy.data.objects:
 if o.type!='MESH':continue
 bpy.context.view_layer.objects.active=o
 m=o.modifiers.new('Distant silhouette','DECIMATE');m.ratio=.16 if 'fused' in o.name else .28;bpy.ops.object.modifier_apply(modifier=m.name);o.data.materials.clear();o.data.materials.append(shell)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'garden-trees-distant.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_attributes=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
print('DISTANT TREES COMPLETE; full native model unchanged',flush=True)
