"""Authored thin-shell transport attributes; buds intentionally remain opaque."""
import math

def smoothstep(a,b,t):
 t=max(0,min(1,(t-a)/(b-a)));return t*t*(3-2*t)

def configure_lotus_optics(parts):
 for o in parts:
  kind=o.get('botanical_part')
  if kind not in {'petal','leaf','bud'}:continue
  mesh=o.data;uvs={}
  for old in ['lotus_transmittance','lotus_thickness']:
   if mesh.attributes.get(old):mesh.attributes.remove(mesh.attributes[old])
  for p in mesh.polygons:
   for li in p.loop_indices:
    uvs.setdefault(mesh.loops[li].vertex_index,mesh.uv_layers[0].data[li].uv.copy())
  transmission=mesh.attributes.get('_lotus_transmittance') or mesh.attributes.new('_lotus_transmittance','FLOAT','POINT')
  thickness=mesh.attributes.get('_lotus_thickness') or mesh.attributes.new('_lotus_thickness','FLOAT','POINT')
  # Creating another attribute may invalidate earlier Blender RNA references.
  transmission=mesh.attributes['_lotus_transmittance'];thickness=mesh.attributes['_lotus_thickness']
  for i in range(len(mesh.vertices)):
   u,v=uvs.get(i,(.5,.5))
   if kind=='petal':
    weight=.30*(.30+.70*smoothstep(.06,.85,v))*(.70+.30*abs(2*u-1)**2)
   elif kind=='leaf':
    x,y=(u-.5)/.48,(v-.5)/.48;r=math.hypot(x,y);angle=math.atan2(y,x)
    weight=.18*(.35+.65*smoothstep(.12,.8,r))*(.72+.28*math.sin(angle*14)**2)
   else:weight=0
   transmission.data[i].value=weight
   thickness.data[i].value=.00065 if kind=='leaf' else .00045
  o['lotus_optics_revision']=1
 # Native Cycles diffusion is a separate approximation. Web transport below
 # uses the exported fraction, not this renderer-specific subsurface model.
 for mat in {o.data.materials[0] for o in parts if o.get('botanical_part') in {'petal','leaf'}}:
  bsdf=mat.node_tree.nodes.get('Principled BSDF');is_leaf='leaves' in mat.name
  bsdf.inputs['Subsurface Weight'].default_value=.10 if is_leaf else .18
  bsdf.inputs['Subsurface Radius'].default_value=(.25,.55,.15) if is_leaf else (.8,.35,.2)
  bsdf.inputs['Subsurface Scale'].default_value=.0006 if is_leaf else .001
