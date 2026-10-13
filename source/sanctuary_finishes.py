"""Exportable gold leaf and polished oxblood lacquer, shared by builds and refinements."""
import bpy
from pathlib import Path
A=Path(__file__).resolve().parents[1]/'dist/assets'
def apply_sanctuary_finishes():
 used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 def material(label):
  matches=[m for m in used if m.name.startswith('Sanctuary | '+label)]
  assert len(matches)==1,(label,[m.name for m in matches])
  return matches[0]
 # During the original build, materials exist before objects are constructed.
 if not used:used=set(bpy.data.materials)
 gold=material('hand burnished gold')
 n=gold.node_tree.nodes;l=gold.node_tree.links;n.clear()
 out=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');l.new(p.outputs[0],out.inputs[0])
 p.inputs['Metallic'].default_value=1
 uv=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(8,8,8);l.new(uv.outputs['UV'],mapping.inputs['Vector'])
 for suffix,slot in [('', 'Base Color'),('-normal','Normal'),('-rough','Roughness')]:
  ext='png' if suffix=='-normal' else 'jpg';t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/f'sanctuary-gold-leaf{suffix}.{ext}'),check_existing=True);t.extension='REPEAT';l.new(mapping.outputs['Vector'],t.inputs['Vector'])
  if suffix:t.image.colorspace_settings.name='Non-Color'
  if slot=='Normal':
   normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.8;l.new(t.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs[slot])
  else:l.new(t.outputs['Color'],p.inputs[slot])
 gold['gold_leaf_revision']=1
 wood=material('oxblood lacquer');p=wood.node_tree.nodes.get('Principled BSDF')
 for node in wood.node_tree.nodes:
  if node.bl_idname=='ShaderNodeMix':node.inputs[7].default_value=(.42,.12,.095,1)
 p.inputs['Metallic'].default_value=0;p.inputs['Coat Weight'].default_value=.45;p.inputs['Coat Roughness'].default_value=.20
