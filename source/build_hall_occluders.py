"""Read-only extraction of actual opaque rectangular interior faces."""
import bpy,json,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'source/庄严内殿.blend';before=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));deps=bpy.context.evaluated_depsgraph_get();rectangles=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.get('sanctuary_interior') or o.get('altar_brocade'):continue
 ev=o.evaluated_get(deps);mesh=ev.to_mesh()
 for p in mesh.polygons:
  if len(p.vertices)!=4 or p.area<.18:continue
  mat=mesh.materials[p.material_index] if mesh.materials else None
  if mat is None or 'water' in mat.name:continue
  shaders=[n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'] if mat.use_nodes else []
  if len(shaders)!=1 or shaders[0].inputs['Alpha'].is_linked or shaders[0].inputs['Alpha'].default_value<.999:continue
  ps=[o.matrix_world@mesh.vertices[i].co for i in p.vertices];vs=[(v.x,v.z,-v.y) for v in ps];lo=[min(v[a] for v in vs) for a in range(3)];hi=[max(v[a] for v in vs) for a in range(3)]
  axes=[a for a in range(3) if hi[a]-lo[a]<1e-6]
  if len(axes)!=1:continue
  a=axes[0];b,c=[i for i in range(3) if i!=a]
  if min(hi[b]-lo[b],hi[c]-lo[c])<.25:continue
  if not all(min(abs(v[b]-lo[b]),abs(v[b]-hi[b]))<1e-6 and min(abs(v[c]-lo[c]),abs(v[c]-hi[c]))<1e-6 for v in vs):continue
  # Shrink by two millimetres to avoid float/export-edge uncertainty.
  lo[b]+=.002;hi[b]-=.002;lo[c]+=.002;hi[c]-=.002
  rectangles.append({'axis':a,'lo':lo,'hi':hi,'source':o.name})
 ev.to_mesh_clear()
assert hashlib.sha256(path.read_bytes()).hexdigest()==before
out={'rectangles':rectangles,'sourceSHA256':before,'sourceUnchanged':True,'inset':.002,
 'geometryBindings':{name:hashlib.sha256((R/'dist/assets'/name).read_bytes()).hexdigest() for name in ['sanctuary.glb','fine-caisson.glb']}}
(R/'dist/assets/hall-occluders.json').write_text(json.dumps(out,separators=(',',':')));print('OCCLUDERS',len(rectangles),flush=True)
