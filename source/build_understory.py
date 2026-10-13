"""Linked, small-leaf woodland shrubs on the actual sculpted terrain surface."""
import bpy,math,random,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';rng=random.Random(82517)
full=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-understory.blend'
if not backup.exists():shutil.copy2(full,backup)
bpy.ops.wm.open_mainfile(filepath=str(full));terrain=next(o for o in bpy.data.objects if o.name.startswith('Sculpted woodland terrain'))
def ground(x,y):
 inv=terrain.matrix_world.inverted();hit,p,normal,index=terrain.ray_cast(inv@Vector((x,y,150)),Vector((0,0,-1)))
 assert hit,(x,y);return (terrain.matrix_world@p).z
centers=[]
# Drifts follow the woodland edge; the axial approach and all paths remain open.
for cluster in range(42):
 a=rng.uniform(-.12,math.pi+.12);radius=rng.uniform(23,52)
 # Native +Y is behind the main hall; side planting stops before the front approach.
 cx=math.cos(a)*radius;cy=math.sin(a)*radius
 for j in range(rng.randint(3,6)):
  x=cx+rng.uniform(-3,3);y=cy+rng.uniform(-2.5,2.5);r=math.hypot(x,y)
  if r<22 or r>55 or (y<10 and abs(x)<19):continue
  if any(math.hypot(x-p[0],y-p[1])<1.45 for p in centers):continue
  z=ground(x,y);slope=max(abs(ground(x+dx,y+dy)-z) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
  if slope>1.0:continue
  centers.append([round(x,3),round(y,3),round(z-.025,4),round(rng.uniform(.70,1.25),3),round(rng.uniform(0,math.tau),4),rng.randrange(3)])
for existing in list(bpy.data.objects):bpy.data.objects.remove(existing,do_unlink=True)
def material(name,leaf=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.69 if leaf else .9
 if leaf:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(A/'green-leaf.png'));v=m.node_tree.nodes.new('ShaderNodeVertexColor');v.layer_name='Pigment'
  mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;m.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(v.outputs['Color'],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],p.inputs['Base Color'])
  nm=m.node_tree.nodes.new('ShaderNodeTexImage');nm.image=bpy.data.images.load(str(A/'green-leaf-normal.png'));nm.image.colorspace_settings.name='Non-Color';normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.3;m.node_tree.links.new(nm.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs[0],p.inputs['Normal'])
  m.use_backface_culling=False
 else:p.inputs['Base Color'].default_value=(.065,.05,.024,1)
 return m
leafmat=material('Understory | waxed evergreen leaf',True);woodmat=material('Understory | fine brown twigs')
def mesh(name,vs,fs,mat,uvs=None,colors=None):
 data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update();data.materials.append(mat);o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o['understory_asset']=True
 for p in data.polygons:p.use_smooth=True
 if uvs:
  uv=data.uv_layers.new()
  for p in data.polygons:
   for li in p.loop_indices:uv.data[li].uv=uvs[data.loops[li].vertex_index]
 if colors:
  color=data.color_attributes.new(name='Pigment',type='FLOAT_COLOR',domain='POINT')
  for c,v in zip(color.data,colors):c.color=v
 return o
prototypes=[];leafcounts=[]
for variant in range(3):
 rng=random.Random(592+variant*317);root=bpy.data.objects.new(f'Understory_{variant}',None);bpy.context.collection.objects.link(root)
 vs=[];fs=[];uv=[];cols=[];wv=[];wf=[];leafcount=0
 def tube(a,b,r1,r2):
  a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');n=len(wv)
  for c,r in [(a,r1),(b,r2)]:
   for k in range(5):wv.append(tuple(c+q@Vector((r*math.cos(k*math.tau/5),r*math.sin(k*math.tau/5),0))))
  for k in range(5):wf.append((n+k,n+(k+1)%5,n+(k+1)%5+5,n+k+5))
 def leaf(base,direction,length):
  global leafcount
  d=direction.normalized();side=d.cross(Vector((0,0,1))).normalized();normal=side.cross(d).normalized();width=length*rng.uniform(.27,.36)
  # Six-sided silhouette and raised midrib: no alpha cards or opaque background quads.
  outline=[(0,0),(.27,-.82),(.62,-1), (1,0),(.62,1),(.27,.82)]
  off=len(vs);shade=rng.uniform(.58,.93);pigment=(shade*.71,shade*.92,shade*.70,1)
  for t,s in outline:
   pos=base+d*length*t+side*width*s+normal*(.10*length*t*t);vs.append(tuple(pos));uv.append((.5+s*.25,.08+t*.84));cols.append(pigment)
  vs.append(tuple(base+d*length*.50+normal*.075*length));uv.append((.5,.5));cols.append((pigment[0]*.85,pigment[1]*.9,pigment[2]*.85,1))
  for k in range(6):fs.append((off+k,off+(k+1)%6,off+6))
  leafcount+=1
 for stem in range(12):
  angle=stem*2.399+variant*.8;spread=rng.uniform(.48,.97);h=rng.uniform(.67,1.13)*(1+.16*variant)
  start=Vector((rng.uniform(-.09,.09),rng.uniform(-.09,.09),-.06));mid=Vector((math.cos(angle)*spread*.35,math.sin(angle)*spread*.35,h*.54));end=Vector((math.cos(angle)*spread,math.sin(angle)*spread,h))
  tube(start,mid,.018,.009);tube(mid,end,.009,.003)
  for shoot in range(4):
   a=angle+(shoot-1.5)*.72;base=mid.lerp(end,.35+shoot*.18);tip=base+Vector((math.cos(a)*.32,math.sin(a)*.32,rng.uniform(.08,.20)))
   tube(base,tip,.004,.0014)
   for node in range(7):
    t=.15+node*.125;anchor=base.lerp(tip,t)
    for sign in [-1,1]:
     direction=Vector((math.cos(a+sign*1.02),math.sin(a+sign*1.02),rng.uniform(-.1,.6)))
     leaf(anchor,direction,rng.uniform(.075,.115))
  leaf(end,Vector((math.cos(angle),math.sin(angle),.45)),.10)
 branch=mesh(f'Understory_twigs_{variant}',wv,wf,woodmat);branch.parent=root
 leaves=mesh(f'Understory_leaves_{variant}',vs,fs,leafmat,uv,cols);leaves.parent=root;prototypes.append(root);leafcounts.append(leafcount)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'understory.glb'),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
for i,(x,y,z,s,rotation,variant) in enumerate(centers):
 for part in prototypes[variant].children:
  ob=part.copy();ob.data=part.data;ob.parent=None;bpy.context.collection.objects.link(ob);ob.location=(x,y,z);ob.scale=(s,)*3;ob.rotation_euler.z=rotation;ob.name=f'Understory shrub {i:03} | '+part.name
for root in prototypes:
 for part in list(root.children):bpy.data.objects.remove(part,do_unlink=True)
 bpy.data.objects.remove(root,do_unlink=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/林下灌木.blend'))
bpy.ops.wm.open_mainfile(filepath=str(full))
for o in list(bpy.data.objects):
 if o.get('understory_asset'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(R/'source/林下灌木.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(full))
meta={'shrubs':centers,'variants':3,'leavesPerVariant':leafcounts,'seed':82517,'terrainPlacement':'raycast actual native terrain','maximumPrototypeRadius':1.45}
(A/'understory.json').write_text(json.dumps(meta,separators=(',',':')));print('UNDERSTORY',len(centers),leafcounts)
