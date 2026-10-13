"""Preserve every object and mesh while refining only two sanctuary finishes."""
import bpy,sys,shutil,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from mural_finishes import apply_mural_finishes
def signature():
 h=hashlib.sha256()
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
   for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return len(bpy.data.objects),h.hexdigest()
reports=[]
for name in ['庄严内殿','听秋寺院']:
 path=R/'source'/f'{name}.blend';backup=path.with_name(path.stem+'-before-mural-plaster.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signature();apply_mural_finishes();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
 panels=[o for o in bpy.data.objects if o.get('sanctuary_interior') and ('celestial garden assembly' in o.name or 'continuous lotus paradise' in o.name)]
 assert len(panels)==4
 for o in panels:
  assert len(o.data.uv_layers)==2
  m=o.data.materials[0];images=[n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(images)==3 and all(i.packed_file for i in images)
  assert m['mural_surface_revision']==1
  width,height=(4.34,2.18) if 'Side wall' in o.name else (3.10,1.99)
  uv=[p.uv[:] for p in o.data.uv_layers['Plaster metres'].data];assert abs(max(p[0] for p in uv)-min(p[0] for p in uv)-width)<1e-5;assert abs(max(p[1] for p in uv)-min(p[1] for p in uv)-height)<1e-5
 reports.append({'file':str(path),'allGeometryAndTransformsPreserved':True,'objects':before[0],'panels':4,'packedMapsPerMaterial':3,'physicalUVMetresVerified':True})

bpy.ops.wm.open_mainfile(filepath=str(R/'source/庄严内殿.blend'));parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')]
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
materials=set(m for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m)
for m in materials:
 group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==m]
 if not group:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=m.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'dist/assets/sanctuary.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
p=R/'dist/assets/sanctuary.json';meta=json.loads(p.read_text());meta['muralRevision']=1;meta['muralArtworks']=2;p.write_text(json.dumps(meta,indent=2))
(R/'evidence/mural-plaster-native.json').write_text(json.dumps(reports,indent=2));print('MURAL VERIFICATION',reports,flush=True)
