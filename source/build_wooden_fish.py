"""Original carved wooden fish, hollow slit resonator, mallet and cushion stand."""
import bpy, math, json, shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color,rough,metal=0,texture=None):
 m=bpy.data.materials.new('Muyu | '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/texture));mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.30,.105,.028,1);m.node_tree.links.new(t.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],p.inputs['Base Color'])
 return m
wood=material('satin rosewood',(.36,.14,.043),.34,texture='pbr-rosewood.jpg');rim=material('warm carved endgrain',(.20,.063,.015),.41);dark=material('cavity and eye',(.021,.006,.002),.84);red=material('wine silk cushion',(.20,.009,.017),.87);gold=material('muted gold braid',(.36,.20,.057),.70,.5);felt=material('wound mallet head',(.49,.31,.15),.89)
wood.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.18
parts=[]
def reg(o,name,mat,assembly):
 o.name=name;o.data.materials.append(mat);o['wooden_fish']=True;o['assembly']=assembly;parts.append(o)
 for p in o.data.polygons:p.use_smooth=True
 return o
def sphere(name,loc,scale,mat,assembly='body'):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=40,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return reg(o,name,mat,assembly)
def cube(name,loc,scale,mat,assembly='stand',bevel=.014):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);reg(o,name,mat,assembly)
 if bevel:
  m=o.modifiers.new('Hand softened corners','BEVEL');m.width=bevel;m.segments=4;bpy.ops.object.modifier_apply(modifier=m.name)
 return o
def path(name,pts,r,mat,assembly='body'):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');return reg(bpy.context.object,name,mat,assembly)
def boolean(body,cutter):
 bpy.context.view_layer.objects.active=body;m=body.modifiers.new('Carved open resonator','BOOLEAN');m.operation='DIFFERENCE';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name);parts.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
# Local Z up; bottom of cushion is zero. Round shell is flattened beneath.
body=sphere('Muyu | hollow resonant shell',(0,0,.168),(.205,.169,.147),wood)
boolean(body,sphere('cavity',(0,0,.162),(.169,.133,.110),dark))
boolean(body,cube('mouth',(0,-.165,.143),(.35,.20,.018),dark,'body',.007))
# Paired carved fish cheeks and genuine open mouth, inset round eyes.
for side in [-1,1]:
 cheek=sphere('Muyu | paired fish cheek',(side*.124,-.126,.166),(.041,.018,.042),wood)
 sphere('Muyu | inset eye',(side*.136,-.160,.194),(.007,.002,.007),dark)
 path('Muyu | eye carved rim',[(side*.136+.012*math.cos(a),-.157,.194+.012*math.sin(a)) for a in [j*math.tau/80 for j in range(81)]],.0035,rim)
 for k in range(3):
  path('Muyu | curling cheek relief',[(side*(.119+.035*math.cos(a)), -.155+.012*math.sin(a),.164-k*.015+.019*math.sin(a)) for a in [j*math.pi/48 for j in range(49)]],.0028,rim)
 # Swept low-relief gills curve flush along the resonator sides.
 for k in range(5):
  pts=[]
  for j in range(49):
   t=j/48;a=side*(.48+k*.18+t*.28);p=.48+t*.95
   pts.append((.206*math.sin(p)*math.sin(a),.170*math.sin(p)*math.cos(a),.168+.148*math.cos(p)))
  path('Muyu | flowing carved gills',pts,.0024,rim)
# Rear handle remains part of picked-up body.
path('Muyu | arched tail handle',[(.075*math.cos(a),.146+.035*math.sin(a),.17+.044*math.sin(a)) for a in [j*math.pi/80 for j in range(81)]],.013,wood)
sphere('Muyu | velvet cushion',(0,0,.026),(.251,.213,.036),red,'stand')
path('Muyu | cushion piping',[(.242*math.cos(a),.204*math.sin(a),.028) for a in [j*math.tau/128 for j in range(129)]],.0036,gold,'stand')
# Instrument bottom .021m beds into soft cushion; no floating contact.
# Mallet is an independent assembly, origin defined in the browser at its grip.
path('Muyu | tapered mallet handle',[(.275,-.14,.073),(.24,.01,.075),(.205,.18,.078)],.009,wood,'mallet')
sphere('Muyu | padded mallet head',(.205,.18,.078),(.031,.032,.034),felt,'mallet')
for k in range(9):
 path('Muyu | mallet winding',[(.205+.032*math.cos(a),.18+(k-4)*.006,.078+.034*math.sin(a)) for a in [j*math.tau/48 for j in range(49)]],.0012,gold,'mallet')
# Small carved stand in front-left aisle. All exported assemblies remain local.
cube('Muyu | stand top',(0,0,-.026),(.67,.54,.06),wood)
cube('Muyu | stand apron',(0,0,-.12),(.59,.46,.13),wood)
for x in [-.255,.255]:
 for y in [-.19,.19]:
  cube('Muyu | tapered leg',(x,y,-.315),(.045,.045,.47),wood)
  cube('Muyu | foot',(x,y,-.534),(.066,.065,.025),rim)
for side in [-1,1]:
 path('Muyu | apron cloud carving',[(side*(.055+.16*t),-.234,-.115+.022*math.sin(t*math.tau)) for t in [j/64 for j in range(65)]],.004,gold,'stand')
# Native assembly is positioned as in the live hall; export uses local parts.
source=R/'source/殿内木鱼.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source))
batches={}
for o in parts:batches.setdefault((o.get('assembly'),o.data.materials[0]),[]).append(o)
for (assembly,mat),objs in batches.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();bpy.context.object.name='Muyu_'+assembly+'_'+mat.name.split('|')[-1].strip();bpy.context.object['assembly']=assembly
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'wooden-fish.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True)
# Preserve all existing native scene geometry.
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
for o in list(bpy.data.objects):
 if o.get('wooden_fish'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o);o.location+=Vector((-.95,6.45,1.62))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
print('WOODEN_FISH_READY', (A/'wooden-fish.glb').stat().st_size,flush=True)
