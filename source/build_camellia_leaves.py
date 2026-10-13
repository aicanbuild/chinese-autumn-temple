"""Replace only the twelve legacy low shrub leaf fields with curved leaf surfaces.
Native Z-up geometry and Y-up instance matrices share the same prototype.
"""
import bpy,bmesh,math,json,shutil,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';file=R/'source/听秋寺院.blend';backup=file.with_name('听秋寺院-before-camellia-leaves.blend')
if not backup.exists():shutil.copy2(file,backup)
bpy.ops.wm.open_mainfile(filepath=str(file))
centers=[(-10,1.4),(10.8,1.2),(-11.7,-1.9),(11.8,-1.8),(-12.4,-8),(12.3,-8.3),(-8.4,-11.8),(8.4,-11.7),(-6.8,11.8),(6.8,11.8),(-14,4.6),(14,4.8)]
legacy=next(o for o in bpy.data.objects if o.type=='MESH' and any(m and m.name=='Clipped garden foliage' for m in o.data.materials))
def signature(o):
 h=hashlib.sha256(np.asarray(o.matrix_world).tobytes())
 if o.type=='MESH':
  for coll,prop,width,dtype in [(o.data.vertices,'co',3,np.float32),(o.data.loops,'vertex_index',1,np.int32),(o.data.polygons,'loop_total',1,np.int32)]:
   v=np.empty(len(coll)*width,dtype=dtype);coll.foreach_get(prop,v);h.update(v.tobytes())
  for uv in o.data.uv_layers:
   v=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',v);h.update(v.tobytes())
  h.update(str([m.name if m else None for m in o.data.materials]).encode())
 return h.hexdigest()
protected={o.name:signature(o) for o in bpy.data.objects if o!=legacy and not o.get('camellia_leaves')}
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));Ci=C.inverted()
selected=[p for p in legacy.data.polygons if max((legacy.matrix_world@legacy.data.vertices[i].co).z for i in p.vertices)<1.35]
rows=[[] for _ in centers]
if selected:
 assert len(selected)==11400,len(selected)
 for p in selected:
  assert len(p.vertices)==4
  v=[legacy.matrix_world@legacy.data.vertices[i].co for i in p.vertices];origin=sum(v,Vector())/4;axis=(v[2]-v[0]).normalized();side=v[1]-v[3];side=(side-axis*side.dot(axis)).normalized();normal=side.cross(axis).normalized()
  if normal.z<0:side=-side;normal=-normal
  length=(v[2]-v[0]).length*.82;m=Matrix.Identity(4)
  for col,d in enumerate([side,axis,normal]):
   for k in range(3):m[k][col]=d[k]*length
  m.translation=origin;world=C@m@Ci;idx=min(range(12),key=lambda i:(origin.x-centers[i][0])**2+(origin.y-centers[i][1])**2)
  shade=.78+.20*((len(rows[idx])*37+idx*19)%101)/100;color=[shade*.85,shade,shade*.78]
  rows[idx].append([*[world[r][c] for c in range(4) for r in range(4)],*color])
 assert all(len(r)==950 for r in rows),[len(r) for r in rows]
 data=np.asarray(rows,dtype='<f4');(A/'camellia-instances.bin').write_bytes(data.tobytes())
 # Keep bamboo polygons and their original UVs unchanged.
 keep=[p for p in legacy.data.polygons if p not in selected];before_keep=[tuple(tuple(legacy.data.vertices[i].co) for i in p.vertices) for p in keep]
 bm=bmesh.new();bm.from_mesh(legacy.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[p.index] for p in selected],context='FACES');bm.to_mesh(legacy.data);bm.free();legacy.data.update()
 after_keep=[tuple(tuple(legacy.data.vertices[i].co) for i in p.vertices) for p in legacy.data.polygons];assert before_keep==after_keep
 legacy['camellia_leaves_removed']=11400
else:
 assert legacy.get('camellia_leaves_removed')==11400
 data=np.frombuffer((A/'camellia-instances.bin').read_bytes(),dtype='<f4').reshape(12,950,19)
# A continuous midrib and cupped wings; no opacity card around the silhouette.
verts=[];uvs=[];rings=[]
for j in range(9):
 t=j/8;ring=[]
 for s in ([0] if j in [0,8] else [-1,0,1]):
  w=math.sin(math.pi*t)**.8;ring.append(len(verts));verts.append((s*.225*w,t-.5,.06*math.sin(math.pi*t)*(1-.72*abs(s))+.03*(t-.35)**2));uvs.append((.5+s*.265*w,.08+t*.84))
 rings.append(ring)
faces=[]
for a,b in zip(rings,rings[1:]):
 if len(a)==1:faces.extend([(a[0],b[1],b[0]),(a[0],b[2],b[1])])
 elif len(b)==1:faces.extend([(a[0],a[1],b[0]),(a[1],a[2],b[0])])
 else:
  for k in range(2):faces.extend([(a[k],a[k+1],b[k+1]),(a[k],b[k+1],b[k])])
# Ensure the leaf front points above the plant.
if Vector(verts[faces[2][1]]).__sub__(Vector(verts[faces[2][0]])).cross(Vector(verts[faces[2][2]])-Vector(verts[faces[2][0]])).z<0:faces=[tuple(reversed(f)) for f in faces]
proto=bpy.data.meshes.new('Camellia | cupped veined leaf');proto.from_pydata(verts,[],faces);proto.update();uv=proto.uv_layers.new(name='Botanical leaf UV')
for p in proto.polygons:
 p.use_smooth=True
 for li in p.loop_indices:uv.data[li].uv=uvs[proto.loops[li].vertex_index]
source=next(m for m in bpy.data.materials if m.name.startswith('Understory | waxed evergreen leaf'))
material=bpy.data.materials.get('Camellia | waxed living leaf') or source.copy();material.name='Camellia | waxed living leaf';material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.55
for n in material.node_tree.nodes:
 if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.3
native=[];points=np.c_[np.asarray(verts),np.ones(len(verts))];tri=np.asarray(faces)
for group in range(12):
 name=f'Camellia leaves | shrub {group:02d}';o=bpy.data.objects.get(name)
 if not o:o=bpy.data.objects.new(name,bpy.data.meshes.new(name));bpy.context.collection.objects.link(o)
 positions=[];polys=[];colors=[]
 for index,row in enumerate(data[group]):
  m=Ci@Matrix(row[:16].reshape(4,4).T.tolist())@C;positions.extend((points@np.asarray(m).T)[:,:3]);polys.extend((tri+index*len(verts)).tolist());colors.extend([(*row[16:19],1)]*len(verts))
 mesh=bpy.data.meshes.new(name+' | curved leaves');mesh.from_pydata(positions,[],polys);mesh.update();mesh.materials.append(material);layer=mesh.uv_layers.new(name='Botanical leaf UV')
 for p in mesh.polygons:
  p.use_smooth=True
  for li in p.loop_indices:layer.data[li].uv=uvs[mesh.loops[li].vertex_index%len(verts)]
 color=mesh.color_attributes.new(name='Pigment',type='FLOAT_COLOR',domain='POINT');color.data.foreach_set('color',np.asarray(colors,dtype=np.float32).ravel());o.data=mesh;o['camellia_leaves']=True;o['plant_index']=group;native.append(o)
assert protected=={name:signature(bpy.data.objects[name]) for name in protected}
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.wm.open_mainfile(filepath=str(file));assert protected=={name:signature(bpy.data.objects[name]) for name in protected}
# Save a directly editable standalone scene without unrelated temple assets.
scene=bpy.data.scenes.new('池岸山茶');
for o in bpy.data.objects:
 if o.get('camellia_leaves'):scene.collection.objects.link(o)
bpy.data.libraries.write(str(R/'source/池岸山茶.blend'),{scene},path_remap='RELATIVE',fake_user=True)
# Export only the reusable prototype, without duplicating existing leaf textures.
proto=bpy.data.meshes.new('Camellia leaf prototype');proto.from_pydata(verts,[],faces);proto.update();layer=proto.uv_layers.new()
for p in proto.polygons:
 p.use_smooth=True
 for li in p.loop_indices:layer.data[li].uv=uvs[proto.loops[li].vertex_index]
shell=bpy.data.materials.new('Camellia | shared runtime maps');shell.use_nodes=True;proto.materials.append(shell);o=bpy.data.objects.new('Camellia_leaf',proto);bpy.context.scene.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.gltf(filepath=str(A/'camellia-leaf.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
meta={'groups':12,'leavesPerGroup':950,'stride':19,'legacyTriangles':22800,'leafTriangles':len(faces),'roughness':.55,'normalStrength':.3,'matrixConvention':'column-major Y-up','centers':centers};(A/'camellia-leaves.json').write_text(json.dumps(meta,separators=(',',':')))
(R/'evidence/camellia-native.json').write_text(json.dumps({**meta,'protectedObjects':len(protected),'bambooPreserved':True,'nativeObjects':len(bpy.data.objects)-1,'instancesBytes':data.nbytes},indent=2));print('CAMELLIAS COMPLETE',meta,len(protected),flush=True)
