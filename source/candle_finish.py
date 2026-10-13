"""Refine existing sanctuary wax without replacing accepted furnishings."""
import math

def finish_candles(objects):
 bodies=[o for o in objects if o.name.startswith('Candle | red wax')]
 drips=[o for o in objects if o.name.startswith('Candle | accumulated wax drip')]
 for o in bodies:
  if o.get('continuous_wax_revision') or o.get('wax_finish_revision')==1:continue
  vs=o.data.vertices;cx=sum(v.co.x for v in vs)/len(vs);cy=sum(v.co.y for v in vs)/len(vs)
  for v in vs:
   ring=v.index//64;a=math.atan2(v.co.y-cy,v.co.x-cx);wave=.0034*math.sin(3*a+cx)+.0018*math.sin(7*a-cy)
   if ring in [2,3,4]:v.co.z+=wave*({2:.6,3:1,4:.35}[ring])
  o['wax_finish_revision']=1;o.data.update()
 for o in drips:
  if o.type!='CURVE' or o.get('wax_finish_revision')==1:continue
  for spline in o.data.splines:
   for i,p in enumerate(spline.points):
    t=i/(len(spline.points)-1)
    # A narrow cooled run ends in a rounded bead, not a uniform tube.
    p.radius=.40+.35*(1-t)+.85*math.exp(-((t-.85)/.12)**2)
    if i==len(spline.points)-1:p.radius=.15
  o['wax_finish_revision']=1
 for o in bodies:
  for m in o.data.materials:
   p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.43
   p.inputs['Subsurface Weight'].default_value=.12;p.inputs['Subsurface Radius'].default_value=(1,.25,.12);p.inputs['Subsurface Scale'].default_value=.012
 rim_ranges=[]
 for o in bodies:
  if o.get('continuous_wax_revision'):continue
  crown=[v.co.z for v in o.data.vertices[3*64:4*64]];span=max(crown)-min(crown);assert .006<span<.011;rim_ranges.append(span)
 for o in drips:
  for spline in o.data.splines:
   radii=[p.radius for p in spline.points];assert min(radii)<.2 and max(radii)>1.1
 return {'bodies':len(bodies),'drips':len(drips)}
