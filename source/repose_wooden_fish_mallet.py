"""Rest the independent beater beside the fish, with its head inwards.
Only mallet object transforms change; all other mesh/UV/transform data is audited.
"""
import bpy,json,shutil,hashlib,array
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
oldhead=Vector((.205,.18,.078));oldgrip=Vector((.275,-.14,.073))
head=Vector((.253,.055,.040));direction=Vector((.07,-.32,-.025)).normalized();grip=head+direction*(oldgrip-oldhead).length
rotation=(oldgrip-oldhead).rotation_difference(grip-head).to_matrix().to_4x4()
transform=Matrix.Translation(head)@rotation@Matrix.Translation(-oldhead)
def target(o):return o.get('wooden_fish') and o.get('assembly')=='mallet'
def signature():
 result={}
 for o in bpy.data.objects:
  if target(o):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for coll,prop,width,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i')]:
    a=array.array(typ,[0])*(len(coll)*width);coll.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result
asset=R/'dist/assets/wooden-fish.glb';backupdir=R/'evidence/mallet-pose-original';backupdir.mkdir(exist_ok=True)
if not (backupdir/asset.name).exists():shutil.copy2(asset,backupdir/asset.name)
reports=[]
for filename in ['殿内木鱼.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-mallet-rest.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signature();mallets=[o for o in bpy.data.objects if target(o)];assert len(mallets)==11,(filename,len(mallets))
 stand=next(o for o in bpy.data.objects if o.name.startswith('Muyu | stand top'))
 center=sum((stand.matrix_world@v.co for v in stand.data.vertices),Vector())/len(stand.data.vertices)
 anchor=center-Vector((0,0,-.026));placement=Matrix.Translation(anchor)@transform@Matrix.Translation(-anchor)
 for o in mallets:
  if not o.get('mallet_rest_revision'):o.matrix_world=placement@o.matrix_world;o['mallet_rest_revision']=1
 bpy.context.view_layer.update();assert signature()==before
 # Audit actual mallet meshes relative to the stand surface.
 points=[o.matrix_world@v.co-anchor for o in mallets for v in o.data.vertices]
 low=min(v.z for v in points);assert .001<low<.012,low
 assert grip.xy.length>head.xy.length+.1
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
 reports.append({'file':filename,'malletParts':11,'preservedObjects':len(before),'minimumMalletHeight':low,'tableTopHeight':.004})
 if filename=='殿内木鱼.blend':
  groups={}
  for o in bpy.data.objects:
   if o.get('wooden_fish'):groups.setdefault((o.get('assembly'),o.data.materials[0]),[]).append(o)
  exports=[]
  for (assembly,mat),objs in groups.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in objs:o.select_set(True)
   bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name='Muyu_'+assembly+'_'+mat.name.split('|')[-1].strip();o['assembly']=assembly;exports.append(o)
  bpy.ops.object.select_all(action='DESELECT')
  for o in exports:o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(asset),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_extras=True)
def web(p):return [p.x,p.z,-p.y]
report={'head':web(head),'grip':web(grip),'native':reports}
(R/'source/wooden-fish-pose.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('MALLET REST',report,flush=True)
