"""An editable stone chozubachi, bamboo spout and hollow wooden hishaku."""
import bpy,math,random,shutil,json,array,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';rng=random.Random(419)
path=R/'source/听秋寺院.blend';backup=path.with_name('听秋寺院-before-handwash.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path))
def sig():
 d={}
 for o in bpy.data.objects:
  if o.get('handwash'):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
  d[o.name]=h.hexdigest()
 return d
before=sig()
for o in list(bpy.data.objects):
 if o.get('handwash'):bpy.data.objects.remove(o,do_unlink=True)
root=bpy.data.objects.new('Entrance | stone purification basin',None);bpy.context.collection.objects.link(root);root.location=(-3.7,-15.6,.20);root['handwash']=True
parts=[]
def mat(name,c,rough=.7,image=None):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough
 if image:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/image),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
stone=mat('Handwash | carved granite',(.37,.39,.33),.72,'handwash-granite.jpg');wood=mat('Handwash | pale hinoki',(.65,.40,.16),.43,'handwash-hinoki.jpg');bamboo=mat('Handwash | green bamboo',(.26,.36,.12),.48);cut=mat('Handwash | cut bamboo end',(.58,.43,.19),.67);rope=mat('Handwash | hemp binding',(.24,.17,.065),.94);dark=mat('Handwash | dark river pebbles',(.075,.10,.084),.66);bronze=mat('Handwash | aged bronze bands',(.14,.085,.025),.36);bronze.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.8
def mesh(name,vs,fs,m,assembly='stone'):
 g=bpy.data.meshes.new(name);g.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);g.update();o=bpy.data.objects.new('Handwash | '+name,g);bpy.context.collection.objects.link(o);o.parent=root;o['handwash']=True;o['handwashAssembly']=assembly;g.materials.append(m);parts.append(o)
 uv=g.uv_layers.new(name='metre grain')
 for p in g.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   v=g.vertices[g.loops[li].vertex_index].co;uv.data[li].uv=(v.x*2+v.z*.35,-v.y*2+v.z*.35)
 return o

def lathe(name,profile,m,pos=(0,0,0),seg=128,rough=0,assembly='stone'):
 vs=[];fs=[]
 for j,(r,y) in enumerate(profile):
  for k in range(seg):
   a=k*math.tau/seg;d=rough*(math.sin(a*7+y*4)+.4*math.sin(a*13-y*8));vs.append((pos[0]+(r+d)*math.cos(a),pos[1]+y,pos[2]+(r+d)*math.sin(a)))
 for j in range(len(profile)-1):
  for k in range(seg):a=j*seg+k;b=j*seg+(k+1)%seg;fs.append((a,b,b+seg,a+seg) if assembly=='water' else (a+seg,b+seg,b,a))
 o=mesh(name,vs,fs,m,assembly)
 uv=o.data.uv_layers.active
 for face in o.data.polygons:
  angles=[]
  for li in face.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;angles.append((math.atan2(-v.y-pos[2],v.x-pos[0])/math.tau)%1)
  for li,a in zip(face.loop_indices,angles):
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   if abs(face.normal.z)>.65:uv.data[li].uv=(v.x*1.5,-v.y*1.5)
   else:
    if max(angles)-min(angles)>.5 and a<.5:a+=1
    uv.data[li].uv=(a*4,(v.z-pos[1])*1.5)
 return o
lathe('stepping plinth',[(0,0),(.93,0),(.96,.035),(.96,.10),(.93,.13),(0,.13)],stone,rough=.012)
lathe('hollow granite bowl',[(0,.13),(.52,.13),(.57,.17),(.58,.24),(.65,.39),(.73,.76),(.76,1.01),(.75,1.105),(.73,1.13),(.56,1.13),(.54,1.10),(.53,1.03),(.515,.95),(.48,.84),(.40,.76),(.28,.715),(0,.70)],stone,rough=.007)
# Narrow raised stone lotus petals sit on the exterior, not floating off the bowl.
for k in range(24):
 a=k*math.tau/24;vs=[];fs=[]
 for j in range(17):
  t=j/16;y=.45+.34*t;r=.665+.20*(y-.45);w=.075*math.sin(math.pi*t)**.7
  for s in [-1,0,1]:
   b=a+s*w;rr=r+.006+.007*(1-abs(s))*math.sin(math.pi*t);vs.append((rr*math.cos(b),y,rr*math.sin(b)))
 for j in range(16):
  for i in range(2):q=j*3+i;fs.append((q,q+1,q+4,q+3))
 mesh('carved lotus petal',vs,fs,stone)
def tube(name,start,end,r,m,assembly='bamboo',inner=0):
 a,b=Vector(start),Vector(end);d=(b-a).normalized();u=d.cross(Vector((0,1,0)))
 if u.length<.01:u=d.cross(Vector((1,0,0)))
 u.normalize();v=d.cross(u).normalized();vs=[];fs=[];n=32
 for p,rr in [(a,r),(b,r),(b,inner),(a,inner)]:
  for k in range(n):q=p+rr*(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n));vs.append(q)
 for j in range(4):
  for k in range(n):q=j*n+k;f=j*n+(k+1)%n;s=((j+1)%4)*n;fs.append((q,f,s+(k+1)%n,s+k))
 return mesh(name,vs,fs,m,assembly)
# Slatted rest leaves the centre of the water unobstructed.
for z in [.28,.41]:tube('ladle rest',(-.73,1.16,z),(.73,1.16,z),.026,bamboo)
tube('bamboo upright',(-.51,.10,-.53),(-.51,1.69,-.53),.052,bamboo,inner=.032)
tube('hollow bamboo spout',(-.51,1.58,-.53),(-.20,1.50,-.19),.043,bamboo,inner=.031)
for y in [.35,.79,1.21,1.65]:lathe('bamboo node',[(.052,-.018),(.059,-.011),(.059,.01),(.052,.018)],cut,(-.51,y,-.53),48,assembly='bamboo')
for j in range(7):tube('tied binding',(-.568,1.50+j*.007,-.54),(-.465,1.50+j*.007,-.52),.0035,rope)
# Hishaku: open thin-wall cup, rounded lip, handle directed toward the visitor.
rest=(.12,1.305,.28)
lathe('wooden ladle cup',[(0,-.108),(.075,-.108),(.105,-.097),(.115,-.015),(.114,.004),(.109,.009),(.101,.003),(.099,-.080),(.085,-.089),(0,-.089)],wood,rest,96,assembly='ladle')
tube('wooden ladle handle',(.12,1.286,.37),(.12,1.275,1.04),.016,wood,'ladle')
lathe('ladle bronze hoop',[(.110,-.01),(.113,-.006),(.113,.006),(.110,.01)],bronze,(.12,1.285,.28),96,assembly='ladle')
for i in range(65):
 a=rng.random()*math.tau;r=rng.uniform(.82,1.10);x=math.cos(a)*r;z=math.sin(a)*r;size=rng.uniform(.035,.08);lathe('drain pebble',[(0,-size*.3),(size*.8,0),(size,size*.25),(size*.7,size*.6),(0,size*.7)],dark,(x,.10,z),12,assembly='stone')
water=mat('Handwash | clear water',(.61,.79,.75),.075);p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.333
lathe('water surface',[(0,1.03),(.53,1.03)],water,seg=128,assembly='water')
assert sig()==before
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));standalone=bpy.data.scenes.new('入口手水钵')
for o in parts+[root]:standalone.collection.objects.link(o)
bpy.data.libraries.write(str(R/'source/入口手水钵.blend'),{standalone},fake_user=True)
# Batch only the web export; the .blend keeps every carved component editable.
groups={}
for o in parts:groups.setdefault((o['handwashAssembly'],o.data.materials[0]),[]).append(o)
exports=[]
for (assembly,material),items in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o['handwashAssembly']=assembly;o.name='Handwash | '+assembly+' | '+material.name;exports.append(o)
parts=exports
# Export the source hierarchy; runtime moves only the ladle assembly.
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for o in parts:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'handwash.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_apply=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=18)
report={'preservedObjects':len(before),'meshes':len(parts),'position':[-3.7,.20,15.6],'waterY':1.23,'innerRadius':.53,'ladleRest':[-3.58,1.505,15.88],'spout':[-3.90,1.70,15.41]};(A/'handwash.json').write_text(json.dumps(report,indent=2));print('HANDWASH COMPLETE',report,flush=True)
