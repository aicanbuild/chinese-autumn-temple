import bpy,bmesh,sys,json,shutil,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from altar_tabletop import build_altar_tabletop,is_altar_top,inside_old_top,REGION
prototype=R/'source/庄严内殿.blend';temple=R/'source/听秋寺院.blend'
def eligible(o):return o.type=='MESH' and any(m and m.name=='Satin gilded bronze' for m in o.data.materials)
def signature():
 out={};removed=0
 for o in bpy.data.objects:
  if is_altar_top(o):continue
  h=hashlib.sha256();h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   faces=[]
   for p in o.data.polygons:
    if eligible(o) and all(inside_old_top(o.matrix_world@o.data.vertices[i].co) for i in p.vertices):removed+=1;continue
    faces.append(tuple(sorted(tuple(round(c,6) for c in o.data.vertices[i].co) for i in p.vertices)))
   for face in sorted(faces):h.update(str(face).encode())
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.points:h.update(str(tuple(p.co)).encode())
  out[o.name]=h.hexdigest()
 return out,removed
for f in [prototype,temple]:
 backup=f.with_name(f.stem+'-before-altar-tabletop.blend')
 if not backup.exists():shutil.copy2(f,backup)
bpy.ops.wm.open_mainfile(filepath=str(prototype));before,_=signature()
for o in list(bpy.data.objects):
 if is_altar_top(o):bpy.data.objects.remove(o,do_unlink=True)
parts,details=build_altar_tabletop();bpy.context.view_layer.update();assert signature()[0]==before
component_count=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(prototype));bpy.ops.wm.open_mainfile(filepath=str(prototype));assert signature()[0]==before
names=[o.name for o in bpy.data.objects if is_altar_top(o)]
bpy.ops.wm.open_mainfile(filepath=str(temple));before,expected=signature();assert expected in (0,6),expected
removed=0
for o in list(bpy.data.objects):
 if is_altar_top(o):bpy.data.objects.remove(o,do_unlink=True)
 elif eligible(o):
  bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if all(inside_old_top(o.matrix_world@v.co) for v in f.verts)];removed+=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
assert removed==expected
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=names
for o in dst.objects:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update();assert signature()[0]==before
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple));bpy.ops.wm.open_mainfile(filepath=str(temple));assert signature()[0]==before
parts=[o for o in bpy.data.objects if is_altar_top(o)];assert len(parts)==8
for o in parts:
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;assert all(f.calc_area()>1e-12 for f in bm.faces),o.name;bm.free()
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
# Each existing cup foot continues to sit on the inset panel at the original height.
deps=bpy.context.evaluated_depsgraph_get();panel=next(o for o in parts if 'inset lacquer panel' in o.name)
for i in range(7):
 ok,p,n,index=panel.ray_cast(Vector(((i-3)*.19,7.99,2.0)),Vector((0,0,-1)))
 assert ok and abs(p.z-1.895)<1e-6,(i,p)
initial=R/'evidence/altar-tabletop-initial-native.json'
initial_removed=json.loads(initial.read_text())['removedLegacyFaces'] if initial.exists() else removed
report={'legacyFacesReplaced':initial_removed,'editableParts':8,'preservedOtherObjects':len(before),'removedLegacyFaces':removed,'survivingFacesAndTransformsPreserved':True,'closedPositiveVolumes':True,'sevenCupContactsVerified':True};(R/'evidence/altar-tabletop-native.json').write_text(json.dumps(report,indent=2));print('TABLETOP NATIVE',report,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(prototype));parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')]
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
materials=set(o.data.materials[0] for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials)
for m in materials:
 group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==m];bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=m.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/sanctuary.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
p=R/'dist/assets/sanctuary.json';meta=json.loads(p.read_text());meta['components']=component_count;meta['altarTabletop']=details
if REGION not in meta['removeRegionsNative']:meta['removeRegionsNative'].append(REGION)
p.write_text(json.dumps(meta,indent=2));print('TABLETOP EXPORTED',component_count,flush=True)
