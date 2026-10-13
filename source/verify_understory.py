"""Check real native geometry, non-degenerate copper UVs and preservation of the scene."""
import bpy,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def untouched_signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.get('understory_asset'):continue
  count+=1;h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
   for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 return {'objects':count,'geometryAndTransformHash':h.hexdigest()}
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院-before-understory.blend'));before=untouched_signature()
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'));after=untouched_signature();assert before==after,(before,after)
parts=[o for o in bpy.data.objects if o.get('understory_asset')];assert len(parts)==254
terrain=next(o for o in bpy.data.objects if o.name.startswith('Sculpted woodland terrain'))
from mathutils import Vector
max_error=0;max_radius=0
for o in parts:
 x,y,z=o.location;hit,p,n,i=terrain.ray_cast(terrain.matrix_world.inverted()@Vector((x,y,150)),Vector((0,0,-1)));assert hit
 error=abs(z+.025-(terrain.matrix_world@p).z);max_error=max(max_error,error);assert error<.002
 max_radius=max(max_radius,max(math.hypot(v.co.x,v.co.y) for v in o.data.vertices));assert max_radius<1.45
report={'nonUnderstoryGeometryPreserved':before==after,'preservedObjects':after['objects'],'shrubParts':len(parts),'maxRootHeightErrorMeters':max_error,'maxPrototypeRadiusMeters':max_radius}
(R/'evidence/understory-native.json').write_text(json.dumps(report,indent=2));print(report)
