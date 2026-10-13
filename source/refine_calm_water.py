"""Match native world normal XY strength to the browser's .42 decode."""
import bpy,shutil,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'source/听秋寺院.blend';backup=path.with_name('听秋寺院-before-calm-water.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path))
water=bpy.data.objects.get('Reflecting pond');assert water
material=water.data.materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links
normal=nodes.get('Pond optics | world surface normal');mix=nodes.get('Pond optics | crossing ripples');assert normal and mix
source=normal.inputs['Color'].links[0].from_socket
for n in list(nodes):
 if n.name.startswith('Pond optics | calm decode'):nodes.remove(n)
# Decode only XY, apply strength, then re-encode while preserving Z. Let the
# existing world-space Normal Map node normalize the resulting vector.
previous=mix.outputs['Color']
for operation,vector,label in [('SUBTRACT',(.5,.5,0),'center'),('MULTIPLY',(.42,.42,1),'strength'),('ADD',(.5,.5,0),'encode')]:
 n=nodes.new('ShaderNodeVectorMath');n.name='Pond optics | calm decode '+label;n.operation=operation;n.inputs[1].default_value=vector;links.new(previous,n.inputs[0]);previous=n.outputs['Vector']
links.new(previous,normal.inputs['Color']);normal.inputs['Strength'].default_value=1
water['pond_optics']='Calm wave slope .273 (= atlas .65 × decode .42); matching nominal slope for browser photon-density layers. Animated map blending remains an approximation.'
bpy.ops.wm.save_as_mainfile(filepath=str(path));report={'objects':len(bpy.data.objects),'normalMaps':2,'decodeXYStrength':.42,'nominalWaveSlopeScale':.273,'geometryChanged':False};(R/'evidence/calm-water-native.json').write_text(json.dumps(report,indent=2));print('CALM WATER NATIVE',report,flush=True)
