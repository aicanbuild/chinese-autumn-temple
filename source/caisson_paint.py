"""Uniform matte mineral paint with fine substrate grain, shared by native builds."""
NAMES={'Sanctuary | azurite painted wood','Sanctuary | malachite painted wood'}
def apply_refined_paint(materials):
 changed=[]
 for m in materials:
  if not any(m.name==name or m.name.startswith(name+'.') for name in NAMES):continue
  n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
  for link in list(p.inputs['Roughness'].links):l.remove(link)
  p.inputs['Roughness'].default_value=.68;p.inputs['Metallic'].default_value=0
  normal=next(x for x in n if x.type=='NORMAL_MAP');normal.inputs['Strength'].default_value=.075
  t=normal.inputs['Color'].links[0].from_node;assert t.type=='TEX_IMAGE'
  mapping=n.get('Refined paint grain scale') or n.new('ShaderNodeMapping');mapping.name='Refined paint grain scale';mapping.inputs['Scale'].default_value=(6,6,6)
  uv=n.get('Refined paint UV') or n.new('ShaderNodeTexCoord');uv.name='Refined paint UV';l.new(uv.outputs['UV'],mapping.inputs['Vector']);l.new(mapping.outputs['Vector'],t.inputs['Vector'])
  m['refined_paint_revision']=1;changed.append(m.name)
 assert all(any(n==base or n.startswith(base+'.') for n in changed) for base in NAMES)
 return changed
