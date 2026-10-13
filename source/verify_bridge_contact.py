"""Independent save/reopen and surface-interpolation audit of bridge visibility."""
import bpy,json,hashlib,array,struct,math,random,bisect
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];ATTR='_bridge_occlusion'
def signatures(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));cache={};result={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  m=o.data;key=m.as_pointer()
  if key not in cache:
   h=hashlib.sha256()
   for collection,prop,width,typ in [(m.vertices,'co',3,'f'),(m.loops,'vertex_index',1,'i'),(m.polygons,'loop_start',1,'i'),(m.polygons,'loop_total',1,'i'),(m.corner_normals,'vector',3,'f')]+[(uv.data,'uv',2,'f') for uv in m.uv_layers]:
    data=array.array(typ,[0])*(len(collection)*width);collection.foreach_get(prop,data);h.update(data.tobytes())
   cache[key]=h.digest()
  result[o.name]=(cache[key],tuple(x for row in o.matrix_world for x in row))
 return result
for name in ['精修木桥','听秋寺院']:
 old=signatures(R/f'source/{name}-before-bridge-contact.blend');new=signatures(R/f'source/{name}.blend');assert old==new,(name,'geometry, normals, UVs or transforms changed')
 parts=[o for o in bpy.data.objects if o.type=='MESH' and o.get('bridge_asset')];assert len(parts)==843
 for o in parts:
  values=o.data.attributes[ATTR].data;assert len(values)==len(o.data.loops);assert all(.2199999<=v.value<=1 for v in values)
 print('NATIVE VERIFIED',name,len(new),'meshes;',len(parts),'bridge parts',flush=True)
# Audit the actual exported triangles, including their interiors, against native BVH.
vs=[];fs=[]
for o in parts:
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in p.vertices] for p in o.data.polygons)
bvh=BVHTree.FromPolygons(vs,fs);golden=math.pi*(3-math.sqrt(5));N=1024;directions=[(math.sqrt((i+.5)/N)*math.cos(i*golden+.731),math.sqrt((i+.5)/N)*math.sin(i*golden+.731),math.sqrt(1-(i+.5)/N)) for i in range(N)]
def visibility(p,n):
 t=n.cross(Vector((0,0,1)) if abs(n.z)<.9 else Vector((0,1,0))).normalized();b=n.cross(t);blocked=0
 for x,y,z in directions:
  hit,_,_,dist=bvh.ray_cast(p+n*.0012,t*x+b*y+n*z,.22)
  if hit is not None:blocked+=(1-dist/.22)**1.5
 return max(.22,1-.86*blocked/N)
web=json.loads((R/'evidence/bridge-contact-samples.json').read_text());values=json.loads((R/'evidence/bridge-contact-values.json').read_text());probes=[];vertex_probes=[];rng=random.Random(947)
for batch,val in zip(web,values):
 p=[Vector(batch['positions'][i:i+3]) for i in range(0,len(batch['positions']),3)];n=[Vector(batch['normals'][i:i+3]) for i in range(0,len(batch['normals']),3)];ao=val['visibility'];ids=batch['indices'];tris=[ids[i:i+3] for i in range(0,len(ids),3)];weights=[];total=0
 for a,b,c in tris:total+=(p[b]-p[a]).cross(p[c]-p[a]).length*.5;weights.append(total)
 for j in range(96):
  a,b,c=tris[bisect.bisect_left(weights,(j+rng.random())/96*total)];u=math.sqrt(rng.random());v=rng.random();w=[1-u,u*(1-v),u*v];point=p[a]*w[0]+p[b]*w[1]+p[c]*w[2];normal=(n[a]*w[0]+n[b]*w[1]+n[c]*w[2]).normalized();interpolated=ao[a]*w[0]+ao[b]*w[1]+ao[c]*w[2];ref=visibility(point,normal);probes.append({'material':batch['material'],'position':list(point),'baked':interpolated,'reference':ref,'error':abs(ref-interpolated)})
 order=sorted(range(len(ao)),key=lambda i:ao[i])
 for j in range(24):
  i=order[round(j*(len(order)-1)/23)];ref=visibility(p[i],n[i]);vertex_probes.append({'material':batch['material'],'error':abs(ref-ao[i])})
report={'nativeGeometryNormalsUVsTransformsPreserved':True,'nativeParts':843,'raysPerReference':N,'vertexMeanError':sum(p['error'] for p in vertex_probes)/len(vertex_probes),'vertexMaxError':max(p['error'] for p in vertex_probes),'interiorMeanError':sum(p['error'] for p in probes)/len(probes),'interiorMaxError':max(p['error'] for p in probes),'interiorPerMaterial':{b['material']:sum(p['error'] for p in probes if p['material']==b['material'])/96 for b in web},'interiorProbes':probes}
(R/'evidence/bridge-contact-native.json').write_text(json.dumps(report,indent=2));print('BRIDGE CONTACT AUDIT',{k:v for k,v in report.items() if k!='interiorProbes'},flush=True)
assert report['vertexMeanError']<.04 and report['vertexMaxError']<.15
