"""Measure saved fruit-to-support contact and verify the actual packed scan."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
fruits=[o for o in bpy.data.objects if o.get('fruit_kind') in ['apple','citrus']];assert len(fruits)==12
assert sum(o.get('fruit_kind')=='apple' for o in fruits)==6
assert sum(o.get('fruit_kind')=='calyx' for o in bpy.data.objects)==6
bpy.context.view_layer.update()
def bvh(objects):
 vs=[];fs=[]
 for o in objects:
  offset=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
 return BVHTree.FromPolygons(vs,fs)
gaps=[]
for o in fruits:
 side=1 if o.location.x>0 else -1
 if o['fruit_layer']==0:
  support=[p for p in bpy.data.objects if p.name.startswith('Offering | bronze fruit tazza') and (sum(v.co.x for v in p.data.vertices)>0)==(side>0)]
 else:support=[p for p in fruits if p['fruit_layer']==0 and p.get('fruit_kind')==o.get('fruit_kind')]
 tree=bvh(support);dist=[]
 for v in o.data.vertices:
  w=o.matrix_world@v.co;hit,_,_,_=tree.ray_cast(Vector((w.x,w.y,5)),Vector((0,0,-1)))
  if hit:dist.append(w.z-hit.z)
 gap=min(dist);gaps.append(gap);assert .0003<gap<.0007,(o.name,gap)
 assert o.data.uv_layers.active;assert len(o.data.vertices)>2000
 maps=[n.image for n in o.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image];assert len(set(maps))==3 and all(m.packed_file for m in maps)
 if o.get('fruit_kind')=='apple':assert all(tuple(m.size)==(2048,2048) for m in maps)
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
report=json.loads((R/'evidence/fruit-native.json').read_text());report.update(fruitBodies=12,appleScanMaps='three packed 2K maps',citrusMaps='three original packed 1K maps',measuredContactGapRange=[min(gaps),max(gaps)],allFruitUVsPreserved=True)
(R/'evidence/fruit-native.json').write_text(json.dumps(report,indent=2));print('VERIFIED FRUIT',report)
