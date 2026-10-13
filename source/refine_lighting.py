"""Apply photographic rosewood and HDR lighting, preserving all sculpted geometry."""
import bpy,json,struct,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
wood=bpy.data.materials.get('Polished ebony cedar')
for node in wood.node_tree.nodes:
 if node.type=='TEX_IMAGE':
  previous=Path(node.image.filepath).name
  suffix='-normal' if 'normal' in previous else '-rough' if 'rough' in previous else ''
  node.image=bpy.data.images.load(str(A/f'pbr-rosewood{suffix}.jpg'),check_existing=True)
  if suffix:node.image.colorspace_settings.name='Non-Color'
 if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.26
p=wood.node_tree.nodes.get('Principled BSDF');stain=wood.node_tree.nodes.get('Restored walnut stain') or wood.node_tree.nodes.new('ShaderNodeMixRGB');stain.name='Restored walnut stain';stain.blend_type='MULTIPLY';stain.inputs[0].default_value=1;stain.inputs[2].default_value=(.3419,.2159,.1301,1);diffuse=next(n for n in wood.node_tree.nodes if n.type=='TEX_IMAGE' and Path(n.image.filepath).name=='pbr-rosewood.jpg');wood.node_tree.links.new(diffuse.outputs['Color'],stain.inputs[1]);wood.node_tree.links.new(stain.outputs[0],p.inputs['Base Color']);p.inputs['Coat Weight'].default_value=.22;p.inputs['Coat Roughness'].default_value=.32
red=bpy.data.materials.get('Restored burgundy lacquer');p=red.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.4;p.inputs['Coat Roughness'].default_value=.32
world=bpy.context.scene.world;world.use_nodes=True;nodes=world.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputWorld');background=nodes.new('ShaderNodeBackground');background.inputs['Strength'].default_value=.6;texture=nodes.new('ShaderNodeTexEnvironment');texture.image=bpy.data.images.load(str(A/'autumn-forest.hdr'),check_existing=True);mapping=nodes.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=.7;coords=nodes.new('ShaderNodeTexCoord');links=world.node_tree.links;links.new(coords.outputs['Generated'],mapping.inputs['Vector']);links.new(mapping.outputs['Vector'],texture.inputs['Vector']);links.new(texture.outputs['Color'],background.inputs['Color']);links.new(background.outputs['Background'],out.inputs['Surface'])
for o in bpy.data.objects:
 if o.type=='LIGHT' and o.data.type=='SUN':
  o.data.energy=2.8;o.data.angle=.08;o.rotation_euler=Vector((15,10,-24)).to_track_quat('-Z','Y').to_euler()
# Re-export only the architecture batches already in the shipped architecture file.
raw=(A/'temple.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];document=json.loads(raw[20:20+size]);names={m['name'] for m in document['meshes']}
bpy.ops.object.select_all(action='DESELECT')
selected=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.data.name in names:o.select_set(True);selected.append(o)
assert len(selected)==len(names),(len(selected),len(names))
bpy.ops.export_scene.gltf(filepath=str(A/'temple.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_image_format='JPEG',export_image_quality=90)
# Preserve the stain in portable glTF as well; the exporter does not retain this MixRGB factor.
raw=(A/'temple.glb').read_bytes();json_size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+json_size]);remainder=raw[20+json_size:]
for material in doc['materials']:
 if material['name']=='Polished ebony cedar':material['pbrMetallicRoughness']['baseColorFactor']=[.3419,.2159,.1301,1]
chunk=json.dumps(doc,separators=(',',':')).encode();chunk+=b' '*((-len(chunk))%4)
(A/'temple.glb').write_bytes(b'glTF'+struct.pack('<II',2,20+len(chunk)+len(remainder))+struct.pack('<II',len(chunk),0x4e4f534a)+chunk+remainder)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
print('Updated photographic finishes and native lighting; preserved',len(selected),'architecture batches.',flush=True)
