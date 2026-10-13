"""Refine original caisson joinery without changing its stepped painted soffits."""
import bpy,math,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
def selected(o):return o.type in {'MESH','CURVE'} and (o.name.startswith(('Caisson |','Dougong |','Ceiling |')) or o.get('ceiling_carving')) and not o.get('caisson_vines')
reports=[]
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-fine-caisson.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));parts=[o for o in bpy.data.objects if selected(o)]
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
 parts=list(bpy.context.selected_objects)
 lacquer=bpy.data.materials.get('Caisson | polished cinnabar joinery') or bpy.data.materials.new('Caisson | polished cinnabar joinery');lacquer.use_nodes=True;p=lacquer.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.13,.025,.015,1);p.inputs['Roughness'].default_value=.32;p.inputs['Coat Weight'].default_value=.52;p.inputs['Coat Roughness'].default_value=.23
 # Fine, restrained wood pore map; colour stays even under the glazing.
 t=lacquer.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/'pbr-rosewood-normal.jpg'),check_existing=True);t.image.colorspace_settings.name='Non-Color';uv=lacquer.node_tree.nodes.new('ShaderNodeTexCoord');mapping=lacquer.node_tree.nodes.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(5,5,5);normal=lacquer.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.13;l=lacquer.node_tree.links;l.new(uv.outputs['UV'],mapping.inputs['Vector']);l.new(mapping.outputs[0],t.inputs['Vector']);l.new(t.outputs[0],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs['Normal'])
 clusters={}
 for o in parts:
  if 'dougong_cluster' in o:clusters.setdefault(o['dougong_cluster'],[]).append(o)
 for group in clusters.values():
  seat=next(o for o in group if o.name.startswith('Dougong | seated dou block'));center=sum((seat.matrix_world@v.co for v in seat.data.vertices),Vector())/len(seat.data.vertices)
  inward=Vector((-center.x,7.1-center.y,0)).normalized();angle=round((math.atan2(inward.y,inward.x)-math.pi/4)/(math.pi/4))*math.pi/4+math.pi/4;inward=Vector((math.cos(angle),math.sin(angle),0));tangent=Vector((inward.y,-inward.x,0))
  for o in group:
   if o.get('fine_caisson'):continue
   inverse=o.matrix_world.inverted()
   for v in o.data.vertices:
    q=o.matrix_world@v.co-center;v.co=inverse@(center+tangent*q.dot(tangent)*.62+inward*q.dot(inward)*.86+Vector((0,0,q.z*.84)))
 # Restore mouldings to their authored curved-crown heights. Solid lotus
 # carvings use their own object tag and must be exported alongside the frame.
 for o in parts:
  if not o.name.startswith('Caisson | concentric gold band') or o.get('fine_caisson_rosette_revision')!=1:continue
  points=[o.matrix_world@v.co for v in o.data.vertices];center=sum(points,Vector())/len(points);radius=sum(math.hypot(p.x,p.y-7.1) for p in points)/len(points);height=5.47 if radius>.95 else 5.60 if radius>.6 else 5.70
  delta=o.matrix_world.inverted().to_3x3()@Vector((0,0,height-center.z))
  for v in o.data.vertices:v.co+=delta
  o['fine_caisson_rosette_revision']=2
 for o in parts:
  if o.get('fine_caisson'):continue
  if not o.data.materials:continue
  mat=o.data.materials[0]
  if 'oxblood' in mat.name:
   o.data.materials[0]=lacquer
   # Reduce deep rectangular frame profiles, anchoring their upper surface.
   if o.name.startswith(('Caisson | deep','Ceiling | lacquer coffer rim')):
    points=[o.matrix_world@v.co for v in o.data.vertices];hi=max(p.z for p in points);inverse=o.matrix_world.inverted();center=sum(points,Vector())/len(points);widths=[max(p[k] for p in points)-min(p[k] for p in points) for k in [0,1]];axis=0 if widths[0]<widths[1] else 1
    for v in o.data.vertices:
     q=o.matrix_world@v.co;q.z=hi+(q.z-hi)*.5;q[axis]=center[axis]+(q[axis]-center[axis])*.67;v.co=inverse@q
  for mod in o.modifiers:
   if mod.type=='BEVEL':mod.segments=5;mod.width=min(mod.width,.004)
  o['fine_caisson']=True
 stand=next((o for o in bpy.data.objects if o.get('wooden_fish') and o.name.startswith('Muyu | stand top')),None)
 if stand:
  center=sum((stand.matrix_world@v.co for v in stand.data.vertices),Vector())/len(stand.data.vertices);delta=Vector((-.95,6.45,1.594))-center
  for o in bpy.data.objects:
   if o.get('wooden_fish'):o.location+=delta
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));reports.append({'file':filename,'parts':len(parts),'bracketClusters':len(clusters),'tangentialWidthScale':.62,'frameDepthScale':.5})
 if filename=='庄严内殿.blend':
  # Only original ceiling parts: seated gold foliage stays a separate exact asset.
  bpy.ops.object.select_all(action='DESELECT')
  for o in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH')
  batches={}
  for o in bpy.context.selected_objects:
   if o.type=='MESH':batches.setdefault(o.data.materials[0],[]).append(o)
  for mat,group in batches.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in group:o.select_set(True)
   bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name='Fine caisson | '+mat.name;o['sourceMaterial']=mat.name
  bpy.ops.object.select_all(action='DESELECT')
  for o in bpy.data.objects:
   if o.name.startswith('Fine caisson |'):o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(A/'fine-caisson.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'evidence/fine-caisson-native.json').write_text(json.dumps(reports,indent=2));print('FINE_CAISSON',reports,flush=True)
