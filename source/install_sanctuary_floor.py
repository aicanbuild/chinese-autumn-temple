"""Replace only the old 43 plank floor; retain other cedar and all furnishings."""
import bpy,bmesh,hashlib,shutil,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'source/听秋寺院.blend';backup=path.with_name(path.stem+'-before-stone-floor.blend')
if not backup.exists():shutil.copy2(path,backup)
def eligible(o):return o.type=='MESH' and any(m and m.name=='Polished ebony cedar' for m in o.data.materials)
def inside(p):return -6.14<p.x<6.14 and 3.46<p.y<10.74 and .90<p.z<1.081 and min(abs(p.y-3.475),abs(p.y-10.725))<.012
def signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.get('sanctuary_floor'):continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type!='MESH':continue
  if not eligible(o):
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
  else:
   for p in o.data.polygons:
    points=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
    if all(inside(v) for v in points):continue
    h.update(str([tuple(v) for v in points]).encode())
 return count,h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(backup));baseline=signature();expected=sum(sum(all(inside(o.matrix_world@o.data.vertices[i].co) for i in p.vertices) for p in o.data.polygons) for o in bpy.data.objects if eligible(o));assert expected==43*6,expected
bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==baseline
for o in list(bpy.data.objects):
 if o.get('sanctuary_floor'):bpy.data.objects.remove(o,do_unlink=True)
 elif eligible(o):
  bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if all(inside(o.matrix_world@v.co) for v in f.verts)];bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
with bpy.data.libraries.load(str(R/'source/主殿石铺地.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==baseline
parts=[o for o in bpy.data.objects if o.get('sanctuary_floor')];assert len(parts)==157
for o in parts:
 vs=[o.matrix_world@v.co for v in o.data.vertices];hi=max(v.z for v in vs);assert abs(hi-(1.062 if o['floor_part']=='Joint bed' else 1.07))<.000001
 assert all(-6.128<p.x<6.118 and 3.474<p.y<10.726 for p in vs)
 if o['floor_part']!='Joint bed':
  assert o.data.uv_layers.active
  # Material variation must be neutral, finite and opaque.
  assert all(.964<c.color[0]<=1 and abs(c.color[0]-c.color[1])<.00001 and c.color[3]==1 for c in o.data.color_attributes[0].data)
report={'editableParts':len(parts),'replacedPlanks':43,'removedOriginalFaces':expected,'preservedObjects':baseline[0],'unrelatedGeometryPreserved':True,'floorTopUnchanged':1.07,'recessedJointDepth':.008};(R/'evidence/sanctuary-floor-native.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
