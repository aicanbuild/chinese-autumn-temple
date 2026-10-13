"""Editable Blender counterpart of the six exact runtime fallen-leaf meshes."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';data=json.loads((R/'source/leaf-specimens.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials=[]
for kind in ['maple','ginkgo']:
 m=bpy.data.materials.new(kind+' | dry botanical leaf');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.76;m.surface_render_method='DITHERED'
 for suffix in ['', '-normal','-surface']:
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/(kind+'-leaf'+suffix+'.png')),check_existing=True)
  if suffix:t.image.colorspace_settings.name='Non-Color'
  if not suffix:l.new(t.outputs['Color'],p.inputs['Base Color']);l.new(t.outputs['Alpha'],p.inputs['Alpha'])
  elif suffix=='-normal':
   normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.38;l.new(t.outputs[0],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs['Normal'])
  else:
   channels=n.new('ShaderNodeSeparateColor');l.new(t.outputs[0],channels.inputs[0]);l.new(channels.outputs['Green'],p.inputs['Roughness'])
 materials.append(m)
for i,s in enumerate(data['shapes']):
 vs=[s['positions'][k:k+3] for k in range(0,len(s['positions']),3)];faces=[s['indices'][k:k+3] for k in range(0,len(s['indices']),3)];g=bpy.data.meshes.new('Curled leaf');g.from_pydata(vs,[],faces);g.update();uv=g.uv_layers.new()
 for face in g.polygons:
  face.use_smooth=True
  for li in face.loop_indices:k=g.loops[li].vertex_index;uv.data[li].uv=s['uv'][k*2:k*2+2]
 g.normals_split_custom_set_from_vertices([s['normals'][k:k+3] for k in range(0,len(s['normals']),3)])
 o=bpy.data.objects.new(('Maple' if s['species']==0 else 'Ginkgo')+' curl '+str(s['variant']),g);bpy.context.collection.objects.link(o);g.materials.append(materials[s['species']]);o.scale=(data['scaleMeters'],)*3;o.location=((s['variant']-1)*.25,(s['species']-.5)*.25,0);o['runtime_batch']=i
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=1.3;area.spaces.active.region_3d.view_location=(0,0,0)
bpy.context.scene.world.color=(.25,.25,.25);bpy.ops.file.pack_all();path=R/'source/落叶标本.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
for o in bpy.data.objects:
 s=data['shapes'][o['runtime_batch']];assert len(o.data.vertices)*3==len(s['positions']);assert len(o.data.polygons)*3==len(s['indices'])
 for i,v in enumerate(o.data.vertices):assert all(abs(v.co[j]-s['positions'][i*3+j])<1e-8 for j in range(3))
 assert min(v.co.z for v in o.data.vertices)==0
 assert o.data.has_custom_normals
 for loop in o.data.loops:
  expected=s['normals'][loop.vertex_index*3:loop.vertex_index*3+3]
  assert sum(o.data.corner_normals[loop.index].vector[j]*expected[j] for j in range(3))>.99999
report={'editableLeafSpecimens':6,'runtimeGeometryMatched':True,'runtimeNormalsMatched':True,'triangles':[len(s['indices'])//3 for s in data['shapes']],'scaleMeters':data['scaleMeters'],'packedImages':len([i for i in bpy.data.images if i.packed_file])};(R/'evidence/leaf-specimens-native.json').write_text(json.dumps(report,indent=2));print(report)
