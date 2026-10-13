"""Bake local sky visibility into a custom corner attribute; preserve original geometry."""
import bpy,math,json,shutil,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];ATTR='_lantern_occlusion';N=96;DIST=.32
src=R/'source/雕刻石灯笼.blend'
for path in [src,R/'source/听秋寺院.blend']:
 backup=path.with_name(path.stem+'-before-lantern-contact.blend')
 if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(src));objects=[o for o in bpy.data.objects if o.type=='MESH'];vs=[];fs=[]
def fingerprint(me):
 return hashlib.sha256(repr(([tuple(v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])).encode()).hexdigest()
for o in objects:
 offset=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([offset+i for i in p.vertices] for p in o.data.polygons)
bvh=BVHTree.FromPolygons(vs,fs);rays=[]
for i in range(N):
 u=(i+.5)/N;a=i*math.pi*(3-math.sqrt(5));rays.append((math.sqrt(u)*math.cos(a),math.sqrt(u)*math.sin(a),math.sqrt(1-u)))
results={};cache={};summary=[]
for o in objects:
 me=o.data;key=fingerprint(me);attr=me.attributes.get(ATTR) or me.attributes.new(ATTR,'FLOAT','CORNER');values=[];nm=o.matrix_world.to_3x3().inverted().transposed()
 for loop in me.loops:
  p=o.matrix_world@me.vertices[loop.vertex_index].co;n=(nm@me.corner_normals[loop.index].vector).normalized();k=tuple(round(v,6) for v in (*p,*n))
  if k not in cache:
   t=n.cross(Vector((0,0,1)) if abs(n.z)<.9 else Vector((0,1,0))).normalized();b=n.cross(t);blocked=0
   for x,y,z in rays:
    hit,_,_,distance=bvh.ray_cast(p+n*.0012,t*x+b*y+n*z,DIST)
    if hit is not None:blocked+=(1-distance/DIST)**1.5
   cache[k]=max(.22,1-.86*blocked/N)
  attr.data[loop.index].value=cache[k];values.append(cache[k])
 assert fingerprint(me)==key;results[key]=values;summary.append({'part':o.name,'samples':len(values),'min':min(values),'mean':sum(values)/len(values)})
 print('BAKED',o.name,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Join by existing materials without regenerating any surface.
for mat in list(bpy.data.materials):
 selected=[o for o in list(bpy.data.objects) if o.type=='MESH' and mat in o.data.materials[:]]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=mat.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/stone-lantern.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_attributes=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Preserve original packed PBR images rather than expanded PNG roughness.
import sys
sys.path.insert(0,str(R/'source'))
from granite_finish import refresh_glb
refresh_glb(R/'dist/assets/stone-lantern.glb')
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'));before={o.name:fingerprint(o.data) for o in bpy.data.objects if o.type=='MESH'};updated=set();count=0
for o in bpy.data.objects:
 if o.type!='MESH' or not o.get('stone_lantern'):continue
 count+=1;me=o.data
 if me.name in updated:continue
 key=fingerprint(me);assert key in results,(o.name,key);a=me.attributes.get(ATTR) or me.attributes.new(ATTR,'FLOAT','CORNER');a.data.foreach_set('value',results[key]);updated.add(me.name)
assert count==736 and len(updated)==46,(count,len(updated))
assert before=={o.name:fingerprint(o.data) for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
report={'rays':N,'radiusMeters':DIST,'uniqueSamples':len(cache),'parts':summary,'preservedMeshes':len(before),'instances':count,'uniqueNativeMeshes':len(updated)}
(R/'evidence/lantern-contact-native.json').write_text(json.dumps(report,indent=2));print('LANTERN CONTACT COMPLETE',len(cache),flush=True)
