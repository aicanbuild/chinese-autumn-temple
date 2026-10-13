"""Store optical attributes without changing any mesh, transform or UV."""
import bpy,sys,json,hashlib,array,shutil,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from lotus_optics import configure_lotus_optics

def signatures():
 result={}
 for o in bpy.data.objects:
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for data,prop,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    a=array.array(kind,[0])*(len(data)*width);data.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result

reports=[]
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-lotus-optics.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures();configure_lotus_optics(list(bpy.data.objects));assert signatures()==before
 bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signatures()==before
 counts={};ranges={}
 for o in bpy.data.objects:
  kind=o.get('botanical_part')
  if kind not in {'petal','leaf','bud'}:continue
  assert o.get('lotus_optics_revision')==1;values=[p.value for p in o.data.attributes['_lotus_transmittance'].data]
  assert len(values)==len(o.data.vertices) and all(math.isfinite(v) and 0<=v<=.300001 for v in values)
  if kind=='bud':assert max(values)==0
  counts[kind]=counts.get(kind,0)+1;ranges[kind]=[min(ranges.get(kind,[1,0])[0],min(values)),max(ranges.get(kind,[1,0])[1],max(values))]
 assert counts=={'petal':120,'bud':4,'leaf':6} or counts=={'petal':120,'leaf':6,'bud':4}
 reports.append({'file':filename,'preservedObjects':len(before),'counts':counts,'fractions':ranges,'geometryTransformsUVUnchanged':True});print('OPTICS VERIFIED',reports[-1],flush=True)

# Reuse the same four geometry batches; custom attributes carry local optical weights.
bpy.ops.wm.open_mainfile(filepath=str(R/'source/庄严内殿.blend'))
names={'Sanctuary | living lotus petals','Sanctuary | living lotus leaves','Sanctuary | lotus pollen and seed heart','Sanctuary | botanical stems'}
for name in names:
 group=[o for o in bpy.data.objects if o.type=='MESH' and len(o.data.materials) and o.data.materials[0].name==name]
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=name;bpy.context.object['sourceMaterial']=name
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.get('sourceMaterial') in names:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/lotus-surfaces.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='NONE',export_extras=True,export_attributes=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'evidence/lotus-optics-native.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False))
