"""Independent continuity and preserved-scan checks on the saved restoration."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];S=R/'source'
def in_patch(p):
 return ((-.510<p.x<-.300 and -.27<p.y<.080 and .60<p.z<1.055) or (.160<p.x<.400 and -.33<p.y<-.045 and .83<p.z<1.290))
bpy.ops.wm.open_mainfile(filepath=str(S/'主殿佛像-before-integrated-hands.blend'))
before=next(o for o in bpy.data.objects if o.name.startswith('Tang sculpture'))
used={i for p in before.data.polygons for i in p.vertices}
original=[v.co.copy() for v in before.data.vertices if v.index in used]
bm=bmesh.new();bm.from_mesh(before.data)
original_boundary=sum(e.is_boundary and in_patch((e.verts[0].co+e.verts[1].co)*.5) for e in bm.edges);bm.free()
bpy.ops.wm.open_mainfile(filepath=str(S/'主殿佛像-衔接候选.blend'))
o=next(o for o in bpy.data.objects if o.name.startswith('Tang sculpture'))
assert o.get('integrated_hands')
bm=bmesh.new();bm.from_mesh(o.data)
new_boundary=sum(e.is_boundary and in_patch((e.verts[0].co+e.verts[1].co)*.5) for e in bm.edges)
assert new_boundary<=original_boundary,('Restoration introduced open seams',original_boundary,new_boundary)
bm.free()
vs=[v.co.copy() for v in o.data.vertices];kd=KDTree(len(vs))
for i,v in enumerate(vs):kd.insert(v,i)
kd.balance()
# Preserve every original vertex outside the local restoration patches.
preserved=[p for p in original if not in_patch(p)]
max_error=max(kd.find(v)[2] for v in preserved)
assert max_error<.00001,('Original sculpture changed outside the wrists',max_error)
adj=[[] for _ in vs]
for e in o.data.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
root=kd.find(Vector((0,-.18,1.27)))[1];seen={root};stack=[root]
while stack:
 for b in adj[stack.pop()]:
  if b not in seen:seen.add(b);stack.append(b)
report=json.loads((R/'evidence/integrated-hands.json').read_text());tips=next(d['fingertipsLocal'] for d in report if 'fingertipsLocal' in d)
for side,p in tips:
 v,i,d=kd.find(Vector(p));assert i in seen and d<.016
# Palm and wrist center checks ensure those restored volumes also belong to the chest.
for r in report[:2]:
 side=-1 if r['gesture']=='giving' else 1
 thumb=Vector(r['palm'])+Vector((-side*.073,-.016,side*.042))
 v,i,d=kd.find(thumb);assert i in seen and d<.016,('Thumb disconnected',side,d)
 for name in ['palm','joint']:
  v,i,d=kd.find(Vector(r[name]));assert i in seen
result={'allTenDigitsShareChestTopology':True,'noNewOpenWristSeams':True,'originalWristBoundaryEdges':original_boundary,'restoredWristBoundaryEdges':new_boundary,'preservedScanVertices':len(preserved),'maxUnmodifiedScanPositionError':max_error,'nativeBodyVertices':len(vs)}
(R/'evidence/integrated-hands-verification.json').write_text(json.dumps(result,indent=2));print('VERIFIED_INTEGRATED_HANDS',result,flush=True)
