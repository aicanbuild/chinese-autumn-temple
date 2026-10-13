"""Geometry-only distance variants. Original native stones remain untouched."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';D=R/'source/stone-detail-assets';D.mkdir(exist_ok=True);source=R/'source/自然池岸.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));layout=json.loads((A/'pond-stones.json').read_text())
originals={}
for o in bpy.data.objects:
 if o.type=='MESH' and o.get('pond_zone'):
  index=int(o.name.rsplit(' ',1)[1]);kind=layout['placements'][index][0];originals.setdefault(kind,o.data)
assert len(originals)==8
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
material=bpy.data.materials.new('Pond stone | distant geometry');material.use_nodes=True

def tree(mesh):
 mesh.calc_loop_triangles();return BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
def error(mesh,target):
 mesh.calc_loop_triangles();maximum=0
 for tri in mesh.loop_triangles:
  a,b,c=[mesh.vertices[i].co for i in tri.vertices]
  for p in (a,b,c,(a+b+c)/3,(a+b)/2,(a+c)/2,(b+c)/2):maximum=max(maximum,target.find_nearest(p)[3])
 return maximum
report={'sourceSHA256':before,'fullAssetSHA256':hashlib.sha256((A/'pond-stones.glb').read_bytes()).hexdigest(),'sampledErrorLimit':.004,'runtimeErrorBudget':.008,'variants':[]}
for kind in range(6):
 full=originals[kind];fullTree=tree(full);accepted=None
 for ratio in [.20,.30,.45,.60,.75,.9,1.]:
  o=bpy.data.objects.new(f'PondStoneDistant_{kind}',full.copy());bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
  mod=o.modifiers.new('Subpixel stone relief','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
  e=max(error(full,tree(o.data)),error(o.data,fullTree))
  if e<=.004:accepted=o;break
  data=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(data)
 assert accepted,f'No acceptable distance geometry for stone {kind}'
 o=accepted;normals=[];color=o.data.color_attributes.get('Color')
 # Preserve smooth source shading and moss pigmentation at each new vertex.
 for v in o.data.vertices:
  p,_,triIndex,_=fullTree.find_nearest(v.co);tri=full.loop_triangles[triIndex];a,b,c=[full.vertices[i] for i in tri.vertices]
  weights=geometry.barycentric_transform(p,a.co,b.co,c.co,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
  normals.append((a.normal*weights.x+b.normal*weights.y+c.normal*weights.z).normalized())
  if color:
   values=[full.color_attributes['Color'].data[i].color for i in tri.vertices];color.data[v.index].color=tuple(sum(weights[k]*values[k][j] for k in range(3)) for j in range(4))
 o.data.normals_split_custom_set_from_vertices(normals)
 o.data.materials.clear();o.data.materials.append(material);o['sourceKind']=kind
 bm=bmesh.new();bm.from_mesh(o.data);assert all(len(edge.link_faces)==2 for edge in bm.edges);assert bm.calc_volume()>0;bm.free()
 report['variants'].append({'kind':kind,'fullTriangles':len(full.loop_triangles),'distantTriangles':len(o.data.polygons),'maximumSampledError':e,'ratio':ratio})
 o.select_set(False);print('STONE LOD',report['variants'][-1],flush=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(D/'pond-stones-distant.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False,export_extras=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/池岸远景.blend'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report['sourceUnchanged']=True;report['bytes']=(D/'pond-stones-distant.glb').stat().st_size
(D/'pond-stones-distant.json').write_text(json.dumps(report,indent=2));print('DONE',report,flush=True)
