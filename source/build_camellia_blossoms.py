"""Editable, layered camellia blooms replacing the sixty legacy flower clusters."""
import bpy,math,json,shutil,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix,Euler
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';full=R/'source/听秋寺院.blend'
backup=full.with_name('听秋寺院-before-camellia-blossoms.blend')
if not backup.exists():shutil.copy2(full,backup)
bpy.ops.wm.read_factory_settings(use_empty=True)
parts=[]
def make(name,vs,fs,colors,rough):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
 for p in mesh.polygons:p.use_smooth=True
 color=mesh.color_attributes.new(name='Pigment',type='FLOAT_COLOR',domain='POINT');color.data.foreach_set('color',np.asarray(colors,dtype=np.float32).ravel())
 mat=bpy.data.materials.new(name);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
 c=mat.node_tree.nodes.new('ShaderNodeVertexColor');c.layer_name='Pigment';mat.node_tree.links.new(c.outputs['Color'],p.inputs['Base Color']);mat.use_backface_culling=False
 mesh.materials.append(mat);o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);parts.append(o);return o
vs=[];fs=[];colors=[]
for layer in range(2):
 for petal in range(6):
  angle=petal*math.tau/6+layer*.51;length=.049 if layer==0 else .035;span=.024 if layer==0 else .020;rings=[]
  for j in range(13):
   t=j/12;ring=[]
   for k in ([5] if j in [0,12] else range(11)):
    s=(k-5)/5;width=span*math.sin(math.pi*t)**.48*(.8+.2*t)
    r=.010+length*t;x=r*math.cos(angle)-s*width*math.sin(angle);y=r*math.sin(angle)+s*width*math.cos(angle)
    z=.006+layer*.007+.015*t*t-.006*math.sin(math.pi*t)+.006*s*s*math.sin(math.pi*t)+.0016*t*t*math.sin(petal*1.7+s*3)
    z+=.00015*math.cos(s*math.pi*7)*math.sin(math.pi*t)
    ring.append(len(vs));vs.append((x,y,z));colors.append((.72+.20*t,.62+.29*t,.43+.42*t,1))
   rings.append(ring)
  for a,b in zip(rings,rings[1:]):
   if len(a)==1:
    for k in range(10):fs.append((a[0],b[k],b[k+1]))
   elif len(b)==1:
    for k in range(10):fs.append((a[k],b[0],a[k+1]))
   else:
    for k in range(10):fs.extend([(a[k],b[k],b[k+1]),(a[k],b[k+1],a[k+1])])
make('Camellia | layered ivory petals',vs,fs,colors,.52)
vs=[];fs=[];colors=[]
def tube(a,b,r1,r2,color,n=7):
 a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');start=len(vs)
 for p,r in [(a,r1),(b,r2)]:
  for k in range(n):vs.append(tuple(p+q@Vector((r*math.cos(k*math.tau/n),r*math.sin(k*math.tau/n),0))));colors.append(color)
 for k in range(n):fs.append((start+k,start+(k+1)%n,start+n+(k+1)%n,start+n+k))
 fs.append(tuple(start+k for k in reversed(range(n))));fs.append(tuple(start+n+k for k in range(n)))
for i in range(38):
 angle=i*2.39996;r=.009*math.sqrt((i+.5)/38);a=(r*.65*math.cos(angle),r*.65*math.sin(angle),.003);b=(r*math.cos(angle),r*math.sin(angle),.021+.004*math.sin(i*1.4))
 tube(a,b,.00065,.00042,(.75,.47,.08,1),6)
 # Small closed anthers, tapered toward the filament rather than floating beads.
 tube((b[0],b[1],b[2]-.0012),b,.0005,.0013,(.85,.43,.035,1),7)
 tube(b,(b[0],b[1],b[2]+.0015),.0013,.0003,(.96,.65,.07,1),7)
make('Camellia | golden stamen cluster',vs,fs,colors,.68)
vs=[];fs=[];colors=[]
tube((0,0,-.035),(0,0,.004),.002,.004,(.07,.115,.021,1),8)
for i in range(5):
 a=i*math.tau/5;off=len(vs)
 for r,s,z in [(0,0,-.006),(.019,-.008,-.002),(.033,0,.004),(.019,.008,-.002),(.017,0,-.006)]:
  vs.append((r*math.cos(a)-s*math.sin(a),r*math.sin(a)+s*math.cos(a),z));colors.append((.12,.20,.033,1))
 fs.extend([(off,off+1,off+4),(off+1,off+2,off+4),(off+2,off+3,off+4),(off+3,off,off+4)])
make('Camellia | calyx and pedicel',vs,fs,colors,.78)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'camellia-blossoms.glb'),export_format='GLB',use_selection=True,export_yup=True,export_vertex_color='ACTIVE',export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
data=np.frombuffer((A/'camellia-instances.bin').read_bytes(),dtype='<f4').reshape(12,950,19);placements=[]
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));Ci=C.inverted()
for group in range(12):
 for j in range(0,950,210):
  row=data[group,j];position=Vector((float(row[12]),-float(row[14]),float(row[13])+.021));angle=group*1.33+j*.032
  m=Euler((.12*math.sin(angle),.12*math.cos(angle),angle)).to_matrix().to_4x4();m.translation=position;world=C@m@Ci;placements.append([world[r][c] for c in range(4) for r in range(4)])
  for prototype in parts:
   o=prototype.copy();o.data=prototype.data;bpy.context.collection.objects.link(o);o.matrix_world=m;o.name=f'Camellia flower {group:02d}-{j:03d} | '+prototype.name;o['camellia_blossom']=True
for o in parts:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/池岸山茶花.blend'))
bpy.ops.wm.open_mainfile(filepath=str(full))
legacy=[o for o in bpy.data.objects if o.type=='MESH' and any(m and m.name=='Ivory camellia petals' for m in o.data.materials)]
def signature(o):
 h=hashlib.sha256(np.asarray(o.matrix_world).tobytes())
 if o.type=='MESH':
  for coll,prop,width,dtype in [(o.data.vertices,'co',3,np.float32),(o.data.loops,'vertex_index',1,np.int32)]:
   v=np.empty(len(coll)*width,dtype=dtype);coll.foreach_get(prop,v);h.update(v.tobytes())
  for uv in o.data.uv_layers:
   v=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',v);h.update(v.tobytes())
  h.update(str([m.name if m else None for m in o.data.materials]).encode())
 return h.hexdigest()
protected={o.name:signature(o) for o in bpy.data.objects if o not in legacy and not o.get('camellia_blossom')};old_triangles=0
for o in legacy:o.data.calc_loop_triangles();old_triangles+=len(o.data.loop_triangles)
if not legacy:old_triangles=json.loads((A/'camellia-blossoms.json').read_text())['legacyTriangles']
for o in list(bpy.data.objects):
 if o in legacy or o.get('camellia_blossom'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(R/'source/池岸山茶花.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:bpy.context.collection.objects.link(o)
assert protected=={name:signature(bpy.data.objects[name]) for name in protected}
bpy.ops.wm.save_as_mainfile(filepath=str(full));bpy.ops.wm.open_mainfile(filepath=str(full));assert protected=={name:signature(bpy.data.objects[name]) for name in protected}
meta={'blooms':60,'petalsPerBloom':12,'stamensPerBloom':38,'legacyTriangles':old_triangles,'matrices':placements};(A/'camellia-blossoms.json').write_text(json.dumps(meta,separators=(',',':')))
report={'blooms':60,'nativeMeshes':len(dst.objects),'protectedObjects':len(protected),'legacyTriangles':old_triangles,'glbBytes':(A/'camellia-blossoms.glb').stat().st_size};(R/'evidence/camellia-blossoms-native.json').write_text(json.dumps(report,indent=2));print('BLOSSOMS VERIFIED',report,flush=True)
