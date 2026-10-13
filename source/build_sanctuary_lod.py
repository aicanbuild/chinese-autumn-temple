"""Build a geometry-only distant interior; keep the editable original untouched."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
source=R/'source/庄严内殿.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
names={'Sanctuary | hand burnished gold','Sanctuary | ivory lotus petals','Sanctuary | oxblood lacquer'}
parts=[o for o in bpy.data.objects if o.type in {'MESH','CURVE'} and o.data.materials and o.data.materials[0].name in names]
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');parts=list(bpy.context.selected_objects)
def tree(mesh):
 mesh.calc_loop_triangles();return BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.loop_triangles],all_triangles=True)
def error(mesh,target):
 # Vertices and triangle centroids in both directions sample silhouette and surface.
 maximum=0
 for v in mesh.vertices:
  hit=target.find_nearest(v.co);maximum=max(maximum,hit[3] if hit else math.inf)
  if maximum>.003:return maximum
 for tri in mesh.loop_triangles:
  center=sum((mesh.vertices[i].co for i in tri.vertices),start=mesh.vertices[0].co*0)/3
  hit=target.find_nearest(center);maximum=max(maximum,hit[3] if hit else math.inf)
  if maximum>.003:return maximum
 return maximum
report={'originalSHA256':before,'sampledErrorLimit':.003,'runtimeErrorBudget':.006,'reducedParts':0,'retainedParts':0,'maximumSampledError':0,'materials':{}}
for index,o in enumerate(parts):
 original=o.data;original.calc_loop_triangles();count=len(original.loop_triangles)
 if count<150:report['retainedParts']+=1;continue
 bpy.context.view_layer.objects.active=o
 # Native dimensions remain in world space, so millimetre limits are meaningful.
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 original=o.data;originalTree=tree(original);o.data=original.copy()
 mod=o.modifiers.new('Distant subpixel carving','DECIMATE');mod.ratio=.28;mod.use_collapse_triangulate=True
 bpy.ops.object.modifier_apply(modifier=mod.name)
 e=max(error(original,tree(o.data)),error(o.data,originalTree))
 if e>.003 or len(o.data.polygons)==0:
  rejected=o.data;o.data=original;bpy.data.meshes.remove(rejected);report['retainedParts']+=1
 else:report['reducedParts']+=1;report['maximumSampledError']=max(report['maximumSampledError'],e)
 if index%100==0:print('LOD PARTS',index,len(parts),flush=True)
groups={name:[o for o in parts if o.data.materials[0].name==name] for name in names}
for name in sorted(names):
 group=groups[name];bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;o['sourceMaterial']=name
 o.data.calc_loop_triangles();report['materials'][name]={'triangles':len(o.data.loop_triangles),'vertices':len(o.data.vertices)}
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.get('sourceMaterial'):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'sanctuary-distant.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='NONE',export_extras=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report['sourceUnchanged']=True;report['bytes']=(A/'sanctuary-distant.glb').stat().st_size
(A/'sanctuary-distant.json').write_text(json.dumps(report,indent=2));print('SANCTUARY LOD',json.dumps(report),flush=True)
