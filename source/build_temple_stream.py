"""Author the east garden creek in Blender, preserving unrelated temple objects."""
import bpy,math,random,json,shutil,array,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]; A=R/'dist/assets'; rng=random.Random(8109)
Z0,Z1=-72.,20.; CORE0=-18.; WATER=-.025

def center(z):return 15+.7*math.cos((z+9)*.22)
def width(z):return (1.07+.17*math.sin(z*.51)+.11*math.sin(z*1.12))*math.exp(min(0.,(z+14)/28))*min(1.,.14+(z-Z0)/3,.14+(Z1-z)/2)
def signature():
 out={}
 for o in bpy.data.objects:
  if o.get('temple_stream') or o.name=='Sculpted woodland terrain':continue
  h=hashlib.sha256(array.array('f',[x for row in o.matrix_world for x in row]).tobytes())
  if o.type=='MESH':
   for seq,prop,n,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i')]:
    a=array.array(kind,[0])*(len(seq)*n);seq.foreach_get(prop,a);h.update(a.tobytes())
  out[o.name]=h.hexdigest()
 return out
path=R/'source/听秋寺院.blend'; backup=path.with_name('听秋寺院-before-extended-stream.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path)); before=signature()
for o in list(bpy.data.objects):
 if o.get('temple_stream'):bpy.data.objects.remove(o,do_unlink=True)
terrain=bpy.data.objects['Sculpted woodland terrain']; g=terrain.data
original=g.attributes.get('pre_stream_height')
if original:
 for v,a in zip(g.vertices,original.data):v.co.z=a.value
else:
 original=g.attributes.new('pre_stream_height','FLOAT','POINT')
 for v,a in zip(g.vertices,original.data):a.value=v.co.z
bvh=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in g.vertices],[list(p.vertices) for p in g.polygons])
def ground(x,z):
 hit=bvh.ray_cast(Vector((x,-z,150)),Vector((0,0,-1)))[0]
 return hit.z if hit else .15

def level(z):
 if z>=CORE0:return WATER
 t=max(0,min(1,(-z-18)/8));t=t*t*(3-2*t)
 return WATER+(max(WATER,ground(center(z),z)-.22)-WATER)*t

def patch_width(z):return max(width(z),.42+2.58*max(0,min(1,(-z-20)/12)))

def bed(x,z):
 q=abs(x-center(z))/max(.1,width(z)); edge=ground(x,z)
 if q<=1:return level(z)-.365+.425*q**3+.035*math.sin(x*5.1+z*2.2)+.018*math.cos(z*6.4+x*3)
 if q<1.45:return level(z)+.06+(edge+.07-level(z)-.06)*((q-1)/.45)
 t=min(1,(q-1.45)/1.05);return edge+.07*(1-t)

def material(name,color,rough=.7,image=None):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if image:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/image),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
sand=material('Creek | pale river gravel',(.43,.38,.27),.86,'sand.jpg')
stone=material('Creek | weathered rounded stones',(.42,.43,.36),.75,'pbr-stone.jpg')
grass=material('Creek | fine bank sedges',(.12,.23,.055),.85)
watermat=material('Creek | crystal water',(.91,.99,.98),.075);p=watermat.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.333
parts=[]
def mesh(name,vs,fs,mat,colors=None):
 m=bpy.data.meshes.new(name);m.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);m.update();o=bpy.data.objects.new('Creek | '+name,m);bpy.context.collection.objects.link(o);o['temple_stream']=True;o['streamAssembly']=name;m.materials.append(mat);parts.append(o)
 uv=m.uv_layers.new(name='world metre UV')
 for poly in m.polygons:
  poly.use_smooth=True
  for li in poly.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.7,-v.y*.7)
 if colors:
  attr=m.color_attributes.new(name='Stone tones',type='FLOAT_COLOR',domain='POINT')
  for a,c in zip(attr.data,colors):a.color=(*c,1)
  n=mat.node_tree.nodes.new('ShaderNodeVertexColor');n.layer_name=attr.name;mat.node_tree.links.new(n.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
 return o
# The detailed bed overlaps the depressed original terrain, joining its exact height at the edges.
vs=[];fs=[];nz,nx=920,48
for iz in range(nz+1):
 z=Z0-1+(Z1-Z0+2)*iz/nz; zc=max(Z0,min(Z1,z)); w=patch_width(zc); end=max(0,min(1,(z-(Z0-1)),Z1+1-z))
 for ix in range(nx+1):
  u=ix/nx*2-1;x=center(zc)+u*abs(u)*w*2.5; y=ground(x,z)*(1-end)+bed(x,zc)*end;vs.append((x,y,z))
for i in range(nz):
 for j in range(nx):a=i*(nx+1)+j;fs.append((a,a+nx+1,a+nx+2,a+1))
mesh('sculpted sand and gravel channel',vs,fs,sand)
changed=0
for v in g.vertices:
 x,y,z=terrain.matrix_world@v.co; wz=-y
 if Z0-.5<wz<Z1+.5:
  zz=max(Z0,min(Z1,wz));w=patch_width(zz);q=abs(x-center(zz))/w
  if q<2.3:v.co.z=min(v.co.z,bed(x,zz)-.85);changed+=1
g.update()
# Flat courtyard water retains its reflection pass; the mountain reach follows
# the actual terrain and is exported separately for its sloped water material.
for name,start,end in [('water surface',CORE0,Z1),('headwater surface',Z0,CORE0)]:
 vs=[];fs=[];steps=round((end-start)*10)
 for i in range(steps+1):
  z=start+(end-start)*i/steps;w=width(z)*.94
  for side in [-1,1]:vs.append((center(z)+side*w,level(z),z))
 for i in range(steps):a=i*2;fs.append((a,a+2,a+3,a+1))
 mesh(name,vs,fs,watermat)
# Smooth irregular rounded stones: shared material, single batched mesh.
rv=[];rf=[];rc=[];heroes=[]
def rock(x,z,rx,rz,ry,y=None,hero=False):
 y=bed(x,z)+ry*.35 if y is None else y;start=len(rv);rings=8;sides=12;phase=rng.random()*math.tau;col=rng.choice([(.38,.39,.33),(.53,.49,.39),(.30,.34,.31),(.64,.59,.47),(.42,.43,.40)])
 for j in range(rings+1):
  a=math.pi*j/rings
  for k in range(sides):
   b=k*math.tau/sides;noise=1+.055*math.sin(b*3+a*4+phase)+.038*math.sin(b*5-a*3);xx=math.sin(a)*math.cos(b)*rx*noise;zz=math.sin(a)*math.sin(b)*rz*noise;yy=math.cos(a)*ry*noise
   rv.append((x+xx,y+yy,z+zz));shade=.72 if y+yy<level(z)+.025 else 1.;rc.append(tuple(c*shade for c in col))
 for j in range(rings):
  for k in range(sides):a=start+j*sides+k;b=start+j*sides+(k+1)%sides;rf.append((a,b,b+sides,a+sides))
 if hero:heroes.append({'x':x,'z':z,'radius':(rx+rz)*.44,'rx':rx,'rz':rz})
for i in range(22):
 z=CORE0+1.5+i*(Z1-CORE0-3)/21+rng.uniform(-.4,.4);x=center(z)+rng.uniform(-.7,.7)*width(z);rx=rng.uniform(.26,.49);rock(x,z,rx,rx*rng.uniform(.85,1.45),rng.uniform(.22,.37),-.15,True)
for s in [-1,1]:
 for i in range(77):
  z=CORE0+rng.random()*(Z1-CORE0);x=center(z)+s*width(z)*rng.uniform(.97,1.4);rx=rng.uniform(.13,.40);rock(x,z,rx,rx*rng.uniform(.75,1.3),rx*rng.uniform(.45,.7))
for i in range(2300):
 z=CORE0+rng.random()*(Z1-CORE0);x=center(z)+rng.uniform(-1.06,1.06)*width(z);rx=rng.uniform(.021,.086);rock(x,z,rx,rx*rng.uniform(.65,1.5),rx*rng.uniform(.35,.65))
# Finer stones upstream preserve the diminishing width, without giant rocks
# overwhelming the narrow distant thread of water.
for i in range(700):
 z=Z0+1+rng.random()*(CORE0-Z0-1);w=width(z);x=center(z)+rng.uniform(-1.12,1.12)*w;rx=rng.uniform(.018,.060)*min(1,w/.7);rock(x,z,rx,rx*rng.uniform(.7,1.4),rx*.5)
for i in range(95):
 z=Z0+1+rng.random()*(CORE0-Z0-1);w=width(z);x=center(z)+rng.choice([-1,1])*w*rng.uniform(.98,1.3);rx=rng.uniform(.09,.24)*min(1,w/.8);rock(x,z,rx,rx*1.2,rx*.6)
mesh('river stones and submerged pebbles',rv,rf,stone,rc)
# Fine curved blades, not billboard bushes.
vs=[];fs=[]
for i in range(260):
 z=CORE0+rng.random()*(Z1-CORE0);x=center(z)+rng.choice([-1,1])*width(z)*rng.uniform(1.28,2.);y=bed(x,z)
 for b in range(rng.randrange(8,17)):
  a=rng.random()*math.tau;h=rng.uniform(.12,.39);bend=rng.uniform(.06,.19);wide=rng.uniform(.004,.012);ox=x+rng.uniform(-.08,.08);oz=z+rng.uniform(-.08,.08);start=len(vs)
  for j in range(5):
   t=j/4
   for sign in [-1,1]:vs.append((ox+math.cos(a)*bend*t*t+sign*wide*(1-t)*math.sin(a),y+h*(t-.2*t*t),oz+math.sin(a)*bend*t*t-sign*wide*(1-t)*math.cos(a)))
  for j in range(4):q=start+2*j;fs.append((q,q+2,q+3,q+1))
mesh('arching bank sedges',vs,fs,grass)
assert signature()==before
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path))
# Standalone native creek is a directly editable collection of complete meshes.
standalone=bpy.data.scenes.new('寺旁清溪')
for o in parts:standalone.collection.objects.link(o)
bpy.data.libraries.write(str(R/'source/寺旁清溪.blend'),{standalone},fake_user=True)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'temple-stream.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_apply=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=18)
bpy.ops.object.select_all(action='DESELECT');terrain.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'terrain.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_apply=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
sys.path.insert(0,str(R/'source'))
from fix_stream_terrain_export import fix
fix(A/'terrain.glb')
# Transfer the same carved mesh into the standalone terrain authoring file.
carved=terrain.data.copy();carved.use_fake_user=True;temp=R/'evidence/stream-terrain-transfer.blend';bpy.data.libraries.write(str(temp),{carved},fake_user=True)
terrainpath=R/'source/山林地形.blend'
if terrainpath.exists():
 backup=terrainpath.with_name('山林地形-before-stream.blend')
 if not backup.exists():shutil.copy2(terrainpath,backup)
 bpy.ops.wm.open_mainfile(filepath=str(terrainpath))
 with bpy.data.libraries.load(str(temp),link=False) as (a,b):b.meshes=a.meshes
 bpy.data.objects['Sculpted woodland terrain'].data=b.meshes[0];bpy.ops.wm.save_as_mainfile(filepath=str(terrainpath))
temp.unlink(missing_ok=True)
layout={'z0':Z0,'z1':Z1,'waterY':WATER,'rocks':heroes,'nativePreservedObjects':len(before),'terrainVerticesCarved':changed,'pebbles':3000,'bankStones':249,'coreStart':CORE0,'extension':'terrain-following tapered headwater','flowBounds':[12,18,Z0,Z1],'sedgeClumps':260}
(A/'temple-stream.json').write_text(json.dumps(layout,indent=2));print('STREAM COMPLETE',json.dumps(layout),flush=True)
