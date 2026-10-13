"""A finished Japanese timber bridge, with editable joinery and gilded giboshi caps."""
import bpy,bmesh,math,random,json,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';rng=random.Random(4271)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
objects=[]
def material(name,color,rough,metal=0,wood=False,coat=0,copper=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Coat Weight'].default_value=coat;p.inputs['Coat Roughness'].default_value=.26
 if wood or copper:
  for suffix,slot in [('', 'Base Color'),('-normal','Normal'),('-rough','Roughness')]:
   node=m.node_tree.nodes.new('ShaderNodeTexImage');stem='pbr-rosewood' if wood else 'bridge-copper';ext='png' if copper and suffix=='-normal' else 'jpg';node.image=bpy.data.images.load(str(A/f'{stem}{suffix}.{ext}'),check_existing=True)
   if suffix:node.image.colorspace_settings.name='Non-Color'
   if slot=='Normal':
    normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.48 if wood else .8;m.node_tree.links.new(node.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs[0],p.inputs[slot])
   elif slot=='Base Color':
    mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*color,1);m.node_tree.links.new(node.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],p.inputs[slot])
   else:
    if copper:
     scale=m.node_tree.nodes.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=rough;m.node_tree.links.new(node.outputs['Color'],scale.inputs[0]);m.node_tree.links.new(scale.outputs[0],p.inputs[slot])
    else:m.node_tree.links.new(node.outputs['Color'],p.inputs[slot])
 return m
wood=material('Bridge | oiled rosewood',(.34,.20,.10),.50,wood=True,coat=.16)
railwood=material('Bridge | polished handrails',(.30,.17,.08),.36,wood=True,coat=.28)
bronze=material('Bridge | satin gilded copper',(.64,.40,.105),.50,.90,copper=True)
patina=material('Bridge | recessed bronze',(.16,.11,.045),.85,.74,copper=True)
def finish(o,name,mat):
 o.name=name;o.data.materials.clear();o.data.materials.append(mat);o['bridge_asset']=True;objects.append(o);return o

def uvwood(o,axis):
 uv=o.data.uv_layers.active or o.data.uv_layers.new();offset=rng.random();v=rng.random()
 for p in o.data.polygons:
  second=max((k for k in range(3) if k!=axis),key=lambda k:(1-abs(p.normal[k]))*o.dimensions[k])
  # Grain follows each member's longest axis, with unique board offsets.
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axis]*(.38 if o.data.materials[0] in [wood,railwood] else 1/.24)+offset,co[second]*(.68 if o.data.materials[0] in [wood,railwood] else 1/.24)+v)

def box(name,center,size,mat=wood,bevel=.007):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,mat);o['weighted_bridge']=True;uvwood(o,max(range(3),key=lambda i:size[i]))
 if bevel:
  mod=o.modifiers.new('Hand finished arris','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
  for p in o.data.polygons:p.use_smooth=True
  mod=o.modifiers.new('Weighted planar normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o

def beam(name,a,b,width,depth,mat=wood):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,depth,(b-a).length),mat,min(width,depth)*.13);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def mesh(name,vs,faces,mat,uvs=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);finish(o,name,mat)
 for p in me.polygons:p.use_smooth=True
 if uvs:
  uv=me.uv_layers.new()
  for p in me.polygons:
   for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
 return o

def lathe(name,x,y,z,profile,mat,n=40):
 vs=[];faces=[];chased='lotus bud cap' in name
 if chased:n=96
 for h,r in profile:
  for i in range(n):
   a=i*math.tau/n
   # Eight shallow chased petal channels wrap the bulb, tapering into the neck/tip.
   envelope=max(0,1-((h-.139)/.073)**2) if chased else 0
   groove=(.5+.5*math.cos(8*a+1.4*(h-.1)))**8
   rr=r-.00065*envelope*groove
   vs.append((x+math.cos(a)*rr,y+math.sin(a)*rr,z+h))
 for j in range(len(profile)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]);o=mesh(name,vs,faces,mat)
 uv=o.data.uv_layers.new();circ=math.tau*max(r for h,r in profile)
 for p in o.data.polygons:
  for k,li in enumerate(p.loop_indices):
   vi=o.data.loops[li].vertex_index;ring,i=divmod(vi,n)
   # Seam vertices have separate loop UVs, avoiding a stretched wraparound face.
   if p.index<(len(profile)-1)*n:
    sector=p.index%n;u=(sector+(k in [1,2]))/n;v=profile[ring][0]
    uv.data[li].uv=(u*circ/.24,v/.24)
   else:
    co=o.data.vertices[vi].co;uv.data[li].uv=((co.x-x)/.24,(co.y-y)/.24)
 return o

def pin(name,center,side,r=.012):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=center);o=bpy.context.object;o.scale=(r*.27,r,r) if side else (r,r,r*.27);finish(o,name,bronze)
 for p in o.data.polygons:p.use_smooth=True

def bz(y):return .52+.61*math.sin((y+12.4)/13.3*math.pi)
# Match the existing walkable bridge arch exactly; each board has a softly eased edge.
for j in range(71):
 y=-12.4+j*.188;o=box('Deck board %02d'%j,(0,y,bz(y)),(2.55,.178,.14));o['deck_center_y']=y;o['deck_top']=bz(y)+.07
 # Traditional plugged fixings sit flush rather than protruding as metallic screws.
 for x in [-1.05,1.05]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.018,depth=.003,location=(x,y,bz(y)+.0705));finish(bpy.context.object,'Flush timber dowel',railwood)
# Rounded rectangular rails sweep along the same bridge arch.
def curved_member(name,x,y0,y1,h,width,depth,mat):
 profile=[];radius=min(width,depth)*.22
 for cx,cz,a0 in [(width/2-radius,depth/2-radius,0),(width/2-radius,-depth/2+radius,90),(-width/2+radius,-depth/2+radius,180),(-width/2+radius,depth/2-radius,270)]:
  for j in range(4):a=math.radians(a0+j*30);profile.append((cx+math.sin(a)*radius,cz+math.cos(a)*radius))
 distances=[0.]
 for j in range(1,len(profile)):distances.append(distances[-1]+math.dist(profile[j-1],profile[j]))
 vs=[];uv=[];fs=[];steps=max(5,int((y1-y0)*9));offset=rng.random()
 for i in range(steps+1):
  y=y0+(y1-y0)*i/steps
  for j,(dx,dz) in enumerate(profile):vs.append((x+dx,y,bz(y)+h+dz));uv.append((y*(.38 if mat in [wood,railwood] else 1/.24)+offset,distances[j]*(.68 if mat in [wood,railwood] else 1/.24)))
 n=len(profile)
 for i in range(steps):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple(steps*n+j for j in range(n))]);return mesh(name,vs,fs,mat,uv)
for side in [-1,1]:
 x=side*1.28
 for j in range(15):
  y=-12.3+j*.94;z=bz(y)
  box('Chamfered railing post',(x,y,z+.49),(.16,.16,1.03),wood,.009)
  box('Copper post shoe',(x,y,z+.075),(.184,.184,.145),patina,.008)
  for dz in [.015,.14]:box('Gilded shoe edging',(x,y,z+dz),(.193,.193,.013),bronze,.003)
  box('Copper top collar',(x,y,z+.945),(.181,.181,.065),bronze,.006)
  lathe('Giboshi | lotus bud cap',x,y,z+1.005,[(0,.100),(.012,.104),(.027,.100),(.039,.081),(.054,.068),(.075,.071),(.095,.087),(.119,.092),(.148,.082),(.176,.060),(.203,.027),(.229,.002)],bronze,48)
  # Fine rings and engraved meridians read in grazing highlights.
  for dz,r in [(.013,.105),(.038,.083),(.068,.073)]:
   lathe('Giboshi | turned ring',x,y,z+1.005+dz,[(-.002,r-.002),(0,r+.001),(.003,r-.002)],patina,40)
  for s in [-1,1]:
   pin('Collar rivet',(x+s*.093,y,z+.945),True,.013)
   for dz in [.04,.105]:pin('Shoe rivet',(x+s*.094,y,z+dz),True,.010)
  if j<14:
   y2=y+.94
   for h,w,d,mat in [(.865,.115,.095,railwood),(.335,.082,.080,wood)]:curved_member('Continuous eased handrail' if h>.5 else 'Lower rail',x,y+.068,y2-.068,h,w,d,mat)
   curved_member('Thin handrail copper inlay',x,y+.071,y2-.071,.915,.030,.006,bronze)
   for rising in [True,False]:
    a=y+.095;b=y2-.095;h0=.38 if rising else .80;h1=.80 if rising else .38
    brace=beam('Joined diagonal brace',(x,a,bz(a)+h0),(x,b,bz(b)+h1),.055,.040,wood)
   # The crossing is bound by a small flush bronze boss.
   pin('Brace crossing rosette',(x+side*.025,(y+y2)/2,bz((y+y2)/2)+.59),True,.025)
 for xbeam in [side*1.03]:curved_member('Arched structural stringer',xbeam,-12.45,.82,-.14,.17,.22,wood)
 for j in range(5):
  y=-11.8+j*2.6;box('Pier timber',(side*1.04,y,(-.85+bz(y)-.2)/2),(.21,.21,bz(y)+.65),wood,.013)
# Seat each pier in the same contoured basin used by the pond asset.
import sys
sys.path.insert(0,str(R/'source'))
from pond_basin import extend_pier
bpy.context.view_layer.update()
for o in objects:
 if o.name.startswith('Pier timber'):extend_pier(o)
# Keep all parts editable in the native source before consolidating GPU material batches.
for o in objects:
 if o.type=='MESH':
  o.data.validate(clean_customdata=False);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  if o.get('weighted_bridge'):
   bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Final planar normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/精修木桥.blend'))
meta={'finishTileMeters':.24,'chasedPetalsPerCap':8,'components':len(objects),'deckBoards':71,'posts':30,'materials':4,'deckOrigin':-12.4,'deckSpacing':.188}
for mat in [wood,railwood,bronze,patina]:
 parts=[o for o in list(bpy.data.objects) if o.type=='MESH' and o.data.materials and o.data.materials[0]==mat]
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();bpy.context.object.name=mat.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'bridge.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Carry the timber stain through glTF's portable base-color multiplier.
b=(A/'bridge.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);tail=b[20+n:]
for m in doc['materials']:
 if m['name']==wood.name:m['pbrMetallicRoughness']['baseColorFactor']=[.34,.20,.10,1]
 if m['name']==railwood.name:m['pbrMetallicRoughness']['baseColorFactor']=[.30,.17,.08,1]
 if m['name'] in [bronze.name,patina.name]:
  m['pbrMetallicRoughness']['baseColorFactor']=list(bronze.diffuse_color if m['name']==bronze.name else patina.diffuse_color)
  m['pbrMetallicRoughness']['roughnessFactor']=.50 if m['name']==bronze.name else .85
chunk=json.dumps(doc,separators=(',',':')).encode();chunk+=b' '*((-len(chunk))%4);(A/'bridge.glb').write_bytes(b'glTF'+struct.pack('<II',2,20+len(chunk)+len(tail))+struct.pack('<II',len(chunk),0x4e4f534a)+chunk+tail)
(A/'bridge.json').write_text(json.dumps(meta,indent=2))
# Replace only the old bridge faces in the complete editable native scene.
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
for o in list(bpy.data.objects):
 if o.get('bridge_asset'):bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
 if o.type!='MESH' or not any(m and m.name in ['Polished ebony cedar','Satin gilded bronze'] for m in o.data.materials):continue
 bm=bmesh.new();bm.from_mesh(o.data);remove=[]
 for f in bm.faces:
  p=o.matrix_world@f.calc_center_median()
  if abs(p.x)<1.43 and -12.53<p.y<1.02 and -1<p.z<2.4:remove.append(f)
 bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
with bpy.data.libraries.load(str(R/'source/精修木桥.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
print('BRIDGE COMPLETE',meta,flush=True)
