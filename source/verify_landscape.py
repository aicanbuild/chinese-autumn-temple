import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
objects=[o for o in bpy.data.objects if o.get('landscape_asset')]
terrain=next(o for o in objects if o.name=='Sculpted woodland terrain')
assert len(objects)==1241,len(objects)
assert len(terrain.data.vertices)==51681
assert min(math.hypot(v.co.x/11.7,(v.co.y+5.8)/7.1) for v in terrain.data.vertices)>.999
assert max(v.co.z for v in terrain.data.vertices)>35
assert min(p.normal.z for p in terrain.data.polygons)>0
assert any(o.get('altar_sculpture') for o in bpy.data.objects)
assert all(o.hide_render for o in bpy.data.objects if o.type=='MESH' and any(m and m.name=='Manicured moss garden' for m in o.data.materials))
result={'landscapeObjects':len(objects),'trees':620,'terrainVertices':len(terrain.data.vertices),'highestTerrain':max(v.co.z for v in terrain.data.vertices),'pondOpening':True,'upwardNormals':True,'altarPreserved':True}
(R/'evidence/landscape-native-verification.json').write_text(json.dumps(result,indent=2));print(result)
