"""Continuous pillar wax, fused cooled runs, rolled crown and shallow melt pool."""
import math,random

def replace_wax_forms(objects,flames):
 import bpy,bmesh
 from mathutils import Vector
 bodies=[o for o in objects if o.name.startswith('Candle | red wax')]
 drips=[o for o in objects if o.name.startswith('Candle | accumulated wax drip')]
 wicks=[o for o in objects if o.name.startswith('Candle | carbon wick')]
 assert len(bodies)==len(wicks)==len(flames)==4
 report=[];updated=[list(p) for p in flames]
 for o in bodies:
  if o.get('continuous_wax_revision')==1:
   i=o['flame_index'];updated[i][1]=o['wax_pool_z']+.015;report.append(dict(o['wax_form']));continue
  points=[o.matrix_world@v.co for v in o.data.vertices]
  cx=(min(p.x for p in points)+max(p.x for p in points))/2;cy=(min(p.y for p in points)+max(p.y for p in points))/2
  i=min(range(4),key=lambda k:(flames[k][0]-cx)**2+(-flames[k][2]-cy)**2)
  cx,fy,fz=flames[i];cy=-fz;bottom=min(p.z for p in points);height=fy-.015-bottom
  radius=max(math.hypot(p.x-cx,p.y-cy) for p in points);pool=height-.012
  rng=random.Random(482+i*139);runs=[(j*math.tau/7+rng.uniform(-.19,.19),rng.uniform(.055,.17)*height/.46,rng.uniform(.004,.007),rng.uniform(.0027,.0051),rng.random()*6.28) for j in range(7)]
  sectors=128;vs=[];faces=[];uvs=[]
  def wave(a):return .0027*math.sin(3*a+i*.7)+.0013*math.sin(7*a-i*.4)
  def rise(a,z):
   d=height-.013-z;result=0
   for angle,length,width,amount,phase in runs:
    t=d/length
    if t<-.06 or t>1.18:continue
    axis=angle+.018*math.sin(t*5+phase);distance=radius*math.atan2(math.sin(a-axis),math.cos(a-axis))
    bead=math.exp(-((t-.91)/.13)**2);w=width*(.74+.34*bead)
    start=max(0,min(1,(t+.06)/.10));end=max(0,min(1,(1.18-t)/.20));envelope=start*start*(3-2*start)*end*end*(3-2*end)
    result+=amount*(.58+.73*bead)*math.exp(-(distance/w)**2)*envelope
   return result
  def add_ring(r,z,crown=False,body=False):
   for j in range(sectors):
    a=j*math.tau/sectors;zz=z+(wave(a) if crown else 0);rr=r
    if body:rr+=rise(a,zz)+.00016*math.sin(a*11+zz*16)*math.sin(math.pi*max(0,min(1,zz/height)))
    vs.append((cx+rr*math.cos(a),cy+rr*math.sin(a),bottom+zz));uvs.append((j/sectors,zz))
  add_ring(radius-.0014,0)
  add_ring(radius,.0014)
  for k in range(1,57):
   t=k/56;z=(height-.021)*(1-(1-t)**1.6);add_ring(radius,z,body=True)
  # Roll over the worn lip into a shallow, nearly level liquid pool.
  for r,z in [(1,height-.012),(.998,height-.007),(.986,height-.002),(.954,height+.0005),(.906,height-.001),(.85,height-.003),(.79,height-.006),(.73,height-.0095),(.68,pool)]:
   add_ring(radius*r,z,crown=True,body=r>.985)
  for k in range(1,9):
   r=.68*(1-k/9)
   for j in range(sectors):
    a=j*math.tau/sectors;zz=pool+wave(a)*(r/.68)**8+.00006*math.sin(a*3)*math.sin(r*9)
    vs.append((cx+radius*r*math.cos(a),cy+radius*r*math.sin(a),bottom+zz));uvs.append((j/sectors,zz))
  rings=len(vs)//sectors
  for ring in range(rings-1):
   for j in range(sectors):a=ring*sectors+j;b=ring*sectors+(j+1)%sectors;faces.append((a,b,b+sectors,a+sectors))
  lower=len(vs);vs.append((cx,cy,bottom));uvs.append((.5,0));upper=len(vs);vs.append((cx,cy,bottom+pool));uvs.append((.5,pool))
  for j in range(sectors):faces.append((lower,(j+1)%sectors,j));faces.append((upper,(rings-1)*sectors+j,(rings-1)*sectors+(j+1)%sectors))
  m=bpy.data.meshes.new('Continuous wax with fused cooled runs');inverse=o.matrix_world.inverted();m.from_pydata([inverse@Vector(v) for v in vs],[],faces);m.update()
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(m);bm.free()
  for p in m.polygons:p.use_smooth=abs(p.normal.z)<.999 or p.center.z>bottom+.01
  uv=m.uv_layers.new()
  for p in m.polygons:
   us=[uvs[m.loops[k].vertex_index][0] for k in p.loop_indices];seam=max(us)-min(us)>.5
   for k in p.loop_indices:u,v=uvs[m.loops[k].vertex_index];uv.data[k].uv=(u+(1 if seam and u<.5 else 0),v)
  for mat in o.data.materials:m.materials.append(mat)
  o.data=m;o['continuous_wax_revision']=1;o['wax_pool_z']=bottom+pool;o['flame_index']=i
  # Match the same candle's existing wick without changing other ritual props.
  wick=min(wicks,key=lambda w:min((w.matrix_world@Vector(p.co[:3])-Vector((cx,cy,bottom+height))).length for s in w.data.splines for p in s.points))
  wick.data.splines.clear();s=wick.data.splines.new('POLY');s.points.add(3);inv=wick.matrix_world.inverted()
  for p,pos in zip(s.points,[(cx,cy,bottom+pool-.004),(cx+.001,cy,bottom+pool+.001),(cx+.003,cy,bottom+pool+.005),(cx+.004,cy,bottom+pool+.007)]):p.co=(*(inv@Vector(pos)),1)
  wick.data.bevel_depth=.0017;wick.data.bevel_resolution=3;wick.data.use_fill_caps=True
  updated[i][1]=bottom+pool+.015
  report.append({'index':i,'radius':radius,'height':height,'bottom':bottom,'pool':bottom+pool,'runs':len(runs),'vertices':len(vs),'triangles':sum(len(p.vertices)-2 for p in m.polygons)})
  o['wax_form']=report[-1]
 for o in drips:
  if o in objects:objects.remove(o)
  bpy.data.objects.remove(o,do_unlink=True)
 # The editable Blender material has the same solid-to-liquid roughness as WebGL.
 for o in bodies:
  i=o['flame_index'];x,y,z=updated[i];radius=o['wax_form']['radius']*.68
  def smooth(a,b,v):
   t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
  values=[]
  for v in o.data.vertices:
   p=o.matrix_world@v.co;r=math.hypot(p.x-x,p.y+z)
   values.append((1-smooth(radius*.80,radius,r))*(1-smooth(.002,.008,abs(p.z-(y-.015)))))
  attribute=o.data.attributes.get('wax_molten') or o.data.attributes.new('wax_molten','FLOAT','POINT');attribute.data.foreach_set('value',values)
  material=o.data.materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links
  attr=nodes.get('Wax molten region') or nodes.new('ShaderNodeAttribute');attr.name='Wax molten region';attr.attribute_name='wax_molten'
  rough=nodes.get('Wax pool roughness') or nodes.new('ShaderNodeMapRange');rough.name='Wax pool roughness';rough.inputs['From Min'].default_value=0;rough.inputs['From Max'].default_value=1;rough.inputs['To Min'].default_value=.43;rough.inputs['To Max'].default_value=.19
  links.new(attr.outputs['Fac'],rough.inputs['Value']);links.new(rough.outputs['Result'],nodes.get('Principled BSDF').inputs['Roughness'])
 return updated,report
