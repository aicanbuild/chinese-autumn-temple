"""Bake short-range wall-frame contact from the actual editable sanctuary.

The paintings remain unchanged. Four inward-facing receivers share a padded
atlas; their normals are explicit because the original paint is double-sided.
"""
import bpy,json,time,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';started=time.time()
source=R/'source/听秋寺院.blend';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.context.view_layer.update()
distance=.16;epsilon=.0002;width,height=2048,1024
panels=[]
for i,(center,u,size,normal) in enumerate([
 ((-3.43,10.139,2.83),(1,0,0),(3.10,1.99),(0,-1,0)),
 ((3.43,10.139,2.83),(1,0,0),(3.10,1.99),(0,-1,0)),
 ((-5.30,7.87,2.78),(0,1,0),(4.34,2.18),(1,0,0)),
 ((5.30,7.87,2.78),(0,1,0),(4.34,2.18),(-1,0,0))]):
 col,row=i%2,i//2;panels.append({'center':center,'u':u,'v':(0,0,1),'size':size,'normal':normal,'atlas':[(col*1024+16)/width,(row*512+16)/height,(col*1024+1008)/width,(row*512+496)/height]})
boxes=[]
for p in panels:
 c,u,v=Vector(p['center']),Vector(p['u']),Vector(p['v']);w,h=p['size'];extent=u*w/2+v*h/2
 boxes.append((c-extent-Vector((distance,)*3),c+extent+Vector((distance,)*3)))
def intersects(points):return any(all(max(p[k] for p in points)>=lo[k] and min(p[k] for p in points)<=hi[k] for k in range(3)) for lo,hi in boxes)
vertices=[];faces=[];sources=[];deps=bpy.context.evaluated_depsgraph_get()
for o in list(bpy.context.scene.objects):
 # Native canopy previews are replaced by wind-driven cards on the web. Their
 # transient contact must not become a permanent dark mark on the paintings.
 if o.type!='MESH' or o.name.startswith('Specimen leaf canopy') or 'celestial garden assembly' in o.name or 'continuous lotus paradise' in o.name:continue
 if not intersects([o.matrix_world@Vector(c) for c in o.bound_box]):continue
 evaluated=o.evaluated_get(deps);mesh=evaluated.to_mesh();world=[o.matrix_world@v.co for v in mesh.vertices]
 selected=[tuple(p.vertices) for p in mesh.polygons if intersects([world[i] for i in p.vertices])]
 if selected:
  used=sorted({i for face in selected for i in face});lookup={i:len(vertices)+j for j,i in enumerate(used)}
  vertices.extend(world[i] for i in used);faces.extend(tuple(lookup[i] for i in face) for face in selected);sources.append({'name':o.name,'faces':len(selected)})
 evaluated.to_mesh_clear()
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
mesh=bpy.data.meshes.new('Measured wall-frame surfaces');mesh.from_pydata(vertices,[],faces);mesh.update()
occluders=bpy.data.objects.new('Mural contact occluders',mesh);bpy.context.collection.objects.link(occluders)
opaque=bpy.data.materials.new('Mural contact | opaque surfaces');opaque.use_nodes=True;mesh.materials.append(opaque)
receiver_vertices=[];receiver_faces=[]
for p in panels:
 c=Vector(p['center'])+Vector(p['normal'])*epsilon;u,v=Vector(p['u']),Vector(p['v']);w,h=p['size'];offset=len(receiver_vertices)
 receiver_vertices.extend(c+u*s*w/2+v*t*h/2 for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)])
 order=(0,1,2,3) if u.cross(v).dot(Vector(p['normal']))>0 else (3,2,1,0)
 receiver_faces.append(tuple(offset+i for i in order))
mesh=bpy.data.meshes.new('Four inward-facing mural receivers');mesh.from_pydata(receiver_vertices,[],receiver_faces);mesh.update()
receiver=bpy.data.objects.new('Mural contact receivers',mesh);bpy.context.collection.objects.link(receiver)
uv=mesh.uv_layers.new(name='Mural contact atlas')
for face,p in zip(mesh.polygons,panels):
 c,u,v=Vector(p['center']),Vector(p['u']),Vector(p['v']);w,h=p['size'];x0,y0,x1,y1=p['atlas']
 assert face.normal.dot(Vector(p['normal']))>.999
 for index in face.loop_indices:
  q=mesh.vertices[mesh.loops[index].vertex_index].co-c;uv.data[index].uv=(x0+(q.dot(u)/w+.5)*(x1-x0),y0+(q.dot(v)/h+.5)*(y1-y0))
mat=bpy.data.materials.new('Mural contact | hemisphere visibility');mat.use_nodes=True;mat.node_tree.nodes.clear();n=mat.node_tree.nodes;l=mat.node_tree.links
ao=n.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=distance;ao.samples=64
emission=n.new('ShaderNodeEmission');output=n.new('ShaderNodeOutputMaterial');l.new(ao.outputs['AO'],emission.inputs['Color']);l.new(emission.outputs[0],output.inputs['Surface'])
image=bpy.data.images.new('Mural frame contact visibility',width=width,height=height,alpha=False,is_data=True);image.generated_color=(1,1,1,1);image.colorspace_settings.name='Non-Color'
target=n.new('ShaderNodeTexImage');target.image=image;n.active=target;mesh.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False
bpy.ops.object.select_all(action='DESELECT');receiver.select_set(True);bpy.context.view_layer.objects.active=receiver
print('MURAL CONTACT BAKE START',{'objects':len(sources),'faces':len(faces)},flush=True)
bpy.ops.object.bake(type='EMIT',use_clear=False,margin=8)
image.filepath_raw=str(A/'mural-contact-ao.png');image.file_format='PNG';image.save();image.pack()
for blocks in [bpy.data.materials,bpy.data.images,bpy.data.meshes]:
 for block in list(blocks):
  if block.users==0:blocks.remove(block)
scene['contact_distance_m']=distance;scene['mural_panels_json']=json.dumps(panels);scene['receiver_epsilon']=epsilon
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/壁画嵌框接触光照.blend'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report={'source':source.name,'sourceSha256':source_hash,'sourceUnchanged':True,'occluders':sources,'faces':len(faces),'panels':panels,'width':width,'height':height,'distance':distance,'epsilon':epsilon,'cyclesSamples':16,'aoSamples':64,'bytes':(A/'mural-contact-ao.png').stat().st_size,'seconds':time.time()-started}
(R/'evidence/mural-contact-bake.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('MURAL CONTACT BAKE COMPLETE',{'faces':len(faces),'seconds':report['seconds'],'bytes':report['bytes']},flush=True)
