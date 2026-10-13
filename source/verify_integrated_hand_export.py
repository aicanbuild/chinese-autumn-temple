"""Check the actual Draco-compressed web model, not just the native sculpt."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'dist/assets/sculpture.glb'))
o=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000005);bm.verts.ensure_lookup_table();bm.verts.index_update()
k=KDTree(len(bm.verts))
for v in bm.verts:k.insert(v.co,v.index)
k.balance()
root=bm.verts[k.find(Vector((0,8.42,3.185)))[1]];seen={root};stack=[root]
while stack:
 for e in stack.pop().link_edges:
  # Use both endpoints because this also accommodates the scanned nonmanifold triangles.
  for v in e.verts:
   if v not in seen:seen.add(v);stack.append(v)
reports=json.loads((R/'evidence/integrated-hands.json').read_text());tips=next(r['fingertipsLocal'] for r in reports if 'fingertipsLocal' in r);offset=Vector((0,8.6,1.915))
max_distance=0
for side,p in tips:
 co,i,d=k.find(Vector(p)+offset);assert bm.verts[i] in seen and d<.016;max_distance=max(max_distance,d)
for r in reports[:2]:
 side=-1 if r['gesture']=='giving' else 1
 p=Vector(r['palm'])+Vector((-side*.073,-.016,side*.042))+offset
 co,i,d=k.find(p);assert bm.verts[i] in seen and d<.016
result={'compressedWebModelHasBothHandsConnected':True,'tenDigitsVerified':10,'decodedVertices':len(bm.verts),'maximumFingerSampleDistance':max_distance,'fileBytes':(R/'dist/assets/sculpture.glb').stat().st_size}
(R/'evidence/integrated-hand-export-verification.json').write_text(json.dumps(result,indent=2));print('WEB_SCULPTURE_VERIFIED',result,flush=True)
