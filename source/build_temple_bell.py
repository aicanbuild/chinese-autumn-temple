"""Original hollow cast-bronze bell with a suspended horizontal timber striker."""
import bpy,bmesh,math,json,shutil,hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';CX,CY=-9,4.1
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
parts=[]
def mat(name,color,metal,rough,texture=None):
 m=bpy.data.materials.new('Temple bell | '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  for suffix,ext,slot in [('', 'jpg','Base Color'),('-normal','png','Normal'),('-rough','jpg','Roughness')]:
   file=A/f'{texture}{suffix}.{ext}'
   if not file.exists():continue
   t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(file),check_existing=True)
   if suffix:t.image.colorspace_settings.name='Non-Color'
   if slot=='Normal':
    n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.22;m.node_tree.links.new(t.outputs[0],n.inputs['Color']);m.node_tree.links.new(n.outputs[0],p.inputs[slot])
   else:m.node_tree.links.new(t.outputs[0],p.inputs[slot])
 return m
bronze=mat('cast bronze',(.30,.19,.075),.88,.43,'incense-bronze');gold=mat('polished raised lines',(.46,.28,.082),.9,.31);wood=mat('timber striker',(.16,.07,.024),0,.58,'pbr-rosewood');rope=mat('braided hemp',(.25,.19,.105),0,.95);iron=mat('forged iron bindings',(.07,.063,.048),.7,.54)
def group(name,p):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=p;o['temple_bell']=True;bpy.context.view_layer.update();return o
bodyGroup=group('Bell_Body',(CX,CY,3.45));hammerGroup=group('Bell_Hammer',(-7.75,CY,2.2));ropeGroups=[group('Bell_Rope_'+str(i),(-7.75+offset,CY,3.45)) for i,offset in enumerate([-.32,.32])]
def reg(o,name,material,parent=bodyGroup):
 o.name=name;o['temple_bell']=True;o.data.materials.append(material);o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted();parts.append(o);return o

def mesh(name,vs,fs,material=bronze,parent=bodyGroup):
 g=bpy.data.meshes.new(name);g.from_pydata(vs,[],fs);g.update();o=bpy.data.objects.new(name,g);bpy.context.collection.objects.link(o)
 bm=bmesh.new();bm.from_mesh(g);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(g);bm.free()
 uv=g.uv_layers.new();
 for p in g.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   v=g.vertices[g.loops[li].vertex_index].co;uv.data[li].uv=((math.atan2(v.y-CY,v.x-CX)/math.tau+.5)*3,v.z*2)
 return reg(o,name,material,parent)
def path(name,points,r,material=gold,parent=bodyGroup):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=3;c.use_fill_caps=True;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,v in zip(s.points,points):p.co=(*v,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);return reg(o,name,material,parent)
def sphere(name,p,scale,material=bronze,parent=bodyGroup):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=p);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 return reg(o,name,material,parent)
def ring(name,r,z,thick=.008,material=gold):return path(name,[(CX+r*math.cos(a),CY+r*math.sin(a),z) for a in [i*math.tau/144 for i in range(145)]],thick,material)
outer=[(.605,1.64),(.611,1.67),(.595,1.70),(.566,1.76),(.531,1.86),(.509,2.0),(.494,2.25),(.480,2.50),(.469,2.69),(.434,2.80),(.367,2.89),(.265,2.96),(.14,3.005),(.005,3.025)]
inner=[(.005,2.982),(.14,2.963),(.247,2.916),(.34,2.849),(.404,2.761),(.431,2.667),(.442,2.50),(.457,2.25),(.472,2),(.49,1.86),(.526,1.76),(.55,1.70),(.556,1.64)]
# Smooth profile interpolation, with a solid annular lip and genuine inner cavity.
def smooth(profile):
 out=[]
 for i in range(len(profile)-1):
  a,b,c,d=[Vector(profile[max(0,min(len(profile)-1,j))]) for j in [i-1,i,i+1,i+2]]
  for k in range(5):
   t=k/5;out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 return out+[Vector(profile[-1])]
profile=smooth(outer)+smooth(inner);N=144;vs=[(CX+r*math.cos(j*math.tau/N),CY+r*math.sin(j*math.tau/N),z) for r,z in profile for j in range(N)];fs=[]
for k in range(len(profile)):
 for j in range(N):a=k*N+j;b=k*N+(j+1)%N;c=((k+1)%len(profile))*N;fs.append((a,b,c+(j+1)%N,c+j))
body=mesh('Bell | continuous hollow bronze shell',vs,fs)
for r,z,t in [(.610,1.671,.009),(.559,1.775,.006),(.502,2.09,.007),(.474,2.60,.006),(.452,2.75,.008),(.318,2.935,.006)]:ring('Bell | turned moulding',r,z,t)
def radius(z):
 for a,b in zip(outer,outer[1:]):
  if a[1]<=z<=b[1]:return a[0]+(b[0]-a[0])*(z-a[1])/(b[1]-a[1])
 return .48
# Four panels of low bosses and fine dividing ribs, directly seated in the casting.
for sector in range(4):
 center=sector*math.pi/2
 for i in range(4):
  for j in range(4):
   a=center+(i-1.5)*.13;z=2.24+j*.09;r=radius(z)-.008
   sphere('Bell | cast shoulder boss',(CX+r*math.cos(a),CY+r*math.sin(a),z),(.019,.019,.025))
 for offset in [-.40,.40]:
  path('Bell | raised panel rib',[(CX+(radius(z)+.003)*math.cos(center+offset),CY+(radius(z)+.003)*math.sin(center+offset),z) for z in [2.10+i*.50/30 for i in range(31)]],.004)
# Lotus striking seats face the hammer and its opposite; eight scalloped petals each.
for direction in [0,math.pi]:
 for j in range(8):
  angle=j*math.tau/8;pts=[]
  for i in range(49):
   t=i*math.tau/48;u=.09*math.cos(angle)+.053*math.cos(t)*math.cos(angle)-.028*math.sin(t)*math.sin(angle);v=.09*math.sin(angle)+.053*math.cos(t)*math.sin(angle)+.028*math.sin(t)*math.cos(angle)
   z=2.22+v;a=direction+u/.5;r=radius(z)+.007;pts.append((CX+r*math.cos(a),CY+r*math.sin(a),z))
  path('Bell | lotus strike petal',pts,.006)
 sphere('Bell | solid lotus striking boss',(CX+.492*math.cos(direction),CY+.492*math.sin(direction),2.22),(.024,.064,.064),gold)
# Open paired crown scrolls carry the suspension eye; no arbitrary written text.
for side in [-1,1]:
 pts=[]
 for i in range(65):
  t=i/64;pts.append((CX+side*(.28*(1-t)),CY,3.0+.27*math.sin(t*math.pi/2)))
 path('Bell | crown scroll handle',pts,.035,bronze)
 path('Bell | chased crown spine',[(x,y-.032,z+.006) for x,y,z in pts],.005)
 sphere('Bell | crown socket',(CX+side*.265,CY,3.015),(.07,.056,.04),bronze)
path('Bell | iron suspension eye',[(CX,CY+.071*math.cos(a),3.335+.12*math.sin(a)) for a in [i*math.tau/96 for i in range(97)]],.022,iron)
# Horizontal log with capped endgrain; separate rope pivots preserve fixed anchors.
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.105,depth=1.05,location=(-7.75,CY,2.2),rotation=(0,math.pi/2,0));o=bpy.context.object;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bevel=o.modifiers.new('Rounded timber ends','BEVEL');bevel.width=.012;bevel.segments=3;reg(o,'Striker | timber log',wood,hammerGroup)
for offset in [-.32,.32]:
 path('Striker | iron collar',[(-7.75+offset,CY+.108*math.cos(a),2.2+.108*math.sin(a)) for a in [i*math.tau/80 for i in range(81)]],.015,iron,hammerGroup)
for i,offset in enumerate([-.32,.32]):
 for strand in range(3):
  pts=[]
  for j in range(161):
   t=j/160;a=t*math.tau*18+strand*math.tau/3;pts.append((-7.75+offset+.009*math.cos(a),CY+.009*math.sin(a),3.45-1.25*t))
  path('Striker | braided suspension',pts,.006,rope,ropeGroups[i])
# Pull cord belongs to the log and remains visibly connected to it.
path('Striker | hanging pull cord',[(-7.30+.012*math.sin(t*40),CY,2.18-t*.72) for t in [i/80 for i in range(81)]],.013,rope,hammerGroup)
path('Striker | pull loop',[(-7.30+.075*math.cos(a),CY,1.40+.085*math.sin(a)) for a in [i*math.tau/64 for i in range(65)]],.012,rope,hammerGroup)
# Verify shell thickness topology before save; source retains individually editable parts.
bm=bmesh.new();bm.from_mesh(body.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>0;assert all(f.calc_area()>1e-12 for f in bm.faces);bm.free()
bpy.context.view_layer.update();bpy.ops.file.pack_all();source=R/'source/铸铜寺钟.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source))
report={'parts':len(parts),'shellClosedManifold':True,'ropeLength':1.25,'strikerRestCenterNative':[-7.75,CY,2.2],'contactAngle':math.asin((.515-.725)/1.25)}
(A/'temple-bell.json').write_text(json.dumps(report,indent=2))
# Batch each independently moving assembly by material.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
for parent in [bodyGroup,hammerGroup,*ropeGroups]:
 for material in [bronze,gold,wood,rope,iron]:
  selected=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==parent and o.data.materials and o.data.materials[0]==material]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=parent.name+' | '+material.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'temple-bell.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Replace only old bell/striker faces in the complete editable temple.
temple=R/'source/听秋寺院.blend';backup=temple.with_name('听秋寺院-before-temple-bell.blend')
if not backup.exists():shutil.copy2(temple,backup)
bpy.ops.wm.open_mainfile(filepath=str(temple))
def selected(name,p):
 if 'gilded' in name.lower() or 'gold' in name.lower():return -9.7<p.x<-8.3 and 1.60<p.z<3.48 and 3.35<p.y<4.85
 if 'cedar' in name.lower():return -8.43<p.x<-8.17 and 2.22<p.z<2.48 and 3.08<p.y<4.73
 if 'deep dark wood' in name.lower():return -8.33<p.x<-8.27 and 2.32<p.z<3.62 and 3.25<p.y<4.65
 return False
removed=0
for o in list(bpy.data.objects):
 if o.get('temple_bell'):bpy.data.objects.remove(o,do_unlink=True);continue
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);take=[f for f in bm.faces if selected(o.data.materials[f.material_index].name if o.data.materials else '',o.matrix_world@f.calc_center_median())];removed+=len(take)
 if take:bmesh.ops.delete(bm,geom=take,context='FACES');bm.to_mesh(o.data)
 bm.free()
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:bpy.context.collection.objects.link(o)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple));bpy.ops.wm.open_mainfile(filepath=str(temple));assert sum(bool(o.get('temple_bell')) for o in bpy.data.objects)==len(parts)+4
report['removedLegacyFaces']=removed;report['nativePartsReopened']=len(parts)+4;(R/'evidence/temple-bell-native.json').write_text(json.dumps(report,indent=2));print('TEMPLE BELL',report,flush=True)
