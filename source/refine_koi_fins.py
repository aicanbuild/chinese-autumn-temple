"""Curved koi fin membranes in the native scene and the shared browser asset."""
import bpy,math,sys,shutil,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets/koi';sys.path.insert(0,str(R/'source'))
from koi_surface_finish import radius
from granite_finish import refresh_glb
baseline=R/'evidence/koi-before-fins.glb'
if not baseline.exists():shutil.copy2(A/'koi.glb',baseline)
def isfin(me):return any(m and m.name.startswith('Translucent fin rays') for m in me.materials)
def fingerprint(me):
 h=hashlib.sha256()
 for v in me.vertices:h.update(str(tuple(v.co)).encode())
 for p in me.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
def smoothprofile(points,u):
 n=len(points);q=min(n-1-1e-9,max(0,u*(n-1)));i=int(q);t=q-i
 # Catmull-Rom with each coordinate clamped to the neighbouring values: rounded
 # outlines cannot grow outside the authored fin silhouette envelope.
 p0=Vector(points[max(0,i-1)]);p1=Vector(points[i]);p2=Vector(points[i+1]);p3=Vector(points[min(n-1,i+2)])
 p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3)
 return Vector([max(min(p1[k],p2[k]),min(max(p1[k],p2[k]),p[k])) for k in range(3)])
def sample(name,u,v):
 side=-1 if '-1' in name else 1
 if name.startswith('Caudal'):
  a=u*math.pi;root=Vector((0,0,-.56));edge=Vector((.009*math.sin(a*2),.235*math.cos(a),-.83-.17*abs(math.cos(a))**1.25));axis=Vector((1,0,0));bow=.004
 elif name.startswith('Pectoral'):
  root=Vector((side*.115,-.025,.29));edge=Vector((side*(.13+math.sin(u*math.pi)*.235),-.045-.026*math.sin(u*math.pi),.32-u*.38));axis=Vector((0,1,0));bow=.010
 elif name.startswith('Pelvic'):
  root=Vector((side*.08,-.065,-.15));edge=Vector((side*(.078+math.sin(u*math.pi)*.135),-.07-.025*math.sin(u*math.pi),-.13-u*.25));axis=Vector((0,1,0));bow=.003
 elif name.startswith('Dorsal'):
  edge=smoothprofile([(0,.095,-.36),(0,.15,-.30),(0,.23,-.10),(0,.252,.11),(0,.20,.27),(0,.126,.30)],u);root=Vector((0,radius((edge.z+.6)/1.25)*.86*.995,edge.z));edge.y=max(root.y,edge.y);edge.y=root.y+(edge.y-root.y)*min(1,u*14,(1-u)*14);axis=Vector((1,0,0));bow=.003
 elif name.startswith('Anal'):
  edge=smoothprofile([(0,-.07,-.41),(0,-.17,-.42),(0,-.18,-.34),(0,-.075,-.21)],u);root=Vector((0,-radius((edge.z+.6)/1.25)*.69*.995,edge.z));edge.y=min(root.y,edge.y);edge.y=root.y+(edge.y-root.y)*min(1,u*14,(1-u)*14);axis=Vector((1,0,0));bow=.002
 else:raise ValueError(name)
 delta=edge-root;length=delta.length;scallop=.0015*(.5-.5*math.cos(u*math.tau*17))*math.sin(u*math.pi)
 edge=root+delta*max(0,1-scallop/max(length,.001));p=root.lerp(edge,v)
 p+=axis*bow*math.sin(v*math.pi)*math.sin(u*math.pi)*(1+.12*math.cos(u*math.tau*17))
 return p
reports=[]
for name in ['锦鲤','听秋寺院']:
 path=R/'source'/(name+'.blend');backup=path.with_name(name+'-before-koi-fins.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));objects={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects};meshes={o.data for o in bpy.data.objects if o.type=='MESH'}
 unchanged={me.name:fingerprint(me) for me in meshes if not isfin(me)};fins=[me for me in meshes if isfin(me)];assert len(fins)==7,[me.name for me in fins]
 report={'file':name,'objects':len(objects),'unrelatedMeshes':len(unchanged),'fins':[]}
 for me in fins:
  oldTriangles=sum(len(p.vertices)-2 for p in me.polygons);mats=list(me.materials);vs=[];uv=[];faces=[];segments=48 if me.name.startswith(('Caudal','Dorsal')) else 32;steps=9
  for j in range(steps+1):
   for i in range(segments+1):
    p=sample(me.name,i/segments,j/steps);vs.append((p.x,-p.z,p.y));uv.append((i/segments,j/steps))
  for j in range(steps):
   for i in range(segments):
    a=j*(segments+1)+i;b=a+1;c=b+segments+1;d=a+segments+1
    for tri in [(a,b,c),(a,c,d)]:
     x,y,z=[Vector(vs[k]) for k in tri]
     if (y-x).cross(z-x).length_squared>1e-16:faces.append(tri)
  me.clear_geometry();me.from_pydata(vs,[],faces);me.update();me.materials.clear()
  for m in mats:me.materials.append(m)
  for layer in list(me.uv_layers):me.uv_layers.remove(layer)
  layer=me.uv_layers.new(name='UVMap')
  for poly in me.polygons:
   poly.use_smooth=True
   for li in poly.loop_indices:layer.data[li].uv=uv[me.loops[li].vertex_index]
  me['refined_fin_v1']=True;report['fins'].append({'name':me.name,'oldTriangles':oldTriangles,'newTriangles':len(faces),'vertices':len(vs)})
 material=fins[0].materials[0];nodes=material.node_tree.nodes;links=material.node_tree.links;p=nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.5;p.inputs['Coat Weight'].default_value=.10;p.inputs['Coat Roughness'].default_value=.28
 tex=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image and 'fin-membrane' in n.image.name)
 image=bpy.data.images.load(str(A/'fin-membrane.png'),check_existing=False);image.name='fin-membrane';image.pack();tex.image=image
 nt=nodes.get('Fin microrelief') or nodes.new('ShaderNodeTexImage');nt.name='Fin microrelief';normal=bpy.data.images.load(str(A/'fin-normal.jpg'),check_existing=False);normal.colorspace_settings.name='Non-Color';normal.pack();nt.image=normal
 nm=nodes.get('Fin ray normal') or nodes.new('ShaderNodeNormalMap');nm.name='Fin ray normal';nm.inputs['Strength'].default_value=.65;links.new(nt.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs[0],p.inputs['Normal'])
 assert objects=={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects};assert unchanged=={me.name:fingerprint(me) for me in meshes if not isfin(me)}
 bpy.ops.wm.save_as_mainfile(filepath=str(path));print('FINS NATIVE SAVED',name,flush=True)
 if name=='锦鲤':
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'koi.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
  b=(A/'koi.glb').read_bytes();doc=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);replace={}
  for im in doc['images']:
   for stem in ['kohaku','sanke','yamabuki','platinum','scales-normal','scales-rough','fin-normal','fin-membrane']:
    if im['name'].startswith(stem):replace[im['name']]=A/(stem+('.png' if stem=='fin-membrane' else '.jpg'));break
  report['export']=refresh_glb(A/'koi.glb',replace)
 reports.append(report)
(R/'evidence/koi-fins-native.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print('FINS COMPLETE',flush=True)
