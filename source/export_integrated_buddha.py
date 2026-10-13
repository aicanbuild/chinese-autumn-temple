"""Promote the inspected, connected restoration and synchronize web/native temple assets."""
import bpy,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';S=R/'source'
validation=R/'evidence/integrated-hands-verification.json'
checked=json.loads(validation.read_text())
assert checked['allTenDigitsShareChestTopology'] and checked['noNewOpenWristSeams']
assert validation.stat().st_mtime>=(S/'主殿佛像-衔接候选.blend').stat().st_mtime
bpy.ops.wm.open_mainfile(filepath=str(S/'主殿佛像-衔接候选.blend'))
body=next(o for o in bpy.data.objects if o.name.startswith('Tang sculpture'))
assert body.get('integrated_hands') and body.get('wrist_topology_verified')
assert body.get('hand_revision')==4
components=len([o for o in bpy.data.objects if o.type=='MESH'])
bpy.ops.wm.save_as_mainfile(filepath=str(S/'主殿佛像.blend'))
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=body
bpy.ops.object.convert(target='MESH');bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=str(A/'sculpture.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
p=A/'sculpture.json';meta=json.loads(p.read_text());meta.update(components=components,handRevision=4,handsIntegrated=True,restoration='Digital gilding and lotus plinth; anatomically sculpted hands fused to scanned forearms; artistic adaptation');p.write_text(json.dumps(meta,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(S/'听秋寺院.blend'))
backup=S/'听秋寺院-before-integrated-hands.blend'
if not backup.exists():shutil.copy2(S/'听秋寺院.blend',backup)
preserved={o.name for o in bpy.data.objects if not o.get('altar_sculpture')}
for o in list(bpy.data.objects):
 if o.get('altar_sculpture'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(S/'主殿佛像.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
assert preserved.issubset({o.name for o in bpy.data.objects})
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(S/'听秋寺院.blend'))
print('INTEGRATED_SCULPTURE_EXPORTED',components,'preserved',len(preserved),'other temple objects',flush=True)
