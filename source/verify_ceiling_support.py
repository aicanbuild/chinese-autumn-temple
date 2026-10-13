"""Independent ray checks against the actual saved, evaluated supporting meshes."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
fields=('Ceiling | mineral blue coffer','Ceiling | rear return coffer','Caisson | corner spandrel','Caisson | round lotus heaven')
reports=[]
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'source'/filename));deps=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];count=0
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.name.startswith(fields):continue
  count+=1;e=o.evaluated_get(deps);m=e.to_mesh();offset=len(vs)
  vs.extend(o.matrix_world@v.co for v in m.vertices);fs.extend(tuple(offset+i for i in p.vertices) for p in m.polygons);e.to_mesh_clear()
 assert count==25,count
 tree=BVHTree.FromPolygons(vs,fs);hits=0;minimum=1;maximum=0
 for o in bpy.data.objects:
  if not o.get('ceiling_carving') or not o.get('back_grid_count'):continue
  for v in list(o.data.vertices)[o['back_grid_count']:]:
   p=o.matrix_world@v.co;hit,normal,index,distance=tree.ray_cast(p-Vector((0,0,.012)),Vector((0,0,1)),.024)
   assert hit is not None,(o.name,tuple(p),'missing support')
   overlap=p.z-hit.z;assert .0008<overlap<.004,(o.name,tuple(p),overlap)
   minimum=min(minimum,overlap);maximum=max(maximum,overlap);hits+=1
 reports.append({'file':filename,'supportMeshes':count,'rayContacts':hits,'minimumOverlapMeters':minimum,'maximumOverlapMeters':maximum})
(R/'evidence/ceiling-support-rays.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print('CEILING SUPPORT RAYS',reports,flush=True)
