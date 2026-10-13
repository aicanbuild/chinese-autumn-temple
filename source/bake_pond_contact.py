"""Bake finite-distance ambient visibility from authored pond geometry only."""
import bpy,bmesh,json,sys,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';started=time.time()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
source=R/'source/听秋寺院.blend'
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
 names=[n for n in src.objects if n=='Riverbed sediment' or n.startswith('Pond bed stone ') or n.startswith('Pier timber') or n.startswith('Pond lotus | fine emergent stalk')]
 dst.objects=names
objects=list(dst.objects)
for o in objects:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update()
bed=next(o for o in objects if o.name=='Riverbed sediment');stones=[o for o in objects if o.get('pond_zone')=='bed'];piers=[o for o in objects if o.name.startswith('Pier timber')]
expected=sum(p[8]=='bed' for p in json.loads((A/'pond-stones.json').read_text())['placements']);assert len(stones)==expected,len(stones)
print('CONTACT SOURCES',{'objects':len(objects),'stones':len(stones),'piers':len(piers)},flush=True)
# A separate bake document leaves the original scene and authored UVs untouched.
bed.data=bed.data.copy();bm=bmesh.new();bm.from_mesh(bed.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.normal.z<.5 or f.calc_center_median().z< -1.75],context='FACES');bm.to_mesh(bed.data);bm.free()
for uv in list(bed.data.uv_layers):bed.data.uv_layers.remove(uv)
uv=bed.data.uv_layers.new(name='Pond contact atlas')
for loop in bed.data.loops:
 p=bed.matrix_world@bed.data.vertices[loop.vertex_index].co
 uv.data[loop.index].uv=((p.x+11.5)/23,(p.y+12.7)/13.8)
opaque=bpy.data.materials.new('Contact | opaque occluders');opaque.use_nodes=True
for o in objects:o.data.materials.clear();o.data.materials.append(opaque)
mat=bpy.data.materials.new('Contact | hemisphere visibility');mat.use_nodes=True;mat.node_tree.nodes.clear();n=mat.node_tree.nodes;l=mat.node_tree.links
ao=n.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.45;ao.samples=64;ao.only_local=False
emission=n.new('ShaderNodeEmission');output=n.new('ShaderNodeOutputMaterial');l.new(ao.outputs['AO'],emission.inputs['Color']);l.new(emission.outputs[0],output.inputs['Surface'])
image=bpy.data.images.new('Pond sediment contact visibility',width=2560,height=1536,alpha=False,float_buffer=False,is_data=True);image.generated_color=(1,1,1,1);image.colorspace_settings.name='Non-Color'
target=n.new('ShaderNodeTexImage');target.image=image;n.active=target;bed.data.materials.clear();bed.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.bake.margin=8;scene.render.bake.use_clear=False
bpy.ops.object.select_all(action='DESELECT');bed.select_set(True);bpy.context.view_layer.objects.active=bed
print('CONTACT BAKE START',flush=True);bpy.ops.object.bake(type='EMIT',use_clear=False,margin=8)
image.filepath_raw=str(A/'pond-contact-ao.png');image.file_format='PNG';image.save();image.pack()
for image_unused in list(bpy.data.images):
 if image_unused.users==0:bpy.data.images.remove(image_unused)
for material_unused in list(bpy.data.materials):
 if material_unused.users==0:bpy.data.materials.remove(material_unused)
scene['contact_distance_m']=.45;scene['contact_atlas_bounds_native']=[-11.5,11.5,-12.7,1.1]
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/池底接触光照.blend'))
report={'source':source.name,'stones':len(stones),'piers':len(piers),'width':2560,'height':1536,'distance':.45,'cyclesSamples':32,'aoSamples':64,'bounds':[-11.5,11.5,-12.7,1.1],'seconds':time.time()-started,'bytes':(A/'pond-contact-ao.png').stat().st_size,'sha256':hashlib.sha256((A/'pond-contact-ao.png').read_bytes()).hexdigest()}
(R/'evidence/pond-contact-bake.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('CONTACT BAKED',report,flush=True)
