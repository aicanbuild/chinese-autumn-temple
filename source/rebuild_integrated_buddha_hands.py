"""Restore Buddhist mudras and fuse them to the scanned sculpture, without remeshing the face.
Work into a candidate first; publish/export only after native topology and render inspection.
"""
import bpy, bmesh, math, json, shutil, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
OFFSET=Vector((0,8.6,1.915))
baseline=R/'source/主殿佛像-before-integrated-hands.blend'
if not baseline.exists():shutil.copy2(R/'source/主殿佛像.blend',baseline)
bpy.ops.wm.open_mainfile(filepath=str(baseline))
body=next(o for o in bpy.data.objects if o.name.startswith('Tang sculpture'))
gold=body.data.materials[0]
original=[v.co.copy() for v in body.data.vertices]
original_faces=[tuple(p.vertices) for p in body.data.polygons]
original_surface_vertices={i for f in original_faces for i in f}
for o in list(bpy.data.objects):
 if o.name.startswith('Restored ') and 'hand' in o.name:bpy.data.objects.remove(o,do_unlink=True)
parts=[]
def mesh(name,vs,fs):
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();d.materials.append(gold)
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);parts.append(o);return o

def ellipsoid(name,c,size):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=c)
 o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(gold);parts.append(o)
 return o

def spline(keys,steps=10):
 result=[]
 for i in range(len(keys)-1):
  q=[keys[max(0,min(len(keys)-1,j))] for j in [i-1,i,i+1,i+2]]
  for k in range(steps):
   t=k/steps;result.append([.5*(2*q[1][d]+(-q[0][d]+q[2][d])*t+(2*q[0][d]-5*q[1][d]+4*q[2][d]-q[3][d])*t*t+(-q[0][d]+3*q[1][d]-3*q[2][d]+q[3][d])*t*t*t) for d in range(len(q[0]))])
 return result+[keys[-1]]

def loft(name,keys,N=48,digit=False):
 rings=spline(keys,8);vs=[];fs=[]
 for i,r in enumerate(rings):
  c=Vector(r[:3]);t=(Vector(rings[min(i+1,len(rings)-1)][:3])-Vector(rings[max(0,i-1)][:3])).normalized()
  front=Vector((0,-1,0));front=(front-t*front.dot(t)).normalized();across=front.cross(t).normalized()
  u=i/(len(rings)-1)
  for k in range(N):
   a=k*math.tau/N;ca=math.cos(a);sa=math.sin(a);w=r[3];depth=r[4]
   # Shallow flexion folds on the palm side of each finger; nails sculpted on its back.
   if digit:
    crease=(math.exp(-((u-.37)/.019)**2)+.7*math.exp(-((u-.68)/.018)**2))*.00022*max(0,sa)**4
    depth-=crease
    if sa<-.72 and .72<u<.97:
     nx=ca/.68;ny=(u-.845)/.105;oval=nx*nx+ny*ny
     depth+=.00035*math.exp(-oval*2)-.00055*math.exp(-((oval-.86)/.12)**2)
   vs.append(c+across*(w*ca)+front*(depth*sa))
 for i in range(len(rings)-1):
  for k in range(N):
   a=i*N+k;b=i*N+(k+1)%N;fs.append((a,b,b+N,a+N))
 fs.extend([tuple(reversed(range(N))),tuple((len(rings)-1)*N+k for k in range(N))])
 return mesh(name,vs,fs)

def apply(o,m):
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)

def palm_detail(hand,palm,side):
 # Engraved lifeline and two fine transverse palm creases, using the remeshed surface.
 up=side
 curves=[]
 for k in range(41):
  t=k/40
  curves.append((-side*(.031-.016*math.sin(t*math.pi)),up*(-.031+.061*t),.00042))
  curves.append((-.035+.07*t,up*(.019+.006*math.sin(math.pi*t)),.00028))
  curves.append((-.030+.060*t,up*(-.005+.007*t+.004*math.sin(math.pi*t)),.00026))
 for v in hand.data.vertices:
  q=v.co-palm
  if abs(q.x)>.054 or abs(q.z)>.049 or q.y>-.011:continue
  # Leave the silhouette and thenar/thumb saddle untouched.
  weight=min(1,max(0,(-q.y-.011)/.007))
  groove=max(depth*math.exp(-((q.x-x)**2+(q.z-z)**2)/.0000007) for x,z,depth in curves)
  v.co.y+=groove*weight

report=[];tips=[];joint_centers=[];hands=[]
for side in [-1,1]:
 parts=[];up=side
 if side<0:
  palm=Vector((-.409,-.190,.828))
  keys=[[-.421,.020,.985,.047,.039],[-.419,.005,.940,.045,.037],[-.416,-.040,.898,.037,.032],[-.412,-.098,.875,.029,.025],[-.410,-.160,.850,.031,.023],[-.409,-.190,.822,.039,.023]]
  joint=Vector((-.416,-.036,.909))
 else:
  palm=Vector((.267,-.255,1.108))
  keys=[[.290,-.103,.908,.047,.041],[.280,-.165,.936,.045,.038],[.272,-.213,.980,.037,.031],[.269,-.239,1.030,.030,.025],[.267,-.251,1.071,.032,.023],[.267,-.255,1.112,.038,.023]]
  joint=Vector((.279,-.172,.944))
 loft('Anatomical forearm, carpus and palm heel',keys)
 # Palm is a rounded metacarpal volume, with a softer heel and distinct thenar/hypothenar pads.
 ellipsoid('Metacarpal palm',palm,(.047,.022,.052))
 ellipsoid('Thenar pad',palm+Vector((-side*.024,.004,-up*.016)),(.023,.018,.028))
 ellipsoid('Hypothenar pad',palm+Vector((side*.024,.005,-up*.018)),(.018,.016,.027))
 for j in range(4):
  fx=(j-1.5)*.0255
  length=([.086,.100,.094,.075] if side>0 else [.072,.089,.096,.083])[j]
  length+=.011
  start=palm+Vector((fx*.82,0,up*(.013+.004*(1-abs(j-1.5)))))
  digit=[]
  for k in range(17):
   t=k/16
   # Slightly fanned, three gently articulated phalanges. Giving hand curls more softly.
   z=up*length*t;y=-.006*t-(.009 if side>0 else .018)*t*t
   fan=min(1,t/.22);fan=fan*fan*(3-2*fan)
   x=fx*(.18*fan+.11*t)+(.002 if j==0 else -.001)*math.sin(t*math.pi)
   radius=(.0122-.0007*abs(j-1.3))*(1-.28*t)
   radius*=1+.045*math.exp(-((t-.38)/.10)**2)+.025*math.exp(-((t-.68)/.09)**2)
   if t>.875:radius*=math.sqrt(max(.0006,(1-t)/.125))
   digit.append(list(start+Vector((x,y,z)))+[max(.00025,radius),max(.00025,radius*.86)])
  loft('Tapered articulated finger',digit,32,True)
  fingeraxis=(Vector(digit[-1][:3])-Vector(digit[-3][:3])).normalized()
  radius=.0080-.0004*abs(j-1.3)
  tip=ellipsoid('Rounded fingertip',Vector(digit[-1][:3])-fingeraxis*.0065,(radius,radius*.88,.008));tip.rotation_euler=fingeraxis.to_track_quat('Z','Y').to_euler()
  tips.append((side,list(start+Vector((fx*(.18+.11),-.006-(.009 if side>0 else .018),up*length*.90)))))
 # Opposed thumb curves out of a broad muscular saddle, rather than a rod pasted on the side.
 thumb=[]
 for k in range(17):
  t=k/16
  p=palm+Vector((-side*(.024+.049*t),.003-.019*math.sin(t*math.pi/2),up*(-.024+.075*t-.009*t*t)))
  radius=.0155*(1-.38*t)
  if t>.875:radius*=math.sqrt(max(.0006,(1-t)/.125))
  thumb.append(list(p)+[max(.00025,radius),max(.00025,radius*.88)])
 loft('Opposed curved thumb',thumb,32,False)
 thumbaxis=(Vector(thumb[-1][:3])-Vector(thumb[-3][:3])).normalized()
 tip=ellipsoid('Soft thumb fingertip',Vector(thumb[-1][:3])-thumbaxis*.006,(.008,.007,.010));tip.rotation_euler=thumbaxis.to_track_quat('Z','Y').to_euler()
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();hand=bpy.context.object
 hand.name='Restored giving hand' if side<0 else 'Restored reassurance hand'
 # Fuse the palm, webs and phalanges into one closed surface first.
 m=hand.modifiers.new('Sculpt anatomical hand union','REMESH');m.mode='VOXEL';m.voxel_size=.00085;apply(hand,m)
 m=hand.modifiers.new('Soft anatomical transitions','SMOOTH');m.factor=.42;m.iterations=3;apply(hand,m)
 palm_detail(hand,palm,side)
 for p in hand.data.polygons:p.use_smooth=True
 # Both assets use the very same gilding material; no smooth plastic-colored replacement.
 hand.location=OFFSET;hands.append(hand)
 report.append({'gesture':'giving' if side<0 else 'reassurance','handVertices':len(hand.data.vertices),'palm':list(palm),'joint':list(joint)})
 joint_centers.append(joint)
if '--hands-only' in sys.argv:
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/主殿佛像-衔接候选.blend'))
 print('HAND_PREVIEW_SAVED',flush=True);sys.exit(0)
for side,hand in zip([-1,1],hands):
 bpy.context.view_layer.objects.active=body
 m=body.modifiers.new('Weld hand into scanned forearm','BOOLEAN');m.operation='UNION';m.solver='EXACT';m.use_hole_tolerant=True;m.object=hand
 apply(body,m)
 bpy.data.objects.remove(hand,do_unlink=True)
 print('FUSED',side,len(body.data.vertices),len(body.data.polygons),flush=True)
# Boolean output is used only around the forearms. Restore original triangles everywhere
# else: the scan has small nonmanifold artifacts, which a global Boolean may clean up.
def local_restoration(p):
 return ((-.510<p.x<-.300 and -.27<p.y<.080 and .60<p.z<1.055) or
         (.160<p.x<.400 and -.33<p.y<-.045 and .83<p.z<1.290))
newverts=[v.co.copy() for v in body.data.vertices]
newfaces=[tuple(p.vertices) for p in body.data.polygons if local_restoration(p.center)]
keep=[f for f in original_faces if not local_restoration(sum((original[i] for i in f),Vector())/len(f))]
meshdata=bpy.data.meshes.new('Continuous scanned sculpture and restored mudras')
meshdata.from_pydata(original+newverts,[],keep+[tuple(i+len(original) for i in f) for f in newfaces]);meshdata.materials.append(gold);meshdata.update();body.data=meshdata
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000005)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_edges],context='VERTS')
# Smooth only the insertion surfaces; all scanned face/drapery beyond the wrists is untouched.
for j in joint_centers:
 chosen=[v for v in bm.verts if (v.co-j).length<.065]
 for _ in range(10):bmesh.ops.smooth_vert(bm,verts=chosen,factor=.40,use_axis_x=True,use_axis_y=True,use_axis_z=True)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(body.data);bm.free();body.data.update()
for p in body.data.polygons:p.use_smooth=True
body['hand_revision']=4;body['integrated_hands']=True;body['restoration_version']=2
# Topological proof: all eight distal fingers are reachable from the scanned chest via mesh edges.
vertices=[v.co for v in body.data.vertices]
closest=lambda p:min(range(len(vertices)),key=lambda i:(vertices[i]-p).length_squared)
root=closest(Vector((0,-.18,1.27)))
adj=[[] for _ in vertices]
for e in body.data.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
seen={root};stack=[root]
while stack:
 for b in adj[stack.pop()]:
  if b not in seen:seen.add(b);stack.append(b)
for side,p in tips:
 i=closest(Vector(p));print('FINGER',side,(vertices[i]-Vector(p)).length,i in seen,flush=True);assert i in seen,('Finger still disconnected',side,p);assert (vertices[i]-Vector(p)).length<.016
report.append({'fingertipsLocal':tips})
report.append({'connectedCoreVertices':len(seen),'allEightFingertipsConnectedToChest':True,'bodyVertices':len(vertices)})
assert len(vertices)>len(original),'Original scanned detail was unexpectedly lost.'
# Verify sampled original face vertices survived exactly: Boolean/smoothing must not rewrite the face.
from mathutils.kdtree import KDTree
kd=KDTree(len(vertices))
for i,p in enumerate(vertices):kd.insert(p,i)
kd.balance()
face=[p for i,p in enumerate(original) if i in original_surface_vertices and p.z>1.42]
max_error=max(kd.find(p)[2] for p in face)
assert max_error<.00001,('Face changed',max_error)
report.append({'preservedFaceVertices':len(face),'maxFacePositionError':max_error})
body['wrist_topology_verified']=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/主殿佛像-衔接候选.blend'))
(R/'evidence/integrated-hands.json').write_text(json.dumps(report,indent=2))
print('INTEGRATED_HANDS',json.dumps(report),flush=True)
