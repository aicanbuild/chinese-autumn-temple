"""Independently ray-test the saved contact atlas against its native geometry."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.wm.open_mainfile(filepath=str(R/'source/池底接触光照.blend'));bpy.context.view_layer.update()
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];bed=next(o for o in objects if o.name=='Riverbed sediment');stones=[o for o in objects if o.get('pond_zone')=='bed']
layout=json.loads((A/'pond-stones.json').read_text())['placements']
assert len(stones)==sum(p[8]=='bed' for p in layout)
for o in stones:
 matches=[p for p in layout if p[-1]=='bed' and abs(p[1]-o.location.x)<1e-5 and abs(p[2]-o.location.y)<1e-5]
 assert len(matches)==1
 p=matches[0];assert abs(p[3]-o.location.z)<1e-5;assert max(abs(p[4+i]-o.scale[i]) for i in range(3))<1e-5
vertices=[];faces=[]
for o in objects:
 offset=len(vertices);vertices.extend([o.matrix_world@v.co for v in o.data.vertices]);faces.extend([tuple(offset+i for i in f.vertices) for f in o.data.polygons])
all_tree=BVHTree.FromPolygons(vertices,faces)
bed_tree=BVHTree.FromPolygons([bed.matrix_world@v.co for v in bed.data.vertices],[tuple(f.vertices) for f in bed.data.polygons])
image=bpy.data.images.load(str(A/'pond-contact-ao.png'),check_existing=False);image.colorspace_settings.name='Non-Color';pixels=list(image.pixels);width,height=image.size
def sample(x,y):
 u=(x+11.5)/23;v=(y+12.7)/13.8;fx=u*width-.5;fy=v*height-.5;i=math.floor(fx);j=math.floor(fy);tx=fx-i;ty=fy-j
 def read(a,b):return pixels[(max(0,min(height-1,b))*width+max(0,min(width-1,a)))*4]
 return (read(i,j)*(1-tx)+read(i+1,j)*tx)*(1-ty)+(read(i,j+1)*(1-tx)+read(i+1,j+1)*tx)*ty
probes=[]
targets=sorted(stones,key=lambda o:o.scale.x*o.scale.y,reverse=True)[:5]
small=sorted([o for o in stones if int(o.name.rsplit(' ',1)[1])>=257],key=lambda o:o.scale.x*o.scale.y)
if small:targets.extend([small[0],small[len(small)//2],small[-1]])
for o in targets:
 probes.append((o.location.x,o.location.y,'covered'))
 for a in range(8):
  p=o.matrix_world@Vector((1.18*math.cos(a*math.tau/8),1.18*math.sin(a*math.tau/8),0));probes.append((p.x,p.y,'rim'))
for x,y in [(-9,-6),(-5,-9),(4,-8),(8,-5),(2,-3),(-3,-2),(0,-5),(0,-8)]:probes.append((x,y,'open'))
results=[];count=2048;golden=math.pi*(3-math.sqrt(5))
for x,y,kind in probes:
 hit,normal,_,_=bed_tree.ray_cast(Vector((x,y,0)),Vector((0,0,-1)),3);assert hit is not None
 tangent=normal.cross(Vector((0,1,0))).normalized();bitangent=normal.cross(tangent);origin=hit+normal*.0002;occluded=0
 for i in range(count):
  r=math.sqrt((i+.5)/count);a=i*golden;direction=tangent*(r*math.cos(a))+bitangent*(r*math.sin(a))+normal*math.sqrt(1-r*r)
  target,_,_,_=all_tree.ray_cast(origin,direction,.45);occluded+=target is not None
 reference=1-occluded/count;baked=sample(x,y);results.append({'point':[x,y,hit.z],'kind':kind,'reference':reference,'baked':baked,'error':abs(reference-baked)})
mean=sum(p['error'] for p in results)/len(results);maximum=max(p['error'] for p in results)
report={'probes':results,'meanAbsoluteError':mean,'maxAbsoluteError':maximum,'referenceRaysPerProbe':count,'stonesAligned':len(stones),'width':width,'height':height}
(R/'evidence/pond-contact-ray-audit.json').write_text(json.dumps(report,indent=2));print('CONTACT INDEPENDENT AUDIT',{'mean':mean,'max':maximum,'probes':len(results)},flush=True)
assert mean<.08 and maximum<.22,(mean,maximum)
assert all(p['baked']<.15 for p in results if p['kind']=='covered')
metadata={'width':width,'height':height,'distance':.45,'nativeBounds':[-11.5,11.5,-12.7,1.1],'stones':len(stones),'inputs':{name:hashlib.sha256((A/name).read_bytes()).hexdigest() for name in ['pond-stones.json','pond-stones.glb','pond-basin.glb','bridge.glb','pond-lotus.glb']},'textureSha256':hashlib.sha256((A/'pond-contact-ao.png').read_bytes()).hexdigest()}
(A/'pond-contact-ao.json').write_text(json.dumps(metadata,indent=2))
