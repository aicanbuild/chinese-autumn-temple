"""Original gilt-copper/blue-enamel candle stands inspired by Chinese altar wares.
Shape reference: The Met 29.110.68, https://www.metmuseum.org/art/collection/search/40725.
Artistic adaptation, not a historical replica. Existing candles and flames stay fixed.
"""
import bpy,math
from mathutils import Vector,Quaternion

def is_stand(o):return bool(o.get('crafted_candlestick')) or o.name.startswith('Candle stand |')

def build_candlesticks():
 used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 gold=next(m for m in used if m.name.startswith('Sanctuary | hand burnished gold'));bronze=next(m for m in used if m.name.startswith('Sanctuary | antique gilt bronze'))
 enamel=bpy.data.materials.get('Sanctuary | deep blue cloisonne enamel') or bpy.data.materials.new('Sanctuary | deep blue cloisonne enamel');enamel.use_nodes=True;enamel.node_tree.nodes.clear();p=enamel.node_tree.nodes.new('ShaderNodeBsdfPrincipled');out=enamel.node_tree.nodes.new('ShaderNodeOutputMaterial');enamel.node_tree.links.new(p.outputs[0],out.inputs[0]);p.inputs['Base Color'].default_value=(.015,.065,.082,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.29;p.inputs['Coat Weight'].default_value=.38;p.inputs['Coat Roughness'].default_value=.23
 # Reuse the original fine casting normal very gently beneath the glassy glaze.
 image=next(n.image for n in bronze.node_tree.nodes if n.type=='TEX_IMAGE' and '-normal' in n.image.name);t=enamel.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;n=enamel.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.08;enamel.node_tree.links.new(t.outputs[0],n.inputs['Color']);enamel.node_tree.links.new(n.outputs[0],p.inputs['Normal'])
 parts=[];stands=[]
 def mesh(name,vs,faces,mat):
  data=bpy.data.meshes.new(name);data.from_pydata(vs,[],faces);data.update();o=bpy.data.objects.new('Candle stand | '+name,data);bpy.context.collection.objects.link(o);data.materials.append(mat);o['sanctuary_interior']=True;o['crafted_candlestick']=True;parts.append(o)
  for face in data.polygons:face.use_smooth=True
  uv=data.uv_layers.new()
  for face in data.polygons:
   axes=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(face.normal[k]))]
   for li in face.loop_indices:
    v=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/.4,v[axes[1]]/.4)
  return o
 def lathe(name,profile,mat,n=96):
  vs=[];rings=[];faces=[]
  for r,z in profile:
   ring=[]
   for j in range(n if r>1e-8 else 1):
    a=j*math.tau/n;ring.append(len(vs));vs.append((r*math.cos(a),r*math.sin(a),z))
   rings.append(ring)
  for i in range(len(rings)-1):
   lower,upper=rings[i:i+2]
   for j in range(n):
    k=(j+1)%n
    if len(lower)==1:faces.append((lower[0],upper[k],upper[j]))
    elif len(upper)==1:faces.append((lower[j],lower[k],upper[0]))
    else:faces.append((lower[j],lower[k],upper[k],upper[j]))
  # The profile may be a closed shell rather than a solid spindle.
  if len(rings[0])>1 and len(rings[-1])>1:
   for j in range(n):faces.append((rings[-1][j],rings[-1][(j+1)%n],rings[0][(j+1)%n],rings[0][j]))
  return mesh(name,vs,faces,mat)
 def tube(name,points,r,mat=gold,closed=False):
  vs=[];faces=[];sides=8;N=len(points)
  points=[Vector(p) for p in points]
  tangents=[(points[(i+1)%N if closed else min(N-1,i+1)]-points[(i-1)%N if closed else max(0,i-1)]).normalized() for i in range(N)]
  axis=Vector((0,0,1)) if abs(tangents[0].z)<.9 else Vector((1,0,0));normals=[tangents[0].cross(axis).normalized()]
  for i in range(1,N):normals.append((tangents[i-1].rotation_difference(tangents[i])@normals[-1]).normalized())
  residual=0
  if closed:
   end=tangents[-1].rotation_difference(tangents[0])@normals[-1];residual=math.atan2(tangents[0].dot(end.cross(normals[0])),end.dot(normals[0]))
  for i,p in enumerate(points):
   normal=Quaternion(tangents[i],residual*i/N)@normals[i];binormal=tangents[i].cross(normal)
   for j in range(sides):a=j*math.tau/sides;vs.append(tuple(p+r*(normal*math.cos(a)+binormal*math.sin(a))))
  for i in range(N if closed else N-1):
   for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;c=((i+1)%N)*sides+(j+1)%sides;d=((i+1)%N)*sides+j;faces.append((a,b,c,d))
  if not closed:faces.extend([tuple(reversed(range(sides))),tuple((N-1)*sides+j for j in range(sides))])
  return mesh(name,vs,faces,mat)
 def ring(name,r,z,wire=.0025,mat=gold):return tube(name,[(r*math.cos(a),r*math.sin(a),z) for a in [i*math.tau/96 for i in range(96)]],wire,mat,True)
 outer=[(.207,.020),(.206,.032),(.187,.041),(.173,.055),(.152,.083),(.136,.125),(.137,.181),(.156,.210),(.156,.230),(.122,.253),(.071,.265),(.055,.277),(.072,.295),(.083,.318),(.077,.341),(.047,.365),(.047,.377),(.085,.391),(.165,.407),(.218,.432),(.229,.447),(.230,.457)]
 def radius(z):
  for (r0,z0),(r1,z1) in zip(outer,outer[1:]):
   if z0<=z<=z1:return r0+(r1-r0)*(z-z0)/(z1-z0)
  return outer[0][0] if z<outer[0][1] else outer[-1][0]
 def relief(name,a,z0,z1,width,radial,bulge=.006,mat=gold):
  # Closed relief patches: the back sits inside the support; no paper petals.
  vs=[];faces=[];nu,nv=12,6
  for layer in range(2):
   for i in range(nu+1):
    t=i/nu;z=z0+(z1-z0)*t;w=max(.018,math.sin(math.pi*t)**.8)*width
    for j in range(nv+1):
     s=2*j/nv-1;angle=a+s*w;rr=radial(z)+(.0008+bulge*math.sin(math.pi*t)*(1-s*s) if layer==0 else -.0012);vs.append((rr*math.cos(angle),rr*math.sin(angle),z))
  count=(nu+1)*(nv+1)
  for i in range(nu):
   for j in range(nv):q=i*(nv+1)+j;faces.extend([(q,q+1,q+nv+2,q+nv+1),(q+count,q+nv+1+count,q+nv+2+count,q+1+count)])
  boundary=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1) for i in range(nu-1,0,-1)]
  for i,q in enumerate(boundary):r=boundary[(i+1)%len(boundary)];faces.append((q,q+count,r+count,r))
  return mesh(name,vs,faces,mat)
 for side in [-1,1]:
  for index,(x,y,base,scale,ground,wr) in enumerate([(side*2.13,7.35,1.095,1.,1.07,.075),(side*2.65,8.18,1.952,.43,1.945,.047)]):
   first=len(parts);bottom=(ground-base)/scale
   profile=[(0,bottom),(.184,bottom),(.201,.008)]+outer+[(.226,.462),(.218,.452),(.210,.440),(.157,.421),(.080,.409),(.045,.407),(.042,.430),(.043,.748),(.060,.758),(.067,.773),(.065,.795),(.044,.815),(.043,.828),(.074,.840),(.125,.858),(.142,.875),(.145,.900),(.143,.915),(.131,.915),(.129,.901),(.115,.893),(.100,.889),(0,.889)]
   lathe('shaped copper body',profile,bronze)
   lathe('candle socket seat',[(0,.888),(.110,.888),(.110,.900),(0,.900)],gold)
   skin=[(radius(z)+.0005,z) for z in [.054,.06,.083,.125,.181,.210,.230,.244]];lathe('blue enamel foot',skin+[(r-.0015,z) for r,z in reversed(skin)],enamel)
   lathe('blue enamel column',[(.0428,.440),(.0438,.737),(.042,.737),(.041,.440)],enamel)
   for z,r in [(.014,.204),(.035,.199),(.251,.125),(.272,.061),(.362,.052),(.456,.229),(.433,.219),(.742,.046),(.814,.046),(.910,.139)]:ring('polished moulding',r,z)
   for j in range(16):
    a=j*math.tau/16;relief('lotus foot relief',a,.059,.237,.125,radius,.0045)
   for j in range(12):relief('underside lotus calyx',j*math.tau/12,.391,.432,.19,radius,.004)
   # Fine floral wire is wrapped around the upper enamel column.
   for j in range(4):
    a=j*math.tau/4
    pts=[]
    for k in range(41):t=k/40;angle=a+.42*math.sin(t*math.tau);r=.046;pts.append((r*math.cos(angle),r*math.sin(angle),.448+.277*t))
    tube('gilt scrolling stem',pts,.0017)
    for z,phase in [(.50,-.19),(.565,.27),(.63,-.19),(.694,.27)]:
     r=.047;angle=a+phase;pts=[]
     for k in range(24):t=k/24;theta=angle+.19*math.sin(t*math.tau);zz=z+.018*math.cos(t*math.tau);pts.append((r*math.cos(theta),r*math.sin(theta),zz))
     tube('gilt leaf wire',pts,.0015,closed=True)
   for o in parts[first:]:o.location=(x,y,base);o.scale=(scale,scale,scale);o['candlestick_index']=len(stands)
   stands.append({'positionNative':[x,y,base],'scale':scale,'supportTop':ground,'candleBase':base+.90*scale,'candleRadius':wr,'parts':len(parts)-first})
 return parts,[enamel],{'stands':stands,'reference':'https://www.metmuseum.org/art/collection/search/40725','parts':len(parts),'revision':1}
