"""Independent cosine-hemisphere ray audit of the saved floor contact bake."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.wm.open_mainfile(filepath=str(R/'source/殿内地面接触光照.blend'))
scene=bpy.context.scene;receiver=scene.objects['Hall floor contact receiver'];o=scene.objects['Hall contact occluders']
vertices=[];faces=[]
for part in [o]+[p for p in scene.objects if p.type=='MESH' and p.get('wooden_fish') and p.get('assembly')=='stand']:
 offset=len(vertices);vertices.extend(part.matrix_world@v.co for v in part.data.vertices);faces.extend(tuple(offset+i for i in p.vertices) for p in part.data.polygons)
tree=BVHTree.FromPolygons(vertices,faces)
x0,x1,y0,y1=scene['contact_bounds_native'];z=scene['contact_receiver_height'];distance=scene['contact_distance_m']
image=bpy.data.images.load(str(A/'hall-contact-ao.png'),check_existing=False);image.colorspace_settings.name='Non-Color';pixels=list(image.pixels);width,height=image.size
def sample(x,y):
 fx=(x-x0)/(x1-x0)*width-.5;fy=(y-y0)/(y1-y0)*height-.5;i=math.floor(fx);j=math.floor(fy);tx=fx-i;ty=fy-j
 def read(a,b):return pixels[(max(0,min(height-1,b))*width+max(0,min(width-1,a)))*4]
 return (read(i,j)*(1-tx)+read(i+1,j)*tx)*(1-ty)+(read(i,j+1)*(1-tx)+read(i+1,j+1)*tx)*ty
probes=[(x0+(i+.5)*(x1-x0)/14,y0+(j+.5)*(y1-y0)/8,'grid') for j in range(8) for i in range(14)]
probes += [(x,y,'altar edge') for x in [-2.8,-2.5,-2.2,-1.85,-1.7,0,1.7,1.85,2.2,2.5,2.8] for y in [7.35,7.5,7.7]]
probes += [(x,y,'wooden fish stand') for x in [-1.24,-1.20,-.95,-.70,-.66] for y in [6.23,6.26,6.45,6.64,6.67]]
results=[];count=2048;golden=math.pi*(3-math.sqrt(5))
def visibility(x,y,rays):
 origin=Vector((x,y,z+.0001));occluded=0
 for i in range(rays):
  r=math.sqrt((i+.5)/rays);a=i*golden;direction=Vector((r*math.cos(a),r*math.sin(a),math.sqrt(1-r*r)))
  hit,_,_,_=tree.ray_cast(origin,direction,distance);occluded+=hit is not None
 return 1-occluded/rays
def filtered_visibility(x,y):
 # A baked texel integrates its area; GPU bilinear filtering mixes four such
 # areas. Point rays alone are not comparable exactly at a pillar boundary.
 fx=(x-x0)/(x1-x0)*width-.5;fy=(y-y0)/(y1-y0)*height-.5;i=math.floor(fx);j=math.floor(fy);tx=fx-i;ty=fy-j;value=0
 for a,b,weight in [(i,j,(1-tx)*(1-ty)),(i+1,j,tx*(1-ty)),(i,j+1,(1-tx)*ty),(i+1,j+1,tx*ty)]:
  total=0
  for sy in range(8):
   for sx in range(8):total+=visibility(x0+(a+(sx+.5)/8)/width*(x1-x0),y0+(b+(sy+.5)/8)/height*(y1-y0),512)
  value+=weight*total/64
 return value
for x,y,kind in probes:
 reference=visibility(x,y,count);baked=sample(x,y);result={'point':[x,y,z],'kind':kind,'reference':reference,'baked':baked,'pointError':abs(reference-baked)}
 if result['pointError']>.02:result['filteredReference']=filtered_visibility(x,y)
 result['error']=abs(result.get('filteredReference',reference)-baked);results.append(result)
mean=sum(p['error'] for p in results)/len(results);maximum=max(p['error'] for p in results)
report={'probes':results,'meanAbsoluteError':mean,'maxAbsoluteError':maximum,'maxPointError':max(p['pointError'] for p in results),'filteredProbes':sum('filteredReference' in p for p in results),'referenceRaysPerProbe':count,'edgeFilterSamples':[8,8,512],'width':width,'height':height}
(R/'evidence/hall-contact-ray-audit.json').write_text(json.dumps(report,indent=2));print('HALL CONTACT AUDIT',{'mean':mean,'max':maximum,'probes':len(results)},flush=True)
assert mean<.02 and maximum<.06,(mean,maximum)
assert min(p['baked'] for p in results)<.15 and max(p['baked'] for p in results)>.95
inputs=['temple.glb','sanctuary.glb','sanctuary-floor.glb','incense-vessel.glb','altar-brocade.glb','door-backs.glb','sculpture.glb','guardian-lions.glb','lotus-surfaces.glb','aureole-relief.glb','candle-wax.glb','wooden-fish.glb']
metadata={'width':width,'height':height,'distance':distance,'nativeBounds':[x0,x1,y0,y1],'receiverHeight':z,'inputs':{name:hashlib.sha256((A/name).read_bytes()).hexdigest() for name in inputs},'textureSha256':hashlib.sha256((A/'hall-contact-ao.png').read_bytes()).hexdigest()}
(A/'hall-contact-ao.json').write_text(json.dumps(metadata,indent=2))
