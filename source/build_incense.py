"""Editable hollow bronze koro, chased lotus relief, scroll ears and granular ash."""
import bpy,bmesh,math,random,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';random.seed(837)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
parts=[]
def material(name,color,metal,rough,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  for suffix,ext,slot in [('', 'jpg','Base Color'),('-normal','png','Normal'),('-rough','jpg','Roughness')]:
   t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/f'{texture}{suffix}.{ext}'),check_existing=True)
   if suffix:t.image.colorspace_settings.name='Non-Color'
   if slot=='Normal':
    normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.55;m.node_tree.links.new(t.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
   else:m.node_tree.links.new(t.outputs['Color'],p.inputs[slot])
 return m
bronze=material('Koro | fine cast bronze',(.33,.20,.076),.86,.43,'incense-bronze')
polished=material('Koro | burnished chased edges',(.49,.29,.083),.87,.32)
recess=material('Koro | dark bronze recesses',(.062,.043,.024),.65,.62)
ash=material('Koro | granular incense ash',(.58,.55,.48),0,.97,'incense-ash')
def register(o,name,mat):
 o.name=name;o['incense_vessel']=True;o.data.materials.clear();o.data.materials.append(mat);parts.append(o)
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o

def mesh(name,vs,fs,mat=bronze,uvfn=None):
 g=bpy.data.meshes.new(name);g.from_pydata(vs,[],fs);g.update();o=bpy.data.objects.new(name,g);bpy.context.collection.objects.link(o);register(o,name,mat)
 bm=bmesh.new();bm.from_mesh(g);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(g);bm.free()
 uv=g.uv_layers.new()
 for p in g.polygons:
  for li in p.loop_indices:
   v=g.vertices[g.loops[li].vertex_index].co;uv.data[li].uv=uvfn(v) if uvfn else (v.x*3+.5,v.y*3+.5)
 return o

def curve(name,points,r,mat=polished):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=3
 s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,v in zip(s.points,points):p.co=(*v,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);register(o,name,mat);return o

def ellipsoid(name,loc,size,mat=bronze,segments=32,rings=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return register(o,name,mat)

def bezier(a,b,c,d,n=36):
 a,b,c,d=map(Vector,[a,b,c,d]);return [(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in [i/n for i in range(n+1)]]
# Smooth outer and inner profiles are joined at the lip and base: real wall thickness.
profile=[(.006,.145),(.11,.145),(.21,.166),(.285,.202),(.335,.256),(.354,.318),(.350,.371),(.330,.415),(.327,.437),(.340,.446),(.341,.462),(.332,.472),(.313,.470),(.307,.457),(.311,.441),(.311,.417),(.329,.372),(.332,.316),(.314,.261),(.263,.211),(.184,.182),(.085,.167),(.006,.167)]
# Catmull interpolation preserves the gently compressed spherical bowl silhouette.
profiles=[]
for i in range(len(profile)-1):
 p0=Vector(profile[max(i-1,0)]);p1=Vector(profile[i]);p2=Vector(profile[i+1]);p3=Vector(profile[min(i+2,len(profile)-1)])
 for j in range(5):
  t=j/5;p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t);profiles.append(p)
profiles.append(Vector(profile[-1]));n=144;vs=[];fs=[]
for r,z in profiles:
 for j in range(n):
  a=j*math.tau/n;vs.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(profiles)-1):
 for j in range(n):a=k*n+j;b=k*n+(j+1)%n;fs.append((a,b,b+n,a+n))
fs.extend([tuple(reversed(range(n))),tuple((len(profiles)-1)*n+j for j in range(n))])
body=mesh('Vessel | continuous inner and outer bronze wall',vs,fs,uvfn=lambda p:(math.atan2(p.y,p.x)/math.tau+.5,p.z*2.5))
# Thin turned rings and beadwork, never huge outlines.
for z,r,thick in [(.443,.335,.005),(.466,.331,.004),(.404,.337,.003),(.221,.307,.003)]:curve('Rim | turned burnished wire',[(r*math.cos(a),r*math.sin(a),z) for a in [j*math.tau/144 for j in range(145)]],thick)
for j in range(72):
 a=j*math.tau/72;ellipsoid('Collar | bronze bead',(math.cos(a)*.341,math.sin(a)*.341,.411),(.004,.004,.0045),polished,12,8)
# Three curved supports, rounded pads, and narrow toe incisions.
for j in range(3):
 a=-math.pi/2+j*math.tau/3
 def radial(r,z):return(r*math.cos(a),r*math.sin(a),z)
 pts=bezier(radial(.21,.177),radial(.20,.105),radial(.30,.09),radial(.275,.029),40)
 curve('Foot | cabriole bronze support',pts,.028,bronze)
 pad=ellipsoid('Foot | rounded resting pad',radial(.276,.022),(.045,.055,.022),bronze);pad.rotation_euler.z=a
 for offset in [-.014,.014]:
  pts=[((.273+t*.031)*math.cos(a)-offset*math.sin(a),(.273+t*.031)*math.sin(a)+offset*math.cos(a),.034-.016*t) for t in [k/10 for k in range(11)]];curve('Foot | shallow chased division',pts,.0014,recess)
# Scroll handles are fully open, with sockets that intersect the bowl wall.
for side in [-1,1]:
 pts=bezier((side*.321,0,.345),(side*.55,0,.345),(side*.535,0,.575),(side*.43,0,.567))
 pts+=bezier((side*.43,0,.567),(side*.368,0,.562),(side*.37,0,.484),(side*.41,0,.491))[1:]
 curve('Ear | open returning scroll',pts,.019,bronze)
 curve('Ear | chased front ridge',[(p.x,-.018,p.z) for p in pts],.0024,polished)
 ellipsoid('Ear | cast socket',(side*.328,0,.35),(.028,.040,.055),bronze)
 ellipsoid('Ear | scroll terminal',(side*.410,0,.491),(.023,.020,.022),polished)
# Low relief lotus medallions conform to the curved body; no floating decoration.
def outer(z):
 p=[(r,z0) for r,z0 in profile[:8]]
 for i in range(len(p)-1):
  if p[i][1]<=z<=p[i+1][1]:
   t=(z-p[i][1])/(p[i+1][1]-p[i][1]);return p[i][0]*(1-t)+p[i+1][0]*t
 return .34
for j in range(3):
 angle=-math.pi/2+j*math.tau/3
 def surface(u,v,depth=.004):
  z=.314+v;r=outer(z)+depth;a=angle+u/max(r,.01);return(r*math.cos(a),r*math.sin(a),z)
 for rad,wire in [(.068,.0024),(.073,.0014)]:curve('Chasing | medallion border',[surface(math.cos(a)*rad,math.sin(a)*rad,.008) for a in [k*math.tau/100 for k in range(101)]],wire)
 for petal in range(8):
  angle2=petal*math.tau/8;pts=[]
  for k in range(49):
   t=k/48*math.tau;u=.021*math.sin(t);v=.031*(1-math.cos(t));xx=u*math.cos(angle2)-v*math.sin(angle2);zz=u*math.sin(angle2)+v*math.cos(angle2);pts.append(surface(xx,zz,.010))
  curve('Chasing | lotus petal',pts,.0021)
 curve('Chasing | central lotus heart',[surface(.012*math.cos(a),.012*math.sin(a),.011) for a in [k*math.tau/48 for k in range(49)]],.003)
# Ash is recessed below the lip, with a slight mound and fine geometric granularity.
n=144;rings=32;vs=[(0,0,.416)];fs=[]
for k in range(1,rings+1):
 r=.311*k/rings
 for j in range(n):
  a=j*math.tau/n;x=r*math.cos(a);y=r*math.sin(a);h=.414+.004*math.exp(-(r/.17)**2)+.0005*math.sin(a*7+r*130)+random.uniform(-.0005,.0005);vs.append((x,y,h))
for j in range(n):fs.append((0,1+j,1+(j+1)%n))
for k in range(rings-1):
 for j in range(n):a=1+k*n+j;b=1+k*n+(j+1)%n;fs.append((a,b,b+n,a+n))
mesh('Ash | subtly uneven recessed surface',vs,fs,ash,uvfn=lambda p:(p.x/.64+.5,p.y/.64+.5))
for j in range(65):
 a=random.random()*math.tau;r=math.sqrt(random.random())*.29;x=r*math.cos(a);y=r*math.sin(a);size=random.uniform(.0009,.0028)
 vs=[(x+math.cos(t)*size,y+math.sin(t)*size,.418+random.uniform(-.0002,.0003)) for t in [k*math.tau/5 for k in range(5)]];mesh('Ash | spent charcoal fleck',vs,[(0,1,2,3,4)],recess)
# World-space placement matches the physical ash and three animated incense sticks.
for o in parts:o.location+=Vector((0,6.6,1.10))
prototype=R/'source/铸铜香炉.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(prototype));components=len(parts)
# Export four compact material batches, retaining editable source components.
for o in list(parts):
 if o.type=='CURVE':bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
for mat in [bronze,polished,recess,ash]:
 bpy.ops.object.select_all(action='DESELECT');selected=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0]==mat]
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=mat.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'incense-vessel.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Native scene replacement is confined to the original vessel footprint.
temple=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-incense.blend'
if not backup.exists():shutil.copy2(temple,backup)
bpy.ops.wm.open_mainfile(filepath=str(temple));preserved={o.name for o in bpy.data.objects if not o.get('incense_vessel') and not o.get('native_incense_stick')}
for o in list(bpy.data.objects):
 if o.get('incense_vessel') or o.get('native_incense_stick'):bpy.data.objects.remove(o,do_unlink=True)
def inside(p):return abs(p.x)<.57 and abs(p.y-6.6)<.43 and 1.0<p.z<2.04
removed=0
for o in bpy.data.objects:
 if o.type!='MESH' or not any(m and ('gilded' in m.name.lower() or 'cedar' in m.name.lower()) for m in o.data.materials):continue
 bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if all(inside(o.matrix_world@v.co) for v in f.verts)]
 removed+=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
# Native unlit sticks have the same length, placement and diameter as runtime sticks.
wood=material('Incense | compressed fragrant powder',(.24,.117,.04),0,.91)
for i in range(3):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.006,depth=.52,location=((i-1)*.095,6.6-(-.07 if i==1 else .03),1.78));o=bpy.context.object;o.name='Incense | unlit replaceable stick';o['native_incense_stick']=True;o.data.materials.append(wood)
assert preserved.issubset({o.name for o in bpy.data.objects})
bounce=bpy.data.objects.get('Main hall | entrance bounce')
if bounce is None:
 bpy.ops.object.light_add(type='AREA',location=(-1.3,4.6,2.8));bounce=bpy.context.object;bounce.name='Main hall | entrance bounce'
bounce.data.energy=45;bounce.data.shape='DISK';bounce.data.size=2.6;bounce.rotation_euler=(Vector((0,6.6,1.4))-bounce.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple))
meta={'components':components,'materials':4,'ashHeight':1.514,'stickBase':1.52,'position':[0,1.10,-6.6],'removedNativeFaces':removed,'preservedObjects':len(preserved)};(A/'incense-vessel.json').write_text(json.dumps(meta,indent=2));print('INCENSE_VESSEL',meta,flush=True)
