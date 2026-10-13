import bpy,bmesh,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];meta=json.loads((R/'source/stone-detail-assets/pond-stones-distant.json').read_text())
assert hashlib.sha256((R/'source/自然池岸.blend').read_bytes()).hexdigest()==meta['sourceSHA256']
assert hashlib.sha256((R/'dist/assets/pond-stones.glb').read_bytes()).hexdigest()==meta['fullAssetSHA256']
bpy.ops.wm.open_mainfile(filepath=str(R/'source/池岸远景.blend'));parts=[o for o in bpy.data.objects if o.type=='MESH'];assert len(parts)==6
result=[]
for o in parts:
 kind=o['sourceKind'];r=meta['variants'][kind];o.data.calc_loop_triangles();assert len(o.data.loop_triangles)==r['distantTriangles'];assert o.data.has_custom_normals
 bm=bmesh.new();bm.from_mesh(o.data);assert all(len(e.link_faces)==2 for e in bm.edges);volume=bm.calc_volume();assert volume>0;bm.free()
 assert o.data.color_attributes['Color'].domain=='POINT';assert len(o.data.color_attributes['Color'].data)==len(o.data.vertices)
 result.append({'kind':kind,'triangles':len(o.data.loop_triangles),'closed':True,'volume':volume,'sourceNormals':True})
(R/'evidence/pond-stone-detail-native.json').write_text(json.dumps({'originalNativeAndGLBUnchanged':True,'parts':result,'build':meta},indent=2));print('VERIFIED',result,flush=True)
