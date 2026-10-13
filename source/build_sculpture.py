"""Original seated altar sculpture, modeled as editable continuous surfaces.
Blender local coordinates: front is -Y. No downloaded or generated image statue.
"""
import bpy, bmesh, math, json, random, sys
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';random.seed(604)
def append_to_temple():
 temple=R/'source/听秋寺院.blend'
 if temple.exists():
  bpy.ops.wm.open_mainfile(filepath=str(temple))
  for o in list(bpy.data.objects):
   if o.get('altar_sculpture'):bpy.data.objects.remove(o,do_unlink=True)
  with bpy.data.libraries.load(str(R/'source/主殿佛像.blend'),link=False) as (src,dst):dst.objects=src.objects
  for o in dst.objects:
   if o:bpy.context.collection.objects.link(o)
  bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple))

if '--append-only' in sys.argv:
 append_to_temple();print('Appended detailed sculpture to the native temple.',flush=True);sys.exit(0)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection' and not c.objects:bpy.data.collections.remove(c)
collection=bpy.data.collections.new('Main altar | original gilded sculpture');bpy.context.scene.collection.children.link(collection)
objects=[]
def mat(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
gold=mat('Sculpture | softly burnished gold',(.64,.405,.145),.86,.36)
robe=mat('Sculpture | warm chased robe',(.43,.24,.078),.80,.43)
recess=mat('Sculpture | bronze in recesses',(.135,.073,.024),.72,.46)
hair=mat('Sculpture | dark patinated curls',(.055,.045,.023),.73,.48)
def register(o,material):
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.data.materials.clear();o.data.materials.append(material);o['altar_sculpture']=True;objects.append(o)
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o
def mesh(name,verts,faces,material):
 g=bpy.data.meshes.new(name);g.from_pydata(verts,[],faces);g.update();o=bpy.data.objects.new(name,g);collection.objects.link(o);g.materials.append(material);o['altar_sculpture']=True;objects.append(o)
 for p in g.polygons:p.use_smooth=True
 return o
def grid(name,fn,nu,nv,material,wrap=False):
 vs=[fn(i/nu,j/nv) for j in range(nv+1) for i in range(nu+1)];fs=[]
 for j in range(nv):
  for i in range(nu):a=j*(nu+1)+i;fs.append((a,a+1,a+nu+2,a+nu+1))
 return mesh(name,vs,fs,material)
def curve(name,pts,r,material,res=3):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=r;c.bevel_resolution=res;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);collection.objects.link(o);c.materials.append(material);o['altar_sculpture']=True;objects.append(o);return o
def ellipsoid(name,center,scale,material,n=48,lat=32,deform=None):
 def fn(u,v):
  a=u*math.tau;p=v*math.pi;co=Vector((scale[0]*math.sin(p)*math.cos(a),scale[1]*math.sin(p)*math.sin(a),scale[2]*math.cos(p)))
  if deform:co=Vector(deform(co,u,v))
  return tuple(Vector(center)+co)
 return grid(name,fn,n,lat,material)
def bezier(a,b,c,d,n=36):
 a,b,c,d=map(Vector,[a,b,c,d]);return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d) for t in [i/n for i in range(n+1)]]
def loft(name,pts,radii,material,steps=20):
 verts=[];faces=[]
 for i,p in enumerate(pts):
  p=Vector(p);direction=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(i-1,0)]);q=direction.to_track_quat('Z','Y');r=radii[i]
  for j in range(steps):verts.append(tuple(p+q@Vector((r*math.cos(j*math.tau/steps),r*.91*math.sin(j*math.tau/steps),0))))
 for i in range(len(pts)-1):
  for j in range(steps):a=i*steps+j;b=i*steps+(j+1)%steps;faces.append((a,b,b+steps,a+steps))
 faces.extend([tuple(range(steps-1,-1,-1)),tuple((len(pts)-1)*steps+j for j in range(steps))]);return mesh(name,verts,faces,material)
def gauss(x,z,cx,cz,sx,sz):return math.exp(-((x-cx)/sx)**2-((z-cz)/sz)**2)
# Continuous oval face. Brow sockets, cheeks, lips and nasal bridge are displacements
# of the same surface rather than glued-on balls.
HC=1.565;RX=.191;RY=.164;RZ=.258

def relief(x,z):
 d=-.042*gauss(x,z,0,1.565,.031,.088)-.035*gauss(x,z,0,1.517,.030,.023)
 d-=.017*(gauss(x,z,-.027,1.508,.017,.018)+gauss(x,z,.027,1.508,.017,.018))
 d+=.013*(gauss(x,z,-.076,1.602,.041,.024)+gauss(x,z,.076,1.602,.041,.024))
 d-=.012*(gauss(x,z,-.079,1.549,.045,.038)+gauss(x,z,.079,1.549,.045,.038))
 d-=.010*gauss(x,z,0,1.458,.070,.024)+.006*gauss(x,z,0,1.408,.063,.031)
 d-=.0045*(gauss(x,z,-.018,1.460,.030,.006)+gauss(x,z,.018,1.460,.030,.006))+.005*gauss(x,z,0,1.445,.045,.007)
 t=(abs(x)-.036)/.09
 if 0<t<1:
  ze=1.600-.007*math.sin(t*math.pi)+.004*t
  d-=.003*math.sin(t*math.pi)*math.exp(-((z-ze-.006)/.006)**2)
  zb=1.641+.014*math.sin(t*math.pi)-.009*t
  d-=.004*math.sin(t*math.pi)*math.exp(-((z-zb)/.010)**2)
 return d

def front(x,z):
 latitude=math.sqrt(max(.0001,1-((z-HC)/RZ)**2));weight=max(0,1-(x/(RX*latitude))**2)**3.5
 return -.008-RY*math.sqrt(max(.005,1-(x/RX)**2-((z-HC)/RZ)**2))+relief(x,z)*weight
def head(u,v):
 a=u*math.tau;p=v*math.pi;x=RX*math.sin(p)*math.cos(a);z=HC+RZ*math.cos(p);y=-.008+RY*math.sin(p)*math.sin(a)
 # Slightly narrow the jaw and temple; the frontal relief fades at the sides.
 y+=relief(x,z)*max(0,-math.sin(a))**7
 return (x,y,z)
headmesh=grid('Face | continuous sculpt with nose, cheeks and chin',head,160,112,gold)
# Neck and anatomical shoulders.
profile=[(.50,.26,.185),(.65,.27,.177),(.82,.235,.151),(.98,.285,.160),(1.10,.318,.146),(1.18,.30,.133),(1.23,.197,.109),(1.26,.102,.089),(1.34,.097,.082)]
def radius(z):
 for i in range(len(profile)-1):
  a,b=profile[i],profile[i+1]
  if z<=b[0]:
   t=max(0,(z-a[0])/(b[0]-a[0]));t=t*t*(3-2*t);return (a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t)
 return profile[-1][1:]
def torso(u,v):
 z=.50+v*.85;r,d=radius(z);a=u*math.tau;return (r*math.cos(a),.035+d*math.sin(a),z)
grid('Torso | shoulders and neck',torso,112,96,gold)
# Almond eyelids, closed in meditation, and a restrained smiling mouth.
for side in [-1,1]:
 pts=[];upper=[];brow=[]
 for i in range(41):
  t=i/40;x=side*(.036+.090*t);z=1.600-.007*math.sin(t*math.pi)+.004*t
  pts.append((x,front(x,z)-.0018,z));upper.append((x,front(x,z+.009)-.0023,z+.009*math.sin(t*math.pi)))
  zz=1.641+.014*math.sin(t*math.pi)-.009*t;brow.append((x,front(x,zz)-.003,zz))
 curve('Half-closed eye | '+str(side),pts,.0010,recess,3)
 curve('Nostril | '+str(side),[(side*(.018+.018*t),front(side*(.018+.018*t),1.501)-.001,1.501+.003*math.sin(t*math.pi)) for t in [i/18 for i in range(19)]],.0019,recess,2)
pts=[]
for i in range(51):
 x=-.061+i*.122/50;z=1.453+.005*(abs(x)/.061)**1.6;pts.append((x,front(x,z)-.0015,z))
curve('Mouth | quiet central seam',pts,.0009,recess,3)
ellipsoid('Urna',(0,front(0,1.688)-.003,1.688),(.006,.004,.006),gold,24,16)
# Elongated earlobes and helix, inset inner ear bowl.
for side in [-1,1]:
 ellipsoid('Ear | elongated lobe '+str(side),(side*.188,.007,1.524),(.045,.026,.105),gold,40,48)
 pts=[(side*(.190+.033*math.cos(a)), -.018-.006*math.sin(a),1.531+.081*math.sin(a)) for a in [i*math.tau/72 for i in range(73)]]
 curve('Ear | helix '+str(side),pts,.006,gold,3)
 pts=[(side*(.190+.016*math.cos(a)),-.021,1.537+.052*math.sin(a)) for a in [-1.3+i*4.8/48 for i in range(49)]]
 curve('Ear | concha shadow '+str(side),pts,.0025,recess,2)
# Full hair cap, individual spiral curls and a small ushnisha at the crown.
def cap(u,v):
 a=u*math.tau;p=.06+v*(1.40-.35*max(0,-math.sin(a)));return (.194*math.sin(p)*math.cos(a),.010+.17*math.sin(p)*math.sin(a),1.605+.243*math.cos(p))
grid('Hair | fitted cap',cap,96,40,hair)
for row in range(9):
 ph=.23+row*.143;count=max(9,round(59*math.sin(ph)))
 for j in range(count):
  a=(j+.5*(row%2))*math.tau/count
  if ph>1.46-.35*max(0,-math.sin(a)):continue
  p=Vector((.196*math.sin(ph)*math.cos(a),.010+.173*math.sin(ph)*math.sin(a),1.605+.246*math.cos(ph)))
  normal=Vector((math.sin(ph)*math.cos(a),math.sin(ph)*math.sin(a),math.cos(ph)));q=normal.to_track_quat('Z','Y');pts=[]
  for k in range(25):
   t=k/24;rr=.0105*(1-t*.78);ang=t*math.pi*3.5;pts.append(tuple(p+q@Vector((rr*math.cos(ang),rr*math.sin(ang),.003*t))))
  curve('Hair | spiral curl',pts,.0029,hair,1)
ellipsoid('Ushnisha | crown',(0,.015,1.842),(.075,.068,.085),hair,48,32)
for row in range(4):
 for i in range(15):
  a=(i+row*.5)*math.tau/15;ph=.35+row*.28
  ellipsoid('Crown curl',(.073*math.sin(ph)*math.cos(a),.015+.067*math.sin(ph)*math.sin(a),1.842+.083*math.cos(ph)),(.008,.008,.008),hair,8,6)
# Crossed legs under a continuous draped lap, with sculpted radial cloth folds.
def lap_deform(co,u,v):
 a=u*math.tau;p=v*math.pi;fold=.012*math.sin(36*a+4*math.sin(p))*math.sin(p)**2
 co.z+=fold*max(0,math.cos(p))+.020*math.exp(-(co.x/.28)**2)*max(0,math.cos(p));return co
ellipsoid('Robe | continuous crossed-leg drapery',(0,-.012,.405),(.705,.355,.175),robe,144,72,lap_deform)
for side in [-1,1]:
 pts=bezier((side*.28,.02,1.165),(side*.40,-.01,1.10),(side*.46,-.065,.75),(side*.388,-.15,.654),48)
 pts+=bezier((side*.388,-.15,.654),(side*.35,-.23,.590),(side*.19,-.295,.588),(side*.10,-.31,.616),36)[1:]
 radii=[.080*(1-i/(len(pts)-1))+.037*i/(len(pts)-1) for i in range(len(pts))]
 loft('Arm | flowing shoulder to wrist '+str(side),pts,radii,gold,32)
for side in [-1,1]:ellipsoid('Shoulder | rounded anatomical transition '+str(side),(side*.281,.015,1.148),(.089,.085,.090),gold,48,32)
# Hands in dhyana: palms overlap, relaxed fingers curve individually, thumbs touch.
for side in [-1,1]:
 z=.610+(side==1)*.046
 ellipsoid('Hand | cupped palm '+str(side),(side*.048,-.326,z),(.113,.053,.032),gold,48,28)
 for finger in range(4):
  yy=-.347+finger*.024;start=(side*.074,yy,z);end=(-side*(.065-finger*.009),yy-.021,z+.006)
  pts=bezier(start,(side*.025,yy-.018,z-.012),(-side*.035,yy-.025,z-.010),end,28)
  radii=[.0105*(1-.35*i/(len(pts)-1)) for i in range(len(pts))];loft('Hand | finger '+str(side)+' '+str(finger),pts,radii,gold,12)
  # Nail beds are shallow metal inlays, not painted rectangles.
  ellipsoid('Hand | fingernail',end,(.014,.0075,.002),robe,20,12)
 pts=bezier((side*.106,-.326,z+.022),(side*.083,-.33,.719),(side*.02,-.337,.735),(0,-.342,.714),28)
 loft('Hand | touching thumb '+str(side),pts,[.016*(1-i/len(pts)*.42) for i in range(len(pts))],gold,16)
# Bare upturned feet resting over the lap cloth, with individual toes.
for side in [-1,1]:
 foot=ellipsoid('Foot | lotus posture '+str(side),(side*.255,-.222,.565),(.155,.067,.042),gold,48,28)
 foot.rotation_euler.z=side*.25
 for j in range(5):
  ellipsoid('Foot | toe', (side*(.37-j*.027),-.228-j*.019,.570),(.021-j*.0016,.029,.020-j*.001),gold,24,16)
# A continuous shoulder robe with diagonal edge, rolled hems, and soft engraved folds.
def robe_surface(u,v):
 a=u*math.tau;top=1.10-.155*math.cos(a);z=.535+v*(top-.535);r,d=radius(z)
 folds=(.008*math.sin(a*27+z*14)+.004*math.sin(a*43-z*9))*math.sin(v*math.pi)*max(.2,-math.sin(a))
 return ((r+.009+folds)*math.cos(a),.035+(d+.012+folds)*math.sin(a),z)
grid('Robe | continuous diagonal shoulder cloth',robe_surface,160,88,robe)
curve('Robe | folded diagonal hem',[robe_surface(i/240,1) for i in range(241)],.009,gold,3)
curve('Robe | lower hem',[robe_surface(i/240,.015) for i in range(241)],.006,gold,3)
# A softly folded sleeve wraps the covered shoulder, without floating linework.
sleeve_path=bezier((-.285,.015,1.173),(-.35,-.005,1.10),(-.419,-.055,.94),(-.424,-.090,.84),64)
def sleeve(u,v):
 n=min(63,int(v*64));t=v*64-n;center=Vector(sleeve_path[n]).lerp(Vector(sleeve_path[n+1]),t)
 direction=Vector(sleeve_path[n+1])-Vector(sleeve_path[n]);q=direction.to_track_quat('Z','Y');a=u*math.tau;rad=.087+.004*math.sin(a*10+v*8)
 return tuple(center+q@Vector((rad*math.cos(a),rad*.91*math.sin(a),0)))
grid('Robe | folded shoulder sleeve',sleeve,72,64,robe)
curve('Robe | sleeve cuff',[sleeve(i/96,1) for i in range(97)],.005,gold,3)
ellipsoid('Lotus | solid cast seat',(0,0,.145),(.615,.416,.130),gold,96,40)
# Elliptical lotus throne: two staggered rows of pointed, cupped petals.
for row in range(2):
 n=24
 for i in range(n):
  a=(i+row*.5)*math.tau/n
  def petal(u,v,a=a,row=row):
   t=u;s=v*2-1;rr=.39+.35*math.sin(t*math.pi/2);w=.092*math.sin(t*math.pi)**.7*s
   z=(.068+.12*t if row else .145-.10*t)+.044*math.sin(t*math.pi)*(1-s*s)
   return (math.cos(a)*rr-math.sin(a)*w,(math.sin(a)*rr+math.cos(a)*w)*.68,z)
  ob=grid('Lotus | sculpted petal %02d-%02d'%(row,i),petal,20,12,gold)
  mod=ob.modifiers.new('Cast petal thickness','SOLIDIFY');mod.thickness=.006
  curve('Lotus | petal vein',[petal(k/24,.5) for k in range(25)],.0028,robe,2)
for z,rx,ry in [(.028,.57,.38),(.051,.62,.42),(.208,.58,.39),(.24,.56,.38)]:
 curve('Lotus | beaded rim',[(math.cos(i*math.tau/128)*rx,math.sin(i*math.tau/128)*ry,z) for i in range(129)],.016,gold,3)
for i in range(72):
 a=i*math.tau/72;ellipsoid('Lotus | bead',(math.cos(a)*.568,math.sin(a)*.385,.233),(.009,.009,.009),gold,10,6)
# Fuse the shoulders and arms into one anatomically continuous casting.
body_parts=[o for o in objects if o.name.startswith(('Torso |','Arm |','Shoulder |'))]
bpy.ops.object.select_all(action='DESELECT')
for o in body_parts:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
 bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();o.select_set(True)
bpy.context.view_layer.objects.active=body_parts[0];bpy.ops.object.join();body=bpy.context.object
mod=body.modifiers.new('Continuous shoulder casting','REMESH');mod.mode='VOXEL';mod.voxel_size=.004;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
mod=body.modifiers.new('Polish anatomical transitions','SMOOTH');mod.factor=.65;mod.iterations=4;bpy.ops.object.modifier_apply(modifier=mod.name)
objects=list(collection.objects)
# Place on the existing altar; keep the native sculpture as separately editable parts.
for o in objects:o.location+=Vector((0,8.6,1.90))
for o in objects:
 if o.type=='CURVE':
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
for o in objects:
 if o.type=='MESH':
  for mod in list(o.modifiers):
   bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
# Save editable full-detail components before batching the portable export.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/主殿佛像.blend'))
counts={'components':len(objects),'vertices':sum(len(o.data.vertices) for o in objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons) for o in objects if o.type=='MESH')}
# Retain native sculpt detail; reduce the fused shoulder/arm casting only for WebGL.
for o in objects:
 if o.name.startswith('Torso |'):
  bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Web shoulder topology','DECIMATE');mod.ratio=.28;bpy.ops.object.modifier_apply(modifier=mod.name)
for material in [gold,robe,recess,hair]:
 parts=[o for o in list(collection.objects) if o.type=='MESH' and o.data.materials[0]==material]
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();bpy.context.object.name=material.name
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(A/'sculpture.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(A/'sculpture.json').write_text(json.dumps(counts,indent=2));print('SCULPTURE',counts,flush=True)
if '--standalone' not in sys.argv:append_to_temple()
