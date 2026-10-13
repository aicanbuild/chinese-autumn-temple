"""Sync the shared daylight direction and color to editable Blender lighting."""
import bpy,math,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];full=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-daylight.blend'
if not backup.exists():shutil.copy2(full,backup)
d=json.loads((R/'dist/assets/daylight.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(full))
def signature():
 h=hashlib.sha256();count=0
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.type!='MESH':continue
  count+=1;h.update(o.name.encode());h.update(str([list(row) for row in o.matrix_world]).encode())
  for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 return count,h.hexdigest()
before=signature();sunlights=[o for o in bpy.data.objects if o.type=='LIGHT' and o.data.type=='SUN'];assert sunlights
position=Vector((d['sunPosition'][0],-d['sunPosition'][2],d['sunPosition'][1]));target=Vector((d['sunTarget'][0],-d['sunTarget'][2],d['sunTarget'][1]))
col=[int(d['sunColor'][i:i+2],16)/255 for i in [1,3,5]];col=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in col]
for o in sunlights:o.location=position;o.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler();o.data.energy=d['sunIntensity'];o.data.color=col
world=bpy.context.scene.world;nodes=world.node_tree.nodes
for node in nodes:
 if node.type=='BACKGROUND':node.inputs['Strength'].default_value=d['nativeEnvironmentStrength']
assert signature()==before;bpy.ops.wm.save_as_mainfile(filepath=str(full));bpy.ops.wm.open_mainfile(filepath=str(full));assert signature()==before
report={'meshGeometryAndTransformsPreserved':True,'meshes':before[0],'sunLights':len(sunlights),'daylight':d,'note':'Shared source direction/color and relative environment level. Browser atmospheric pass remains a real-time approximation.'}
(R/'evidence/daylight-native.json').write_text(json.dumps(report,indent=2));print(report)
