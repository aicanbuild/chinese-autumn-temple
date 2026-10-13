"""Refine four existing koi bodies/materials without replacing scene placements."""
import bpy,sys,math,json,shutil,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets/koi';sys.path.insert(0,str(R/'source'))
from koi_surface_finish import radius,old_radius
from granite_finish import refresh_glb
baseline=R/'evidence/koi-before-finish.glb'
if not baseline.exists():shutil.copy2(A/'koi.glb',baseline)
report=[]
# Original tube coordinates make the narrow seam reproducible on repeated runs.
originalGillNames=['Operculum crease -1','Operculum crease 1']
with bpy.data.libraries.load(str(R/'source/锦鲤-before-koi-finish.blend'),link=False) as (src,dst):dst.meshes=originalGillNames.copy()
originalGills={name:[tuple(v.co) for v in me.vertices] for name,me in zip(originalGillNames,dst.meshes)}
for me in dst.meshes:bpy.data.meshes.remove(me)

def body(me):return any(m and m.name.startswith('Koi ') and any(k in m.name for k in ['kohaku','sanke','yamabuki','platinum']) for m in me.materials)
def gill(me):return me.name.startswith('Operculum crease')
def eye(me):return me.name.startswith(('Iris ','Pupil '))
def fingerprint(me):
 h=hashlib.sha256()
 for v in me.vertices:h.update(str(tuple(v.co)).encode())
 for p in me.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
for name in ['锦鲤','听秋寺院']:
 file=R/'source'/(name+'.blend');backup=file.with_name(name+'-before-koi-finish.blend')
 if not backup.exists():shutil.copy2(file,backup)
 bpy.ops.wm.open_mainfile(filepath=str(file))
 oldobjects={o.name:(o.type,tuple(v for row in o.matrix_world for v in row)) for o in bpy.data.objects}
 meshset={o.data for o in bpy.data.objects if o.type=='MESH'};others={me.name:fingerprint(me) for me in meshset if not body(me) and not gill(me) and not eye(me)}
 changed=[];delta=0
 for me in meshset:
  if not body(me):continue
  changed.append(me.name)
  if me.get('continuous_koi_profile'):continue
  for v in me.vertices:
   t=max(0,min(1,(-v.co.y+.6)/1.25));ratio=radius(t)/old_radius(t);before=v.co.copy();v.co.x*=ratio;v.co.z*=ratio;delta=max(delta,(v.co-before).length)
  me.update();me['continuous_koi_profile']=True
 assert len(changed)==4,(name,changed)
 gills=[]
 for me in meshset:
  if not gill(me):continue
  gills.append(me.name)
  if me.get('surface_koi_gill')==2:continue
  for v,original in zip(me.vertices,originalGills[me.name]):
   v.co=original
   side=1 if v.co.x>=0 else -1;a=max(-.6,min(1.15,math.atan2(v.co.z/.117,abs(v.co.x)/.134)))
   ox=side*.134*math.cos(a);oy=.117*math.sin(a);oz=.323+.032*math.cos(a);r=radius((oz+.6)/1.25)
   vertical=.86 if oy>0 else .69;f=.997/math.hypot(ox/r,oy/(r*vertical))
   v.co.x=ox*f+(v.co.x-ox)*.32;v.co.z=oy*f+(v.co.z-oy)*.32
  me.update();me['surface_koi_gill']=2
 assert len(gills)==2,(name,gills)
 eyes=[]
 for me in meshset:
  if not eye(me):continue
  eyes.append(me.name)
  if me.get('refined_koi_eye'):continue
  from mathutils import Vector
  side=1 if sum(v.co.x for v in me.vertices)>0 else -1
  r=radius((.462+.6)/1.25);a=math.atan2(.042/(r*.86),.093/r)
  surface=Vector((side*r*math.cos(a),-.462,r*.86*math.sin(a)))
  normal=Vector((side*math.cos(a),0,math.sin(a)/.86)).normalized()
  iriscenter=surface-normal*.008
  pupil=me.name.startswith('Pupil ')
  oldcenter=Vector((side*(.113 if pupil else .093),-(.469 if pupil else .462),.046 if pupil else .042))
  newcenter=iriscenter+(Vector((side*.020,-.007,.004))*.65 if pupil else Vector())
  for v in me.vertices:v.co=newcenter+(v.co-oldcenter)*.65
  me.update();me['refined_koi_eye']=True
 assert len(eyes)==4,(name,eyes)
 for m in {m for me in meshset if gill(me) for m in me.materials}:
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.06,.035,.025,1);p.inputs['Roughness'].default_value=.8



 used={m for me in meshset if body(me) for m in me.materials};images={}
 for key,filename in [('normal','scales-normal.jpg'),('rough','scales-rough.jpg')]:
  image=bpy.data.images.load(str(A/filename),check_existing=False);image.name='Refined koi '+key;image.colorspace_settings.name='Non-Color';images[key]=image
 for m in used:
  p=m.node_tree.nodes.get('Principled BSDF');assert p
  p.inputs['Roughness'].default_value=1;p.inputs['Coat Weight'].default_value=.18;p.inputs['Coat Roughness'].default_value=.25
  normal=next(n for n in m.node_tree.nodes if n.type=='NORMAL_MAP');normal.inputs['Strength'].default_value=1
  nt=normal.inputs['Color'].links[0].from_node;nt.image=images['normal']
  node=m.node_tree.nodes.get('Koi scale roughness') or m.node_tree.nodes.new('ShaderNodeTexImage');node.name='Koi scale roughness';node.image=images['rough'];m.node_tree.links.new(node.outputs['Color'],p.inputs['Roughness'])
 for image in images.values():image.pack()
 assert oldobjects=={o.name:(o.type,tuple(v for row in o.matrix_world for v in row)) for o in bpy.data.objects}
 assert others=={me.name:fingerprint(me) for me in meshset if not body(me) and not gill(me) and not eye(me)}
 bpy.ops.wm.save_as_mainfile(filepath=str(file));item={'file':name,'bodyMeshes':changed,'gillMeshes':gills,'eyeMeshes':eyes,'maximumVertexChangeMeters':delta,'otherMeshCount':len(others),'objectsPreserved':len(oldobjects)};print('KOI SAVED',item,flush=True)
 if name=='锦鲤':
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'koi.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
  # Reuse exact authored skin images and the refined RGB normal. Exporter's
  # metallic/roughness pack is retained because it has the required channel layout.
  b=(A/'koi.glb').read_bytes();import struct;d=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
  replacements={}
  for im in d.get('images',[]):
   if im['name'] in ['Refined koi normal','scales-normal']:replacements[im['name']]=A/'scales-normal.jpg'
   if im['name']=='scales-rough':replacements[im['name']]=A/'scales-rough.jpg'
   for kind in ['kohaku','sanke','yamabuki','platinum','fin-membrane']:
    if im['name']==kind:replacements[im['name']]=A/(kind+('.png' if kind=='fin-membrane' else '.jpg'))
  item['export']=refresh_glb(A/'koi.glb',replacements);item['images']=[im['name'] for im in d['images']]
 report.append(item)
(R/'evidence/koi-finish-native.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('KOI FINISH COMPLETE',flush=True)
