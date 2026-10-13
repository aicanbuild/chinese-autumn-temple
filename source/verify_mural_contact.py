"""Independent hemisphere visibility audit for four inward-facing murals."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.wm.open_mainfile(filepath=str(R/'source/壁画嵌框接触光照.blend'))
scene=bpy.context.scene;panels=json.loads(scene['mural_panels_json']);distance=scene['contact_distance_m'];epsilon=scene['receiver_epsilon']
o=scene.objects['Mural contact occluders'];tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
image=bpy.data.images.load(str(A/'mural-contact-ao.png'),check_existing=False);image.colorspace_settings.name='Non-Color';pixels=list(image.pixels);width,height=image.size
assert all(p.normal.dot(Vector(panel['normal']))>.999 for p,panel in zip(scene.objects['Mural contact receivers'].data.polygons,panels))
def texel(x,y):return pixels[(max(0,min(height-1,y))*width+max(0,min(width-1,x)))*4]
def sample(u,v):
 x,y=u*width-.5,v*height-.5;i,j=math.floor(x),math.floor(y);a,b=x-i,y-j
 return (texel(i,j)*(1-a)+texel(i+1,j)*a)*(1-b)+(texel(i,j+1)*(1-a)+texel(i+1,j+1)*a)*b
golden=math.pi*(3-math.sqrt(5));rays=4096;results=[]
directions=[(math.sqrt((i+.5)/rays)*math.cos(i*golden),math.sqrt((i+.5)/rays)*math.sin(i*golden),math.sqrt(1-(i+.5)/rays)) for i in range(rays)]
for k,p in enumerate(panels):
 c,u,v,n=map(Vector,(p['center'],p['u'],p['v'],p['normal']));w,h=p['size'];a,b,d,e=p['atlas']
 # Centre, central field and several measured distances inward from each edge.
 probes=[(.5,.5),(.25,.25),(.75,.75),(.25,.75),(.75,.25)]
 if k<2:probes.append((.704 if k==0 else .296,.962))
 for gap in [.003,.015,.04,.08,.14]:probes.extend([(gap/w,.5),(1-gap/w,.5),(.5,gap/h),(.5,1-gap/h)])
 for s,t in probes:
  point=c+u*(s-.5)*w+v*(t-.5)*h+n*(epsilon+.0001);hits=0
  for x,y,z in directions:hits+=tree.ray_cast(point,u*x+v*y+n*z,distance)[0] is not None
  reference=1-hits/rays;baked=sample(a+s*(d-a),b+t*(e-b));results.append({'panel':k,'st':[s,t],'point':list(point),'reference':reference,'baked':baked,'error':abs(reference-baked)})
  if t==.962:
   hit=tree.ray_cast(point,n,distance);index=hit[2];offset=0;owner=None
   for entry in json.loads((R/'evidence/mural-contact-bake.json').read_text())['occluders']:
    if index is not None and offset<=index<offset+entry['faces']:owner=entry['name'];break
    offset+=entry['faces']
   print('MURAL LOCAL CONTACT',{'panel':k,'object':owner,'hit':list(hit[0]) if hit[0] else None},flush=True)
mean=sum(p['error'] for p in results)/len(results);maximum=max(p['error'] for p in results)
report={'probes':results,'raysPerProbe':rays,'meanAbsoluteError':mean,'maxAbsoluteError':maximum,'minVisibility':min(p['baked'] for p in results),'maxVisibility':max(p['baked'] for p in results),'normalsVerified':True}
(R/'evidence/mural-contact-ray-audit.json').write_text(json.dumps(report,indent=2));print('MURAL CONTACT AUDIT',{k:v for k,v in report.items() if k!='probes'},flush=True)
assert mean<.025 and maximum<.09,(mean,maximum)
assert report['minVisibility']<.9 and report['maxVisibility']>.97
bake=json.loads((R/'evidence/mural-contact-bake.json').read_text())
assert not any(o['name'].startswith('Specimen leaf canopy') for o in bake['occluders'])
assert hashlib.sha256((R/'source'/bake['source']).read_bytes()).hexdigest()==bake['sourceSha256']
assert len(scene.objects)==2 and len(scene.objects['Mural contact receivers'].data.polygons)==4
assert any(i.packed_file and tuple(i.size)==(2048,1024) for i in bpy.data.images)
assert all(p['baked']>.5 for p in results if p['st'][1]==.962)
inputs=['temple.glb','sanctuary.glb','sanctuary.json','door-backs.glb','aureole-relief.glb','caisson-vines.glb']
metadata={'width':width,'height':height,'distance':distance,'epsilon':epsilon,'panels':panels,'inputs':{n:hashlib.sha256((A/n).read_bytes()).hexdigest() for n in inputs},'textureSha256':hashlib.sha256((A/'mural-contact-ao.png').read_bytes()).hexdigest()}
(A/'mural-contact-ao.json').write_text(json.dumps(metadata,indent=2))
