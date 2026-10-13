"""Bake finite-distance floor contact from the editable, furnished temple."""
import bpy,json,time,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';started=time.time()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
source=R/'source/听秋寺院.blend'
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update()
x0,x1,y0,y1=-6.1275,6.1175,3.475,10.725
floor_z=1.0702;distance=1.0
low=Vector((x0-distance,y0-distance,floor_z));high=Vector((x1+distance,y1+distance,floor_z+distance))
def intersects(points):return all(max(p[k] for p in points)>=low[k] and min(p[k] for p in points)<=high[k] for k in range(3))
vertices=[];faces=[];sources=[];depsgraph=bpy.context.evaluated_depsgraph_get()
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or o.get('sanctuary_floor') or (o.get('wooden_fish') and o.get('assembly')!='stand') or not intersects([o.matrix_world@Vector(c) for c in o.bound_box]):continue
 evaluated=o.evaluated_get(depsgraph);mesh=evaluated.to_mesh();world=[o.matrix_world@v.co for v in mesh.vertices];selected=[tuple(p.vertices) for p in mesh.polygons if intersects([world[i] for i in p.vertices])]
 if selected:
  used=sorted({i for f in selected for i in f});lookup={i:len(vertices)+j for j,i in enumerate(used)};vertices.extend(world[i] for i in used);faces.extend(tuple(lookup[i] for i in f) for f in selected);sources.append({'name':o.name,'faces':len(selected)})
 evaluated.to_mesh_clear()
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
mesh=bpy.data.meshes.new('Actual floor-near temple surfaces');mesh.from_pydata(vertices,[],faces);mesh.update();occluders=bpy.data.objects.new('Hall contact occluders',mesh);bpy.context.collection.objects.link(occluders)
opaque=bpy.data.materials.new('Hall contact | opaque occluders');opaque.use_nodes=True;mesh.materials.append(opaque)
# A horizontal receiver 0.2 mm above the authored 1.07 m stone top avoids
# self-intersection. It covers the 8 mm recessed joints with the same atlas;
# it intentionally measures furniture/wall contact, not micro-bevel occlusion.
mesh=bpy.data.meshes.new('Floor contact receiver');mesh.from_pydata([(x0,y0,floor_z),(x1,y0,floor_z),(x1,y1,floor_z),(x0,y1,floor_z)],[],[(0,1,2,3)]);mesh.update();receiver=bpy.data.objects.new('Hall floor contact receiver',mesh);bpy.context.collection.objects.link(receiver)
uv=mesh.uv_layers.new(name='Hall floor contact atlas')
for loop in mesh.loops:
 p=mesh.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((p.x-x0)/(x1-x0),(p.y-y0)/(y1-y0))
mat=bpy.data.materials.new('Hall contact | hemisphere visibility');mat.use_nodes=True;mat.node_tree.nodes.clear();n=mat.node_tree.nodes;l=mat.node_tree.links
ao=n.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=distance;ao.samples=64
emission=n.new('ShaderNodeEmission');output=n.new('ShaderNodeOutputMaterial');l.new(ao.outputs['AO'],emission.inputs['Color']);l.new(emission.outputs[0],output.inputs['Surface'])
image=bpy.data.images.new('Hall floor contact visibility',width=1536,height=1024,alpha=False,float_buffer=False,is_data=True);image.generated_color=(1,1,1,1);image.colorspace_settings.name='Non-Color';target=n.new('ShaderNodeTexImage');target.image=image;n.active=target;mesh.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.bake.use_clear=False
bpy.ops.object.select_all(action='DESELECT');receiver.select_set(True);bpy.context.view_layer.objects.active=receiver
print('HALL CONTACT BAKE START',{'objects':len(sources),'faces':len(faces),'vertices':len(vertices)},flush=True)
bpy.ops.object.bake(type='EMIT',use_clear=False,margin=8)
image.filepath_raw=str(A/'hall-contact-ao.png');image.file_format='PNG';image.save();image.pack()
for block in list(bpy.data.images):
 if block.users==0:bpy.data.images.remove(block)
for block in list(bpy.data.materials):
 if block.users==0:bpy.data.materials.remove(block)
for block in list(bpy.data.meshes):
 if block.users==0:bpy.data.meshes.remove(block)
scene['contact_distance_m']=distance;scene['contact_bounds_native']=[x0,x1,y0,y1];scene['contact_receiver_height']=floor_z
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/殿内地面接触光照.blend'))
report={'source':source.name,'occluders':sources,'faces':len(faces),'width':1536,'height':1024,'distance':distance,'receiverHeight':floor_z,'nativeBounds':[x0,x1,y0,y1],'cyclesSamples':16,'aoSamples':64,'seconds':time.time()-started,'bytes':(A/'hall-contact-ao.png').stat().st_size}
(R/'evidence/hall-contact-bake.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('HALL CONTACT BAKED', {k:v for k,v in report.items() if k!='occluders'},flush=True)
