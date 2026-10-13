"""Two small original lotus patches, reusing the detailed authored temple blossoms."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(R/'source/听秋寺院.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Lotus |')]
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update();rng=random.Random(9021)
for o in list(bpy.data.objects):
 if o.get('pond_lotus'):bpy.data.objects.remove(o,do_unlink=True)
leafmat=next(m for m in bpy.data.materials if m.name.startswith('Sanctuary | living lotus leaves'))
stemmat=next(m for m in bpy.data.materials if m.name.startswith('Sanctuary | botanical stems'))
center=Vector((2.05,8.37,3.055));original=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.get('lotus_bouquet'):continue
 if o.get('botanical_part') not in ['petal','stamens'] and not o.get('flower_calyx') and not o.name.startswith(('Lotus | flat seed receptacle','Lotus | receptacle stigma')):continue
 points=[o.matrix_world@v.co for v in o.data.vertices];c=sum(points,Vector())/len(points)
 if (c-center).length<.245:original.append(o)
assert len(original)>15,len(original)
for o in list(bpy.data.objects):
 if o not in original:bpy.data.objects.remove(o,do_unlink=True)
parts=[]
def reg(o):
 o['pond_lotus']=True
 for key in ['lotus_bouquet','sanctuary_interior','botanical_part']:
  if key in o:del o[key]
 parts.append(o);return o
def tube(points):
 curve=bpy.data.curves.new('Pond lotus stalk','CURVE');curve.dimensions='3D';curve.bevel_depth=.007;curve.bevel_resolution=2;s=curve.splines.new('POLY');s.points.add(len(points)-1)
 for p,v in zip(s.points,points):p.co=(*v,1)
 o=bpy.data.objects.new('Pond lotus | fine emergent stalk',curve);bpy.context.collection.objects.link(o);curve.materials.append(stemmat);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=reg(bpy.context.object);o['pond_stem_grounded']=True;return o
def stalk(end):
 base=Vector((end[0]+.08,end[1]-.05,-1.72));end=Vector(end);tube([base.lerp(end,t)+Vector((.035*math.sin(math.pi*t),0,0)) for t in [j/20 for j in range(21)]])
def leaf(c,r,tilt,phase):
 vs=[];fs=[];uv=[];rot=Matrix.Rotation(tilt,4,'X')@Matrix.Rotation(phase,4,'Z');N=96;M=16
 for j in range(M+1):
  t=j/M
  for k in range(N):
   a=k*math.tau/N;radius=r*t*(1+.025*math.sin(a*7+phase));z=.032*t*t+.008*math.sin(a*6+phase)*t**3
   vs.append(Vector(c)+rot@Vector((radius*math.cos(a),radius*math.sin(a),z)));uv.append((.5+.48*t*math.cos(a),.5+.48*t*math.sin(a)))
 for j in range(M):
  for k in range(N):a=j*N+k;b=j*N+(k+1)%N;fs.append((a,a+N,b+N,b))
 d=bpy.data.meshes.new('Peltate radial lotus leaf');d.from_pydata(vs,[],fs);d.update();d.materials.append(leafmat);layer=d.uv_layers.new()
 for p in d.polygons:
  p.use_smooth=True
  for li in p.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
 o=bpy.data.objects.new('Pond lotus | gently cupped radial leaf',d);bpy.context.collection.objects.link(o);m=o.modifiers.new('Thin living leaf edge','SOLIDIFY');m.thickness=.0014;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name);reg(o);stalk(c)
patches=[(-6.3,-6.9),(7.3,-4.7)]
for patch,(x,y) in enumerate(patches):
 for j in range(7):
  a=j*2.399963+patch;rad=.66*math.sqrt(j/6);r=rng.uniform(.28,.39);z=.015 if j%3 else .16
  c=(x+rad*math.cos(a),y+rad*math.sin(a),z);leaf(c,r,.04 if z<.1 else .20,j*.7)
 for k in range(2 if patch==0 else 1):
  dest=Vector((x+(-.22 if k==0 else .38),y+(.1 if k==0 else -.22),.39+k*.16));scale=1.55 if k==0 else 1.18
  for source in original:
   o=source.copy();o.data=source.data.copy();bpy.context.collection.objects.link(o);o.data.transform(Matrix.Translation(dest)@Matrix.Diagonal((scale,scale,scale,1))@Matrix.Translation(-center)@source.matrix_world);o.matrix_world=Matrix.Identity(4);o.name='Pond lotus | '+source.name;reg(o)
  stalk(dest)
# Save the independently editable additions before merging into the full scene.
for o in original:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/池中荷花.blend'))
batches={}
for o in parts:batches.setdefault(o.data.materials[0],[]).append(o)
for mat,group in batches.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name='Pond lotus | '+mat.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'pond-lotus.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
report={'patches':2,'leaves':14,'flowers':3,'radiusMetres':1.05,'centersNative':patches,'bytes':(A/'pond-lotus.glb').stat().st_size};(R/'evidence/pond-lotus.json').write_text(json.dumps(report,indent=2));print('POND_LOTUS_READY',report,flush=True)

bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
for o in list(bpy.data.objects):
 if o.get('pond_lotus'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(R/'source/池中荷花.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
