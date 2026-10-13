"""Round the two bed-stone prototypes and nest small gravel around existing stones."""
import bpy,bmesh,math,random,json,hashlib,shutil,sys
from pathlib import Path
from mathutils import Vector,noise
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';sys.path.insert(0,str(R/'source'))
from pond_basin import seat_stone,basin_height
for name in ['pond-stones.glb','pond-stones.json','pond-contact-ao.png']:
 p=R/'evidence'/('gravel-before-'+name)
 if not p.exists():shutil.copy2(A/name,p)
layout=json.loads((R/'evidence/gravel-before-pond-stones.json').read_text());original=layout['placements'];rng=random.Random(410827)
# Small groups settle on the downstream side of larger cobbles. Leave broad open
# sediment between groups and keep every new piece clear of existing silhouettes.
bed=[p for p in original if p[8]=='bed'];anchors=rng.sample(bed,40);placements=[list(p) for p in original];occupied=[(p[1],p[2],max(p[4:6])) for p in bed]
for a in anchors:
 for j in range(9):
  for attempt in range(80):
   angle=rng.uniform(0,math.tau);reach=rng.uniform(.20,.68);x=a[1]+math.cos(angle)*reach;y=a[2]+math.sin(angle)*reach
   sx=rng.uniform(.018,.060);sy=sx*rng.uniform(.68,1.15);sz=sx*rng.uniform(.40,.74)
   if abs(x)<1.55 or math.hypot(x/11.5,(y+5.8)/6.9)>.90:continue
   if any(math.hypot(x-xx,y-yy)<rr+max(sx,sy)+.012 for xx,yy,rr in occupied):continue
   p=[6+len(placements)%2,x,y,0,sx,sy,sz,rng.random()*math.tau,'bed'];placements.append(p);occupied.append((x,y,max(sx,sy)));break
assert len(placements)==len(original)+360,len(placements)
def signature(me):return hashlib.sha256(repr(([tuple(v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])).encode()).hexdigest()
def make_mesh(k):
 bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1)
 for v in bm.verts:
  n=v.co.normalized();r=.86+.065*math.sin(n.x*3.2+n.y*1.8+k)+.035*math.cos(n.z*4-n.y*2+k)
  v.co=n*r;v.co.x+=.075*(1-n.x*n.x)*n.y;v.co.y+=.045*(1-n.y*n.y)*n.z
 me=bpy.data.meshes.new(f'Water worn gravel {k}');bm.to_mesh(me);bm.free();me.update();uv=me.uv_layers.new(name='UVMap')
 for f in me.polygons:
  f.use_smooth=True
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co.normalized();uv.data[li].uv=(.5+math.atan2(v.y,v.x)/math.tau,.5+math.asin(v.z)/math.pi)
 color=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
 for v in me.vertices:
  shade=.91+.055*noise.noise_vector(v.co*3+Vector((k*2,4,9))).z;color.data[v.index].color=(shade,shade*.975,shade*.925,1)
 return me
records=[]
for filename in ['自然池岸','听秋寺院']:
 path=R/'source'/(filename+'.blend');backup=path.with_name(filename+'-before-gravel.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));parts=[o for o in bpy.data.objects if o.get('pond_stone')];before={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects};untouched={o.data.name:signature(o.data) for o in bpy.data.objects if o.type=='MESH' and o.get('pond_zone')!='bed'}
 # Original numeric names bind source prototypes to the preserved layout.
 prototypes={}
 for o in parts:
  i=int(o.name.rsplit(' ',1)[1])
  if i<len(original):prototypes[original[i][0]]=o.data
 assert len(prototypes)==8
 for k in [6,7]:
  old=prototypes[k];new=make_mesh(k)
  for mat in old.materials:new.materials.append(mat)
  for o in parts:
   if o.data==old:o.data=new
  prototypes[k]=new
 for i,p in enumerate(placements):
  if p[8]!='bed':continue
  o=bpy.data.objects.get(f'Pond bed stone {i:03d}')
  if o is None:o=bpy.data.objects.new(f'Pond bed stone {i:03d}',prototypes[p[0]]);bpy.context.collection.objects.link(o)
  o.location=p[1:4];o.scale=p[4:7];o.rotation_euler=(0,0,p[7]);o['pond_stone']=True;o['pond_zone']='bed';seat_stone(o,embed=.004 if i>=len(original) else .010);p[3]=o.location.z
 bpy.context.view_layer.update();maxTop=-999;supportErrors=[]
 for o in bpy.data.objects:
  if o.get('pond_zone')!='bed':continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];maxTop=max(maxTop,max(p.z for p in pts));supportErrors.append(min(p.z-basin_height(p.x,p.y) for p in pts))
 assert maxTop<-.70,maxTop
 for o in bpy.data.objects:
  if o.name in before and o.get('pond_zone')!='bed':assert tuple(v for row in o.matrix_world for v in row)==before[o.name],o.name
 assert untouched=={o.data.name:signature(o.data) for o in bpy.data.objects if o.type=='MESH' and o.get('pond_zone')!='bed'}
 bpy.ops.wm.save_as_mainfile(filepath=str(path));report={'file':filename,'objects':len(bpy.data.objects),'bedStones':len(supportErrors),'addedStones':360,'maxTop':maxTop,'minEmbeddedSupport':min(supportErrors),'maxEmbeddedSupport':max(supportErrors),'unchangedMeshes':len(untouched)};records.append(report);print('GRAVEL NATIVE',report,flush=True)
 if filename=='自然池岸':
  bpy.ops.object.select_all(action='DESELECT');shell=bpy.data.materials.new('Pond stone | browser shader');shell.use_nodes=True
  for k in range(8):
   me=prototypes[k].copy();me.materials.clear();me.materials.append(shell);o=bpy.data.objects.new(f'PondStone_{k}',me);bpy.context.collection.objects.link(o);o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(A/'pond-stones.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
layout['placements']=placements;layout['gravelRevision']=1;layout['bedStones']=517;layout['addedGravel']=360;(A/'pond-stones.json').write_text(json.dumps(layout,separators=(',',':')))
(R/'evidence/gravel-native.json').write_text(json.dumps(records,indent=2));print('GRAVEL COMPLETE',flush=True)
