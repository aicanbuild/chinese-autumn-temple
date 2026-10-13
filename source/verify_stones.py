import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
parts=[o for o in bpy.data.objects if o.get('pond_stone')];meta=json.loads((R/'dist/assets/pond-stones.json').read_text());assert len(parts)==len(meta['placements'])
unique={o.data for o in parts};assert len(unique)==8
for data in unique:
 bm=bmesh.new();bm.from_mesh(data);assert all(len(e.link_faces)==2 for e in bm.edges),'Every stone must be closed';assert bm.calc_volume()>1;bm.free()
for o in parts:
 if o['pond_zone']=='bank':assert abs(o.location.x)>1.75
 if o['pond_zone']=='bed':assert max((o.matrix_world@v.co).z for v in o.data.vertices)<-.70
assert len([o for o in bpy.data.objects if o.get('bridge_asset')])==843
assert len([o for o in bpy.data.objects if o.get('landscape_asset')])==1241
assert any(o.get('detailed_koi') for o in bpy.data.objects)
assert any(o.get('altar_sculpture') for o in bpy.data.objects)
result={'stones':len(parts),'closedPrototypeMeshes':len(unique),'bankStones':sum(o['pond_zone']=='bank' for o in parts),'submergedStones':sum(o['pond_zone']!='bank' for o in parts),'bridgeApproachClear':True,'bridgeForestKoiAndAltarPreserved':True};(R/'evidence/stones-native-verification.json').write_text(json.dumps(result,indent=2));print(result)
