"""Add chart-blend data while protecting geometry, planting layout and primary UVs."""
import bpy,sys,json,hashlib,shutil
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from tree_bark_uv import authored_paths
from bark_junctions import add_bark_blend,configure_native_bark
A=R/'dist/assets';layout=json.loads((A/'garden-trees.json').read_text());paths,anchors=authored_paths(layout['trees']);assert np.max(np.abs(np.asarray(anchors)-np.asarray(layout['anchors'])))<1e-7
names=[f'Garden tree {i:02d} fused trunk' for i in range(15)]
def signatures():
 result={}
 for o in bpy.data.objects:
  h=hashlib.sha256(np.asarray(o.matrix_world).tobytes())
  if o.type=='MESH':
   for coll,prop,width,dtype in [(o.data.vertices,'co',3,np.float32),(o.data.loops,'vertex_index',1,np.int32),(o.data.polygons,'loop_total',1,np.int32),(o.data.polygons,'material_index',1,np.int32)]:
    v=np.empty(len(coll)*width,dtype=dtype);coll.foreach_get(prop,v);h.update(v.tobytes())
   h.update(str([m.name if m else None for m in o.data.materials]).encode())
   for uv in o.data.uv_layers:
    if uv.name=='BarkBlendUV':continue
    v=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',v);h.update(v.tobytes())
  result[o.name]=h.hexdigest()
 return result
back=R/'evidence/bark-junction-original';back.mkdir(exist_ok=True)
for name in ['garden-trees.glb','garden-trees-distant.glb']:
 if not (back/name).exists():shutil.copy2(A/name,back/name)
report=[]
for filename in ['庭院曲枝树木.blend','听秋寺院.blend']:
 file=R/'source'/filename;backup=file.with_name(file.stem+'-before-bark-blend.blend')
 if not backup.exists():shutil.copy2(file,backup)
 bpy.ops.wm.open_mainfile(filepath=str(file));before=signatures();stats=[]
 for i,name in enumerate(names):stats.append(add_bark_blend(bpy.data.objects[name].data,paths[i]))
 # Clone for fused trunks: untouched twigs/pines keep their original shader.
 original=bpy.data.objects[names[0]].data.materials[0];mat=original if original.get('bark_junction_revision') else original.copy();mat.name='Specimen bark | blended fork charts';configure_native_bark(mat,A,bpy.data.objects[names[0]].data.uv_layers[0].name)
 # Check material assignments separately; geometry/UV equality before assignment.
 assert before==signatures(),[n for n,h in before.items() if signatures()[n]!=h]
 for name in names:bpy.data.objects[name].data.materials[0]=mat
 after=signatures();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.wm.open_mainfile(filepath=str(file));assert after==signatures()
 report.append({'file':filename,'objects':len(before),'geometryPrimaryUVAndTransformsPreserved':True,'fusedTrunks':len(names),'charts':stats})
 if filename=='庭院曲枝树木.blend':
  shell=bpy.data.materials.new('Specimen bark | runtime shared maps');shell.use_nodes=True
  for o in bpy.data.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(shell)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'garden-trees.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_attributes=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'evidence/bark-junction-native.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=int));print('BARK JUNCTIONS',[(r['file'],r['objects']) for r in report],flush=True)
