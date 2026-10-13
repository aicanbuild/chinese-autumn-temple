"""Save and validate continuous candle wax in both editable native projects."""
import bpy,bmesh,sys,json,hashlib,array,shutil,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'));from wax_forms import replace_wax_forms
A=R/'dist/assets';layout=json.loads((A/'sanctuary.json').read_text());original_flames=layout['flames'];reports=[]
def signatures():
 result={}
 for o in bpy.data.objects:
  if o.name.startswith('Candle |'):continue
  h=hashlib.sha256();h.update(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for items,prop,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    values=array.array(kind,[0])*(len(items)*width);items.foreach_get(prop,values);h.update(values.tobytes())
   for uv in o.data.uv_layers:
    values=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',values);h.update(values.tobytes())
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.points:h.update(array.array('f',p.co).tobytes())
  result[o.name]=h.hexdigest()
 return result

def verify(flames):
 bodies=[o for o in bpy.data.objects if o.get('continuous_wax_revision')];assert len(bodies)==4
 assert not any(o.name.startswith('Candle | accumulated wax drip') for o in bpy.data.objects)
 for o in bodies:
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;assert all(f.calc_area()>1e-12 for f in bm.faces);bm.free()
  assert all(math.isfinite(v) for p in o.data.vertices for v in p.co)
  attribute=o.data.attributes.get('wax_molten');assert attribute and max(p.value for p in attribute.data)>.99;assert o.data.materials[0].node_tree.nodes.get('Wax pool roughness')
  i=o['flame_index'];assert abs(o['wax_pool_z']-(flames[i][1]-.015))<1e-6
  # Native wick tip must sit inside the same runtime flame root.
  x,y,z=flames[i];points=[w.matrix_world@p.co.to_3d() for w in bpy.data.objects if w.name.startswith('Candle | carbon wick') for s in w.data.splines for p in s.points]
  assert min((p.x-x-.004)**2+(p.y+z)**2+(p.z-y+.008)**2 for p in points)<1e-10
 return {'bodies':4,'closedPositiveVolumes':True,'detachedDrips':0,'wickPoolAndFlameAligned':True,'nativePoolRoughness':True}

for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-continuous-wax.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures();flames,details=replace_wax_forms(list(bpy.data.objects),original_flames);assert signatures()==before;verify(flames)
 bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signatures()==before;result=verify(flames);result.update(file=filename,preservedObjects=len(before),wax=details);reports.append(result);print('WAX VERIFIED',filename,len(before),flush=True)
 if filename.startswith('庄严'):components=sum(bool(o.get('sanctuary_interior')) for o in bpy.data.objects)
layout['flames']=flames;layout['components']=components;layout['continuousWax']=details;(A/'sanctuary.json').write_text(json.dumps(layout,indent=2))
# Geometry-only replacement preserves the exact existing browser materials and other assets.
bpy.ops.wm.open_mainfile(filepath=str(R/'source/庄严内殿.blend'))
parts=[o for o in bpy.data.objects if o.name.startswith('Candle | red wax') or o.name.startswith('Candle | carbon wick')]
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');parts=list(bpy.context.selected_objects)
groups={name:[o for o in parts if o.data.materials[0].name==name] for name in {o.data.materials[0].name for o in parts}}
for name,group in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=name;bpy.context.object['sourceMaterial']=name
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.get('sourceMaterial') in groups:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'candle-wax.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='NONE',export_extras=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'evidence/wax-forms-native.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False));print('WAX EXPORTED',json.dumps(details),flush=True)
