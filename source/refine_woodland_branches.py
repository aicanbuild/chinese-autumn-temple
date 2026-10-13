"""Refine near woodland skeletons while retaining every crown and placement."""
import bpy,math,random,json,hashlib,shutil
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';records=[]
def signature(me):return hashlib.sha256(repr(([tuple(v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons],[[tuple(v.uv) for v in uv.data] for uv in me.uv_layers])).encode()).hexdigest()
def signatures():
 cache={};out={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  if o.data.name not in cache:cache[o.data.name]=signature(o.data)
  out[o.name]=cache[o.data.name]
 return out

def build(species):
 vs=[];faces=[];uv=[]
 def tube(points,radii,sides=8,root=False):
  offset=len(vs);distance=0;previous=None
  for i,(p,r) in enumerate(zip(points,radii)):
   if i:distance+=(p-points[i-1]).length
   direction=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
   if previous is None:frame=direction.cross(Vector((0,1,0)) if abs(direction.y)<.9 else Vector((1,0,0))).normalized()
   else:frame=(previous-direction*previous.dot(direction)).normalized()
   previous=frame;cross=direction.cross(frame)
   for k in range(sides+1):
    angle=k/sides*math.tau;rr=r
    if root:rr*=1+(.20*math.exp(-max(p.z,0)*2.8)+.025)*math.cos(angle*5+species*.8)
    vs.append(tuple(p+(frame*math.cos(angle)+cross*math.sin(angle))*rr));uv.append((k/sides*math.tau*(.16 if root else radii[0])*.55,distance*.55))
  for i in range(len(points)-1):
   for k in range(sides):q=offset+i*(sides+1)+k;faces.append((q,q+1,q+sides+2,q+sides+1))
  faces.append(tuple(offset+k for k in reversed(range(sides))));end=offset+(len(points)-1)*(sides+1);faces.append(tuple(end+k for k in range(sides)))
 def curve(a,b,r0,r1,segments,sides,bend):
  a,b=Vector(a),Vector(b);points=[];radii=[]
  for i in range(segments+1):
   t=i/segments;points.append(a.lerp(b,t)+Vector(bend)*math.sin(t*math.pi));radii.append(r1+(r0-r1)*(1-t)**1.25)
  tube(points,radii,sides)
 rng=random.Random(240+species*170);trunk=[Vector((math.sin(j*.57)*.17,math.cos(j*.43)*.13,j*.60)) for j in range(12)]
 pts=[];rs=[]
 for i in range(34):
  z=-.70 if i==0 else -.14+(6.6+.14)*i/33;j=max(0,min(11,z/.6));pts.append(Vector((math.sin(j*.57)*.17,math.cos(j*.43)*.13,z)));rs.append(.19*(1-j/12)**1.3+.015+.17*math.exp(-max(z,0)*4.2))
 tube(pts,rs,12,True)
 tips=[]
 for b in range(10):
  angle=b*2.399+species*.7;start=trunk[3+b//2];reach=(2.1-b*.11)*rng.uniform(.85,1.13);end=start+Vector((math.cos(angle)*reach,math.sin(angle)*reach,.7+.1*b))
  # Sink the enlarged branch collar into the trunk; rise gradually toward the crown.
  curve(start,end,.078*(1-b*.055),.018,7,8,(0,0,-.16))
  for j in range(3):
   aa=angle+(j-1)*.72;tip=end+Vector((math.cos(aa)*.66,math.sin(aa)*.66,.55+rng.random()*.35));tips.append(tuple(tip));curve(end,tip,.024,.005,5,6,(-math.sin(aa)*.06,math.cos(aa)*.06,-.065))
   for side in [-1,1]:
    q=tip-Vector((math.cos(aa)*.25,math.sin(aa)*.25,.2));direction=aa+side*.85;target=tip+Vector((math.cos(direction)*.45,math.sin(direction)*.45,side*.10));curve(q,target,.007,.0012,3,5,(0,0,.04))
   for k in range(72):
    for _ in range(9):rng.random()
 me=bpy.data.meshes.new(f'Refined Woodland Branches {species}');me.from_pydata(vs,[],faces);me.update();layer=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  p.use_smooth=True
  for i in p.loop_indices:layer.data[i].uv=uv[me.loops[i].vertex_index]
 me.validate();return me,tips
for filename in ['山林地形.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-woodland-branches.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures();changed=[]
 # The current browser maps supersede stale packed leaves in the native source.
 for image in list(bpy.data.images):
  name=Path(bpy.path.abspath(image.filepath)).name
  if name not in [f'{s}-{kind}.png' for s in ['green','ginkgo','maple'] for kind in ['leaf','spray']]:continue
  replacement=bpy.data.images.load(str(A/name),check_existing=False);replacement.colorspace_settings.name=image.colorspace_settings.name;replacement.pack();image.user_remap(replacement)
 for species in range(3):
  matches=[o for o in bpy.data.objects if o.type=='MESH' and f'| Branches_{species}_0' in o.name];assert matches
  old=matches[0].data;new,tips=build(species)
  for mat in old.materials:new.materials.append(mat)
  for o in matches:o.data=new;changed.append(o.name)
  # Replayed center paths must agree with the actual retained 72-leaf clusters.
  leaf=next(o for o in bpy.data.objects if o.type=='MESH' and f'| Leaves_{species}_0' in o.name)
  assert len(leaf.data.vertices)==30*72*5
  max_error=0
  for i,tip in enumerate(tips):
   center=sum((leaf.data.vertices[i*72*5+k*5+4].co-Vector((0,0,.027)) for k in range(72)),Vector())/72
   max_error=max(max_error,(center-Vector(tip)).length)
  assert max_error<.19,(species,max_error)
  records.append({'file':filename,'species':species,'trees':len(matches),'oldFaces':len(old.polygons),'newFaces':len(new.polygons),'vertices':len(new.vertices),'maxLeafClusterCenterOffset':max_error})
 terrain=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='Sculpted woodland terrain')
 bv=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(p.vertices) for p in terrain.data.polygons]);root_gap=-999
 for name in changed:
  o=bpy.data.objects[name]
  for v in list(o.data.vertices)[:13]:
   point=o.matrix_world@v.co;hit,_,_,_=bv.ray_cast(point+Vector((0,0,30)),Vector((0,0,-1)),60);assert hit is not None
   root_gap=max(root_gap,point.z-hit.z)
 assert root_gap<0,root_gap
 print('ROOT CAPS BELOW TERRAIN',root_gap,flush=True)
 after=signatures()
 for name,value in before.items():
  if name not in changed:assert value==after[name],name
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));print('NATIVE SAVED',filename,len(changed),flush=True)
 if filename=='山林地形.blend':
  # Export the same six prototypes; only the three near skeletons were changed.
  bpy.ops.object.select_all(action='DESELECT')
  for lod in range(2):
   for species in range(3):
    root=bpy.data.objects.new(f'Woodland_{species}_{lod}',None);bpy.context.collection.objects.link(root);root.select_set(True)
    for kind in ['Branches','Leaves']:
     src=next(o for o in bpy.data.objects if o.type=='MESH' and f'| {kind}_{species}_{lod}' in o.name);copy=bpy.data.objects.new(f'{kind}_{species}_{lod}',src.data);bpy.context.collection.objects.link(copy);copy.parent=root;copy.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(A/'woodland.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Keep existing browser texture bytes instead of exporter recompression.
import sys
sys.path.insert(0,str(R/'source'))
from granite_finish import refresh_glb
refresh_glb(A/'woodland.glb',{name:A/(name+('.jpg' if name.startswith('pbr-') else '.png')) for name in ['pbr-bark-normal','pbr-bark','green-leaf','ginkgo-leaf','maple-leaf','green-spray','ginkgo-spray','maple-spray']})
(R/'evidence/woodland-branches-native.json').write_text(json.dumps(records,indent=2));print('WOODLAND BRANCHES COMPLETE',flush=True)
