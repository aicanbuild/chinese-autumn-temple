"""Keep the editable Blender pond's wave normals in sync with the browser optics."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
water=bpy.data.objects.get('Reflecting pond');assert water
mat=water.data.materials[0];mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links
for n in list(nodes):
 if n.name.startswith('Pond optics |'):nodes.remove(n)
def node(kind,name):
 n=nodes.new(kind);n.name='Pond optics | '+name;return n
geometry=node('ShaderNodeNewGeometry','world coordinates')
mapping=node('ShaderNodeMapping','four metre ripples');mapping.inputs['Scale'].default_value=(.25,.25,.25)
links.new(geometry.outputs['Position'],mapping.inputs['Vector'])
for axis,speed in [(0,.00010),(1,.000035)]:
 driver=mapping.inputs['Location'].driver_add('default_value',axis).driver;driver.expression=f'frame*{speed}'
normals=[]
for i in range(2):
 texture=node('ShaderNodeTexImage',f'wave normals {i}');texture.image=bpy.data.images.load(str(A/f'pond-ripples-{i}.png'),check_existing=True);texture.image.colorspace_settings.name='Non-Color';texture.extension='REPEAT';links.new(mapping.outputs['Vector'],texture.inputs['Vector']);normals.append(texture)
mix=node('ShaderNodeMixRGB','crossing ripples');mix.inputs[0].default_value=.5
links.new(normals[0].outputs['Color'],mix.inputs[1]);links.new(normals[1].outputs['Color'],mix.inputs[2])
normal=node('ShaderNodeNormalMap','world surface normal');normal.space='WORLD';normal.inputs['Strength'].default_value=1.
previous=mix.outputs[0]
for operation,vector,label in [('SUBTRACT',(.5,.5,0),'center'),('MULTIPLY',(.42,.42,1),'strength'),('ADD',(.5,.5,0),'encode')]:
 n=node('ShaderNodeVectorMath','calm decode '+label);n.operation=operation;n.inputs[1].default_value=vector;links.new(previous,n.inputs[0]);previous=n.outputs['Vector']
links.new(previous,normal.inputs['Color'])
principled=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');links.new(normal.outputs['Normal'],principled.inputs['Normal'])
principled.inputs['Roughness'].default_value=.075;principled.inputs['IOR'].default_value=1.333;principled.inputs['Transmission Weight'].default_value=.93
water['pond_optics']='48-wave normal field, animated in world coordinates; Three.js projects baked photon density onto submerged receivers.'
if hasattr(water,'is_caustics_caster'):water.is_caustics_caster=True
for o in bpy.data.objects:
 if o.get('pond_stone') and hasattr(o,'is_caustics_receiver'):o.is_caustics_receiver=True
assert len([o for o in bpy.data.objects if o.get('stone_lantern')])==736
assert len([o for o in bpy.data.objects if o.get('pond_stone')])==len(json.loads((A/'pond-stones.json').read_text())['placements'])
assert len([o for o in bpy.data.objects if o.get('bridge_asset')])==843
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
result={'nativeWaterNormals':2,'worldSpace':True,'animated':True,'ior':1.333,'geometryPreserved':True}
(R/'evidence/water-native-verification.json').write_text(json.dumps(result,indent=2));print(result)
