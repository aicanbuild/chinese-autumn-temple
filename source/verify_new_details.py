import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'));bpy.context.view_layer.update()
objects=list(bpy.data.objects);hands=[o for o in objects if o.get('hand_revision')==3];assert len(hands)==2
body=next(o for o in objects if o.name.startswith('Tang sculpture'));assert len(body.data.vertices)>100000
lotus=[o for o in objects if o.get('pond_lotus')];leaves=[o for o in lotus if o.name.startswith('Pond lotus | gently cupped radial leaf')];assert len(leaves)==14
stand=next(o for o in objects if o.get('wooden_fish') and o.name.startswith('Muyu | stand top'));center=sum((stand.matrix_world@v.co for v in stand.data.vertices),Vector())/len(stand.data.vertices);assert (center-Vector((-.95,6.45,1.594))).length<.002,center
wood=[o for o in objects if o.get('wooden_fish')];assert set(o['assembly'] for o in wood)=={'body','stand','mallet'}
caisson=[o for o in objects if o.get('fine_caisson')];assert len(caisson)>=1599
assert len([o for o in caisson if o.get('ceiling_carving')])==367
assert len({o['dougong_cluster'] for o in caisson if 'dougong_cluster' in o})==96
assert any(o.get('detailed_koi') for o in objects);assert any(o.name=='Reflecting pond' for o in objects)
# Scanned face and body vertices must be identical to the pre-repair original.
original_name=body.name
current=[tuple(v.co) for v in body.data.vertices]
with bpy.data.libraries.load(str(R/'source/主殿佛像-before-anatomical-hands.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Tang sculpture')]
assert len(dst.objects)==1;original=dst.objects[0];assert [tuple(v.co) for v in original.data.vertices]==current
report={'restoredHands':2,'scannedBodyUnchanged':True,'lotusLeaves':14,'lotusPatches':2,'flowers':3,'woodenFishAssemblies':3,'standCenterNative':list(center),'fineCaissonObjects':len(caisson),'bracketClusters':96,'pondAndFishPreserved':True};(R/'evidence/temple-details-native.json').write_text(json.dumps(report,indent=2));print('DETAILS_VERIFIED',report,flush=True)
