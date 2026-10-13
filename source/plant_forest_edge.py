"""Cluster existing fine shrubs and ferns at the woodland edge on actual terrain."""
import bpy,json,math,random,shutil
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';full=R/'source/听秋寺院.blend';backup=full.with_name('听秋寺院-before-forest-edge.blend')
if not backup.exists():shutil.copy2(full,backup)
bpy.ops.wm.open_mainfile(filepath=str(full));terrain=bpy.data.objects['Sculpted woodland terrain'];bv=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(p.vertices) for p in terrain.data.polygons])
def ground(x,y):
 p,n,_,_=bv.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),200);return p,n
old=json.loads((A/'understory.json').read_text())['shrubs'];trees=json.loads((A/'woodland.json').read_text())['trees'];rng=random.Random(91027);plants=[]
anchors=[p for p in trees if 25<math.hypot(p[0],p[1])<64 and abs(p[0])>23 and -54<p[1]<33]
for tree in anchors:
 angle=rng.uniform(0,math.tau);cx=tree[0]+math.cos(angle)*2.6;cy=tree[1]+math.sin(angle)*2.6
 for attempt in range(35):
  a=rng.uniform(0,math.tau);r=math.sqrt(rng.random())*rng.uniform(2.3,4.7);x=cx+math.cos(a)*r;y=cy+math.sin(a)*r
  if abs(x)<22 or math.hypot(x,y)<24 or math.hypot(x,y)>68 or y<-57 or y>36:continue
  if y<-16 and abs(x)<28 and math.hypot(x,y)<57:continue
  if any(math.hypot(x-t[0],y-t[1])<.75 for t in trees):continue
  if any(math.hypot(x-p[0],y-p[1])<1.5 for p in old):continue
  if any(math.hypot(x-p[0],y-p[1])<.68 for p in plants):continue
  x,y=round(x,4),round(y,4)
  p,n=ground(x,y)
  if p is None or n.z<.79:continue
  kind='shrub' if rng.random()<.27 else 'fern';variant=rng.randrange(3 if kind=='shrub' else 4);scale=rng.uniform(.38,.72) if kind=='shrub' else rng.uniform(.55,1.1);yaw=rng.uniform(0,math.tau)
  # Ferns follow the slope; woody shrubs grow vertically from buried stems.
  normal=n if kind=='fern' else Vector((0,0,1));burial=.035 if kind=='fern' else .095
  plants.append([round(x,4),round(y,4),round(p.z-burial,4),round(scale,4),round(yaw,5),kind,variant,*[round(v,6) for v in normal]])
# Reuse the native shrub meshes without altering them.
prototypes={}
for variant in range(3):
 parts=[]
 for kind in ['twigs','leaves']:
  o=next(o for o in bpy.data.objects if o.type=='MESH' and f'Understory_{kind}_{variant}' in o.name);parts.append(o.data)
 prototypes[('shrub',variant)]=parts
# The browser fern prototypes are in a display grid; normalize each to width 1 m.
with bpy.data.libraries.load(str(R/'source/池岸蕨类.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('fern_02')]
ferns=sorted(dst.objects,key=lambda o:o.name)
assert len(ferns)==4,[o.name for o in ferns]
fernNames=[]
for variant,o in enumerate(ferns):
 me=o.data.copy();me.transform(o.matrix_world);xs=[v.co.x for v in me.vertices];ys=[v.co.y for v in me.vertices];zs=[v.co.z for v in me.vertices];width=max(xs)-min(xs);center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,min(zs)))
 for v in me.vertices:v.co=(v.co-center)/width
 for i,m in enumerate(me.materials):
  m=m.copy();m.name='Forest edge | '+m.name;me.materials[i]=m;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.9
  source=p.inputs['Base Color'].links[0].from_socket;mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
  def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
  mix.inputs[2].default_value=(*[linear(v/255) for v in [179,189,131]],1);m.node_tree.links.new(source,mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],p.inputs['Base Color'])
 prototypes[('fern',variant)]=[me];fernNames.append(o.name)
for o in ferns:bpy.data.objects.remove(o,do_unlink=True)
# Preserve all non-edge objects and their transforms/data identity.
before={o.name:(o.type,o.data.name if o.type=='MESH' else None,tuple(v for row in o.matrix_world for v in row)) for o in bpy.data.objects if not o.get('forest_edge')}
for o in list(bpy.data.objects):
 if o.get('forest_edge'):bpy.data.objects.remove(o,do_unlink=True)
created=[];rootError=0
for i,row in enumerate(plants):
 x,y,z,s,yaw,kind,variant,nx,ny,nz=row;normal=Vector((nx,ny,nz));q=Vector((0,0,1)).rotation_difference(normal)@Quaternion((0,0,1),yaw)
 p,_=ground(x,y);rootError=max(rootError,abs(z+(.035 if kind=='fern' else .095)-p.z))
 for part,me in enumerate(prototypes[(kind,variant)]):
  o=bpy.data.objects.new(f'Forest edge {i:03d} | {kind} {variant} {part}',me);bpy.context.collection.objects.link(o);o.location=(x,y,z);o.rotation_mode='QUATERNION';o.rotation_quaternion=q;o.scale=(s,)*3;o['forest_edge']=True;created.append(o)
assert rootError<.0001
assert before=={o.name:(o.type,o.data.name if o.type=='MESH' else None,tuple(v for row in o.matrix_world for v in row)) for o in bpy.data.objects if not o.get('forest_edge')}
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(full));print('FULL NATIVE SAVED',len(plants),flush=True)
# Standalone editable planting file, sharing meshes just like the browser.
for o in list(bpy.data.objects):
 if not o.get('forest_edge'):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/山林地被.blend'))
meta={'plants':plants,'fernNames':fernNames,'seed':91027,'ground':'actual terrain raycast','shrubs':sum(p[5]=='shrub' for p in plants),'ferns':sum(p[5]=='fern' for p in plants),'maximumRootErrorMeters':rootError}
(A/'forest-edge.json').write_text(json.dumps(meta,separators=(',',':')));(R/'evidence/forest-edge-native.json').write_text(json.dumps({k:v for k,v in meta.items() if k!='plants'},indent=2));print('FOREST EDGE COMPLETE',meta['shrubs'],meta['ferns'],rootError,flush=True)
