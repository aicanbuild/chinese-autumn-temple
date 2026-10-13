"""Restore the archived scanned body, without any digitally reconstructed hands."""
import bpy, json, shutil, hashlib, struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=R/'source';A=R/'dist/assets'
baseline=S/'主殿佛像-before-integrated-hands.blend'
assert baseline.exists(), 'The unmodified scanned body archive is required.'

def signature(mesh):
 h=hashlib.sha256()
 for v in mesh.vertices:h.update(struct.pack('<3f',*v.co))
 for p in mesh.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<%dI'%len(p.vertices),*p.vertices))
 return h.hexdigest()

for name in ['主殿佛像','听秋寺院']:
 backup=S/(name+'-before-removing-restored-hands.blend')
 if not backup.exists():shutil.copy2(S/(name+'.blend'),backup)
bpy.ops.wm.open_mainfile(filepath=str(S/'主殿佛像.blend'))
body=next(o for o in bpy.data.objects if o.name.startswith('Tang sculpture'))
gold=body.data.materials[0]
with bpy.data.libraries.load(str(baseline),link=False) as (src,dst):
 dst.objects=[name for name in src.objects if name.startswith('Tang sculpture')]
assert len(dst.objects)==1
original=dst.objects[0];expected=signature(original.data)
body.data=original.data.copy();body.data.name='Original scanned Buddha | unrestored hands'
body.data.materials.clear();body.data.materials.append(gold)
bpy.data.objects.remove(original,do_unlink=True)
for o in list(bpy.data.objects):
 if o.name.startswith('Restored ') and 'hand' in o.name:bpy.data.objects.remove(o,do_unlink=True)
for key in ['integrated_hands','wrist_topology_verified']:
 if key in body:del body[key]
body['hand_revision']=5;body['restored_hands_removed']=True
assert signature(body.data)==expected
parts=[o for o in bpy.data.objects if o.type=='MESH']
assert len(parts)==36
assert all(o.get('altar_sculpture') for o in parts)
report={'restoredHands':0,'originalScanGeometryRestored':True,'bodyGeometrySHA256':expected,'bodyVertices':len(body.data.vertices),'bodyFaces':len(body.data.polygons),'components':len(parts)}
bpy.ops.wm.save_as_mainfile(filepath=str(S/'主殿佛像.blend'))
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=body
bpy.ops.object.convert(target='MESH');bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=str(A/'sculpture.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
p=A/'sculpture.json';meta=json.loads(p.read_text())
meta.update(components=36,handRevision=5,handsIntegrated=False,restoredHands=False,restoration='Digital gilding and lotus plinth; original scanned hand losses preserved, no reconstructed hands')
p.write_text(json.dumps(meta,indent=2))

bpy.ops.wm.open_mainfile(filepath=str(S/'听秋寺院.blend'))
preserved={o.name for o in bpy.data.objects if not o.get('altar_sculpture')}
for o in list(bpy.data.objects):
 if o.get('altar_sculpture'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(S/'主殿佛像.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
assert preserved.issubset({o.name for o in bpy.data.objects})
body=next(o for o in dst.objects if o and o.name.startswith('Tang sculpture'))
assert signature(body.data)==expected
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(S/'听秋寺院.blend'))
report['otherTempleObjectsPreserved']=len(preserved)
(R/'evidence/sculpture-hands-removed.json').write_text(json.dumps(report,indent=2))
print('SCULPTURE_HANDS_REMOVED',json.dumps(report),flush=True)
