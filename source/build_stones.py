"""Closed weathered stone prototypes, arranged as a low natural pond bank."""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector,noise
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Pond stone | granite moss and wet edge');mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.84
geo=nodes.new('ShaderNodeNewGeometry');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=1.45;links.new(geo.outputs['Position'],mapping.inputs[0])
for suffix,slot in [('', 'Base Color'),('-normal','Normal'),('-rough','Roughness')]:
 t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/f'pbr-stone{suffix}.jpg'),check_existing=True);t.projection='BOX';t.projection_blend=.28;links.new(mapping.outputs[0],t.inputs['Vector'])
 if suffix:t.image.colorspace_settings.name='Non-Color'
 if slot=='Base Color':
  c=nodes.new('ShaderNodeVertexColor');c.layer_name='Color';mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;links.new(t.outputs['Color'],mix.inputs[1]);links.new(c.outputs['Color'],mix.inputs[2]);diffuse=mix.outputs[0]
 elif slot=='Normal':
  bump=nodes.new('ShaderNodeNormalMap');bump.inputs['Strength'].default_value=.28;links.new(t.outputs['Color'],bump.inputs['Color']);links.new(bump.outputs[0],p.inputs[slot])
 else:rough=t.outputs['Color']
# Soft capillary transition over the waterline, visible in the native material too.
xyz=nodes.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Position'],xyz.inputs[0]);ramp=nodes.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=-.045;ramp.inputs['From Max'].default_value=.09;ramp.inputs['To Min'].default_value=.52;ramp.inputs['To Max'].default_value=1;links.new(xyz.outputs['Z'],ramp.inputs['Value'])
mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;links.new(diffuse,mix.inputs[1]);links.new(ramp.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],p.inputs['Base Color'])
r=nodes.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=-.045;r.inputs['From Max'].default_value=.09;r.inputs['To Min'].default_value=.26;r.inputs['To Max'].default_value=.88;links.new(xyz.outputs['Z'],r.inputs['Value']);links.new(r.outputs[0],p.inputs['Roughness'])
shell=bpy.data.materials.new('Pond stone | browser shader');shell.use_nodes=True;shell.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.85
prototypes=[]
for k in range(8):
 rng=random.Random(840+k*97);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5 if k<6 else 2,radius=1);o=bpy.context.object;o.name=f'PondStone_{k}';o['pond_stone']=True;o.data.materials.append(mat)
 planes=[]
 for j in range(8):
  n=Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-.5,1))).normalized();planes.append((n,rng.uniform(.79,.98)))
 for v in o.data.vertices:
  n=v.co.normalized();r=1+.095*noise.noise_vector(n*1.8+Vector((k*7.1,3.2,8.7))).x+.025*noise.noise_vector(n*7+Vector((k,12,5))).y
  for normal,limit in planes:
   dot=n.dot(normal)
   if dot>.05:
    plane=limit/dot;h=max(0,min(1,.5+.5*(plane-r)/.07));r=plane*(1-h)+r*h-.07*h*(1-h)
  v.co=n*r
  v.co.x+=.04*math.sin(v.co.z*3+k);v.co.y+=.03*math.cos(v.co.x*5+k)
 o.data.update()
 for f in o.data.polygons:f.use_smooth=True
 uv=o.data.uv_layers.new()
 for f in o.data.polygons:
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co.normalized();uv.data[li].uv=(.5+math.atan2(v.y,v.x)/math.tau,.5+math.asin(v.z)/math.pi)
 color=o.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
 for v in o.data.vertices:
  shade=.83+.12*noise.noise_vector(v.co*4+Vector((k*2,4,9))).z;moss=max(0,v.normal.z-.18)*max(0,noise.noise_vector(v.co*2.5+Vector((k,6,9))).x+.20)
  color.data[v.index].color=(shade*(1-.30*moss),shade*(1-.04*moss),shade*(1-.40*moss),1)
 prototypes.append(o)
# Model-only portable prototypes reuse the already-loaded photographic stone textures.
for o in prototypes:o.data.materials[0]=shell
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'pond-stones.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
for o in prototypes:o.data.materials[0]=mat
rng=random.Random(90412);placements=[]
# Low broad stones follow the pool; avoid both ends of the bridge.
for i in range(72):
 a=(i+rng.uniform(-.13,.13))*math.tau/72;x=11.52*math.cos(a);y=-5.8+6.91*math.sin(a)
 if abs(x)<1.75:continue
 sx=rng.uniform(.50,.78);sy=rng.uniform(.34,.52);sz=rng.uniform(.22,.40);angle=math.atan2(6.91*math.cos(a),-11.52*math.sin(a))+rng.uniform(-.22,.22)
 placements.append([rng.randrange(6),x,y,.025,sx,sy,sz,angle,'bank'])
 # Smaller stones lodge between the larger stones, beneath the waterline.
 if i%2==0:
  a+=.033;placements.append([rng.randrange(6),11.15*math.cos(a),-5.8+6.59*math.sin(a),-.22,rng.uniform(.20,.39),rng.uniform(.17,.30),rng.uniform(.12,.22),rng.random()*math.tau,'toe'])
# Smooth gravel sits on the riverbed, without sharp peaks near swimming fish.
for i in range(200):
 a=rng.random()*math.tau;r=math.sqrt(rng.random())*.88;x=11.5*math.cos(a)*r;y=-5.8+6.9*math.sin(a)*r
 if abs(x)<1.5:continue
 placements.append([6+i%2,x,y,-.84,rng.uniform(.08,.22),rng.uniform(.07,.20),rng.uniform(.045,.115),rng.random()*math.tau,'bed'])
for i,(kind,x,y,z,sx,sy,sz,rotation,zone) in enumerate(placements):
 o=prototypes[kind].copy();o.data=prototypes[kind].data;bpy.context.collection.objects.link(o);o.name=f'Pond {zone} stone {i:03d}';o.location=(x,y,z);o.scale=(sx,sy,sz);o.rotation_euler.z=rotation;o['pond_zone']=zone
for o in prototypes:bpy.data.objects.remove(o,do_unlink=True)
import sys
sys.path.insert(0,str(R/'source'))
from pond_basin import seat_stone
for o in bpy.data.objects:
 if o.get('pond_zone')=='bed':
  seat_stone(o);index=int(o.name.rsplit(' ',1)[1]);placements[index][3]=o.location.z
meta={'placements':placements,'prototypes':8,'waterline':-.025,'basinRevision':1};(A/'pond-stones.json').write_text(json.dumps(meta,separators=(',',':')))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/自然池岸.blend'))
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
for o in list(bpy.data.objects):
 if o.get('pond_stone'):bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
 if o.type!='MESH' or not any(m and m.name in ['Natural mossy bank stones','Soft forest moss'] for m in o.data.materials):continue
 bm=bmesh.new();bm.from_mesh(o.data);remove=[]
 for f in bm.faces:
  p=o.matrix_world@f.calc_center_median()
  if (p.x/11.5)**2+((p.y+5.8)/6.9)**2<1.28 and p.z<1.15:remove.append(f)
 bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
with bpy.data.libraries.load(str(R/'source/自然池岸.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
print('POND STONES COMPLETE',len(placements),'closed stones',flush=True)
