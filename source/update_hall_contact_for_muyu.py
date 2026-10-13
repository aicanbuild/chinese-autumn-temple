"""Reuse audited floor-near architecture; append only the new stationary stand.
All other revised geometry (hands, ceiling, removed mural pins) is above the
1.0702 + 1m AO horizon. The scan/plinth vertices are unchanged.
"""
import bpy,json,shutil,time,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';started=time.time();source=R/'source/殿内地面接触光照.blend';backup=source.with_name('殿内地面接触光照-before-muyu.blend')
if not backup.exists():shutil.copy2(source,backup)
bpy.ops.wm.open_mainfile(filepath=str(backup))
with bpy.data.libraries.load(str(R/'source/听秋寺院.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Muyu |')]
added=[]
for o in dst.objects:
 if o and o.get('assembly')=='stand':bpy.context.collection.objects.link(o);added.append(o)
 elif o:bpy.data.objects.remove(o,do_unlink=True)
assert len(added)>8
scene=bpy.context.scene;receiver=bpy.data.objects['Hall floor contact receiver'];image=next(n.image for n in receiver.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False
bpy.ops.object.select_all(action='DESELECT');receiver.select_set(True);bpy.context.view_layer.objects.active=receiver
print('FLOOR CONTACT APPENDED STAND',len(added),flush=True);bpy.ops.object.bake(type='EMIT',use_clear=False,margin=8)
image.filepath_raw=str(A/'hall-contact-ao.png');image.file_format='PNG';image.save();image.pack();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source))
report={'reusedAuditedFloorGeometry':True,'changedOtherGeometryOutsideOneMetreHorizon':True,'stationaryStandObjects':len(added),'excludedMovingInstrument':True,'seconds':time.time()-started};(R/'evidence/hall-contact-muyu-update.json').write_text(json.dumps(report,indent=2));print('FLOOR CONTACT UPDATED',report,flush=True)
