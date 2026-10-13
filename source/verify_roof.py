"""Verify actual saved tile shells, using coordinate-welded topology per kiln tint."""
import bpy,json,collections,math,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/精修筒瓦.blend'))
o=next(o for o in bpy.data.objects if o.get('roof_shell_revision'));mesh=o.data
rgba=np.empty(len(mesh.loops)*4,dtype=np.float32);mesh.color_attributes['Kiln tint'].data.foreach_get('color',rgba);rgba=rgba.reshape(-1,4)
assert np.isfinite(rgba).all() and rgba[:,:3].min()>=.9499 and rgba[:,:3].max()<=1.0001
assert np.max(np.abs(rgba[:,0]-rgba[:,1]))<1e-6 and np.max(np.abs(rgba[:,1]-rgba[:,2]))<1e-6
assert np.all(rgba[:,3]==1)
tex=np.empty(len(mesh.loops)*2,dtype=np.float32);mesh.uv_layers['UVMap'].data.foreach_get('uv',tex);assert np.isfinite(tex).all()
groups=[];i=0
while i<len(mesh.polygons):
 if not mesh.polygons[i].use_smooth:i+=1;continue
 groups.append([mesh.polygons[k] for k in range(i,i+76)]);i+=76
assert len(groups)==2864,len(groups)
minimum=1;normals=0
for polygons in groups:
 assert len(polygons)==76
 edges=collections.Counter();orientation=collections.Counter()
 for p in polygons:
  points=[tuple(round(v,6) for v in mesh.vertices[k].co) for k in p.vertices]
  for a,b in zip(points,points[1:]+points[:1]):
   pair=tuple(sorted((a,b)));edges[pair]+=1;orientation[pair]+=1 if a<b else -1
 assert all(n==2 for n in edges.values()),'open tile shell'
 assert all(n==0 for n in orientation.values()),'inconsistent winding'
 assert all(p.use_smooth and p.normal.z>0 for p in polygons[:24])
 assert all(p.use_smooth and p.normal.z<0 for p in polygons[24:48])
 top=mesh.vertices[polygons[0].vertices[0]].co;bottom=mesh.vertices[polygons[24].vertices[-1]].co
 # The bottom face is reversed; its last corner corresponds to the first top corner.
 gap=abs(top.z-bottom.z);assert abs(gap-.008)<1e-5,gap;minimum=min(minimum,gap)
 normals+=sum(p.use_smooth for p in polygons)
assert normals==2864*48
for m in mesh.materials:
 maps=[n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(maps)==3 and all(i.packed_file for i in maps)
p=R/'evidence/roof-shells-native.json';r=json.loads(p.read_text());r.update({'verifiedClosedShells':len(groups),'minimumMeasuredThickness':minimum,'consistentOutwardWinding':True,'smoothSurfaceFaces':normals,'glazeMapsPacked':True,'allKilnColorsNeutralAndBounded':True,'finiteUVs':True});p.write_text(json.dumps(r,indent=2));print(r,flush=True)
