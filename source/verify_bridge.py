import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
parts=[o for o in bpy.data.objects if o.get('bridge_asset')]
meta=json.loads((R/'dist/assets/bridge.json').read_text());assert len(parts)==meta['components']
boards=[o for o in parts if 'deck_center_y' in o];assert len(boards)==71
for o in boards:
 y=o['deck_center_y'];expected=.52+.61*math.sin((y+12.4)/13.3*math.pi)+.07
 points=[o.matrix_world@v.co for v in o.data.vertices];assert abs(max(v.z for v in points)-expected)<.0001
assert len([o for o in parts if o.name.startswith('Giboshi | lotus bud cap')])==30
assert len([o for o in parts if o.name.startswith('Joined diagonal brace')])==56
assert len([o for o in bpy.data.objects if o.get('landscape_asset')])==1241
assert any(o.get('detailed_koi') for o in bpy.data.objects)
assert any(o.get('altar_sculpture') for o in bpy.data.objects)
result={'components':len(parts),'boards':len(boards),'giboshiCaps':30,'diagonalBraces':56,'deckHeightMatchesExistingWalkSurface':True,'landscapeFishAndAltarPreserved':True}
(R/'evidence/bridge-native-verification.json').write_text(json.dumps(result,indent=2));print(result)
