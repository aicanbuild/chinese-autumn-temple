"""Original editable sanctuary: mineral murals, recessed caisson and ritual furnishings.

Run with Blender, preserving the accepted Tang sculpture and chased incense vessel.
Coordinates are native Z-up; exported GLB uses Y-up.
"""
import bpy,bmesh,math,random,json,shutil,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';random.seed(719)
sys.path.insert(0,str(R/'source'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
parts=[];flames=[]
def mat(name,c,metal=0,rough=.5,texture=None):
 m=bpy.data.materials.new('Sanctuary | '+name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/texture),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
wood=mat('oxblood lacquer',(.16,.025,.018),.05,.32)
dark=mat('carved rosewood',(.043,.019,.011),.05,.40)
gold=mat('hand burnished gold',(.67,.41,.12),.82,.32)
bronze=mat('antique gilt bronze',(.25,.14,.048),.8,.44)
blue=mat('azurite painted wood',(.018,.080,.13),.05,.7)
green=mat('malachite painted wood',(.030,.16,.105),.05,.7)
ivory=mat('ivory lotus petals',(.80,.68,.44),.12,.46)
wax=mat('vermilion beeswax',(.46,.018,.012),0,.48)
wick=mat('charred cotton wick',(.017,.009,.005),0,.95)
celadon=mat('celadon porcelain',(.19,.37,.31),.08,.2)
orange=mat('citrus offering',(.87,.25,.028),0,.66)
red=mat('apple offering',(.31,.022,.010),0,.29)
leaf=mat('botanical stems',(.025,.10,.029),0,.77)
pink=mat('lotus rose petals',(.66,.22,.21),0,.59)
painting=mat('original mineral mural',(.75,.75,.75),0,.88,'sanctuary-mural.png')
materials=[wood,dark,gold,bronze,blue,green,ivory,wax,wick,celadon,orange,red,leaf,pink,painting]
def crafted_surface(m,texture,normal_strength,rough_factor,tint=None):
 # Existing CC0 rosewood and original bronze maps, in physical scale.
 nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
 for suffix,slot in [('-normal','Normal'),('-rough','Roughness')]+([('', 'Base Color')] if tint else []):
  ext='png' if texture=='incense-bronze' and suffix=='-normal' else 'jpg'
  t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/f'{texture}{suffix}.{ext}'),check_existing=True);t.extension='REPEAT'
  if suffix:t.image.colorspace_settings.name='Non-Color'
  if slot=='Normal':
   normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=normal_strength;links.new(t.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs[0],p.inputs[slot])
  elif slot=='Roughness':
   mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=rough_factor;links.new(t.outputs['Color'],mul.inputs[0]);links.new(mul.outputs[0],p.inputs[slot])
  else:
   mix=nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[7].default_value=(*tint,1);links.new(t.outputs['Color'],mix.inputs[6]);links.new(mix.outputs[2],p.inputs[slot])
 m['crafted_surface']=True
crafted_surface(wood,'pbr-rosewood',.13,.68,(.50,.25,.28))
crafted_surface(dark,'pbr-rosewood',.20,.78,(.24,.20,.15))
crafted_surface(gold,'incense-bronze',.34,.76)
crafted_surface(bronze,'incense-bronze',.50,1.0)
for m in [blue,green]:crafted_surface(m,'pbr-rosewood',.075,1.0)
from caisson_paint import apply_refined_paint
apply_refined_paint([blue,green])
for m in [wood,dark]:
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.24;p.inputs['Coat Roughness'].default_value=.28
from sanctuary_finishes import apply_sanctuary_finishes
apply_sanctuary_finishes()
def reg(o,name,m):
 o.name=name;o['sanctuary_interior']=True;o.data.materials.append(m);parts.append(o);return o
def mesh(name,vs,fs,m,smooth=False,uvs=None):
 g=bpy.data.meshes.new(name);g.from_pydata(vs,[],fs);g.update();o=bpy.data.objects.new(name,g);bpy.context.collection.objects.link(o);reg(o,name,m)
 for p in g.polygons:p.use_smooth=smooth
 if uvs:
  uv=g.uv_layers.new()
  for p in g.polygons:
   for i in p.loop_indices:uv.data[i].uv=uvs[g.loops[i].vertex_index]
 elif m.get('crafted_surface'):
  # Follow each member's long axis, selecting a non-collapsed second axis per face.
  mins=[min(v[i] for v in vs) for i in range(3)];sizes=[max(v[i] for v in vs)-mins[i] for i in range(3)];axis=max(range(3),key=lambda i:sizes[i]);uv=g.uv_layers.new();offset=(sum(name.encode('utf8'))%179)/179
  for p in g.polygons:
   second=max([i for i in range(3) if i!=axis],key=lambda i:(1-abs(p.normal[i]))*max(sizes[i],.001));first=axis
   if abs(p.normal[axis])>.95:first=min([i for i in range(3) if i!=second],key=lambda i:abs(p.normal[i]))
   for li in p.loop_indices:
    v=g.vertices[g.loops[li].vertex_index].co;uv.data[li].uv=((v[first]-mins[first])*.50+offset,(v[second]-mins[second])*.70+offset*.37)
 return o
def box(name,p,s,m=wood,bevel=.012):
 x,y,z=p;a,b,c=[v/2 for v in s]
 o=mesh(name,[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
 if bevel:
  mod=o.modifiers.new('Soft crafted edges','BEVEL');mod.width=min(bevel,min(s)*.24);mod.segments=2
 return o
def line(name,pts,r=.009,m=gold):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=2;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);return reg(o,name,m)
def ellipse(name,p,s,m=gold,n=48,rings=20):
 # Shared topology built directly, avoiding expensive scene-wide operator updates.
 vs=[];fs=[]
 for k in range(rings+1):
  ph=math.pi*k/rings
  for j in range(n):
   a=math.tau*j/n;vs.append((p[0]+s[0]*math.sin(ph)*math.cos(a),p[1]+s[1]*math.sin(ph)*math.sin(a),p[2]+s[2]*math.cos(ph)))
 for k in range(rings):
  for j in range(n):a=k*n+j;b=k*n+(j+1)%n;fs.append((a,b,b+n,a+n))
 return mesh(name,vs,fs,m,True)
def lathe(name,p,profile,m,n=64):
 vs=[(p[0]+r*math.cos(j*math.tau/n),p[1]+r*math.sin(j*math.tau/n),p[2]+z) for r,z in profile for j in range(n)];fs=[]
 for k in range(len(profile)-1):
  for j in range(n):a=k*n+j;b=k*n+(j+1)%n;fs.append((a,b,b+n,a+n))
 return mesh(name,vs,fs,m,True)
def ring(name,x,y,z,r,wire=.012,m=gold,vertical=False,n=96):
 return line(name,[(x+r*math.cos(a),y if vertical else y+r*math.sin(a),z+r*math.sin(a) if vertical else z) for a in [i*math.tau/n for i in range(n+1)]],wire,m)
def flower(name,x,y,z,r,m=gold,plane='wall',petals=8):
 for k in range(petals):
  a=k*math.tau/petals;vs=[];fs=[]
  for i in range(9):
   t=i/8;d=r*(.10+.9*t);w=r*.23*math.sin(math.pi*t)
   for sign in [-1,0,1]:
    u=d*math.cos(a)-sign*w*math.sin(a);v=d*math.sin(a)+sign*w*math.cos(a);relief=max(.016,r*.16)*math.sin(math.pi*t)*(1-abs(sign)*.7)
    vs.append((x+u,y-relief,z+v) if plane=='wall' else (x+u,y+v,z-relief))
  for i in range(8):
   for j in range(2):q=i*3+j;fs.append((q,q+1,q+4,q+3))
  mesh(name+' | petal',vs,fs,m,True)
 ellipse(name+' | heart',(x,y-.007,z) if plane=='wall' else (x,y,z-.01),(r*.13,.025,r*.13) if plane=='wall' else (r*.13,r*.13,.02),m,16,8)
def frame(x,y,z,w,h):
 for margin,thick,material in [(0,.085,dark),(.063,.023,gold),(.105,.033,wood),(.136,.009,gold)]:
  for sign in [-1,1]:
   box('Mural | carved moulding',(x,y-margin*.13,z+sign*(h/2-margin)),(w-2*margin,.065,thick),material)
   box('Mural | carved upright',(x+sign*(w/2-margin),y-margin*.13,z),(thick,.065,h-2*margin),material)
def mural(name,center,w,h,side=0):
 x,y,z=center;vs=[(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)]
 if side:vs=[(x,y+u,z+v) for u,_,v in vs]
 else:vs=[(x+u,y,z+v) for u,_,v in vs]
 mesh(name,vs,[(0,1,2,3)] if side>=0 else [(3,2,1,0)],painting,False,[(0,0),(1,0),(1,1),(0,1)])
# Wall dado and layered frames: enough depth to read as architecture, not floating art.
for x in [-3.43,3.43]:
 box('Mural | recessed mineral plaster',(x,10.19,2.83),(3.38,.08,2.27),dark)
 mural('Rear wall | celestial garden assembly',(x,10.139,2.83),3.10,1.99)
 frame(x,10.09,2.83,3.40,2.28)
for side in [-1,1]:
 x=side*5.30
 # Side wall painting faces inward; the scene material is double-sided as well.
 mural('Side wall | continuous lotus paradise',(x,7.87,2.78),4.34,2.18,side)
 for z in [1.61,3.95]:box('Side wall | gilded mural rail',(x-side*.025,7.87,z),(.06,4.55,.045),gold)
 for y in [5.60,10.12]:box('Side wall | lacquer upright',(x-side*.035,y,2.78),(.07,.11,2.39),dark)
 for y in [5.9,6.8,7.7,8.6,9.5]:
  box('Side wall | wainscot panel',(x-side*.03,y,1.36),(.075,.84,.42),wood)
  box('Side wall | brass inset',(x-side*.072,y,1.36),(.012,.66,.026),gold)
for x in [-4.8,-3.9,-3,-2.1,2.1,3,3.9,4.8]:
 box('Rear wall | paneled dado',(x,10.08,1.36),(.84,.10,.45),wood)
 flower('Dado | carved lotus',x,10.015,1.36,.14)
# Recessed square-to-octagonal caisson: real open well with four decreasing tiers.
cy=7.10
for x in [-4.45,-3.05,3.05,4.45]:
 for y in [5.95,7.22,8.49,9.76]:
  box('Ceiling | mineral blue coffer',(x,y,4.36),(1.33,1.20,.11),blue)
  for s in [-1,1]:
   box('Ceiling | lacquer coffer rim',(x+s*.67,y,4.25),(.10,1.3,.18),wood)
   box('Ceiling | lacquer coffer rim',(x,y+s*.615,4.25),(1.42,.085,.18),wood)
   box('Ceiling | gilded inset',(x+s*.56,y,4.283),(.012,1.05,.013),gold,0)
   box('Ceiling | gilded inset',(x,y+s*.51,4.283),(1.13,.012,.013),gold,0)
  flower('Ceiling | lotus rosette',x,y,4.294,.37,gold,'ceiling',8)
# Fill the front/rear rectangular borders, preserving the central skyward opening.
for y in [4.57,9.63]:box('Caisson | deep transverse beam',(0,y,4.30),(4.72,.23,.29),wood)
for x in [-2.35,2.35]:box('Caisson | deep longitudinal beam',(x,cy,4.30),(.22,5.18,.29),wood)
def polygon_ring(radius,z,n=8):return [(radius*math.cos(math.pi/8+i*math.tau/n),cy+radius*math.sin(math.pi/8+i*math.tau/n),z) for i in range(n)]
levels=[(2.48,4.36),(2.15,4.61),(1.79,4.89),(1.43,5.16),(1.08,5.43)]
for k in range(len(levels)-1):
 r,z=levels[k];r2,z2=levels[k+1];lo=polygon_ring(r,z);hi=polygon_ring(r2,z2)
 mesh('Caisson | inward stepped painted soffit',lo+hi,[(j,(j+1)%8,(j+1)%8+8,j+8) for j in range(8)],blue if k%2==0 else green)
 for radius,height in [(r,z),(r-.065,z+.05),(r2,z2)]:
  pts=polygon_ring(radius,height);line('Caisson | octagonal gilt moulding',pts+[pts[0]],.023)
# Each bracket cluster sits on an actual octagonal edge, not an unrelated circle.
# Tangential curved gong arms and radial cantilevers intersect their supporting dou.
def carved_gong(name,profile,center,depth,origin,tangent,inward,radial=False):
 n=len(profile);vs=[]
 for sign in [-1,1]:
  for along,h in profile:
   u=center[0]+(sign*depth/2 if radial else along)
   v=center[1]+(along if radial else sign*depth/2)
   vs.append((origin.x+tangent.x*u+inward.x*v,origin.y+tangent.y*u+inward.y*v,origin.z+center[2]+h))
 fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=mesh(name,vs,fs,wood)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 mod=o.modifiers.new('Carved rounded edges','BEVEL');mod.width=.004;mod.segments=3
 return o

gong_profile=[(-.22,.085),(-.20,.061),(-.16,.025),(-.10,.006),(0,0),(.10,.006),(.16,.025),(.20,.061),(.22,.085),(.215,.137),(.18,.12),(.13,.087),(.07,.072),(-.07,.072),(-.13,.087),(-.18,.12),(-.215,.137)]
radial_profile=[(-.015,.008),(.045,.013),(.10,.045),(.18,.10),(.25,.148),(.34,.21),(.355,.279),(.30,.271),(.23,.225),(.16,.18),(.08,.102),(.025,.080),(-.015,.080)]
cluster_count=0
for level,(r,z) in enumerate(levels[:-1]):
 corners=[Vector(p) for p in polygon_ring(r,z)]
 for edge in range(8):
  a=corners[edge];b=corners[(edge+1)%8];tangent=(b-a).normalized();inward=Vector((-tangent.y,tangent.x,0))
  for t in [.18,.5,.82]:
   origin=a.lerp(b,t);origin+=inward*.028;start=len(parts)
   def block(name,u,v,h,w,d,height,m=wood):
    center=origin+tangent*u+inward*v+Vector((0,0,h));o=box(name,center,(w,d,height),m,.004)
    for vertex in o.data.vertices:
     q=vertex.co-center;vertex.co=center+tangent*q.x+inward*q.y+Vector((0,0,q.z))
    return o
   block('Dougong | seated dou block',0,.045,-.015,.145,.15,.09)
   carved_gong('Dougong | lower cloud gong',gong_profile,(0,.045,.015),.10,origin,tangent,inward)
   for side in [-1,1]:block('Dougong | lower bearing block',side*.18,.045,.15,.095,.125,.063)
   carved_gong('Dougong | rising radial arm',radial_profile,(0,.045,.02),.095,origin,tangent,inward,True)
   carved_gong('Dougong | upper crossing gong',[(u*.83,h*.72) for u,h in gong_profile],(0,.285,.205),.105,origin,tangent,inward)
   for side in [-1,1]:block('Dougong | upper gilt bearing',side*.15,.285,.326,.077,.123,.050,gold)
   for side in [-1,1]:
    pts=[]
    for v,h in radial_profile[:7]:
     q=origin+tangent*(side*.049)+inward*(v+.045)+Vector((0,0,h+.036));pts.append(tuple(q))
    line('Dougong | chased radial arris',pts,.0034,gold)
   # A fine highlight follows the arm's lower carved silhouette.
   pts=[]
   for u,h in gong_profile[:9]:
    q=origin+tangent*u+inward*(-.008)+Vector((0,0,h+.020));pts.append(tuple(q))
   line('Dougong | gilt cloud outline',pts,.0035,gold)
   for o in parts[start:]:o['dougong_cluster']=cluster_count
   cluster_count+=1
# Four corner spandrels seal the space between the square frame and octagonal well.
for sx in [-1,1]:
 for sy in [-1,1]:
  vs=[(sx*2.35,cy+sy*2.35,4.36),(sx*.94,cy+sy*2.35,4.36),(sx*2.35,cy+sy*.94,4.36)]
  mesh('Caisson | corner spandrel',vs,[(0,1,2)],green)
  flower('Caisson | corner gilt lotus',sx*1.92,cy+sy*1.92,4.345,.21,gold,'ceiling',8)
lathe('Caisson | round lotus heaven',(0,cy,5.43),[(1.08,0),(.99,.16),(.78,.27),(0,.31)],blue,96)
for r,z in [(1.02,5.47),(.87,5.60),(.40,5.70)]:ring('Caisson | concentric gold band',0,cy,z,r,.02)
flower('Caisson | central gilded lotus',0,cy,5.68,.79,gold,'ceiling',16)
flower('Caisson | layered lotus inner whorl',0,cy,5.53,.46,gold,'ceiling',12)
flower('Caisson | lotus heart whorl',0,cy,5.44,.23,ivory,'ceiling',8)
for a in [i*math.tau/16 for i in range(16)]:flower('Caisson | small lotus crown',math.cos(a)*.92,cy+math.sin(a)*.92,5.46,.10,ivory,'ceiling',6)
for x in [-1.8,-.6,.6,1.8]:
 box('Ceiling | rear return coffer',(x,10.0,4.36),(1.18,.69,.1),blue)
 flower('Ceiling | rear return lotus',x,10.0,4.295,.22,gold,'ceiling',8)
# Upper wall frieze ties the mural bays to the ceiling.
for x in [i*.46 for i in range(-11,12)]:
 box('Frieze | blue enamel field',(x,10.12,4.09),(.45,.09,.23),blue)
 flower('Frieze | lotus gilding',x,10.04,4.09,.092,gold)
# Elegant almond aureole behind the accepted sculpture; fine ribs replace the gear outline.
vs=[(0,9.24,2.93)]+[(1.10*math.sin(a)*(.85+.15*abs(math.sin(a))),9.24,2.93+1.21*math.cos(a)) for a in [i*math.tau/96 for i in range(97)]]
mesh('Shrine | shaped mandorla backing',vs,[(0,i,i+1) for i in range(1,97)],dark)
for w,h,r in [(.97,1.12,.034),(1.05,1.18,.012),(.85,1.00,.009)]:
 pts=[]
 for j in range(161):
  a=j*math.tau/160;pts.append((w*math.sin(a)*(0.85+.15*abs(math.sin(a))),9.205,2.93+h*math.cos(a)))
 line('Aureole | almond gilded rim',pts,r,gold)
for j in range(44):
 a=j*math.tau/44
 pts=[((.86+t*.16)*math.sin(a),9.19,2.93+(1.01+t*.18)*math.cos(a)) for t in [0,.5,1]]
 line('Aureole | fine chased rays',pts,.006,bronze)
# Extended altar: central sculpture pedestal retained, flanking tables and carved apron.
for x in [-2.30,2.30]:
 box('Altar | side offering tabletop',(x,8.30,1.875),(1.10,1.18,.14),dark,.025)
 box('Altar | gilt tabletop lip',(x,8.30,1.812),(1.13,1.20,.021),gold,.003)
 for dx in [-.43,.43]:
  for dy in [-.42,.42]:box('Altar | square mortised leg',(x+dx,8.30+dy,1.44),(.10,.10,.74),wood)
 box('Altar | cloud apron',(x,7.75,1.68),(1.04,.09,.23),wood)
for x in [-1.16,0,1.16]:
 box('Altar | recessed front panel',(x,7.876,1.42),(1.06,.06,.57),dark)
 frame(x,7.821,1.42,1.09,.56)
 flower('Altar | carved eight petal lotus',x,7.778,1.42,.21,gold)
 for sign in [-1,1]:
  pts=[(x+sign*(.20+t*.24),7.775,1.42+.075*math.sin(t*math.tau)) for t in [i/20 for i in range(21)]];line('Altar | flowing vine relief',pts,.009,gold)
# Turned bronze candleholders, wax drips, recessed melted crowns and black wicks.
candle_profile=[(.18,0),(.20,.025),(.20,.045),(.155,.065),(.13,.10),(.095,.15),(.058,.20),(.04,.27),(.042,.61),(.075,.65),(.085,.68),(.06,.72),(.04,.76),(.065,.82),(.15,.845),(.17,.87),(.17,.885),(.09,.9)]
for side in [-1,1]:
 for index,(x,y,base,scale) in enumerate([(side*2.13,7.35,1.095,1.0),(side*2.65,8.18,1.952,.43)]):
  lathe('Candle stand | turned gilt bronze',(x,y,base),[(r*scale,z*scale) for r,z in candle_profile],bronze)
  for z,r in [(.04,.20),(.68,.084),(.88,.17)]:ring('Candle stand | polished bead rim',x,y,base+z*scale,r*scale,.007*scale)
  wz=base+.90*scale;wr=.075 if index==0 else .047;wh=.46 if index==0 else .27
  lathe('Candle | red wax and melted top',(x,y,wz),[(0,0),(wr,0),(wr,wh-.018),(wr*.83,wh),(wr*.62,wh-.01),(wr*.42,wh-.026),(0,wh-.03)],wax,64)
  for j in range(7):
   a=j*math.tau/7;length=random.uniform(.035,.14)*(1 if index==0 else .6);r=wr+.001
   pts=[(x+r*math.cos(a),y+r*math.sin(a),wz+wh-.02-t*length) for t in [k/12 for k in range(13)]];line('Candle | accumulated wax drip',pts,.0045,wax)
  tip=wz+wh-.005;line('Candle | carbon wick',[(x,y,tip-.022),(x+.004,y,tip+.012)],.003,wick)
  flames.append([x,tip+.020,-y])
# Seven porcelain water cups across the front of the accepted Buddha's pedestal.
for i in range(7):
 x=(i-3)*.19;y=7.99
 lathe('Offering | celadon water cup',(x,y,1.895),[(.028,0),(.029,.018),(.052,.025),(.057,.066),(.052,.073),(.047,.067),(.042,.026),(.008,.022)],celadon,40)
 ring('Offering | gilt cup rim',x,y,1.965,.054,.0025)
 lathe('Offering | still water',(x,y,1.951),[(0,0),(.047,0)],celadon,40)
for side in [-1,1]:
 x=side*1.20;y=8.10
 lathe('Offering | bronze fruit tazza',(x,y,1.895),[(.13,0),(.14,.025),(.07,.07),(.04,.14),(.12,.17),(.23,.20),(.25,.225),(.245,.245),(.21,.235),(.05,.21)],gold,64)
 # Paired celadon vases with individually curved lotus leaves and petals.
 x=side*2.18;y=8.48
 lathe('Offering | celadon lotus vase',(x,y,1.952),[(.12,0),(.13,.045),(.17,.12),(.18,.25),(.145,.38),(.072,.48),(.070,.60),(.09,.625),(.085,.644),(.062,.635),(.056,.59)],celadon,64)
 for z,r in [(2.00,.133),(2.576,.088)]:ring('Vase | gilt rim',x,y,z,r,.005)
import sys
sys.path.insert(0,str(R/'source'))
from altar_fruit import build_altar_fruit
fruit_parts,fruit_materials,fruit_report=build_altar_fruit();parts.extend(fruit_parts);materials.extend(fruit_materials)
# Detailed botanical bouquets share three additional finishes.
import sys
sys.path.insert(0,str(R/'source'))
from lotus_bouquet import build_lotus_bouquets
lotus_parts,lotus_materials=build_lotus_bouquets();parts.extend(lotus_parts);materials.extend(lotus_materials)
# Save the editable asset, then batch export by material for a modest draw-call budget.
import sys
sys.path.insert(0,str(R/'source'))
from candlesticks import is_stand,build_candlesticks
for old in parts[:]:
 if is_stand(old):parts.remove(old);bpy.data.objects.remove(old,do_unlink=True)
candlestick_parts,candlestick_materials,candlestick_details=build_candlesticks();parts.extend(candlestick_parts);materials.extend(candlestick_materials)
from altar_carving import is_altar_carving,build_altar_carving
for old in parts[:]:
 if is_altar_carving(old):parts.remove(old);bpy.data.objects.remove(old,do_unlink=True)
altar_parts,altar_details=build_altar_carving();parts.extend(altar_parts)
from candle_finish import finish_candles
finish_candles(parts)
from wax_forms import replace_wax_forms
flames,wax_details=replace_wax_forms(parts,flames)
from mural_finishes import apply_mural_finishes
materials.append(apply_mural_finishes())
from offering_cups import is_offering_cup,build_offering_cups
for old in parts[:]:
 if is_offering_cup(old):parts.remove(old);bpy.data.objects.remove(old,do_unlink=True)
cup_parts,cup_materials,cup_details=build_offering_cups();parts.extend(cup_parts);materials.extend(cup_materials)
from altar_tabletop import build_altar_tabletop
top_parts,top_details=build_altar_tabletop();parts.extend(top_parts)
from ceiling_carving import is_ceiling_carving,build_ceiling_carving
for old in parts[:]:
 if is_ceiling_carving(old):parts.remove(old);bpy.data.objects.remove(old,do_unlink=True)
ceiling_parts,ceiling_details=build_ceiling_carving();parts.extend(ceiling_parts)
prototype=R/'source/庄严内殿.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(prototype));component_count=len(parts)
print('SANCTUARY editable parts',component_count,flush=True)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
for m in materials:
 bpy.ops.object.select_all(action='DESELECT');group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==m]
 if not group:continue
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=m.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'sanctuary.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Only replace the previous coffer grid, back panels, aureole and apron, never the statue.
from mural_cleanup import MURAL_INTRUSION_REGIONS
regions=[[-5.24,5.24,5.16,10.24,4.07,4.27],[-5.65,5.65,10.16,10.34,1.46,3.97],[-1.27,1.27,8.92,9.07,1.76,4.30],[-1.62,1.62,7.82,7.99,1.13,1.76]]+MURAL_INTRUSION_REGIONS
regions.append(top_details['removeRegionNative'])
temple=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-sanctuary.blend'
if not backup.exists():shutil.copy2(temple,backup)
bpy.ops.wm.open_mainfile(filepath=str(temple));preserved_sculpture=sum(bool(o.get('altar_sculpture')) for o in bpy.data.objects);preserved_incense=sum(bool(o.get('incense_vessel')) for o in bpy.data.objects)
for o in list(bpy.data.objects):
 if o.get('sanctuary_interior'):bpy.data.objects.remove(o,do_unlink=True)
def inside(p,r):return r[0]<p.x<r[1] and r[2]<p.y<r[3] and r[4]<p.z<r[5]
removed=0
for o in bpy.data.objects:
 if o.type!='MESH' or not any(m and ('gilded' in m.name.lower() or 'cedar' in m.name.lower()) for m in o.data.materials):continue
 bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if any(all(inside(o.matrix_world@v.co,r) for v in f.verts) for r in regions)];removed+=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
assert preserved_sculpture==sum(bool(o.get('altar_sculpture')) for o in bpy.data.objects)
assert preserved_incense==sum(bool(o.get('incense_vessel')) for o in bpy.data.objects)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple))
meta={'components':component_count,'flames':flames,'removeRegionsNative':regions,'preservedSculpture':preserved_sculpture,'preservedIncense':preserved_incense,'removedFaces':removed,'caissonTop':5.74,'muralPanels':4,'dougongClusters':cluster_count,'surfaceRevision':2,'fruitRevision':1,'fruitDetails':fruit_report,'lotusRevision':1,'lotusBotany':{'openFlowers':6,'buds':4,'peltateLeaves':6,'petals':120,'stamens':288}}
meta['finishRevision']=1
meta['muralRevision']=1;meta['muralArtworks']=2;meta['removedMuralFasteners']=2
meta['ceilingCarving']=ceiling_details
meta['candlesticks']=candlestick_details
meta['continuousWax']=wax_details
meta['altarRelief']=altar_details
meta['offeringCups']=cup_details
meta['altarTabletop']=top_details
(A/'sanctuary.json').write_text(json.dumps(meta,indent=2));print('SANCTUARY',json.dumps(meta),flush=True)
