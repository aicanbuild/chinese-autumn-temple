"""CC0 Tang Buddha scan by Daniel Pett, with original digital hand/plinth restoration.
Source: https://zenodo.org/records/10244486 ; Smithsonian F1917.243.
The restoration is an artistic adaptation, not a historical reconstruction.
"""
import bpy, math, json, shutil
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'source/reference-assets/tang-buddha-cc0.glb'))
scan=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in scan:
 o.parent=None;o.matrix_world=Matrix.Identity(4)
 o.data.transform(Matrix.Rotation(-math.pi/2,4,'X'))
vs=[v.co.copy() for o in scan for v in o.data.vertices];low=Vector([min(v[i] for v in vs) for i in range(3)]);high=Vector([max(v[i] for v in vs) for i in range(3)]);center=(low+high)*.5;scale=1.915/(high.z-low.z)
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
gold=material('Tang Buddha | satin restored gilding',(.60,.365,.116),.72,.47)
base=material('Tang Buddha | burnished lotus pedestal',(.39,.205,.066),.78,.40)
for o in scan:
 o.data.transform(Matrix.Diagonal((scale,scale,scale,1))@Matrix.Translation(Vector((-center.x,-center.y,-low.z))))
 o.name='Tang sculpture | scanned face and flowing drapery';o.data.materials.clear();o.data.materials.append(gold)
 for p in o.data.polygons:p.use_smooth=True
# Join photograph reconstruction chunks, merge only coincident boundaries.
bpy.ops.object.select_all(action='DESELECT')
for o in scan:o.select_set(True)
bpy.context.view_layer.objects.active=scan[0];bpy.ops.object.join();body=bpy.context.object
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.remove_doubles(threshold=.000025);bpy.ops.object.mode_set(mode='OBJECT')
# Repair hands with joined organic surfaces; slight relaxed bends avoid stick fingers.
def ellipsoid(name,loc,size,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=loc);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def tube(name,pts,radius):
 verts=[];faces=[]
 for i,p in enumerate(pts):
  tangent=Vector(pts[min(len(pts)-1,i+1)])-Vector(pts[max(0,i-1)]);q=tangent.to_track_quat('Z','Y');r=radius*(1-.32*i/(len(pts)-1))
  for j in range(16):verts.append(Vector(p)+q@Vector((r*math.cos(j*math.tau/16),r*math.sin(j*math.tau/16),0)))
 for i in range(len(pts)-1):
  for j in range(16):a=i*16+j;b=i*16+(j+1)%16;faces.append((a,b,b+16,a+16))
 faces+=[tuple(range(15,-1,-1)),tuple((len(pts)-1)*16+j for j in range(16))]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(gold);return o
for side in [-1,1]:
 # Left in the image gives; right in the image reassures, extending scanned wrists.
 x=side*(.38 if side<0 else .29);y=-.355;z=.94 if side<0 else 1.05;up=1 if side>0 else -1
 parts=[ellipsoid('Restored hand | wrist',(x,y,z),(.047,.050,.07),gold),ellipsoid('Restored hand | palm',(x+side*.015,y-.043,z+up*.057),(.059,.030,.079),gold)]
 for j in range(4):
  fx=x+(j-1.5)*.027;length=[.074,.098,.106,.084][j];startz=z+up*.100
  pts=[(fx+side*.007*t,y-.044-.024*math.sin(t*math.pi*.7),startz+up*length*t) for t in [k/16 for k in range(17)]]
  parts.append(tube('Restored hand | articulated finger',pts,.014))
  parts.append(ellipsoid('Restored hand | fingertip',pts[-1],(.010,.010,.011),gold))
 pts=[(x-side*(.04+.04*t),y-.035-.04*t,z+up*(.025+.055*t)) for t in [k/16 for k in range(17)]];parts.append(tube('Restored hand | thumb',pts,.018));parts.append(ellipsoid('Restored hand | thumb tip',pts[-1],(.012,.012,.012),gold))
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();hand=bpy.context.object;hand.name='Restored giving hand' if side<0 else 'Restored reassurance hand';rem=hand.modifiers.new('Fused sculpted hand','REMESH');rem.mode='VOXEL';rem.voxel_size=.0028;bpy.ops.object.modifier_apply(modifier=rem.name);sm=hand.modifiers.new('Soft knuckles','SMOOTH');sm.factor=.7;sm.iterations=3;bpy.ops.object.modifier_apply(modifier=sm.name)
 for p in hand.data.polygons:p.use_smooth=True
# A restrained new lotus collar covers the incomplete archaeological bottom edge.
for z,rad,depth in [(.10,.58,.19),(.22,.57,.055),(.015,.61,.045)]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=rad,depth=depth,location=(0,0,z));o=bpy.context.object;o.name='Restored lotus | turned plinth';o.scale.y=.76;o.data.materials.append(base);bevel=o.modifiers.new('Rounded metal edges','BEVEL');bevel.width=.012;bevel.segments=3
for j in range(32):
 a=j*math.tau/32;o=ellipsoid('Restored lotus | petal',(math.cos(a)*.56,math.sin(a)*.425,.135),(.047,.03,.09),gold);o.rotation_euler.z=a-math.pi/2
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
for o in objects:o.location+=Vector((0,8.6,1.915));o['altar_sculpture']=True;o['source_license']='CC0-1.0';o['restoration_version']=2
components=len(objects)
prototype=R/'source/主殿佛像.blend'
if prototype.exists() and not (R/'source/主殿佛像-before-scan.blend').exists():shutil.copy2(prototype,R/'source/主殿佛像-before-scan.blend')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(prototype))
# Export detail and lighter distant geometry with shared silhouette placement.
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=body
for o in objects:
 for mod in list(o.modifiers):
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.context.view_layer.objects.active=body;bpy.ops.object.join()
def export(name):
 bpy.ops.export_scene.gltf(filepath=str(A/name),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
export('sculpture.glb');dec=body.modifiers.new('Distant silhouette','DECIMATE');dec.ratio=.10;bpy.ops.object.modifier_apply(modifier=dec.name);export('sculpture-distant.glb')
(A/'sculpture.json').write_text(json.dumps({'components':components,'source':'https://zenodo.org/records/10244486','author':'Daniel Pett','license':'CC0-1.0','object':'Smithsonian F1917.243','restoration':'New digital gilding, hands and lotus plinth; artistic adaptation','height':1.915},indent=2))
# Replace only tagged altar geometry in the complete editable scene.
temple=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-scan.blend'
if not backup.exists():shutil.copy2(temple,backup)
bpy.ops.wm.open_mainfile(filepath=str(temple));preserved={o.name for o in bpy.data.objects if not o.get('altar_sculpture')}
for o in list(bpy.data.objects):
 if o.get('altar_sculpture'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
assert preserved.issubset({o.name for o in bpy.data.objects})
for o in bpy.data.objects:
 if o.type=='LIGHT' and o.data.type=='SUN':o.data.energy=3.7;o.data.color=(1,.79,.51);o.data.angle=.055;o.rotation_euler=Vector((18,8,-24)).to_track_quat('-Z','Y').to_euler()
for m in bpy.data.materials:
 if 'ceramic' in m.name.lower() and m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:p.inputs['Coat Weight'].default_value=.48;p.inputs['Coat Roughness'].default_value=.20
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(temple));print('BUDDHA_RESTORED preserved',len(preserved),'scene objects',flush=True)
