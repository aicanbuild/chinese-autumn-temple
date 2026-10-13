"""Editable sloping terrain and linked woodland; the browser instances the same trees."""
import bpy,bmesh,math,random,json,struct
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';random.seed(9137)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def hash2(x,y):return math.sin(x*127.1+y*311.7+7.3)*43758.5453%1

def noise(x,y):
 ix=math.floor(x);iy=math.floor(y);fx=smooth(x-ix);fy=smooth(y-iy)
 return (hash2(ix,iy)*(1-fx)+hash2(ix+1,iy)*fx)*(1-fy)+(hash2(ix,iy+1)*(1-fx)+hash2(ix+1,iy+1)*fx)*fy

def fbm(x,y):return sum(noise(x*2**k,y*2**k)*.5**k for k in range(5))/1.9375

def height(x,y):
 r=math.hypot(x,y);fade=smooth((r-21)/24)
 peaks=[(-66,57,40,39),(27,101,51,45),(88,27,37,36),(-110,-39,25,52),(63,-88,22,49)]
 h=sum(amp*math.exp(-((x-cx)**2+(y-cy)**2)/(w*w)) for cx,cy,amp,w in peaks)
 h+=6*fbm(x*.035,y*.035)+2.6*(noise(x*.11,y*.11)-.5)
 h*=.80+.3*fbm(x*.024+23,y*.024-8)
 clearing=.18-.14*(math.hypot(x/11.5,(y+5.8)/6.9)-1)
 return max(-.23,clearing)+fade*h

def material(name,color,texture=None,leaf=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.91
 if texture:
  image=bpy.data.images.load(str(A/texture),check_existing=True);t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
  if leaf:m.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED';m.use_backface_culling=False
 if not leaf and texture:
  file=A/(texture[:-4]+'-normal.jpg')
  if file.exists():
   t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(file),check_existing=True);t.image.colorspace_settings.name='Non-Color';n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.42;m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs[0],p.inputs['Normal'])
 return m
terrainMat=material('Landscape | forest floor',(.38,.43,.28),'pbr-earth.jpg')
barkMat=material('Woodland | bark',(.3,.27,.19),'pbr-bark.jpg')
leafMats=[material('Woodland | '+name,(.6,.7,.4),name+'-leaf.png',True) for name in ['green','ginkgo','maple']]
farLeafMats=[material('Woodland | '+name+' sprays',(.6,.7,.4),name+'-spray.png',True) for name in ['green','ginkgo','maple']]

def mesh(name,vs,fs,mat,uvs=None,colors=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);o['landscape_asset']=True
 if colors and not mat.node_tree.nodes.get('Leaf and soil shading'):
  nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');source=p.inputs['Base Color'].links[0].from_socket
  color=nodes.new('ShaderNodeVertexColor');color.layer_name='Color';mix=nodes.new('ShaderNodeMixRGB');mix.name='Leaf and soil shading';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;links.new(source,mix.inputs[1]);links.new(color.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],p.inputs['Base Color'])
 for p in me.polygons:p.use_smooth=True
 if uvs:
  layer=me.uv_layers.new(name='UVMap')
  for p in me.polygons:
   for li in p.loop_indices:layer.data[li].uv=uvs[me.loops[li].vertex_index]
 if colors:
  ca=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
  for i,c in enumerate(colors):ca.data[i].color=(*c,1)
 return o
# Rings begin at the exact pond cutout and gradually open into a 540 m terrain.
vs=[];uv=[];cols=[];faces=[];N=320;NR=160
for j in range(NR+1):
 t=j/NR;rad=11.7+(270-11.7)*t**1.50
 for i in range(N+1):
  a=i/N*math.tau;stretch=7.1/11.7+(1-7.1/11.7)*smooth((rad-11.7)/25)
  x=math.cos(a)*rad;y=-5.8+math.sin(a)*rad*stretch;z=height(x,y);vs.append((x,y,z));uv.append((x/7,y/7))
  shade=.65+.32*fbm(x*.12,y*.12);slope=math.hypot(height(x+1,y)-z,height(x,y+1)-z)
  cols.append((shade*(.23+.09*min(1,slope)),shade*(.39-.09*min(1,slope)),shade*.16))
for j in range(NR):
 for i in range(N):a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
terrain=mesh('Sculpted woodland terrain',vs,faces,terrainMat,uv,cols)
bm=bmesh.new();bm.from_mesh(terrain.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(terrain.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');terrain.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'terrain.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Procedural linked tree prototypes have real branches and individually curled leaves.
prototypes=[]
for lod in range(2):
 for species in range(3):
  rng=random.Random(240+species*170+lod*6);woodv=[];woodf=[];wooduv=[];lv=[];lf=[];luv=[];lc=[]
  root=bpy.data.objects.new(f'Woodland_{species}_{lod}',None);bpy.context.collection.objects.link(root);root['landscape_asset']=True
  def tube(a,b,r1,r2,n=7):
   a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');start=len(woodv)
   for p,r in [(a,r1),(b,r2)]:
    for k in range(n):woodv.append(tuple(p+q@Vector((r*math.cos(k*math.tau/n),r*math.sin(k*math.tau/n),0))));wooduv.append((k/n,(p-a).length*.5))
   for k in range(n):woodf.append((start+k,start+(k+1)%n,start+(k+1)%n+n,start+k+n))
  trunk=[(math.sin(j*.57)*.17,math.cos(j*.43)*.13,j*.60) for j in range(12)]
  for j in range(11):tube(trunk[j],trunk[j+1],.19*(1-j/12)**1.3+.015,.19*(1-(j+1)/12)**1.3+.012,9)
  for b in range(10):
   a=b*2.399+species*.7;start=Vector(trunk[3+b//2]);reach=(2.1-b*.11)*rng.uniform(.85,1.13)
   end=start+Vector((math.cos(a)*reach,math.sin(a)*reach,.7+0.1*b));tube(start,end,.065*(1-b*.055),.018)
   for j in range(3):
    aa=a+(j-1)*.72;tip=end+Vector((math.cos(aa)*.66,math.sin(aa)*.66,.55+rng.random()*.35));tube(end,tip,.020,.004,5)
    count=72 if lod==0 else 13
    for k in range(count):
     angle=rng.random()*math.tau;r=math.sqrt(rng.random())*.78;center=tip+Vector((math.cos(angle)*r,math.sin(angle)*r,(rng.random()+rng.random()-1)*.49))
     size=rng.uniform(.13,.22) if lod==0 else rng.uniform(.48,.68)
     az=rng.random()*math.tau;tilt=rng.uniform(-.65,.65);u=Vector((math.cos(az),math.sin(az),tilt))*size;v=Vector((-math.sin(az),math.cos(az),rng.uniform(-.65,.65)))*size*.60
     at=len(lv);lv.extend([tuple(center-u-v),tuple(center+u-v),tuple(center+u+v),tuple(center-u+v),tuple(center+Vector((0,0,.027)))])
     luv.extend([(0,0),(1,0),(1,1),(0,1),(.5,.5)]);lf.extend([(at,at+1,at+4),(at+1,at+2,at+4),(at+2,at+3,at+4),(at+3,at,at+4)])
     shade=rng.uniform(.72,1.05)*(1-.15*(1-r/.78));lc.extend([(shade,shade,shade*.93)]*5)
  wood=mesh(f'Branches_{species}_{lod}',woodv,woodf,barkMat,wooduv);wood.parent=root
  leaves=mesh(f'Leaves_{species}_{lod}',lv,lf,(leafMats if lod==0 else farLeafMats)[species],luv,lc);leaves.parent=root;prototypes.append(root)
bpy.ops.object.select_all(action='DESELECT')
for root in prototypes:
 root.select_set(True)
 for ob in root.children:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'woodland.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
# Loose groves separated by gullies. The front approach remains open.
rng=random.Random(6812);trees=[]
for attempt in range(12000):
 if len(trees)>=620:break
 a=rng.random()*math.tau;r=math.sqrt(rng.uniform(26**2,143**2));x=math.cos(a)*r;y=math.sin(a)*r
 if y<-16 and abs(x)<28 and r<57:continue
 if fbm(x*.043+9,y*.043+21)<.37:continue
 if any((x-p[0])**2+(y-p[1])**2<(3.4 if r<65 else 4.3)**2 for p in trees):continue
 scale=rng.uniform(.80,1.38)*(1.13 if r>65 else 1);species=rng.choices([0,1,2],[.78,.12,.10])[0];lod=int(r>65)
 trees.append([round(x,3),round(y,3),round(height(x,y)-.04,3),round(scale,3),round(rng.random()*math.tau,4),species,lod])
(A/'woodland.json').write_text(json.dumps({'trees':trees,'terrainRings':NR,'terrainSegments':N,'seed':6812},separators=(',',':')))
# Native source: the very same tree meshes are shared by hundreds of editable instances.
for i,(x,y,z,scale,rotation,species,lod) in enumerate(trees):
 proto=prototypes[lod*3+species]
 for part in proto.children:
  copy=part.copy();copy.data=part.data;copy.parent=None;bpy.context.collection.objects.link(copy);copy.location=(x,y,z);copy.rotation_euler.z=rotation;copy.scale=(scale,)*3;copy.name=f'Woodland tree {i:03d} | '+part.name;copy['landscape_asset']=True
for root in prototypes:
 for part in list(root.children):bpy.data.objects.remove(part,do_unlink=True)
 bpy.data.objects.remove(root,do_unlink=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/山林地形.blend'))
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
for o in list(bpy.data.objects):
 if o.type=='MESH' and any(m and m.name=='Manicured moss garden' for m in o.data.materials):o.hide_render=True;o.hide_set(True)
 if o.get('landscape_asset'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(R/'source/山林地形.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
print('LANDSCAPE COMPLETE',len(trees),'trees; terrain',len(vs),'vertices',flush=True)
