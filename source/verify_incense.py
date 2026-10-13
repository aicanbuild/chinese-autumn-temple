import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/铸铜香炉.blend'))
parts=[o for o in bpy.data.objects if o.get('incense_vessel')];meta=json.loads((R/'dist/assets/incense-vessel.json').read_text());assert len(parts)==meta['components']
body=next(o for o in parts if o.name.startswith('Vessel |'))
# A downward ray through the vessel's open mouth must reach its deep interior floor.
hit,point,normal,index=body.ray_cast(Vector((0,0,1)),Vector((0,0,-1)));assert hit and .14<point.z<.18,(hit,point)
assert len([o for o in parts if o.name.startswith('Foot | cabriole')])==3
assert len([o for o in parts if o.name.startswith('Ear | open')])==2
ash=next(o for o in parts if o.name.startswith('Ash | subtly'));z=[(ash.matrix_world@v.co).z for v in ash.data.vertices];assert 1.51<min(z)<max(z)<1.52
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
assert len([o for o in bpy.data.objects if o.get('incense_vessel')])==meta['components']
assert len([o for o in bpy.data.objects if o.get('native_incense_stick')])==3
assert len([o for o in bpy.data.objects if o.get('altar_sculpture')])==38
assert any(o.get('detailed_koi') for o in bpy.data.objects)
assert bpy.data.objects.get('Reflecting pond')
result={'editableVesselComponents':len(parts),'hollowBowl':True,'interiorFloorLocalZ':point.z,'ashWorldHeight':[min(z),max(z)],'legs':3,'openHandles':2,'nativeIncenseSticks':3,'retainedRestoredSculpture':True,'retainedPondAndFish':True}
(R/'evidence/incense-native-verification.json').write_text(json.dumps(result,indent=2));print('VERIFIED',result,flush=True)
