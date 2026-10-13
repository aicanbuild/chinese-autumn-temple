import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
parts=[o for o in bpy.data.objects if o.get('stone_lantern')]
assert len(parts)==736
assert len({o.data for o in parts})==46
for i in range(16):assert len([o for o in parts if o['lantern_index']==i])==46
faces=[o for o in parts if o['lantern_index']==0 and 'pierced stone face' in o.name]
assert len(faces)==4
for o in faces:
 # Cast through the actual central aperture in local mesh coordinates.
 hit,*_=o.ray_cast(Vector((0,-1,1.487)),Vector((0,1,0)))
 assert not hit,'Round stone window must remain open'
assert len([o for o in bpy.data.objects if o.get('bridge_asset')])==843
assert len([o for o in bpy.data.objects if o.get('pond_stone')])==257
assert len([o for o in bpy.data.objects if o.get('landscape_asset')])==1241
assert any(o.get('detailed_koi') for o in bpy.data.objects)
assert any(o.get('altar_sculpture') for o in bpy.data.objects)
result={'lamps':16,'editableParts':len(parts),'sharedPartMeshes':46,'openStoneWindowsVerified':True,'bridgeStonesForestKoiAltarPreserved':True}
(R/'evidence/lanterns-native-verification.json').write_text(json.dumps(result,indent=2));print(result)
