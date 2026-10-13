"""Remove only two measured legacy fasteners and preserve the rest of the temple."""
import bpy,bmesh,json,hashlib,shutil,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from mural_cleanup import MURAL_INTRUSION_REGIONS as regions
path=R/'source/听秋寺院.blend';backup=path.with_name('听秋寺院-before-mural-fasteners.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path))
def inside(p,r):return r[0]<p.x<r[1] and r[2]<p.y<r[3] and r[4]<p.z<r[5]
def signatures():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode());count+=1
  if o.type!='MESH':continue
  for face in o.data.polygons:
   points=[o.matrix_world@o.data.vertices[i].co for i in face.vertices]
   if o.name=='Satin gilded bronze' and any(all(inside(p,r) for p in points) for r in regions):continue
   h.update(str([tuple(p) for p in points]).encode())
 return count,h.hexdigest()
before=signatures();o=bpy.data.objects['Satin gilded bronze'];bm=bmesh.new();bm.from_mesh(o.data)
faces=[f for f in bm.faces if any(all(inside(o.matrix_world@v.co,r) for v in f.verts) for r in regions)]
assert len(faces)==128,len(faces)
vertices={v for f in faces for v in f.verts};assert len(vertices)==130
bmesh.ops.delete(bm,geom=list(vertices),context='VERTS');bm.to_mesh(o.data);bm.free()
assert signatures()==before
bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signatures()==before
for o in bpy.data.objects:
 if o.name=='Satin gilded bronze':assert not any(any(inside(o.matrix_world@v.co,r) for r in regions) for v in o.data.vertices)
meta_path=R/'dist/assets/sanctuary.json';meta=json.loads(meta_path.read_text())
for r in regions:
 if r not in meta['removeRegionsNative']:meta['removeRegionsNative'].append(r)
meta['removedMuralFasteners']=2;meta_path.write_text(json.dumps(meta,indent=2))
report={'removedFasteners':2,'removedVertices':130,'removedFaces':128,'objects':before[0],'otherFacesAndTransformsUnchanged':True,'source':str(path),'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'regions':regions}
(R/'evidence/mural-fasteners-native.json').write_text(json.dumps(report,indent=2));print('MURAL FASTENERS REMOVED',report,flush=True)
