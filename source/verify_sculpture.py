import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
parts=[o for o in bpy.data.objects if o.get('altar_sculpture')]
meta=json.loads((R/'dist/assets/sculpture.json').read_text());assert len(parts)==meta['components'],(len(parts),meta)
body=next(o for o in parts if o.name.startswith('Tang sculpture |'))
assert len(body.data.vertices)>100000,'Scanned face and robe detail must survive.'
assert not body.get('integrated_hands') and body.get('hand_revision')==5
assert body.get('restored_hands_removed')
assert not any(o.name.startswith('Restored ') and 'hand' in o.name for o in parts)
assert all(o.get('restoration_version')==2 for o in parts)
bounds=[o.matrix_world@Vector(c) for o in parts for c in o.bound_box]
assert min(p.z for p in bounds)>1.89 and max(p.z for p in bounds)<3.95
assert any(o.get('detailed_koi') for o in bpy.data.objects),'Existing fish must survive source assembly.'
assert bpy.data.objects.get('Reflecting pond')
result={'editableComponents':len(parts),'nativeVertices':sum(len(o.data.vertices) for o in parts),'scannedBodyVertices':len(body.data.vertices),'restoredHands':0,'handsFusedToBody':False,'height':max(p.z for p in bounds)-min(p.z for p in bounds),'nativeTemplePreservesFishAndWater':True}
(R/'evidence/sculpture-native-verification.json').write_text(json.dumps(result,indent=2));print('VERIFIED',result,flush=True)
