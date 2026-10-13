"""Update only branch UVs in both native projects, retaining all geometry."""
import bpy,sys,json,hashlib,shutil
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from tree_bark_uv import authored_paths,align_bark
from bark_junctions import add_bark_blend
A=R/'dist/assets';layout=json.loads((A/'garden-trees.json').read_text())
paths,anchors=authored_paths(layout['trees'])
assert np.max(np.abs(np.asarray(anchors)-np.asarray(layout['anchors'])))<1e-7,'Authored skeleton replay differs from the original leaf layout'

def geometry_hash(o,include_uv=True):
 h=hashlib.sha256();h.update(np.asarray(o.matrix_world).tobytes())
 if o.type=='MESH':
  for elements,attribute,width,dtype in [(o.data.vertices,'co',3,np.float32),(o.data.loops,'vertex_index',1,np.int32),(o.data.polygons,'loop_total',1,np.int32),(o.data.polygons,'material_index',1,np.int32)]:
   values=np.empty(len(elements)*width,dtype=dtype);elements.foreach_get(attribute,values);h.update(values.tobytes())
  h.update(str([m.name if m else None for m in o.data.materials]).encode())
  if include_uv:
   for layer in o.data.uv_layers:
    values=np.empty(len(layer.data)*2,dtype=np.float32);layer.data.foreach_get('uv',values);h.update(values.tobytes())
 return h.hexdigest()

names=[f'Garden tree {i:02d} fused trunk' for i in range(15)]
new_uv={};report={}
for filename in ['庭院曲枝树木.blend','听秋寺院.blend']:
 file=R/'source'/filename;backup=file.with_name(file.stem+'-before-bark-uv.blend')
 if not backup.exists():shutil.copy2(file,backup)
 bpy.ops.wm.open_mainfile(filepath=str(file))
 before={o.name:geometry_hash(o,include_uv=o.name not in names) for o in bpy.data.objects}
 stats=[]
 for i,name in enumerate(names):
  o=bpy.data.objects[name]
  if filename=='庭院曲枝树木.blend':
   stats.append(align_bark(o.data,paths[i]));uv=np.empty(len(o.data.uv_layers.active.data)*2,dtype=np.float32);o.data.uv_layers.active.data.foreach_get('uv',uv);new_uv[name]=uv
  else:
   assert len(o.data.uv_layers.active.data)*2==len(new_uv[name]);o.data.uv_layers.active.data.foreach_set('uv',new_uv[name]);o.data.update();add_bark_blend(o.data,paths[i])
 assert before=={o.name:geometry_hash(o,include_uv=o.name not in names) for o in bpy.data.objects},'Unexpected geometry, placement, material or unrelated UV changes'
 bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.wm.open_mainfile(filepath=str(file))
 assert before=={o.name:geometry_hash(o,include_uv=o.name not in names) for o in bpy.data.objects},'Saved native file changed unrelated content'
 for name in names:
  uv=np.empty(len(bpy.data.objects[name].data.uv_layers.active.data)*2,dtype=np.float32);bpy.data.objects[name].data.uv_layers.active.data.foreach_get('uv',uv);assert np.array_equal(uv,new_uv[name])
 report[filename]={'preservedObjects':len(before),'updatedUVObjects':len(names),'stats':stats,'backup':str(backup)}
 if filename=='庭院曲枝树木.blend':
  shell=bpy.data.materials.new('Specimen bark | runtime shared maps');shell.use_nodes=True
  for o in bpy.data.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(shell)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'garden-trees.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_attributes=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
  assert (A/'garden-trees.glb').stat().st_size<3*1024*1024
(R/'evidence/tree-bark-native.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('BARK UV COMPLETE',json.dumps({k:v['preservedObjects'] for k,v in report.items()},ensure_ascii=False),flush=True)
