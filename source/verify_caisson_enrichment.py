"""Independent proximity audit against saved evaluated ceiling geometry."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/庄严内殿.blend'));deps=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.get('caisson_vines') or not (o.name.startswith(('Caisson |','Ceiling |','Dougong |')) or o.get('ceiling_carving')):continue
 e=o.evaluated_get(deps);m=e.to_mesh();start=len(vs);vs.extend(o.matrix_world@v.co for v in m.vertices);fs.extend(tuple(start+i for i in p.vertices) for p in m.polygons);e.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs);count=0;maximum=0;paintmax=0;reports=[]
for o in bpy.data.objects:
 if not o.get('caisson_vines'):continue
 localmax=0;paint=o.data.materials[0].name.startswith(('Caisson | mineral polychrome','Caisson | painted square'))
 for v in o.data.vertices:
  point=o.matrix_world@v.co;hit,normal,face,d=tree.find_nearest(point);assert hit is not None;assert d<(.0015 if paint else .012),(o.name,d,tuple(point));localmax=max(localmax,d);count+=1
 maximum=max(maximum,localmax)
 if paint:paintmax=max(paintmax,localmax)
 reports.append({'part':o.name,'maximumDistance':localmax})
report={'checkedVertices':count,'maximumDistance':maximum,'maximumPaintDistance':paintmax,'parts':reports};(R/'evidence/caisson-enrichment-support.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('SUPPORT',count,maximum,paintmax,flush=True)
