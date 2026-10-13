"""Refine only where interpolated local visibility misses the actual surface."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/精修木桥.blend'));vs=[];fs=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in p.vertices] for p in o.data.polygons)
bvh=BVHTree.FromPolygons(vs,fs);golden=math.pi*(3-math.sqrt(5));dirs={n:[(math.sqrt((i+.5)/n)*math.cos(i*golden),math.sqrt((i+.5)/n)*math.sin(i*golden),math.sqrt(1-(i+.5)/n)) for i in range(n)] for n in [32,96]};cache={}
def ao(p,n,count=32):
 key=(count,)+tuple(round(x,6) for x in (*p,*n))
 if key in cache:return cache[key]
 t=n.cross(Vector((0,0,1)) if abs(n.z)<.9 else Vector((0,1,0))).normalized();b=n.cross(t);blocked=0
 for x,y,z in dirs[count]:
  hit,_,_,d=bvh.ray_cast(p+n*.0012,t*x+b*y+n*z,.22)
  if hit is not None:blocked+=(1-d/.22)**1.5
 value=max(.22,1-.86*blocked/count);cache[key]=value;return value
batches=json.loads((R/'evidence/bridge-contact-coarse.json').read_text());values=[];report=[]
for batch in batches:
 fields={k:[Vector(batch[k][i:i+w]) for i in range(0,len(batch[k]),w)] for k,w in [('positions',3),('normals',3),('localPositions',3),('localNormals',3),('uv',2)]};p=fields['positions'];n=fields['normals'];tris=[batch['indices'][i:i+3] for i in range(0,len(batch['indices']),3)];before=len(tris);levels=[]
 for level in range(3):
  splits={};tested={};vertex={}
  def value(i):
   if i not in vertex:vertex[i]=ao(p[i],n[i])
   return vertex[i]
  def midpoint(a,b):
   key=tuple(sorted((a,b)))
   if key not in splits:
    splits[key]=len(p)
    for field,data in fields.items():
     v=(data[a]+data[b])*.5
     if field in ['normals','localNormals']:v.normalize()
     data.append(v)
   return splits[key]
  for a,b,c in tris:
   # Tiny faces already resolve joinery; only test larger original surface patches.
   if (p[b]-p[a]).cross(p[c]-p[a]).length*.5<.00008:continue
   for x,y in [(a,b),(b,c),(c,a)]:
    key=tuple(sorted((x,y)))
    if key in tested:continue
    tested[key]=True
    if (p[x]-p[y]).length<.025:continue
    v=ao((p[x]+p[y])*.5,(n[x]+n[y]).normalized())
    if abs(v-(value(x)+value(y))*.5)>.055:midpoint(x,y)
   center=(p[a]+p[b]+p[c])/3;normal=(n[a]+n[b]+n[c]).normalized()
   if abs(ao(center,normal)-(value(a)+value(b)+value(c))/3)>.075:
    for x,y in [(a,b),(b,c),(c,a)]:
     if (p[x]-p[y]).length>.025:midpoint(x,y)
  if not splits:break
  out=[]
  for v in tris:
   m=[splits.get(tuple(sorted((v[k],v[(k+1)%3])))) for k in range(3)];count=sum(x is not None for x in m)
   if count==0:out.append(v)
   elif count==3:
    a,b,c=v;ab,bc,ca=m;out.extend([(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)])
   elif count==1:
    k=next(j for j in range(3) if m[j] is not None);a,b,c=v[k],v[(k+1)%3],v[(k+2)%3];out.extend([(a,m[k],c),(m[k],b,c)])
   else:
    k=next(j for j in range(3) if m[(j+2)%3] is not None and m[j] is not None);a,b,c=v[(k+2)%3],v[k],v[(k+1)%3];ab,bc=m[(k+2)%3],m[k];out.extend([(ab,b,bc),(a,ab,c),(ab,bc,c)])
  tris=out;levels.append(len(tris));print(batch['material'],'pass',level,'triangles',len(tris),'samples',len(cache),flush=True)
 for k,data in fields.items():batch[k]=[x for v in data for x in v]
 batch['indices']=[i for tri in tris for i in tri];visibility=[ao(p[i],n[i],96) for i in range(len(p))];values.append({'mesh':batch['mesh'],'primitive':batch['primitive'],'visibility':visibility});report.append({'material':batch['material'],'before':before,'after':len(tris),'vertices':len(p),'levels':levels})
 print('FINAL',report[-1],flush=True)
(R/'evidence/bridge-contact-samples.json').write_text(json.dumps(batches));(R/'evidence/bridge-contact-values.json').write_text(json.dumps(values));(R/'evidence/bridge-contact-refinement.json').write_text(json.dumps(report,indent=2));print('ADAPTIVE CONTACT COMPLETE',flush=True)
