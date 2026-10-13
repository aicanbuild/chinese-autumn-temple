"""Small original moss shoots rooted on the actual bank stones and terrain."""
import bpy,math,random,json,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';rng=random.Random(126031)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(R/'source/听秋寺院.blend'),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n.startswith('Pond bank stone ') or n=='Sculpted woodland terrain']
surfaces=list(dst.objects)
for o in surfaces:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update()
vs=[];faces=[]
for o in surfaces:
 at=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(at+i for i in p.vertices) for p in o.data.polygons)
bvh=BVHTree.FromPolygons(vs,faces)
stones=sorted([o for o in surfaces if o.get('pond_zone')=='bank'],key=lambda o:o.name)
assert len(stones)==66
mat=bpy.data.materials.new('Bank moss | fine velvet leaves');mat.use_nodes=True;mat.use_backface_culling=False
p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.88
c=mat.node_tree.nodes.new('ShaderNodeVertexColor');c.layer_name='Moss pigment';mat.node_tree.links.new(c.outputs['Color'],p.inputs['Base Color'])
batches={i:[[],[],[]] for i in range(4)};roots=[];patches=[]
for index,stone in enumerate(stones):
 if index%3!=1 or abs(stone.location.x)<2.9:continue
 center=stone.location.copy();out=Vector((center.x/11.5,(center.y+5.8)/6.9,0)).normalized()
 # An irregular crescent grows over the outer shoulder and into the stone foot.
 center+=out*.30;radius=rng.uniform(.18,.29);patches.append([*center,radius])
 for shoot in range(460):
  angle=rng.random()*math.tau;rr=radius*math.sqrt(rng.random());x=center.x+math.cos(angle)*rr;y=center.y+math.sin(angle)*rr
  if math.sin(x*26+y*12)+math.cos(x*17-y*23)<-.85:continue
  hit,n,face,distance=bvh.ray_cast(Vector((x,y,3)),Vector((0,0,-1)),4)
  if hit is None or n.z<.58 or hit.z<.10:continue
  root=hit-n*.0015;roots.append([*hit,*n]);q=n.to_track_quat('Z','Y');height=rng.uniform(.015,.036);spin=rng.random()*math.tau
  batch=int(x>0)+2*int(y>-5.8);verts,polys,colors=batches[batch]
  def vertex(v,col):verts.append(tuple(root+q@Vector(v)));colors.append((*col,1));return len(verts)-1
  # Stem carries each leaf at its actual junction. Roots are buried 1.5 mm.
  start=len(verts)
  for z,rad in [(0,.00065),(height,.0002)]:
   for k in range(4):a=k*math.tau/4;vertex((math.cos(a)*rad,math.sin(a)*rad,z),(.025,.044,.012))
  for k in range(4):polys.append((start+k,start+(k+1)%4,start+(k+1)%4+4,start+k+4))
  shade=rng.uniform(.72,1.18)
  for leaf in range(12):
   t=leaf/12;a=spin+leaf*2.399;length=rng.uniform(.006,.012)*(1-.28*t);w=length*rng.uniform(.18,.26);z=height*(.16+.78*t)
   direction=Vector((math.cos(a),math.sin(a),rng.uniform(.45,.85))).normalized();side=Vector((-math.sin(a),math.cos(a),0));base=Vector((0,0,z));mid=base+direction*length*.5;tip=base+direction*length
   color=tuple(v*shade for v in (.050+.028*t,.083+.055*t,.015+.009*t));offset=len(verts)
   for point,factor in [(base,.64),(mid-side*w,.85),(mid+Vector((0,0,w*.32)),1),(mid+side*w,.85),(tip,1.06)]:vertex(point,tuple(v*factor for v in color))
   polys.extend([(offset,offset+1,offset+2),(offset,offset+2,offset+3),(offset+1,offset+4,offset+2),(offset+2,offset+4,offset+3)])
parts=[]
for index,(vertices,polygons,colors) in batches.items():
 me=bpy.data.meshes.new(f'Bank moss quarter {index}');me.from_pydata(vertices,[],polygons);me.update();me.materials.append(mat)
 ca=me.color_attributes.new(name='Moss pigment',type='FLOAT_COLOR',domain='POINT')
 for v,col in zip(ca.data,colors):v.color=col
 for f in me.polygons:f.use_smooth=True
 o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);o['bank_moss']=True;parts.append(o)
for o in surfaces:bpy.data.objects.remove(o,do_unlink=True)
prototype=R/'source/池岸立体苔藓.blend';bpy.ops.wm.save_as_mainfile(filepath=str(prototype))
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'bank-moss.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=18,export_draco_normal_quantization=12)
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in parts)
report={'patches':len(patches),'shoots':len(roots),'triangles':triangles,'batches':len(parts),'rootBurialMeters':.0015,'rootsNative':roots,'patchesNative':patches}
(A/'bank-moss.json').write_text(json.dumps(report,separators=(',',':')))
full=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-bank-moss.blend'
if not backup.exists():shutil.copy2(full,backup)
bpy.ops.wm.open_mainfile(filepath=str(full));before={o.name:(o.type,len(o.data.vertices) if o.type=='MESH' else 0) for o in bpy.data.objects if not o.get('bank_moss')}
for o in list(bpy.data.objects):
 if o.get('bank_moss'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:bpy.context.collection.objects.link(o)
assert before=={o.name:(o.type,len(o.data.vertices) if o.type=='MESH' else 0) for o in bpy.data.objects if not o.get('bank_moss')}
bpy.ops.wm.save_as_mainfile(filepath=str(full));print('BANK MOSS',json.dumps({k:v for k,v in report.items() if not k.endswith('Native')}),flush=True)
