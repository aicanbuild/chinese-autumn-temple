"""Original Nelumbo-inspired altar stems, cup petals, seed hearts and peltate leaves."""
import bpy,math,random
from mathutils import Vector,Matrix
from pathlib import Path
A=Path(__file__).resolve().parents[1]/'dist/assets'

def build_lotus_bouquets():
 parts=[];rng=random.Random(4166)
 def material(name,color,rough,texture=None):
  m=bpy.data.materials.new('Sanctuary | '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;m.diffuse_color=(*color,1)
  if texture:
   tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(A/(texture+'.jpg')),check_existing=True);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
   tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(A/(texture+'-normal.png')),check_existing=True);tex.image.colorspace_settings.name='Non-Color';normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.17; m.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs[0],p.inputs['Normal'])
  return m
 petalmat=material('living lotus petals',(1,1,1),.62,'lotus-petal');leafmat=material('living lotus leaves',(.15,.25,.10),.67,'lotus-leaf');pollen=material('lotus pollen and seed heart',(.60,.34,.028),.68)
 stemmat=next(m for m in bpy.data.materials if m.name=='Sanctuary | botanical stems')
 def mesh(name,vs,fs,mat,uvs=None):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();d.materials.append(mat);o=bpy.data.objects.new('Lotus | '+name,d);bpy.context.collection.objects.link(o);o['sanctuary_interior']=True;o['lotus_bouquet']=True;parts.append(o)
  for p in d.polygons:p.use_smooth=True
  if uvs:
   layer=d.uv_layers.new()
   for p in d.polygons:
    for li in p.loop_indices:layer.data[li].uv=uvs[d.loops[li].vertex_index]
  return o
 def tube(name,points,r,mat=stemmat):
  vs=[];fs=[];n=8
  for i,p in enumerate(points):
   p=Vector(p);d=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)]);q=d.to_track_quat('Z','Y');radius=r*(1-.22*i/(len(points)-1))
   for k in range(n):vs.append(tuple(p+q@Vector((radius*math.cos(k*math.tau/n),radius*math.sin(k*math.tau/n),0))))
  for j in range(len(points)-1):
   for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
  return mesh(name,vs,fs,mat)
 def stem(base,end,name):
  base=Vector(base);end=Vector(end);delta=end-base
  return tube(name,[base+delta*(i/20)+Vector((.016*math.sin(math.pi*i/20),.009*math.sin(math.pi*i/20),0)) for i in range(21)],.0055)
 def ellipsoid(name,center,scale,mat,n=20,rings=12):
  vs=[];fs=[]
  for j in range(rings+1):
   ph=j*math.pi/rings
   for k in range(n):a=k*math.tau/n;vs.append(tuple(Vector(center)+Vector((scale[0]*math.sin(ph)*math.cos(a),scale[1]*math.sin(ph)*math.sin(a),scale[2]*math.cos(ph)))))
  for j in range(rings):
   for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
  return mesh(name,vs,fs,mat)
 def flower(center,opening,phase):
  center=Vector(center);tilt=Matrix.Rotation(.32+.12*math.sin(phase),4,'X')@Matrix.Rotation(.14*math.cos(phase),4,'Y')
  for tier,n in enumerate([8,7,5]):
   for k in range(n):
    angle=k*math.tau/n+tier*.37+phase;length=(.145-.021*tier)*rng.uniform(.94,1.06);width=(.057-.006*tier)*rng.uniform(.94,1.04);vs=[];fs=[];uv=[]
    for i in range(19):
     t=i/18;rad=.021+(length*opening)*math.sin(t*1.42);height=.012+t*(.058+.025*tier)+(1-opening)*length*t-.020*opening*t**5
     w=width*math.sin(math.pi*t)**.72
     for j in range(9):
      s=(j-4)/4;curl=.022*s*s*math.sin(math.pi*t)+.003*math.sin(t*math.pi*3+phase)*s*t
      p=Vector((rad*math.cos(angle)-s*w*math.sin(angle),rad*math.sin(angle)+s*w*math.cos(angle),height+curl));vs.append(tuple(center+tilt@p));uv.append(((s+1)/2,t))
    for i in range(18):
     for j in range(8):a=i*9+j;fs.append((a,a+1,a+10,a+9))
    o=mesh('cupped veined petal',vs,fs,petalmat,uv);o['botanical_part']='petal'
  ellipsoid('flat seed receptacle',center+tilt@Vector((0,0,.040)),(.029,.029,.014),pollen,32,12)
  # Numerous thin stamens form a ring; combine them into one editable object per flower.
  stamens=[]
  for k in range(48):
   a=k*2.39996;r=.032+.012*(k%3)/2;h=.050+.009*math.sin(a*3)
   pts=[center+tilt@Vector((r*math.cos(a),r*math.sin(a),.013)),center+tilt@Vector(((r+.003)*math.cos(a),(r+.003)*math.sin(a),h))]
   st=tube('fine stamen',pts,.00065,pollen);cap=ellipsoid('pollen anther',pts[-1],(.0017,.0013,.0036),pollen,8,6);stamens.extend([st,cap])
  bpy.ops.object.select_all(action='DESELECT')
  for o in stamens:o.select_set(True);parts.remove(o)
  bpy.context.view_layer.objects.active=stamens[0];bpy.ops.object.join();o=bpy.context.object;o.name='Lotus | ring of 48 stamens';o['botanical_part']='stamens';parts.append(o)
  for k in range(12):
   a=k*2.4;r=.021*math.sqrt((k+.5)/12);ellipsoid('receptacle stigma',center+tilt@Vector((r*math.cos(a),r*math.sin(a),.054)),(.0017,.0017,.0014),stemmat,8,6)
 def bud(center,phase):
  vs=[];fs=[];uv=[];center=Vector(center)
  for j in range(25):
   t=j/24;r=.037*math.sin(math.pi*t)**.85*(1-.24*t)
   for k in range(48):
    a=k*math.tau/48;rr=r*(1+.025*math.cos(a*5+phase));vs.append(tuple(center+Vector((rr*math.cos(a),rr*math.sin(a),t*.12))));uv.append((k/48,t))
  for j in range(24):
   for k in range(48):a=j*48+k;b=j*48+(k+1)%48;fs.append((a,b,b+48,a+48))
  o=mesh('unopened pink bud',vs,fs,petalmat,uv);o['botanical_part']='bud'
 def leaf(center,radius,tilt,phase):
  vs=[];fs=[];uv=[];center=Vector(center);rot=Matrix.Rotation(tilt,4,'X')@Matrix.Rotation(phase,4,'Z')
  for j in range(13):
   t=j/12
   for k in range(96):
    a=k*math.tau/96;r=radius*t*(1+.034*math.sin(a*5+phase));z=.045*t*t+.009*math.sin(a*5+phase)*t**3+.003*math.cos(a*14)*t
    vs.append(tuple(center+rot@Vector((r*math.cos(a),r*math.sin(a),z))));uv.append((.5+.48*t*math.cos(a),.5+.48*t*math.sin(a)))
  for j in range(12):
   for k in range(96):a=j*96+k;b=j*96+(k+1)%96;fs.append((a,a+96,b+96,b))
  o=mesh('radial peltate leaf',vs,fs,leafmat,uv);o['botanical_part']='leaf';o['stem_attachment']=tuple(center)
 for side in [-1,1]:
  x=side*2.18;y=8.48;base=(x,y,2.43)
  blooms=[(-.13,-.11,3.04,1.),(.16,.05,3.21,.85),(-.12,.16,3.34,.53),(.22,-.08,3.02,0),(.02,.04,3.43,0)]
  for j,(dx,dy,z,opening) in enumerate(blooms):
   end=(x+side*dx,y+dy,z+(.015 if side>0 else 0));stem(base,end,'arched flower stalk')
   if opening:flower(end,opening,j*1.4+side*.3)
   else:bud(end,j)
  for j,(dx,dy,z,r,tilt) in enumerate([(-.24,.08,2.89,.19,.46),(.25,.12,2.98,.18,-.32),(.04,-.15,2.76,.145,.20)]):
   end=(x+side*dx,y+dy,z);stem(base,end,'central leaf stalk');leaf(end,r,tilt,j*1.7+side)
 from lotus_surfaces import refine_lotus_surfaces
 refine_lotus_surfaces(parts)
 from lotus_optics import configure_lotus_optics
 configure_lotus_optics(parts)
 return parts,[petalmat,leafmat,pollen]
