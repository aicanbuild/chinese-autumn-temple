"""Install the refined pair while verifying all unrelated native geometry."""
import bpy,bmesh,hashlib,shutil,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'source/听秋寺院.blend';backup=path.with_name(path.stem+'-before-guardians.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path))
def eligible(o):return o.type=='MESH' and any(m and m.name in ['Carved pale limestone','Deep dark wood'] for m in o.data.materials)
def inside(p,x):return abs(p.x-x)<.70 and 1.44<p.y<3.01 and .80<p.z<2.51
def selected(vs):return any(all(inside(p,x) for p in vs) and any(p.z>.926 for p in vs) for x in [-3.6,3.6])
def signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.get('guardian_scan'):continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type!='MESH':continue
  if not eligible(o):
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
  else:
   for p in o.data.polygons:
    points=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
    if selected(points):continue
    h.update(str([tuple(v) for v in points]).encode())
 return count,h.hexdigest()
before=signature();removed=0
for o in list(bpy.data.objects):
 if o.get('guardian_scan'):bpy.data.objects.remove(o,do_unlink=True)
 elif eligible(o):
  bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if selected([o.matrix_world@v.co for v in f.verts])];removed+=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
assert signature()==before,'Unrelated architecture changed'
with bpy.data.libraries.load(str(R/'source/门前石狮.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Guardian |')]
for o in dst.objects:bpy.context.collection.objects.link(o)
assert len(dst.objects)==2
bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
statues=[o for o in bpy.data.objects if o.get('guardian_scan')];assert len(statues)==2
bounds=[]
for o in statues:
 ps=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(p[k] for p in ps) for k in range(3)];hi=[max(p[k] for p in ps) for k in range(3)];assert abs(lo[2]-.925)<.00001;assert abs(hi[2]-2.385)<.00001;assert hi[0]-lo[0]<1.36 and hi[1]-lo[1]<1.51;bounds.append([lo,hi]);assert len(o.data.uv_layers)==1
report={'sculptures':2,'preservedObjects':before[0],'unrelatedGeometryPreserved':True,'removedOldFaces':removed,'boundsZUp':bounds,'onOriginalPedestals':True};(R/'evidence/guardians-native.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
