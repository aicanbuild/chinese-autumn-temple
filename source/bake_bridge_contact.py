"""Local indirect visibility for bridge joinery; original geometry is never exported again."""
import bpy,math,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];ATTR='_bridge_occlusion';N=96;DIST=.22;BIAS=.0012
src=R/'source/精修木桥.blend';main=R/'source/听秋寺院.blend'
def signature(o):
 m=o.data;h=hashlib.sha256()
 for data in [[tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons],[tuple(n.vector) for n in m.corner_normals],[[tuple(x.uv) for x in uv.data] for uv in m.uv_layers],list(o.matrix_world)]:h.update(repr(data).encode())
 return h.hexdigest()
for path in [src,main]:
 backup=path.with_name(path.stem+'-before-bridge-contact.blend')
 if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(src));objects=[o for o in bpy.data.objects if o.type=='MESH'];assert len(objects)==843
before={o.name:signature(o) for o in objects};vs=[];fs=[]
for o in objects:
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in p.vertices] for p in o.data.polygons)
bvh=BVHTree.FromPolygons(vs,fs);golden=math.pi*(3-math.sqrt(5))
def rays(count,phase=0):
 return [(math.sqrt((i+.5)/count)*math.cos(i*golden+phase),math.sqrt((i+.5)/count)*math.sin(i*golden+phase),math.sqrt(1-(i+.5)/count)) for i in range(count)]
hemisphere=rays(N);cache={}
def visibility(p,n,directions=hemisphere):
 t=n.cross(Vector((0,0,1)) if abs(n.z)<.9 else Vector((0,1,0))).normalized();b=n.cross(t);blocked=0
 for x,y,z in directions:
  hit,_,_,distance=bvh.ray_cast(p+n*BIAS,t*x+b*y+n*z,DIST)
  if hit is not None:blocked+=(1-distance/DIST)**1.5
 return max(.22,1-.86*blocked/len(directions))
def sample(p,n):
 k=tuple(round(v,6) for v in (*p,*n))
 if k not in cache:cache[k]=visibility(p,n)
 return cache[k]
results={};parts=[]
for index,o in enumerate(objects):
 me=o.data;nm=o.matrix_world.to_3x3().inverted().transposed();attr=me.attributes.get(ATTR) or me.attributes.new(ATTR,'FLOAT','CORNER');values=[]
 for loop in me.loops:
  p=o.matrix_world@me.vertices[loop.vertex_index].co;n=(nm@me.corner_normals[loop.index].vector).normalized();values.append(sample(p,n))
 attr.data.foreach_set('value',values);assert signature(o)==before[o.name];results[signature(o)]=values;parts.append({'name':o.name,'samples':len(values),'min':min(values),'mean':sum(values)/len(values)})
 if index%100==0:print('NATIVE',index,'/',len(objects),'unique samples',len(cache),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(src))
web=json.loads((R/'evidence/bridge-contact-samples.json').read_text());webstats=[]
for batch in web:
 values=[]
 for i in range(0,len(batch['positions']),3):values.append(sample(Vector(batch['positions'][i:i+3]),Vector(batch['normals'][i:i+3])))
 batch['visibility']=values;webstats.append({'material':batch['material'],'vertices':len(values),'min':min(values),'mean':sum(values)/len(values)});print('WEB',webstats[-1],flush=True)
# Independent angular sampling at stratified dark/open points across all materials.
reference=rays(1024,.731);probes=[]
for batch in web:
 order=sorted(range(len(batch['visibility'])),key=lambda i:batch['visibility'][i])
 for j in range(24):
  i=order[round(j*(len(order)-1)/23)];p=Vector(batch['positions'][i*3:i*3+3]);n=Vector(batch['normals'][i*3:i*3+3]);v=visibility(p,n,reference);probes.append({'material':batch['material'],'position':list(p),'baked':batch['visibility'][i],'reference':v,'error':abs(v-batch['visibility'][i])})
mean=sum(p['error'] for p in probes)/len(probes);maximum=max(p['error'] for p in probes);assert mean<.04 and maximum<.15,(mean,maximum)
(R/'evidence/bridge-contact-values.json').write_text(json.dumps([{'mesh':b['mesh'],'primitive':b['primitive'],'visibility':b['visibility']} for b in web]))
bpy.ops.wm.open_mainfile(filepath=str(main));all_before={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'};updated=0
for o in bpy.data.objects:
 if o.type!='MESH' or not o.get('bridge_asset'):continue
 key=signature(o);assert key in results,('standalone/main mismatch',o.name);a=o.data.attributes.get(ATTR) or o.data.attributes.new(ATTR,'FLOAT','CORNER');a.data.foreach_set('value',results[key]);updated+=1
assert updated==843;assert all_before=={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.save_as_mainfile(filepath=str(main));bpy.ops.wm.open_mainfile(filepath=str(main))
assert all_before=={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
for o in bpy.data.objects:
 if o.type=='MESH' and o.get('bridge_asset'):
  values=[v.value for v in o.data.attributes[ATTR].data];assert len(values)==len(o.data.loops);assert all(.2199999<=v<=1 for v in values)
report={'rays':N,'radiusMeters':DIST,'normalOffsetMeters':BIAS,'uniqueSamples':len(cache),'parts':parts,'web':webstats,'preservedSceneMeshes':len(all_before),'nativeBridgeParts':updated,'independentAudit':{'rays':1024,'meanError':mean,'maxError':maximum,'probes':probes}}
(R/'evidence/bridge-contact-native.json').write_text(json.dumps(report,indent=2));print('BRIDGE CONTACT COMPLETE',{'uniqueSamples':len(cache),'meanAuditError':mean,'maxAuditError':maximum},flush=True)
