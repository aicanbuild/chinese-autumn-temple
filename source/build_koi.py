"""Build anatomically oriented editable koi meshes and retain them in the temple .blend."""
import bpy, math, random
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets/koi'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def P(p):return (p[0],-p[2],p[1]) # model space x / up / forward -> Blender

def mat(name,color,rough=.4,tex=None,alpha=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if tex:
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(A/tex),check_existing=True);m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
  if alpha:m.node_tree.links.new(node.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED';m.use_transparency_overlap=False
 return m
skins={}
for k in ['kohaku','sanke','yamabuki','platinum']:
 m=mat('Koi '+k,(.7,.6,.4),tex=k+'.jpg');p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.24;p.inputs['Coat Roughness'].default_value=.27
 n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(A/'scales-normal.jpg'),check_existing=True);n.image.colorspace_settings.name='Non-Color';b=m.node_tree.nodes.new('ShaderNodeNormalMap');b.inputs['Strength'].default_value=.35;m.node_tree.links.new(n.outputs['Color'],b.inputs['Color']);m.node_tree.links.new(b.outputs[0],p.inputs['Normal']);skins[k]=m
finmat=mat('Translucent fin rays',(.7,.65,.45),.48,'fin-membrane.png',True)
eye=mat('Koi glossy black pupil',(.008,.012,.010),.13);iris=mat('Koi bronze iris',(.37,.28,.09),.29);lip=mat('Soft ivory koi lips',(.64,.58,.42),.5);gill=mat('Gill seam',(.19,.14,.085),.65)
proto=bpy.data.objects.new('Koi_kohaku',None);bpy.context.collection.objects.link(proto)
def mesh(name,vs,fs,uvs,material):
 me=bpy.data.meshes.new(name);me.from_pydata([P(p) for p in vs],[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=proto;me.materials.append(material)
 if uvs:
  uv=me.uv_layers.new(name='UVMap')
  for poly in me.polygons:
   for li in poly.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
 for p in me.polygons:p.use_smooth=True
 return ob

def sphere(name,c,s,material,n=20,lat=14):
 vs=[];uv=[];fs=[]
 for j in range(lat+1):
  ph=j*math.pi/lat
  for i in range(n+1):
   a=i*math.tau/n;vs.append((c[0]+s[0]*math.sin(ph)*math.cos(a),c[1]+s[1]*math.cos(ph),c[2]+s[2]*math.sin(ph)*math.sin(a)));uv.append((i/n,j/lat))
 for j in range(lat):
  for i in range(n):a=j*(n+1)+i;fs.append((a,a+1,a+n+2,a+n+1))
 return mesh(name,vs,fs,uv,material)
def curve(name,points,r,material):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=3;cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*P(co),1)
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.parent=proto;cu.materials.append(material)
 return ob
# Smooth body profile has broad shoulders, narrower head, and a defined tail peduncle.
profile=[(0,.022),(.10,.034),(.27,.097),(.49,.158),(.66,.166),(.79,.138),(.90,.097),(.97,.052),(1,.006)]
def radius(t):
 for (a,r),(b,q) in zip(profile,profile[1:]):
  if a<=t<=b:
   f=(t-a)/(b-a);f=f*f*(3-2*f);return r+(q-r)*f
 return .006
vs=[];uv=[];fs=[];rows=72;sides=48
for j in range(rows+1):
 t=j/rows;z=t*1.25-.6;r=radius(t)
 for i in range(sides+1):
  a=i*math.tau/sides;up=math.sin(a);vs.append((math.cos(a)*r,up*r*(.86 if up>0 else .69),z));uv.append((i/sides,t))
for j in range(rows):
 for i in range(sides):a=j*(sides+1)+i;fs.append((a,a+1,a+sides+2,a+sides+1))
mesh('Body | scale relief and continuous flex',vs,fs,uv,skins['kohaku'])
# Each fin is a curved membrane with intermediate vertices, enabling smooth deformation.
def fin(name,root,edge):
 vs=[];uv=[];fs=[];steps=7
 for j in range(steps+1):
  t=j/steps
  for i,e in enumerate(edge):
   p=Vector(root).lerp(Vector(e),t);p.x+=math.sin(t*math.pi)*.008
   vs.append(tuple(p));uv.append((i/(len(edge)-1),t))
 for j in range(steps):
  for i in range(len(edge)-1):a=j*len(edge)+i;fs.append((a,a+1,a+len(edge)+1,a+len(edge)))
 return mesh(name,vs,fs,uv,finmat)
edge=[]
for i in range(33):
 a=i/32*math.pi;y=.235*math.cos(a);z=-.83-.17*abs(math.cos(a))**1.25;edge.append((.009*math.sin(a*2),y,z))
fin('Caudal fin | vertical forked tail',(0,0,-.56),edge)
for side in [-1,1]:
 edge=[]
 for i in range(25):
  a=i/24;edge.append((side*(.13+math.sin(a*math.pi)*.235),-.045-.026*math.sin(a*math.pi),.32-a*.38))
 fin('Pectoral fin '+str(side),(side*.115,-.025,.29),edge)
 edge=[(side*(.078+math.sin(i/16*math.pi)*.135),-.07-.025*math.sin(i/16*math.pi),-.13-i/16*.25) for i in range(17)]
 fin('Pelvic fin '+str(side),(side*.08,-.065,-.15),edge)
 # Iris and pupil are separately modeled so grazing highlights remain crisp.
 sphere('Iris '+str(side),(side*.093,.042,.462),(.027,.027,.023),iris)
 sphere('Pupil '+str(side),(side*.113,.046,.469),(.010,.018,.017),eye)
 # A recessed curved gill edge follows the shoulder surface.
 pts=[]
 for i in range(21):
  a=-.6+i/20*1.75;pts.append((side*(.134*math.cos(a)),.117*math.sin(a),.323+.032*math.cos(a)))
 curve('Operculum crease '+str(side),pts,.0028,gill)
 for z,reach in [(.586,.10),(.55,.065)]:
  a=Vector((side*.041,-.034,z));b=Vector((side*.068,-.051,z+.055));c=Vector((side*reach,-.063,z+.023))
  curve('Sensory barbel '+str(side),[tuple((1-t)**2*a+2*(1-t)*t*b+t*t*c) for t in [i/16 for i in range(17)]],.0025,lip)
fin('Dorsal fin',(0,.092,-.05),[(0,.095,-.36),(0,.15,-.30),(0,.23,-.10),(0,.252,.11),(0,.20,.27),(0,.126,.30)])
fin('Anal fin',(0,-.06,-.27),[(0,-.07,-.41),(0,-.17,-.42),(0,-.18,-.34),(0,-.075,-.21)])
# Small subterminal mouth with soft upper/lower lip, never a painted black dot.
sphere('Mouth opening',(0,-.026,.639),(.026,.012,.004),gill)
pts=[(.029*math.cos(i*math.tau/40),-.026+.015*math.sin(i*math.tau/40),.642) for i in range(41)]
curve('Mouth rim',pts,.0039,lip)
# Convert curves for web export; four species share mesh data except for the body material.
for ob in list(proto.children):
 if ob.type=='CURVE':
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
variants=[proto]
for k in ['sanke','yamabuki','platinum']:
 root=bpy.data.objects.new('Koi_'+k,None);bpy.context.collection.objects.link(root);variants.append(root)
 for ob in proto.children:
  cp=ob.copy();cp.data=ob.data;cp.parent=root;bpy.context.collection.objects.link(cp)
  if ob.name.startswith('Body'):
   cp.data=ob.data.copy();cp.data.materials.clear();cp.data.materials.append(skins[k])
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(A/'koi.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/锦鲤.blend'))
# Append the editable fish into the complete native temple scene, beneath the water surface.
temple=R/'source/听秋寺院.blend'
if temple.exists():
 bpy.ops.wm.open_mainfile(filepath=str(temple))
 for ob in list(bpy.data.objects):
  if ob.get('detailed_koi'):bpy.data.objects.remove(ob,do_unlink=True)
 with bpy.data.libraries.load(str(R/'source/锦鲤.blend'),link=False) as (src,dst):dst.objects=src.objects
 imported=[o for o in dst.objects if o]
 for o in imported:bpy.context.collection.objects.link(o);o['detailed_koi']=True
 roots=[o for o in imported if o.parent is None]
 random.seed(71127)
 for i in range(16):
  root=roots[i%len(roots)];a=i*math.tau/16
  inst=root if i<4 else root.copy()
  if i>=4:
   bpy.context.collection.objects.link(inst)
   for child in root.children:
    ob=child.copy();ob.data=child.data;ob.parent=inst;bpy.context.collection.objects.link(ob);ob['detailed_koi']=True
  inst.location=(math.cos(a)*(4+i%4),-5.8+math.sin(a)*(2.4+i%3*.5),-.38-i%4*.05);inst.rotation_euler.z=a+.8;inst.scale=(.78,)*3;inst['detailed_koi']=True
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple))
print('Detailed koi exported and appended to editable temple scene.',flush=True)
