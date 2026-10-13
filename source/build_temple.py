import bpy, bmesh, math, random, json, sys
from mathutils import Vector
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'source'))
A=R/'dist/assets'
random.seed(20261007)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
M={}; G={}; anchors=[]
def material(name,color,tex=None,metal=0,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if tex:
  if tex in ['wood','stone'] and (A/f'pbr-{tex}.jpg').exists():tex='pbr-'+tex
  for suffix,slot in [('', 'Base Color'),('-rough','Roughness'),('-normal','Normal')]:
   node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(A/f'{tex}{suffix}.jpg'),check_existing=True)
   if suffix: node.image.colorspace_settings.name='Non-Color'
   if slot=='Normal':
    n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.5;m.node_tree.links.new(node.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs[0],p.inputs[slot])
   else:m.node_tree.links.new(node.outputs['Color'],p.inputs[slot])
 M[name]=m;return name
wood=material('Polished ebony cedar',(.12,.065,.035),'lacquer',rough=.3)
red=material('Restored burgundy lacquer',(.19,.025,.015),rough=.28)
stone=material('Honed silver granite',(.65,.63,.57),'cut-granite')
rockstone=material('Natural mossy bank stones',(.4,.42,.38),'pbr-stone')
tile=material('Charcoal glazed ceramic',(.10,.13,.12),'glazed-tile')
moss=material('Soft forest moss',(.18,.25,.06),'moss')
sand=material('Riverbed sediment',(.33,.38,.26),'sand')
plaster=material('Ivory lime plaster',(.55,.51,.40),rough=.85)
gold=material('Satin gilded bronze',(.83,.54,.16),metal=.82,rough=.26)
carving=material('Carved pale limestone',(.38,.39,.33),rough=.72)
pinegreen=material('Deep green pine needles',(.035,.105,.055),rough=.81)
bamboo=material('Living bamboo jade',(.15,.24,.075),rough=.45)
shrubgreen=material('Clipped garden foliage',(.13,.23,.07),rough=.8)
flower=material('Ivory camellia petals',(.9,.83,.62),rough=.6)
dark=material('Deep dark wood',(.037,.025,.015),rough=.86)
paper=material('Warm paper lantern',(.94,.66,.29),rough=.7)
screen=material('Unbleached silk shoji',(.47,.39,.24),rough=.83)
bark=material('Ridged maple bark',(.14,.08,.035),'pbr-bark')
earth=material('Manicured moss garden',(.2,.22,.1),'moss')
def face(key,vs,uv=None):
 if key not in G:G[key]=[[],[],[]]
 v,f,u=G[key];i=len(v);v.extend(vs);f.append(tuple(range(i,i+len(vs))))
 u.extend(uv or [(0,0),(1,0),(1,1),(0,1)][:len(vs)])
def box(key,c,s):
 x,y,z=c;a,b,d=[v/2 for v in s]
 pts=[(x-a,y-b,z-d),(x+a,y-b,z-d),(x+a,y+b,z-d),(x-a,y+b,z-d),(x-a,y-b,z+d),(x+a,y-b,z+d),(x+a,y+b,z+d),(x-a,y+b,z+d)]
 for inds,wh in [([0,3,2,1],(s[0],s[1])),([4,5,6,7],(s[0],s[1])),([0,1,5,4],(s[0],s[2])),([1,2,6,5],(s[1],s[2])),([2,3,7,6],(s[0],s[2])),([3,0,4,7],(s[1],s[2]))]:
  uv=[(0,0),(wh[0],0),wh,(0,wh[1])]
  if key==wood:
   vv=(random.randrange(12)+.20)/13;uu=random.random();ww=.037
   uv=[(uu,vv),(uu+wh[0]*.3,vv),(uu+wh[0]*.3,vv+ww),(uu,vv+ww)] if wh[0]>=wh[1] else [(uu,vv),(uu,vv+ww),(uu+wh[1]*.3,vv+ww),(uu+wh[1]*.3,vv)]
  face(key,[pts[i] for i in inds],uv)
def tube(key,a,b,r1,r2=None,n=10):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();q=d.to_track_quat('Z','Y');r2=r1 if r2==None else r2
 rings=[]
 for p,r in [(a,r1),(b,r2)]:rings.append([p+q@Vector((math.cos(i*math.tau/n)*r,math.sin(i*math.tau/n)*r,0)) for i in range(n)])
 for i in range(n):
  j=(i+1)%n;uv=[(i/n*2,0),(j/n*2,0),(j/n*2,(b-a).length),(i/n*2,(b-a).length)]
  if key==wood:uv=[(0,.10+i/n*.035),(0,.10+j/n*.035),((b-a).length*.3,.10+j/n*.035),((b-a).length*.3,.10+i/n*.035)]
  face(key,[rings[0][i],rings[0][j],rings[1][j],rings[1][i]],uv)
 for ring in rings:
  for i in range(1,n-1):face(key,[ring[0],ring[i],ring[i+1]],[(0,0),(1,0),(1,1)])
def sphere(key,c,sc,n=16,lat=10):
 for j in range(lat):
  for i in range(n):
   pts=[];uv=[]
   for di,dj in [(0,0),(1,0),(1,1),(0,1)]:
    th=(i+di)*math.tau/n;ph=(j+dj)*math.pi/lat
    pts.append((c[0]+sc[0]*math.sin(ph)*math.cos(th),c[1]+sc[1]*math.sin(ph)*math.sin(th),c[2]+sc[2]*math.cos(ph)));uv.append(((i+di)/n,(j+dj)/lat))
   face(key,pts,uv)
def rock(c,sc):
 # Each stone has its own asymmetric rounded profile and a moss cap.
 n=15;lat=9;seed=random.random()*12
 for j in range(lat):
  for i in range(n):
   vs=[]
   for di,dj in [(0,0),(1,0),(1,1),(0,1)]:
    th=(i+di)*math.tau/n;ph=(j+dj)*math.pi/lat
    rr=1+.09*math.sin(th*3+ph*5+seed)+.06*math.cos(th*5-ph*3)
    vs.append((c[0]+sc[0]*math.sin(ph)*math.cos(th)*rr,c[1]+sc[1]*math.sin(ph)*math.sin(th)*rr,c[2]+sc[2]*math.cos(ph)*rr))
   face(moss if j==0 and random.random()<.85 else rockstone,vs)
def roof(cx,cy,w,d,z,rise):
 def height(x,t):return z+rise*max(0,1-t)**1.75+.27*t**7+.26*(abs(x)/w)**9*t**5
 nx=round(w*2/.25);ny=round(d/.30)
 for side in [-1,1]:
  for ix in range(nx):
   x=-w+ix*(2*w/nx)
   for iy in range(ny):
    t0=iy/ny;t1=(iy+1.13)/ny;rad=w/nx
    # Semi-cylindrical overlapping ceramic tiles, not a flat roof texture.
    for j in range(5):
     pts=[];uv=[]
     for q,t in [(j,t0),(j+1,t0),(j+1,t1),(j,t1)]:
      off=q/5*rad*2;xx=x+off
      zz=height(xx,t)+math.sin(q/5*math.pi)*.055
      pts.append((cx+xx,cy+side*t*d,zz));uv.append((q/5,t*2))
     face(tile,pts,uv)
  # Continuous wood underlay and dark fascia at both eaves.
  for i in range(24):
   t=i/24;t2=(i+1)/24
   face(wood,[(cx-w,cy+side*t*d,height(-w,t)-.11),(cx+w,cy+side*t*d,height(w,t)-.11),(cx+w,cy+side*t2*d,height(w,t2)-.11),(cx-w,cy+side*t2*d,height(-w,t2)-.11)])
  for i in range(nx):
   x=-w+i*2*w/nx;x2=x+2*w/nx
   tube(gold,(cx+x,cy+side*d,height(x,1)),(cx+x2,cy+side*d,height(x2,1)),.045,n=10)
   sphere(gold,(cx+x+.08,cy+side*(d+.035),height(x,1)),(.052,.035,.052),n=10,lat=6)
  for x in [-w,w]:
   for i in range(22):
    t=i/22;t2=(i+1)/22;tube(gold,(cx+x,cy+side*t*d,height(x,t)+.05),(cx+x,cy+side*t2*d,height(x,t2)+.05),.052,n=10)
 # Thick ridge, stacked caps and uplifted finials.
 tube(gold,(cx-w-.12,cy,z+rise+.08),(cx+w+.12,cy,z+rise+.08),.095,n=16)
 for x in [-w,w]:
  sign=1 if x>0 else -1
  pts=[(cx+x+sign*i*.13,cy,z+rise+.08+.03*i*i) for i in range(7)]
  for i in range(6):tube(gold,pts[i],pts[i+1],.095-i*.011,n=12)
  sphere(gold,pts[-1],(.07,.07,.08),n=10,lat=6)
 # Curved gable closed with timber louvers.
 for x in [-w+.2,w-.2]:
  for j in range(-20,21):
   t=abs(j/20);yy=cy+j/20*d*.95;h=height(x,t)-z
   box(wood,(cx+x,yy,z+h/2-.08),(.12,.11,h+.08))
def bracket(x,y,z):
 for i in range(4):
  box(wood,(x,y,z+i*.105),(.24+i*.17,.28+i*.13,.105))
 for dx in [-.38,.38]:
  tube(wood,(x,y,z-.08),(x+dx,y,z+.27),.068,n=6)
def lantern(x,y,z,scale=1):
 def B(k,c,s):box(k,(x+c[0]*scale,y+c[1]*scale,z+c[2]*scale),tuple(v*scale for v in s))
 B(stone,(0,0,.1),(.72,.72,.2));B(stone,(0,0,.27),(.5,.5,.16))
 tube(stone,(x,y,z+.3*scale),(x,y,z+1.18*scale),.14*scale,.1*scale,n=8)
 B(stone,(0,0,1.15),(.53,.53,.14));B(paper,(0,0,1.46),(.31,.31,.45))
 for a in [-1,1]:
  for b in [-1,1]: B(stone,(a*.21,b*.21,1.47),(.065,.065,.56))
 B(stone,(0,0,1.79),(.74,.74,.13)); B(stone,(0,0,1.93),(.53,.53,.12))
 sphere(stone,(x,y,z+2.12*scale),(.09*scale,.09*scale,.11*scale),n=12,lat=6)
# Garden base: a topologically open oval pool, with landscaped land around it.
CY=-5.8;RX=11.5;RY=6.9
for i in range(128):
 a=i*math.tau/128;b=(i+1)*math.tau/128
 def P(t,r,z):return (math.cos(t)*RX*r,CY+math.sin(t)*RY*r,z)
 face(earth,[P(a,1,.18),P(b,1,.18),P(b,3,-.1),P(a,3,-.1)],[(P(a,1,.18)[0]*.23,P(a,1,.18)[1]*.23),(P(b,1,.18)[0]*.23,P(b,1,.18)[1]*.23),(P(b,3,-.1)[0]*.23,P(b,3,-.1)[1]*.23),(P(a,3,-.1)[0]*.23,P(a,3,-.1)[1]*.23)])
 face(stone,[P(a,1,.18),P(b,1,.18),P(b,.97,-1),P(a,.97,-1)])
face(sand,[(-15,-15,-.9),(15,-15,-.9),(15,3,-.9),(-15,3,-.9)],[(0,0),(7,0),(7,7),(0,7)])
for i in range(105):
 t=math.tau*i/105;x=math.cos(t)*RX;y=CY+math.sin(t)*RY
 if abs(x)<1.65 and y<-9:continue
 rock((x,y,.13),(random.uniform(.3,.66),random.uniform(.32,.7),random.uniform(.26,.64)))
for i in range(185):
 x=random.uniform(-11,11);y=random.uniform(-12,1)
 if (x/RX)**2+((y-CY)/RY)**2<.88:rock((x,y,-.78),(random.uniform(.06,.25),random.uniform(.08,.25),random.uniform(.04,.13)))
# Individual paving stones; cut joints, edge variation, broad entrance court.
for ix in range(-7,8):
 for iy in range(5):
  x=ix*.88;y=1+iy*.83
  box(stone,(x,y,.4),(.856,.81,.19+random.uniform(-.013,.013)))
for side in [-1,1]:
 for j in range(27):
  y=-10+j*.75;x=side*(13.0+.65*math.sin(j*.17))
  box(stone,(x,y,.27),(1.45,.725,.19))
  if j%6==1:lantern(x+side*1.05,y,.16,.8)
# Main raised temple platform and front stairs.
box(stone,(0,7.1,.46),(12.4,7.7,.7));box(stone,(0,7.1,.85),(12.75,8,.18))
for j in range(4):box(stone,(0,2.6+j*.34,.17+j*.16),(5.3,.72,.2+j*.1))
for i in range(43):box(wood,(-5.99+i*.285,7.1,.99),(.275,7.25,.16))
for x in [-5.6,-2.8,2.8,5.6]:
 for y in [3.85,10.35]:
  box(stone,(x,y,1.13),(.52,.52,.3));tube(red,(x,y,1.23),(x,y,4.55),.16,.13,n=16)
  bracket(x,y,4.2)
for y in [3.85,10.35]:
 box(wood,(0,y,4.47),(12,.24,.32));box(red,(0,y,4.05),(11.5,.18,.12))
for x in [-5.6,5.6]:box(wood,(x,7.1,4.47),(.27,7.1,.32))
for x in [-5.4,5.4]:
 box(plaster,(x,7.8,2.48),(.15,4.8,2.84))
box(plaster,(0,10.4,2.49),(10.8,.18,2.8))
# Front sliding wooden lattice panels, leaving a central entry open.
for x in [-4.35,-2.88,2.88,4.35]:
 box(dark,(x,5.1,2.53),(1.32,.13,2.87))
 box(screen,(x,5.02,3.06),(1.18,.018,1.51))
 for dx in [-.66,.66]:box(wood,(x+dx,4.93,2.54),(.07,.14,2.9))
 for iz in range(10):box(wood,(x,4.91,2.3+iz*.163),(1.31,.09,.035))
 for ix in range(8):box(wood,(x-.58+ix*.166,4.9,3.02),(.032,.10,1.57))
 for z in [1.16,2.18,3.91]:box(wood,(x,4.88,z),(1.35,.15,.085))
 for dx in [-.45,-.15,.15,.45]:box(wood,(x+dx,4.97,1.67),(.018,.08,.88))
roof(0,7.1,6.75,4.4,4.62,2.1)
# Rafter ends below the eaves.
for i in range(49):
 x=-6.3+i*.2625
 for side in [-1,1]:tube(wood,(x,7.1+side*2.3,4.58),(x,7.1+side*4.3,4.51),.055,n=8)
# Temple plaque and warm interior altar.
box(dark,(0,3.68,4.04),(2.1,.16,.53));box(gold,(0,3.58,4.30),(2.13,.05,.034));box(gold,(0,3.58,3.78),(2.13,.05,.034))
box(wood,(0,8.65,1.39),(3.3,1.45,.77));box(gold,(0,8.65,1.84),(3.5,1.6,.11))
# The independent detailed altar sculpture is built by build_sculpture.py.
# Bronze incense vessel with handles and individual sticks.
tube(gold,(0,6.6,1.01),(0,6.6,1.5),.25,.38,n=32)
for side in [-1,1]:tube(gold,(side*.27,6.6,1.3),(side*.5,6.6,1.62),.045,n=12)
for i in range(7):
 x=random.uniform(-.19,.19);y=6.6+random.uniform(-.17,.17)
 tube(wood,(x,y,1.49),(x+.02,y,2.0),.009,n=5)
# Arched timber bridge over the reflecting koi pond.
box(stone,(0,-12.85,.28),(2.95,1.3,.50))
def bz(y):return .52+.61*math.sin((y+12.4)/13.3*math.pi)
for j in range(71):
 y=-12.4+j*.188
 box(wood,(0,y,bz(y)),(2.55,.178,.14))
for side in [-1,1]:
 for j in range(15):
  y=-12.3+j*.94;z=bz(y)
  box(wood,(side*1.28,y,z+.46),(.13,.13,1.02));sphere(gold,(side*1.28,y,z+1.015),(.075,.075,.04),n=16,lat=8)
  if j<14:
   y2=y+.94
   for h in [.35,.86]:tube(wood,(side*1.28,y,z+h),(side*1.28,y2,bz(y2)+h),.048,n=8)
 for j in range(5):tube(wood,(side*1.04,-11.8+j*2.6,-.85),(side*1.04,-11.8+j*2.6,bz(-11.8+j*2.6)-.13),.105,n=10)
# Bell pavilion, with a visibly modeled hanging temple bell.
cx=-9;cy=4.1
box(stone,(cx,cy,.55),(4,4,.6))
for x in [-1.45,1.45]:
 for y in [-1.45,1.45]:tube(wood,(cx+x,cy+y,.85),(cx+x,cy+y,3.67),.14,n=14);bracket(cx+x,cy+y,3.5)
roof(cx,cy,2.2,2.2,3.8,1.2)
tube(wood,(cx-1.6,cy,3.45),(cx+1.6,cy,3.45),.13,n=10)
tube(gold,(cx,cy,3.47),(cx,cy,2.98),.045,n=10)
for j in range(14):
 z=1.64+j*.1;r=.61-.21*(j/13)**.5
 tube(gold,(cx,cy,z),(cx,cy,z+.1),r,r-.016,n=32)
for z in [1.66,1.76,2.15,2.75]:tube(gold,(cx,cy,z),(cx,cy,z+.035),.62 if z<1.8 else .46,n=32)
for j in range(4):
 for i in range(12):
  t=i*math.tau/12;sphere(gold,(cx+.48*math.cos(t),cy+.48*math.sin(t),2.25+j*.13),(.035,.035,.035),n=6,lat=4)
tube(wood,(cx+.7,cy-1,2.35),(cx+.7,cy+.6,2.35),.115,n=16)
for y in [-.8,.45]:tube(dark,(cx+.7,cy+y,2.35),(cx+.7,cy+y,3.6),.015,n=6)
# Right-side covered resting platform.
cx=9;cy=4.3
box(stone,(cx,cy,.51),(3.9,4.1,.55))
for i in range(16):box(wood,(cx-1.77+i*.236,cy,.86),(.225,3.7,.13))
for x in [-1.5,1.5]:
 for y in [-1.5,1.5]:tube(wood,(cx+x,cy+y,.86),(cx+x,cy+y,3.2),.11,n=12);bracket(cx+x,cy+y,3.05)
roof(cx,cy,2.2,2.2,3.4,.95)
for x in [-1.2,1.2]:
 box(wood,(cx+x,cy,1.3),(.5,2.6,.16))
 for y in [-1,1]:box(wood,(cx+x,cy+y,1.08),(.16,.19,.48))
for x,y in [(-4,1.0),(4,1.0),(-3,-12.8),(3,-12.8),(-7.5,9),(7.5,9)]:lantern(x,y,.18,1)
# Boundary wall gives the garden an enclosed, quiet horizon.
for x in range(-16,17):
 box(plaster,(x,13.8,1.12),(.98,.35,2.35));box(stone,(x,13.8,.18),(.99,.46,.46))
 for k in range(4):box(tile,(x-.38+k*.25,13.8,2.36),(.255,.66,.14))
# Branching trees. Canopy anchors are also used by GPU-instanced leaves in Three.js.
trees=[(-12,-3,6.8,0),(-10.2,-11,7,1),(10.6,-10,6.2,0),(12,-1,7.7,1),(-13,5,8.1,0),(13,9,8.6,1),(-7,12,8.5,1),(6,13,8,0),(-15,-8,7.8,2),(16,-7,8.8,2),(-15,13,10,2),(0,16,10,2),(17,15,10,2),(-19,3,10,2),(18,3,9,2)]
def branch(a,vec,length,r,depth,kind):
 direction=Vector(vec).normalized();b=Vector(a)+direction*length
 mid=Vector(a).lerp(b,.5)+Vector((random.uniform(-.09,.09),random.uniform(-.09,.09),0))
 tube(bark,a,mid,r,r*.8,n=9);tube(bark,mid,b,r*.8,r*.61,n=9)
 if depth in [1,2]:
  anchors.append([round(b.x,3),round(b.y,3),round(b.z,3),kind,random.uniform(.65,1.0)])
 if depth<=0:
  anchors.append([round(b.x,3),round(b.y,3),round(b.z,3),kind,random.uniform(.70,1.08)]);return
 for j in range(3):
  ang=random.random()*math.tau
  dd=Vector((math.cos(ang)*.68,math.sin(ang)*.68,random.uniform(-.1,.86)))+direction*.4
  branch(b,dd,length*random.uniform(.62,.75),r*.53,depth-1,kind)
for x,y,h,kind in trees:
 branch((x,y,.15),(random.uniform(-.2,.2),random.uniform(-.2,.2),1),h*.4,.30 if kind<2 else .4,3,kind)
 for j in range(6):
  t=j*math.tau/6;tube(bark,(x+math.cos(t)*.72,y+math.sin(t)*.72,.17),(x,y,.94),.1,.2,n=8)
 for j in range(7):rock((x+random.uniform(-1,1),y+random.uniform(-1,1),.12),(random.uniform(.1,.35),random.uniform(.1,.35),random.uniform(.05,.13)))
# Ferns and grass: narrow individually curved blades around rocks and the pool.
for j in range(250):
 t=random.random()*math.tau;r=random.uniform(1.04,1.3);x=RX*math.cos(t)*r;y=CY+RY*math.sin(t)*r
 if abs(x)<2 or y>1:continue
 h=random.uniform(.16,.51);a=random.random()*math.tau
 for i in range(3):
  ang=a+i*2.1;w=.025
  face(moss,[(x-w,y,.18),(x+w,y,.18),(x+math.cos(ang)*h*.35,y+math.sin(ang)*h*.35,.18+h),(x+math.cos(ang)*h*.54,y+math.sin(ang)*h*.54,.18+h*.73)])
# Detailed restoration is actual editable mesh geometry, shared with the web export.
exec(compile((R/'source/restoration.py').read_text(),str(R/'source/restoration.py'),'exec'))
# Compose mesh batches by material. UVs carry actual timber / stone grain.
objs=[]
for name,(vs,fs,uvs) in G.items():
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(M[name]);objs.append(o)
 uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  for li in poly.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
 # Small surface bevels keep edges from looking machine-perfect.
 if name in [stone,wood,red,plaster]:
  mod=o.modifiers.new('Hand softened edges','BEVEL');mod.width=.013;mod.segments=2
  mod.limit_method='ANGLE'
  bpy.context.view_layer.objects.active=o
  bpy.ops.object.modifier_apply(modifier=mod.name)
 if name in [stone,rockstone,bark,gold,carving]:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.to_mesh(o.data);bm.free();o.data.update()
 for p in o.data.polygons:p.use_smooth=name in [stone,rockstone,bark,gold,carving]
 if name==tile:
  from roof_tiles import refine_roof_mesh
  refine_roof_mesh(o)
 if name==sand:
  from pond_basin import basin_mesh
  o.data=basin_mesh();o.data.materials.append(M[sand]);o['pond_basin_revision']=1
 if name==stone:
  mod=o.modifiers.new('Weighted stone normals','WEIGHTED_NORMAL');mod.keep_sharp=True
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
print('Architecture meshes',len(objs),'polygons',sum(len(o.data.polygons) for o in objs),flush=True)
# Export compact real architecture to the web. Foliage is instanced by the runtime.
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'temple.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_image_format='JPEG',export_image_quality=90)
with open(A/'garden.json','w') as f:json.dump({'anchors':anchors,'trees':trees,'pool':{'cx':0,'cy':CY,'rx':RX,'ry':RY}},f,separators=(',',':'))
# Native Blender scene also contains the complete leafy crowns, organized by species.
for kind,(name,col) in enumerate([('Autumn maple foliage',(.63,.15,.035)),('Golden ginkgo foliage',(.85,.51,.035)),('Forest green foliage',(.19,.26,.055))]):
 mat=material(name,col,rough=.77);verts=[];faces=[]
 for x,y,z,k,r in anchors:
  if k!=kind:continue
  for j in range(100):
   p=Vector((x+random.gauss(0,r*.65),y+random.gauss(0,r*.65),z+random.gauss(0,r*.37)))
   size=random.uniform(.07,.145);a=random.random()*math.tau;b=random.uniform(-.6,.6)
   u=Vector((math.cos(a),math.sin(a),b))*size;v=Vector((-math.sin(a),math.cos(a),.3))*size*.62;i=len(verts)
   verts.extend([p-u,p+v,p+u,p-v,p+Vector((0,0,.02))])
   faces.extend([(i,i+1,i+4),(i+1,i+2,i+4),(i+2,i+3,i+4),(i+3,i,i+4)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(M[mat])
# A native editable water plane, camera and lights for the source document.
water=material('Water — replaced by real-time reflection / refraction',(.11,.30,.22),rough=.12)
M[water].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.7
verts=[(math.cos(i*math.tau/128)*RX,CY+math.sin(i*math.tau/128)*RY,-.02) for i in range(128)]
me=bpy.data.meshes.new('Pond surface');me.from_pydata(verts,[],[list(range(128))]);me.update();o=bpy.data.objects.new('Reflecting pond',me);bpy.context.collection.objects.link(o);me.materials.append(M[water])
bpy.ops.object.light_add(type='SUN',location=(6,-9,15));bpy.context.object.rotation_euler=(.5,-.45,-.4);bpy.context.object.data.energy=2.4;bpy.context.object.data.angle=.09
bpy.ops.object.camera_add(location=(20,-26,17));cam=bpy.context.object;direction=Vector((0,1,2))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.lens=41;bpy.context.scene.camera=cam
bpy.context.scene.world.color=(.3,.37,.42)
# Imported CC0 fern clumps are retained as editable linked geometry in the source.
fernfile=A/'fern/fern.gltf'
if fernfile.exists():
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.import_scene.gltf(filepath=str(fernfile))
 fernparts=[o for o in bpy.context.selected_objects if o.type=='MESH']
 for k,part in enumerate(fernparts):
  width=max(part.dimensions.x,part.dimensions.y)
  for i in range(24):
   a=(i+k*.21)/24*math.tau;r=random.uniform(1.04,1.16);x=math.cos(a)*RX*r;y=CY+math.sin(a)*RY*r
   if abs(x)<2.1:x+=2.3 if x>=0 else -2.3
   o=part.copy();o.data=part.data;bpy.context.collection.objects.link(o);o.location=(x,y,.21);o.rotation_euler.z=random.random()*math.tau;o.scale*=random.uniform(.65,1.15)/width
  bpy.data.objects.remove(part,do_unlink=True)

bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=64
bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=1000;bpy.context.scene.render.resolution_percentage=100
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
print('COMPLETE',len(anchors),'canopy anchors',flush=True)
