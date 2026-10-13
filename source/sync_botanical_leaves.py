"""Preserve the assembled temple while updating leaf surfaces and folded canopies."""
import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';path=R/'source/听秋寺院.blend'
backup=path.with_name('听秋寺院-叶片更新前.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path))
canopies=[o for o in bpy.data.objects if o.name.startswith('Specimen leaf canopy ')]
assert len(canopies)==3
protected={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in bpy.data.objects if o.type=='MESH' and o not in canopies}
files={f'{k}-{v}.png':A/f'{k}-{v}.png' for k in ['maple','ginkgo','green'] for v in ['leaf','spray']}
for image in list(bpy.data.images):
 name=Path(bpy.path.abspath(image.filepath)).name
 if name in files:
  new=bpy.data.images.load(str(files[name]),check_existing=False);new.pack();image.user_remap(new)
materials=[]
for material in list(bpy.data.materials):
 if not material.use_nodes:continue
 nodes=material.node_tree.nodes;links=material.node_tree.links
 textures=[n for n in nodes if n.type=='TEX_IMAGE' and n.image and Path(bpy.path.abspath(n.image.filepath)).name in [k+'-leaf.png' for k in ['maple','ginkgo','green']]]
 if not textures:continue
 albedo=textures[0];kind=Path(albedo.image.filepath).name.split('-')[0];principled=nodes.get('Principled BSDF');output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
 for n in list(nodes):
  if n.label=='Botanical surface':nodes.remove(n)
 def node(type):
  n=nodes.new(type);n.label='Botanical surface';return n
 def texture(suffix):
  n=node('ShaderNodeTexImage');n.image=bpy.data.images.load(str(A/f'{kind}-leaf-{suffix}.png'),check_existing=True);n.image.colorspace_settings.name='Non-Color';n.image.pack();return n
 normal=texture('normal');surface=texture('surface');normal_map=node('ShaderNodeNormalMap');normal_map.inputs['Strength'].default_value=.38;links.new(normal.outputs['Color'],normal_map.inputs['Color']);links.new(normal_map.outputs[0],principled.inputs['Normal'])
 channels=node('ShaderNodeSeparateColor');links.new(surface.outputs['Color'],channels.inputs[0]);links.new(channels.outputs['Green'],principled.inputs['Roughness'])
 translucent=node('ShaderNodeBsdfTranslucent');links.new(albedo.outputs['Color'],translucent.inputs['Color']);links.new(normal_map.outputs[0],translucent.inputs['Normal'])
 weight=node('ShaderNodeMath');weight.operation='MULTIPLY';weight.inputs[1].default_value=.24;links.new(channels.outputs['Red'],weight.inputs[0])
 scatter=node('ShaderNodeMixShader');links.new(weight.outputs[0],scatter.inputs[0]);links.new(principled.outputs[0],scatter.inputs[1]);links.new(translucent.outputs[0],scatter.inputs[2])
 for link in list(principled.inputs['Alpha'].links):links.remove(link)
 principled.inputs['Alpha'].default_value=1
 transparent=node('ShaderNodeBsdfTransparent');cutout=node('ShaderNodeMixShader');links.new(albedo.outputs['Alpha'],cutout.inputs[0]);links.new(transparent.outputs[0],cutout.inputs[1]);links.new(scatter.outputs[0],cutout.inputs[2]);links.new(cutout.outputs[0],output.inputs['Surface'])
 material.surface_render_method='DITHERED';materials.append(material.name)
folded=0
for o in canopies:
 if o.get('botanical_fold_version')==1:continue
 original=o.data;vertices=[tuple(v.co) for v in original.vertices];faces=[];uvs=[];layer=original.uv_layers.active
 for poly in original.polygons:
  assert len(poly.vertices)==4
  ids=list(poly.vertices);coords=[original.vertices[i].co for i in ids];size=(coords[1]-coords[0]).length
  center=sum(coords,Vector())/4+poly.normal*size*.10;center_id=len(vertices);vertices.append(tuple(center))
  corner_uv=[tuple(layer.data[li].uv) for li in poly.loop_indices]
  for i in range(4):faces.append((ids[i],ids[(i+1)%4],center_id));uvs.extend([corner_uv[i],corner_uv[(i+1)%4],(.5,.5)])
  folded+=1
 mesh=bpy.data.meshes.new(original.name+' folded');mesh.from_pydata(vertices,[],faces);mesh.update();uv=mesh.uv_layers.new()
 for i,value in enumerate(uvs):uv.data[i].uv=value
 for face in mesh.polygons:face.use_smooth=True
 for material in original.materials:mesh.materials.append(material)
 o.data=mesh;o['botanical_fold_version']=1
assert protected=={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in bpy.data.objects if o.type=='MESH' and o not in canopies}
assert len(bpy.data.objects)==4172
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path))
report={'foldedLeaves':folded,'updatedMaterials':materials,'preservedOtherMeshes':len(protected),'objects':len(bpy.data.objects)}
(R/'evidence/botanical-native-verification.json').write_text(json.dumps(report,indent=2));print(report)
