"""Check real native geometry, non-degenerate copper UVs and preservation of the scene."""
import bpy,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def untouched_signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.get('bridge_asset'):continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 return {'objects':count,'geometryAndTransformHash':h.hexdigest()}
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院-before-bridge-finish.blend'));before=untouched_signature()
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'));after=untouched_signature();assert before==after,(before,after)
caps=[o for o in bpy.data.objects if o.get('bridge_asset') and o.name.startswith('Giboshi | lotus bud cap')];assert len(caps)==30
min_relief=1
for o in caps:
 assert len(o.data.vertices)==12*96
 cx=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices);cy=sum(v.co.y for v in o.data.vertices)/len(o.data.vertices)
 ring=o.data.vertices[8*96:9*96];r=[math.hypot(v.co.x-cx,v.co.y-cy) for v in ring];depth=max(r)-min(r);assert .0005<depth<.00075;min_relief=min(min_relief,depth)
 uv=o.data.uv_layers.active
 for p in o.data.polygons:
  if len(p.vertices)!=4:continue
  a,b,c=[uv.data[i].uv for i in list(p.loop_indices)[:3]];assert abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))>1e-8
 for mat in o.data.materials:
  images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(images)==3 and all(i.packed_file for i in images)
report={'nonBridgeGeometryPreserved':before==after,'preservedObjects':after['objects'],'caps':len(caps),'minimumChasedReliefMillimeters':min_relief*1000,'copperMapsPacked':True,'copperSideUVsNondegenerate':True}
(R/'evidence/bridge-finish-native.json').write_text(json.dumps(report,indent=2));print(report)
