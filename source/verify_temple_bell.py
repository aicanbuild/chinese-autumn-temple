"""Verify every legacy face outside the replacement bounds survives the native update."""
import bpy,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def selected(name,p):
 if 'gilded' in name.lower() or 'gold' in name.lower():return -9.7<p.x<-8.3 and 1.60<p.z<3.48 and 3.35<p.y<4.85
 if 'cedar' in name.lower():return -8.43<p.x<-8.17 and 2.22<p.z<2.48 and 3.08<p.y<4.73
 if 'deep dark wood' in name.lower():return -8.33<p.x<-8.27 and 2.32<p.z<3.62 and 3.25<p.y<4.65
 return False
def snapshot(path,filter_old):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={};removed=0
 for o in bpy.data.objects:
  if o.get('temple_bell'):continue
  h=hashlib.sha256();h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   faces=[]
   for p in o.data.polygons:
    if filter_old and selected(o.data.materials[p.material_index].name if o.data.materials else '',o.matrix_world@p.center):removed+=1;continue
    faces.append(tuple(sorted(tuple(round(c,6) for c in o.data.vertices[i].co) for i in p.vertices)))
   for face in sorted(faces):h.update(str(face).encode())
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.points:h.update(str(tuple(p.co)).encode());h.update(str(p.radius).encode())
  out[o.name]=h.hexdigest()
 return out,removed
before,removed=snapshot(R/'source/听秋寺院-before-temple-bell.blend',True);after,_=snapshot(R/'source/听秋寺院.blend',False)
assert before==after,[name for name in before if before[name]!=after.get(name)][:20]
p=R/'evidence/temple-bell-native.json';report=json.loads(p.read_text());report.update({'allLegacySurvivingFacesAndTransformsPreserved':True,'preservedObjects':len(before),'independentlyVerifiedRemovedFaces':removed});p.write_text(json.dumps(report,indent=2));print('BELL PRESERVATION VERIFIED',len(before),removed,flush=True)
