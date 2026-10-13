"""Original small celadon offering bowls: complete foot, walls and water surface.
Material/form reference: Met 48373 and British Museum 1909,0401.11.
Not a replica of either museum object. Native coordinates are Z-up.
"""
import bpy,math,bmesh
from mathutils import Vector
SUPPORT_TOP=1.895

def is_offering_cup(o):
 return bool(o.get('crafted_offering_cup')) or any(o.name.startswith('Offering | '+s) for s in ['celadon water cup','gilt cup rim','still water'])

def build_offering_cups():
 parts=[]
 used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 gold=next(m for m in used if m.name.startswith('Sanctuary | hand burnished gold'))
 bronze=next(m for m in used if m.name.startswith('Sanctuary | antique gilt bronze'))
 def material(name,color,rough):
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=rough;return m,p
 glaze,p=material('Sanctuary | jade celadon offering porcelain',(.23,.39,.32),.21);p.inputs['Coat Weight'].default_value=.65;p.inputs['Coat Roughness'].default_value=.12;p.inputs['IOR'].default_value=1.48
 t=glaze.node_tree.nodes.new('ShaderNodeTexImage');t.image=next(n.image for n in bronze.node_tree.nodes if n.type=='TEX_IMAGE' and '-normal' in n.image.name)
 n=glaze.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.025;glaze.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);glaze.node_tree.links.new(n.outputs[0],p.inputs['Normal'])
 foot,p=material('Sanctuary | unglazed celadon foot',(.37,.24,.13),.79)
 water,p=material('Sanctuary | clear offering water',(.46,.56,.51),.035);p.inputs['Alpha'].default_value=.27;p.inputs['IOR'].default_value=1.333;p.inputs['Coat Weight'].default_value=1;p.inputs['Coat Roughness'].default_value=.025;water.surface_render_method='DITHERED'
 def lathe(name,profile,index,materials,foot_segments=()):
  vs=[];rings=[];faces=[];segments=[];N=96
  for r,z in profile:
   ring=[]
   for j in range(N if r>1e-8 else 1):
    a=j*math.tau/N;ring.append(len(vs));vs.append((r*math.cos(a),r*math.sin(a),z))
   rings.append(ring)
  for k,(a,b) in enumerate(zip(rings,rings[1:])):
   for j in range(N):
    h=(j+1)%N
    if len(a)==1:faces.append((a[0],b[h],b[j]))
    elif len(b)==1:faces.append((a[j],a[h],b[0]))
    else:faces.append((a[j],a[h],b[h],b[j]))
    segments.append(k)
  if len(rings[0])>1 and len(rings[-1])>1:
   a,b=rings[-1],rings[0]
   for j in range(N):faces.append((a[j],a[(j+1)%N],b[(j+1)%N],b[j]));segments.append(-1)
  data=bpy.data.meshes.new(name);data.from_pydata(vs,[],faces);data.update();o=bpy.data.objects.new('Offering cup | '+name,data);bpy.context.collection.objects.link(o);o.location=((index-3)*.19,7.99,SUPPORT_TOP)
  for m in materials:data.materials.append(m)
  for face,k in zip(data.polygons,segments):face.use_smooth=True;face.material_index=1 if k in foot_segments else 0
  # Preserve outward orientation for the closed ceramic shell and water volume.
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
  uv=data.uv_layers.new(name='Craft surface')
  for face in data.polygons:
   axes=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(face.normal[k]))]
   for li in face.loop_indices:
    v=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/.12,v[axes[1]]/.12)
  o['sanctuary_interior']=True;o['crafted_offering_cup']=True;o['cup_index']=index;parts.append(o);return o
 # Recessed underside -> bare support ring -> curved bowl -> rounded lip -> inner well.
 profile=[(0,.008),(.020,.008),(.022,.005),(.022,.001),(.023,0),(.028,0),(.030,.0015),(.031,.004),(.031,.010),(.029,.014),(.031,.018),(.038,.024),(.044,.033),(.050,.046),(.055,.060),(.057,.070),(.0567,.072),(.0555,.073),(.054,.0725),(.0535,.071),(.0522,.060),(.0472,.046),(.0412,.033),(.0352,.026),(.030,.021),(.016,.020),(0,.020)]
 for i in range(7):
  lathe('closed porcelain bowl',profile,i,[glaze,foot],range(2,7))
  # Thin gilding follows the actual rounded lip, replacing the bulky detached torus.
  rim=[(.0555+.0007*math.cos(a),.0728+.0007*math.sin(a)) for a in [j*math.tau/12 for j in range(12)]]
  lathe('fine gilt lip',rim,i,[gold])
  # A closed shallow surface with a 0.8 mm meniscus. The inner wall contains it.
  lathe('still water meniscus',[(0,.056),(.044,.056),(.0498,.056),(.0506,.0568),(.0506,.0558),(.044,.055),(0,.055)],i,[water])
 return parts,[glaze,foot,water],{'cups':7,'parts':21,'supportTop':SUPPORT_TOP,'cupHeight':.073,'outerDiameter':.114,'waterLevel':SUPPORT_TOP+.056,'meniscusRise':.0008,'rimWireRadius':.0007,'closedCeramicBodies':True}
