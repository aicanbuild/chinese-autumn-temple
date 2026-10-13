"""CC0 scanned apples and original dimpled citrus, settled onto the existing trays."""
import bpy,math,random
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
def is_fruit(o):
 return bool(o.get('altar_fruit')) or any(o.name.startswith('Offering | '+n) for n in ['fresh seasonal fruit','fruit crown','fruit stem'])

def build_altar_fruit():
 rng=random.Random(943);parts=[];bodies=[];contacts=[]
 def tag(o,kind):
  o['altar_fruit']=True;o['sanctuary_interior']=True;o['fruit_kind']=kind;parts.append(o);return o
 # Import the verified original scan, preserving UVs, surface maps and stem.
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/'source/reference-assets/apple/food_apple_01.gltf'))
 imported=[o for o in bpy.data.objects if o not in before];apple=next(o for o in imported if o.type=='MESH');assert len([o for o in imported if o.type=='MESH'])==1
 apple.data=apple.data.copy();coords=[apple.matrix_world@v.co for v in apple.data.vertices];lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)));hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)));center=(lo+hi)/2;span=max(hi.x-lo.x,hi.y-lo.y)
 apple.data.transform(Matrix.Scale(1/span,4)@Matrix.Translation(-center)@apple.matrix_world)
 apple.matrix_world.identity();applemat=apple.data.materials[0];applemat.name='Sanctuary | scanned apple offering';prototype=apple.data
 for o in imported:bpy.data.objects.remove(o,do_unlink=True)
 # Orange peel uses original measured-scale texture detail rather than a smooth sphere.
 citrus=bpy.data.materials.new('Sanctuary | textured citrus offering');citrus.use_nodes=True;p=citrus.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.65
 for suffix,slot in [('', 'Base Color'),('-rough','Roughness'),('-normal','Normal')]:
  t=citrus.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/('citrus-peel'+suffix+'.jpg')),check_existing=True)
  if suffix:t.image.colorspace_settings.name='Non-Color'
  if slot=='Normal':
   n=citrus.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.62;citrus.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);citrus.node_tree.links.new(n.outputs[0],p.inputs[slot])
  else:citrus.node_tree.links.new(t.outputs['Color'],p.inputs[slot])
 green=next(m for m in bpy.data.materials if m.name=='Sanctuary | botanical stems')
 def orange(index):
  vs=[];fs=[];uv=[];n=64;rows=40;phase=index*1.618
  for j in range(rows+1):
   ph=j*math.pi/rows
   for k in range(n+1):
    a=k*math.tau/n;rr=.5*math.sin(ph)*(1+.014*math.cos(a*3+phase)*math.sin(ph)+.010*math.sin(a*7-phase));z=.445*math.cos(ph)-.038*math.exp(-(ph/.25)**2)+.025*math.exp(-((math.pi-ph)/.23)**2)
    vs.append((rr*math.cos(a),rr*math.sin(a),z));uv.append((k/n,1-j/rows))
  for j in range(rows):
   for k in range(n):a=j*(n+1)+k;fs.append((a,a+1,a+n+2,a+n+1))
  d=bpy.data.meshes.new('Dimpled citrus');d.from_pydata(vs,[],fs);d.update();d.materials.append(citrus)
  for face in d.polygons:face.use_smooth=True
  layer=d.uv_layers.new()
  for f in d.polygons:
   for li in f.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
  o=bpy.data.objects.new('Offering | dimpled citrus',d);bpy.context.collection.objects.link(o);tag(o,'citrus')
  # Five attached calyx lobes sit in the shallow stem depression.
  cv=[];cf=[]
  for k in range(5):
   a=k*math.tau/5;off=len(cv)
   for r,angle,z in [(0,a,.414),(.025,a-.55,.414),(.059,a,.420),(.025,a+.55,.414)]:cv.append((r*math.cos(angle),r*math.sin(angle),z))
   cf.append(tuple(off+i for i in range(4)))
  cd=bpy.data.meshes.new('Citrus calyx');cd.from_pydata(cv,[],cf);cd.materials.append(green);cap=bpy.data.objects.new('Offering | citrus calyx',cd);bpy.context.collection.objects.link(cap);cap.parent=o;tag(cap,'calyx')
  return o
 def bvh(objects):
  vs=[];fs=[]
  for o in objects:
   off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
  return BVHTree.FromPolygons(vs,fs)
 def settle(o,support):
  bpy.context.view_layer.update();gaps=[]
  for v in o.data.vertices:
   w=o.matrix_world@v.co;hit,normal,index,distance=support.ray_cast(Vector((w.x,w.y,5)),Vector((0,0,-1)))
   if hit:gaps.append(w.z-hit.z)
  assert gaps
  o.location.z-=min(gaps)-.0005;bpy.context.view_layer.update();contacts.append(.0005)
 for side in [-1,1]:
  plate=next(o for o in bpy.data.objects if o.name.startswith('Offering | bronze fruit tazza') and ((sum(v.co.x for v in o.data.vertices)/len(o.data.vertices))>0)==(side>0))
  tray=bvh([plate]);lower=[]
  for i in range(6):
   if side>0:
    o=bpy.data.objects.new('Offering | scanned apple',prototype);bpy.context.collection.objects.link(o);tag(o,'apple')
   else:o=orange(i)
   angle=i*math.tau/5;diameter=(.145 if i<5 else .15)*rng.uniform(.97,1.03);o.scale=(diameter,diameter*rng.uniform(.97,1.03),diameter*rng.uniform(.97,1.03));o.rotation_euler=(rng.uniform(-.06,.06),rng.uniform(-.06,.06),rng.uniform(0,math.tau))
   o.location=(side*1.20+(math.cos(angle)*.132 if i<5 else 0),8.10+(math.sin(angle)*.132 if i<5 else 0),3.0)
   settle(o,tray if i<5 else bvh(lower));o['fruit_layer']=0 if i<5 else 1;o['nominal_contact_gap']=.0005;bodies.append(o)
   if i<5:lower.append(o)
 return parts,[applemat,citrus],{'apples':6,'citrus':6,'contactGap':.0005}
