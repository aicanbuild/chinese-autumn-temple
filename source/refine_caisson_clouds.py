"""Round and taper the 288 carved cloud arms, preserving their bearing tops.
Run after refine_caisson_seats.py. Native projects and browser export stay in sync.
"""
import bpy,bmesh,math,json,shutil,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
PREFIX=('Dougong | lower cloud gong','Dougong | upper crossing gong','Dougong | rising radial arm','Dougong | chased radial arris','Dougong | gilt cloud outline')
def chosen(o):return o.type=='MESH' and o.name.startswith(PREFIX)
def ceiling(o):return o.type in {'MESH','CURVE'} and (o.name.startswith(('Caisson |','Dougong |','Ceiling |')) or o.get('ceiling_carving')) and not o.get('caisson_vines')
def signature():
 result={}
 for o in bpy.data.objects:
  if chosen(o):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for coll,prop,width,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    a=array.array(typ,[0])*(len(coll)*width);coll.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result

def smooth(points,closed=True,steps=2):
 points=[Vector(p) for p in points]
 for _ in range(steps):
  out=[] if closed else [points[0]]
  for i in range(len(points) if closed else len(points)-1):
   a,b=points[i],points[(i+1)%len(points)];out.extend([a*.75+b*.25,a*.25+b*.75])
  if not closed:out.append(points[-1])
  points=out
 return points

gong=[(-.22,.085),(-.20,.078),(-.16,.059),(-.10,.021),(0,0),(.10,.021),(.16,.059),(.20,.078),(.22,.085),(.215,.137),(.18,.12),(.13,.087),(.07,.072),(-.07,.072),(-.13,.087),(-.18,.12),(-.215,.137)]
radial=[(-.015,.008),(.045,.013),(.10,.063),(.18,.131),(.25,.184),(.34,.232),(.355,.279),(.30,.271),(.23,.225),(.16,.18),(.08,.102),(.025,.080),(-.015,.080)]

def replace(o,vertices,faces,smooth_sides=False):
 mesh=bpy.data.meshes.new(o.name+' | fine curved carving');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in vertices],[],faces);mesh.update()
 for mat in o.data.materials:mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;bm.to_mesh(mesh);bm.free()
 for p in mesh.polygons:p.use_smooth=smooth_sides and len(p.vertices)==4
 uv=mesh.uv_layers.new(name='Fine carving grain')
 for p in mesh.polygons:
  for li in p.loop_indices:
   v=vertices[mesh.loops[li].vertex_index];uv.data[li].uv=(v.x*.7+v.y*.31,v.z*.7+v.y*.43)
 
 for mod in list(o.modifiers):
  if mod.name in ['Silk smooth carved arris','Carved face weighted normals']:o.modifiers.remove(mod)
 o.data=mesh;o['cloud_carving_revision']=2

def tube(o,points,radius):
 vs=[];fs=[];n=8
 for j,p in enumerate(points):
  d=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized();u=d.cross(Vector((0,0,1))).normalized();v=d.cross(u).normalized()
  for k in range(n):vs.append(p+radius*(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n)))
 for j in range(len(points)-1):
  for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple((len(points)-1)*n+k for k in range(n))]);replace(o,vs,fs,True)

reports=[]
backupdir=R/'evidence/cloud-carving-original';backupdir.mkdir(exist_ok=True)
asset=R/'dist/assets/fine-caisson.glb'
if not (backupdir/asset.name).exists():shutil.copy2(asset,backupdir/asset.name)
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-cloud-carving.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signature();targets=[o for o in bpy.data.objects if chosen(o)];assert len(targets)==576
 clusters={}
 for o in bpy.data.objects:
  if 'dougong_cluster' in o:clusters.setdefault(o['dougong_cluster'],[]).append(o)
 for ci,group in clusters.items():
  level=ci//24;edge=(ci%24)//3;t=[.18,.5,.82][ci%3];r,z=[(2.48,4.36),(2.15,4.61),(1.79,4.89),(1.43,5.16)][level];a=math.pi/8+edge*math.tau/8;b=a+math.tau/8
  p=Vector((r*math.cos(a),7.1+r*math.sin(a),z));q=Vector((r*math.cos(b),7.1+r*math.sin(b),z));ta=(q-p).normalized();inside=Vector((-ta.y,ta.x,0));origin=p.lerp(q,t)+inside*.028;center=origin+inside*.045+Vector((0,0,-.015))
  def world(u,v,h):
   point=origin+ta*u+inside*v+Vector((0,0,h));d=point-center
   return center+ta*d.dot(ta)*.62+inside*d.dot(inside)*.86+Vector((0,0,d.z*.84))
  for o in group:
   if not chosen(o) or o.get('cloud_carving_revision')==2:continue
   if o.name.startswith(('Dougong | lower cloud gong','Dougong | upper crossing gong','Dougong | rising radial arm')):
    radial_arm='rising' in o.name;upper='upper' in o.name
    profile=smooth(radial if radial_arm else [(x*(.83 if upper else 1),y*(.72 if upper else 1)) for x,y in gong]);depth=.070 if radial_arm else .076 if upper else .072;v0=.285 if upper else .045;h0=.205 if upper else .02 if radial_arm else .015
    vs=[world(sign*depth/2 if radial_arm else p.x,v0+p.x if radial_arm else v0+sign*depth/2,h0+p.y) for sign in [-1,1] for p in profile];n=len(profile);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    replace(o,vs,faces,True)
    bevel=o.modifiers.new('Silk smooth carved arris','BEVEL');bevel.width=.0012;bevel.segments=3
    bevel.affect='EDGES';bevel.limit_method='ANGLE';bevel.angle_limit=.5
    normal=o.modifiers.new('Carved face weighted normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=30
   elif 'radial arris' in o.name:
    oldcenter=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices);side=1 if (oldcenter-center).dot(ta)>0 else -1
    tube(o,[world(side*.0357,.045+p.x,.022+p.y) for p in smooth(radial[:7],False)],.00145)
   else:
    tube(o,[world(p.x,.008,.018+p.y) for p in smooth(gong[:9],False)],.00145)
 # Keep lacquer quietly polished; grain should not read as deeply sawn lumber.
 mat=next(o.data.materials[0] for o in targets if 'lower cloud gong' in o.name)
 p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.38;p.inputs['Coat Weight'].default_value=.35;p.inputs['Coat Roughness'].default_value=.27
 for node in mat.node_tree.nodes:
  if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.035
 assert signature()==before
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
 reports.append({'file':filename,'carvedArms':288,'fittedGoldArrises':288,'preservedObjects':len(before),'otherGeometryUVTransformsUnchanged':True})
 if filename=='庄严内殿.blend':
  bpy.ops.object.select_all(action='DESELECT');parts=[o for o in bpy.data.objects if ceiling(o)]
  for o in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');groups={}
  for o in bpy.context.selected_objects:groups.setdefault(o.data.materials[0],[]).append(o)
  exports=[]
  for mat,group in groups.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in group:o.select_set(True)
   bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name='Fine caisson | '+mat.name;o['sourceMaterial']=mat.name;exports.append(o)
  bpy.ops.object.select_all(action='DESELECT')
  for o in exports:o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(asset),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=18,export_draco_normal_quantization=14)
(R/'evidence/caisson-cloud-native.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print('CLOUD CARVING',reports,flush=True)
