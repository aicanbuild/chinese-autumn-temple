"""Detailed stone lanterns: curved eaves, pierced firebox, lotus capital and eased stone."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
parts=[]
def material(name,color,rough=.7,metal=0,texture=False,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 if texture:
  for suffix,slot in [('', 'Base Color'),('-normal','Normal'),('-rough','Roughness')]:
   t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/f'cut-granite{suffix}.jpg'),check_existing=True)
   if suffix:t.image.colorspace_settings.name='Non-Color'
   if slot=='Normal':
    n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.6;m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs[0],p.inputs[slot])
   else:m.node_tree.links.new(t.outputs['Color'],p.inputs[slot])
 return m
stone=material('Lantern | fine carved granite',(.64,.63,.58),texture=True)
recess=material('Lantern | shaded carved courses',(.23,.24,.21),.85)
bronze=material('Lantern | antique bronze grille',(.32,.21,.075),.42,.72)
light=material('Lantern | warm inner screen',(.8,.34,.075),.86,emission=1.1)
def finish(o,name,mat):
 o.name=name;o.data.materials.clear();o.data.materials.append(mat);o['stone_lantern']=True;parts.append(o);return o

def uvproject(o):
 uv=o.data.uv_layers.active or o.data.uv_layers.new()
 for face in o.data.polygons:
  omit=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=omit]
  for li in face.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*1.3+.21,p[axes[1]]*1.3+.37)

def bevel(o,r=.01):
 mod=o.modifiers.new('Soft carved edge','BEVEL');mod.width=r;mod.segments=3;mod.limit_method='ANGLE';bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in o.data.polygons:p.use_smooth=True
 mod=o.modifiers.new('Flat faces and polished arrises','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o

def box(name,pos,size,mat=stone,r=.009):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,mat);uvproject(o)
 return bevel(o,r) if r else o

def mesh(name,vs,faces,mat=stone,smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);finish(o,name,mat);uvproject(o)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=smooth
 return o

def lathe(name,z,profile,mat=stone,n=64,flutes=0):
 vs=[];fs=[]
 for h,r in profile:
  for i in range(n):a=i/n*math.tau;radius=r*(1+flutes*math.cos(a*8));vs.append((radius*math.cos(a),radius*math.sin(a),z+h))
 for j in range(len(profile)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]);return mesh(name,vs,fs,mat)
box('Foot | eased square plinth',(0,0,.09),(.76,.76,.18),r=.026)
box('Foot | inset course',(0,0,.203),(.62,.62,.062),recess,.012)
box('Foot | bevelled upper block',(0,0,.258),(.57,.57,.09),r=.021)
lathe('Base | torus and spreading foot',.296,[(0,.23),(.019,.24),(.036,.21),(.062,.17),(.081,.159)],n=64)
lathe('Shaft | subtly fluted entasis',.365,[(j*.67/24,.157-.032*(j/24)+.010*math.sin(j/24*math.pi)) for j in range(25)],n=64,flutes=.014)
lathe('Capital | lower neck',1.02,[(0,.13),(.021,.14),(.034,.17),(.053,.19)],n=64)
lathe('Capital | lotus bowl',1.055,[(0,.17),(.024,.20),(.048,.25),(.075,.29),(.094,.31),(.110,.308)],n=64)
# Low-relief lotus petals carved around the capital.
for j in range(16):
 a=j/16*math.tau;vs=[];fs=[]
 for u in range(13):
  t=u/12;rr=.18+.132*t;z=1.069+.093*t
  for v in range(7):
   w=(v/6*2-1)*.048*math.sin(t*math.pi)**.7;bulge=.009*math.sin(t*math.pi)*(1-(v/6*2-1)**2);vs.append(((rr+bulge)*math.cos(a)-w*math.sin(a),(rr+bulge)*math.sin(a)+w*math.cos(a),z))
 for u in range(12):
  for v in range(6):k=u*7+v;fs.append((k,k+1,k+8,k+7))
 mesh('Capital | lotus relief',vs,fs)
box('Chamber | lower tray',(0,0,1.196),(.625,.625,.071),r=.014)
box('Chamber | inset floor',(0,0,1.238),(.48,.48,.026),recess,.008)
# Thick square stone faces with genuinely open round apertures.
for side in range(4):
 vs=[];fs=[];n=48
 for depth in [-.025,.025]:
  for ring in ['outer','inner']:
   for i in range(n):
    a=i/n*math.tau;r=.226/max(abs(math.cos(a)),abs(math.sin(a))) if ring=='outer' else .152
    vs.append((r*math.cos(a),.237+depth,1.487+r*math.sin(a)))
 for i in range(n):
  j=(i+1)%n;fs.extend([(i,j,j+n,i+n),(i+2*n,i+3*n,j+3*n,j+2*n),(i,i+2*n,j+2*n,j),(i+n,j+n,j+3*n,i+3*n)])
 o=mesh('Firebox | pierced stone face',vs,fs,smooth=False);o.rotation_euler.z=side*math.pi/2;bevel(o,.004)
 # Thin bronze muntins are recessed inside the opening.
 for orientation in [0,1]:
  o=box('Firebox | recessed bronze cross',(0,.222,1.487),(.284,.014,.012) if orientation==0 else (.012,.014,.284),bronze,.003);o.rotation_euler.z=side*math.pi/2
  o.location.x=-math.sin(side*math.pi/2)*.222;o.location.y=math.cos(side*math.pi/2)*.222
for x in [-.225,.225]:
 for y in [-.225,.225]:box('Chamber | stone corner post',(x,y,1.484),(.073,.073,.49),r=.011)
box('Light | recessed warm chamber',(0,0,1.487),(.378,.378,.365),light,.01)
box('Chamber | upper lintel',(0,0,1.745),(.58,.58,.063),r=.014)
# A solid curved stone canopy; the eaves rise gently toward all four corners.
N=36;half=.505
vs=[];fs=[]
def roofheight(x,y):
 r=max(abs(x),abs(y))/half
 return 1.988-.196*r+.057*r**6+.045*(abs(x*y)/(half*half))**4
for layer in range(2):
 for j in range(N+1):
  for i in range(N+1):
   x=-half+2*half*i/N;y=-half+2*half*j/N;vs.append((x,y,roofheight(x,y)-layer*.056))
offset=(N+1)**2
for j in range(N):
 for i in range(N):
  k=j*(N+1)+i;fs.extend([(k,k+1,k+N+2,k+N+1),(offset+k+N+1,offset+k+N+2,offset+k+1,offset+k)])
boundary=list(range(N+1))+[j*(N+1)+N for j in range(1,N+1)]+[N*(N+1)+i for i in range(N-1,-1,-1)]+[j*(N+1) for j in range(N-1,0,-1)]
for i,k in enumerate(boundary):nextk=boundary[(i+1)%len(boundary)];fs.append((k,offset+k,offset+nextk,nextk))
o=mesh('Canopy | carved curved stone eaves',vs,fs);bevel(o,.004)
lathe('Crown | lotus collar',1.977,[(0,.105),(.018,.112),(.032,.104),(.044,.082)],n=64)
lathe('Crown | carved bud',2.014,[(0,.078),(.024,.084),(.058,.075),(.097,.054),(.132,.035),(.192,.002)],n=64,flutes=.018)
# Export one original, then instance the identical finished pieces in the native garden.
for o in parts:
 if o.type=='MESH':o.data.validate(clean_customdata=False)
# Keep the original prototype editable in a separate file.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/雕刻石灯笼.blend'))
# Work on copies for material batching, retaining the original prototype file.
for mat in [stone,recess,bronze,light]:
 selected=[o for o in list(bpy.data.objects) if o.type=='MESH' and o.data.materials and o.data.materials[0]==mat]
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=mat.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'stone-lantern.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
placements=[]
for side in [-1,1]:
 for j in [1,7,13,19,25]:placements.append([side*(14.05+.65*math.sin(j*.17)),-10+j*.75,.16,.8])
placements += [[x,y,.18,1] for x,y in [(-4,1),(4,1),(-3,-12.8),(3,-12.8),(-7.5,9),(7.5,9)]]
(A/'stone-lantern.json').write_text(json.dumps({'placements':placements,'height':2.206,'parts':len(parts)},separators=(',',':')))
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
for o in list(bpy.data.objects):
 if o.get('stone_lantern'):bpy.data.objects.remove(o,do_unlink=True)
def contained(points):
 return any(all(abs(p.x-x)<.376*s and abs(p.y-y)<.376*s and z-.006<p.z<z+2.236*s for p in points) for x,y,z,s in placements)
for o in bpy.data.objects:
 if o.type!='MESH' or not any(m and m.name in ['Honed silver granite','Warm paper lantern'] for m in o.data.materials):continue
 bm=bmesh.new();bm.from_mesh(o.data);remove=[f for f in bm.faces if contained([o.matrix_world@v.co for v in f.verts])];bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
with bpy.data.libraries.load(str(R/'source/雕刻石灯笼.blend'),link=False) as (src,dst):dst.objects=src.objects
protos=dst.objects
for index,(x,y,z,s) in enumerate(placements):
 for proto in protos:
  copy=proto.copy();copy.data=proto.data;bpy.context.collection.objects.link(copy);copy.location=Vector((x,y,z))+proto.location*s;copy.scale=proto.scale*s;copy.name=f'Stone lantern {index:02d} | '+proto.name;copy['lantern_index']=index
for o in protos:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
print('STONE LANTERNS COMPLETE',len(placements),'lanterns with',len(parts),'editable pieces each',flush=True)
