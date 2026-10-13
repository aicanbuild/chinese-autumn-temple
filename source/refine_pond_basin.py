"""Install a real pond basin, seat gravel, and extend timber piers into sediment."""
import bpy,bmesh,json,sys,shutil,hashlib,array,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';sys.path.insert(0,str(R/'source'))
from pond_basin import basin_mesh,basin_height,seat_stone,extend_pier
files=['自然池岸.blend','精修木桥.blend','听秋寺院.blend']
def affected(o):return o.name=='Riverbed sediment' or o.get('pond_zone')=='bed' or bool(o.get('bridge_asset') and o.name.startswith('Pier timber'))
def signature():
 out={}
 for o in bpy.data.objects:
  if affected(o):continue
  h=hashlib.sha256();h.update(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for collection,prop,width,code in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    values=array.array(code,[0])*(len(collection)*width);collection.foreach_get(prop,values);h.update(values.tobytes())
   for uv in o.data.uv_layers:
    values=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',values);h.update(values.tobytes())
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.points:h.update(array.array('f',p.co).tobytes())
  out[o.name]=h.hexdigest()
 return out
layout=json.loads((A/'pond-stones.json').read_text());reports=[]
for filename in files:
 file=R/'source'/filename;backup=file.with_name(file.stem+'-before-pond-basin.blend')
 if not backup.exists():shutil.copy2(file,backup)
 bpy.ops.wm.open_mainfile(filepath=str(file));bpy.context.view_layer.update();before=signature();stones=0;piers=[]
 for o in bpy.data.objects:
  if o.get('pond_zone')=='bed':
   seat_stone(o);stones+=1
   placements=[p for p in layout['placements'] if p[-1]=='bed' and abs(p[1]-o.location.x)<1e-5 and abs(p[2]-o.location.y)<1e-5]
   assert len(placements)==1,(o.name,placements);placements[0][3]=o.location.z
  elif o.get('bridge_asset') and o.name.startswith('Pier timber'):piers.append(extend_pier(o))
  elif o.name=='Riverbed sediment':
   materials=list(o.data.materials);o.data=basin_mesh()
   for m in materials:o.data.materials.append(m)
   assert all(abs(o.matrix_world[i][j]-(1 if i==j else 0))<1e-8 for i in range(4) for j in range(4))
   o['pond_basin_revision']=1
 bpy.context.view_layer.update();assert signature()==before
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.wm.open_mainfile(filepath=str(file));assert signature()==before
 reports.append({'file':filename,'stonesSeated':stones,'piers':piers,'preservedOtherObjects':len(before)})
 if filename=='精修木桥.blend':
  # Re-export the existing four material batches after moving only the pier feet.
  materials=set(o.data.materials[0] for o in bpy.data.objects if o.type=='MESH' and o.data.materials)
  for m in materials:
   group=[o for o in bpy.data.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==m];bpy.ops.object.select_all(action='DESELECT')
   for o in group:o.select_set(True)
   bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=m.name
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'bridge.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
  b=(A/'bridge.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);tail=b[20+n:]
  colors={'Bridge | oiled rosewood':[.34,.20,.10,1],'Bridge | polished handrails':[.30,.17,.08,1],'Bridge | satin gilded copper':[.64,.40,.105,1],'Bridge | recessed bronze':[.16,.11,.045,1]}
  for m in doc['materials']:
   m['pbrMetallicRoughness']['baseColorFactor']=colors[m['name']]
   if m['name']=='Bridge | satin gilded copper':m['pbrMetallicRoughness']['roughnessFactor']=.50
   if m['name']=='Bridge | recessed bronze':m['pbrMetallicRoughness']['roughnessFactor']=.85
  chunk=json.dumps(doc,separators=(',',':')).encode();chunk+=b' '*((-len(chunk))%4);(A/'bridge.glb').write_bytes(b'glTF'+struct.pack('<II',2,20+len(chunk)+len(tail))+struct.pack('<II',len(chunk),0x4e4f534a)+chunk+tail)
# Independent checks on the reopened full temple and its actual triangulated bed.
bed=bpy.data.objects['Riverbed sediment'];bm=bmesh.new();bm.from_mesh(bed.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.free()
tree=BVHTree.FromPolygons([v.co for v in bed.data.vertices],[tuple(p.vertices) for p in bed.data.polygons]);stone_contacts=[]
for o in bpy.data.objects:
 if o.get('pond_zone')=='bed':
  distances=[]
  for v in o.data.vertices:
   p=o.matrix_world@v.co;hit,_,_,_=tree.ray_cast(Vector((p.x,p.y,0)),Vector((0,0,-1)),3);assert hit is not None;distances.append(p.z-hit.z)
  contact=min(distances);assert -.014<contact<-.006,(o.name,contact);stone_contacts.append(contact)
 elif o.get('bridge_asset') and o.name.startswith('Pier timber'):
  points=[o.matrix_world@v.co for v in o.data.vertices];bottom=min(p.z for p in points)
  for p in points:
   if p.z<bottom+.001:
    hit,_,_,_=tree.ray_cast(Vector((p.x,p.y,0)),Vector((0,0,-1)),3);assert hit is not None;assert .07<hit.z-p.z<.17,(o.name,tuple(p),hit.z-p.z)
assert len(stone_contacts)==sum(p[-1]=='bed' for p in layout['placements'])
report={'projects':reports,'closedBasin':True,'bedVertices':len(bed.data.vertices),'bedTriangles':sum(len(p.vertices)-2 for p in bed.data.polygons),'stoneContacts':len(stone_contacts),'minStoneEmbedding':-max(stone_contacts),'maxStoneEmbedding':-min(stone_contacts)}
(R/'evidence/pond-basin-native.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('BASIN NATIVE',report,flush=True)
bpy.ops.object.select_all(action='DESELECT');bed.select_set(True);bpy.context.view_layer.objects.active=bed
bpy.ops.export_scene.gltf(filepath=str(A/'pond-basin.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='NONE',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
layout['basinRevision']=1;(A/'pond-stones.json').write_text(json.dumps(layout,separators=(',',':')))
meta={'revision':1,'vertices':report['bedVertices'],'triangles':report['bedTriangles'],'waterY':-.025,'edgeHeight':-.98,'centralDepth':-.025-basin_height(0,-5.8),'supportEmbedding':.12,'stones':len(stone_contacts)}
(A/'pond-basin.json').write_text(json.dumps(meta,indent=2));print('BASIN EXPORTED',meta,flush=True)
