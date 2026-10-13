"""Curved specimen trees, fused trunk/root junctions and branch-attached leaf sprays."""
import bpy,bmesh,math,random,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
sys.path.insert(0,str(R/'source'))
from tree_bark_uv import align_bark
from branch_cambers import cambers
layout=json.loads((A/'garden.json').read_text());trees=layout['trees'];rng=random.Random(4811)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Specimen bark');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.91
for suffix,slot in [('', 'Base Color'),('-rough','Roughness'),('-normal','Normal')]:
 t=mat.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/f'pbr-bark{suffix}.jpg'),check_existing=True)
 if suffix:t.image.colorspace_settings.name='Non-Color'
 if slot=='Normal':
  n=mat.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.38;mat.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);mat.node_tree.links.new(n.outputs[0],p.inputs[slot])
 else:mat.node_tree.links.new(t.outputs['Color'],p.inputs[slot])
anchors=[];objects=[]

def curve(a,b,bend,steps=12):
 a=Vector(a);b=Vector(b);bend=Vector(bend)
 return [a.lerp(b,t/steps)+bend*math.sin(t/steps*math.pi) for t in range(steps+1)]

def tube(vs,fs,uv,points,r0,r1,n=12):
 offset=len(vs);distance=0;previousU=None
 for j,p in enumerate(points):
  if j:distance+=(p-points[j-1]).length
  d=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
  if previousU is None:u=d.cross(Vector((0,1,0))).normalized()
  else:u=(previousU-d*previousU.dot(d)).normalized()
  if u.length<.1:u=d.cross(Vector((1,0,0))).normalized()
  v=d.cross(u).normalized();previousU=u;r=r0+(r1-r0)*(j/(len(points)-1))**.85
  for k in range(n+1):
   angle=k/n*math.tau;rr=r*(1+.065*math.sin(angle*5+j*.19));vs.append(tuple(p+(u*math.cos(angle)+v*math.sin(angle))*rr));uv.append((k/n*max(.34,r0*math.tau*1.7),distance*.65))
 for j in range(len(points)-1):
  for k in range(n):a=offset+j*(n+1)+k;fs.append((a,a+1,a+n+2,a+n+1))
 fs.append(tuple(reversed([offset+k for k in range(n)])));fs.append(tuple(offset+(len(points)-1)*(n+1)+k for k in range(n)))

def mesh(name,vs,fs,uv):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat)
 layer=me.uv_layers.new()
 for face in me.polygons:
  face.use_smooth=True
  for li in face.loop_indices:layer.data[li].uv=uv[me.loops[li].vertex_index]
 o['garden_tree']=True;return o

for index,(x,y,h,kind) in enumerate(trees):
 vs=[];fs=[];uv=[];angle=rng.random()*math.tau;lean=Vector((math.cos(angle)*.32,math.sin(angle)*.32,0))
 trunk=curve((0,0,.08),(lean.x,lean.y,h*.88),(lean.y*.8,-lean.x*.8,.08),28)
 radius=(.27 if kind<2 else .34)*(h/7)**.55;tube(vs,fs,uv,trunk,radius,.026,20);bark_paths=[(trunk,radius,.026)]
 for k in range(7):
  a=k/7*math.tau+rng.uniform(-.18,.18);start=Vector((math.cos(a)*rng.uniform(.67,.97),math.sin(a)*rng.uniform(.67,.97),.10));end=Vector((0,0,.92))
  root_path=curve(start,end,(math.cos(a)*.10,math.sin(a)*.10,-.13),10)
  tube(vs,fs,uv,root_path,.055,radius*.63,12);bark_paths.append((root_path,.055,radius*.63))
 limbs=[]
 for level in range(7):
  t=.34+level*.068;start=trunk[round(t*28)];a=angle+level*2.399+rng.uniform(-.25,.25)
  reach=h*(.37-level*.016)*(1.12 if kind==0 else .94);end=start+Vector((math.cos(a)*reach,math.sin(a)*reach,h*(.16+.017*level)))
  points=curve(start,end,(math.cos(a)*.12,math.sin(a)*.12,-h*.07),16);r=radius*(.49-level*.032);tube(vs,fs,uv,points,r,.033,14);limbs.append((points,a,r));bark_paths.append((points,r,.033))
 base=mesh(f'Garden tree {index:02d} fused trunk',vs,fs,uv)
 # Fuse the actual major junctions. Fine twigs retain explicit curved rings.
 bpy.context.view_layer.objects.active=base;base.select_set(True);base.data.remesh_voxel_size=.043;bpy.ops.object.voxel_remesh()
 mod=base.modifiers.new('Rounded branch junctions','SMOOTH');mod.factor=.7;mod.iterations=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=base.modifiers.new('Preserve silhouette with fewer polygons','DECIMATE');mod.ratio=.48;bpy.ops.object.modifier_apply(modifier=mod.name)
 for face in base.data.polygons:
  face.use_smooth=True
 align_bark(base.data,bark_paths)
 camber_audit=cambers(base.data,bark_paths,index);base['branch_cambers_revision']=1;base['branch_cambers_audit']=json.dumps(camber_audit)
 base.select_set(False);base.location=(x,y,.08);objects.append(base)
 vs=[];fs=[];uv=[]
 for points,a,r in limbs:
  for j in range(3):
   start=points[7+j*3];az=a+(j-1)*.82+rng.uniform(-.2,.2);reach=h*.14*rng.uniform(.85,1.2)
   end=start+Vector((math.cos(az)*reach,math.sin(az)*reach,h*rng.uniform(.09,.16)))
   second=curve(start,end,(math.cos(az)*.13,math.sin(az)*.13,-.14),10);tube(vs,fs,uv,second,.041,.012,10)
   for k in range(3):
    start=second[4+k*2];az2=az+(k-1)*.85;reach=rng.uniform(.42,.74);end=start+Vector((math.cos(az2)*reach,math.sin(az2)*reach,rng.uniform(.21,.43)))
    twig=curve(start,end,(0,0,-.09),8);tube(vs,fs,uv,twig,.014,.0028,7)
    for n in [3,6,8]:
     q=twig[n]+Vector((x,y,.08));d=(twig[-1]-twig[0]).normalized();anchors.append([round(q.x,4),round(q.y,4),round(q.z,4),kind,rng.uniform(.40,.66),*d])
 detail=mesh(f'Garden tree {index:02d} fine twigs',vs,fs,uv);detail.location=(x,y,.08);objects.append(detail)
 print('TREE',index,'base faces',len(base.data.polygons),'twigs',len(detail.data.polygons),flush=True)

# Keep the six pruned pine silhouettes and their existing needle clouds.
pines=[(-7.4,.55,3.6),(7.4,.55,3.5),(-12.9,-6,3.1),(12.6,-5.8,3.8),(-5.4,-13.5,2.6),(6,-13.7,2.8)]
for i,(x,y,h) in enumerate(pines):
 vs=[];fs=[];uv=[];tube(vs,fs,uv,curve((0,0,.12),(.18,0,h),(-.24,.08,0),25),.15,.045,16)
 for level in range(6):
  z=.8+level*h*.14;a=level*2.35;reach=(1-level*.10)*1.45
  tube(vs,fs,uv,curve((0,0,z-.15),(math.cos(a)*reach,math.sin(a)*reach,z+.23),(0,0,-.11),14),.063,.019,10)
 o=mesh(f'Cloud pine {i:02d} curved trunk',vs,fs,uv);o.location=(x,y,0);objects.append(o)

# Keep bark texture payload shared with the original architecture in the browser.
shell=bpy.data.materials.new('Specimen bark | runtime shared maps');shell.use_nodes=True
for o in objects:o.data.materials[0]=shell
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'garden-trees.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_attributes=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
from bark_junctions import configure_native_bark
blended=mat.copy();blended.name='Specimen bark | blended fork charts';configure_native_bark(blended,A,next(o for o in objects if 'fused trunk' in o.name).data.uv_layers[0].name)
for o in objects:o.data.materials[0]=blended if 'fused trunk' in o.name else mat
(A/'garden-trees.json').write_text(json.dumps({'trees':trees,'pines':pines,'anchors':anchors},separators=(',',':')))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/庭院曲枝树木.blend'))
print('TREE PROTOTYPES COMPLETE',len(trees),len(pines),len(anchors),flush=True)
