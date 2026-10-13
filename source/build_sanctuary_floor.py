"""Editable honed stone paving, fine joints and a dark perimeter course."""
import bpy,math,random,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';rng=random.Random(1791)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,tint=(1,1,1)):
 m=bpy.data.materials.new('Sanctuary floor | '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*tint,1);p.inputs['Roughness'].default_value=1;p.inputs['Metallic'].default_value=0
 for suffix,slot,ext in [('', 'Base Color','jpg'),('-normal','Normal','png'),('-rough','Roughness','jpg')]:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/f'sanctuary-stone{suffix}.{ext}'),check_existing=True)
  if suffix:t.image.colorspace_settings.name='Non-Color'
  if slot=='Normal':
   n=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs[0],n.inputs['Color']);m.node_tree.links.new(n.outputs[0],p.inputs[slot])
  elif slot=='Base Color':
   mix=m.node_tree.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[7].default_value=(*tint,1);m.node_tree.links.new(t.outputs[0],mix.inputs[6]);m.node_tree.links.new(mix.outputs[2],p.inputs[slot])
  else:m.node_tree.links.new(t.outputs[0],p.inputs[slot])
 return m
stone=material('honed limestone',(.58,.61,.58));border=material('smoked stone border',(.28,.31,.28));grout=bpy.data.materials.new('Sanctuary floor | recessed lime joint');grout.use_nodes=True;grout.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.12,.13,.12,1);grout.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.92
parts=[]
def slab(name,x,y,w,d,mat,top=1.07,bottom=.94,bevel=.0025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,(top+bottom)/2));o=bpy.context.object;o.name=name;o.dimensions=(w,d,top-bottom);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);o['sanctuary_floor']=True;o['floor_part']=name.split(' | ')[0]
 if bevel:
  mod=o.modifiers.new('Hand eased stone arris','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 # Planar faces stay planar; the small rounded arrises have smooth normals.
 for f in o.data.polygons:f.use_smooth=max(abs(q) for q in f.normal)<.999
 uv=o.data.uv_layers.active or o.data.uv_layers.new();offset=(rng.random()*4,rng.random()*4);a=rng.choice([0,math.pi/2,math.pi,math.pi*1.5]);ca,sa=math.cos(a),math.sin(a)
 for f in o.data.polygons:
  omit=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=omit]
  for li in f.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co;u,v=p[axes[0]]/1.6,p[axes[1]]/1.6;uv.data[li].uv=(u*ca-v*sa+offset[0],u*sa+v*ca+offset[1])
 # Use uniform subtle stone-to-stone tint, with all channels kept equal.
 tint=rng.uniform(.965,1);o.color=(tint,tint,tint,1)
 if mat!=grout:
  attr=o.data.color_attributes.new(name='Stone variation',type='FLOAT_COLOR',domain='CORNER')
  for v in attr.data:v.color=(tint,tint,tint,1)
 parts.append(o);return o
xmin,xmax=-6.1275,6.1175;ymin,ymax=3.475,10.725;edge=.16;joint=.004
ix0,ix1=xmin+edge,xmax-edge;iy0,iy1=ymin+edge,ymax-edge
nx,ny=14,8;dx,dy=(ix1-ix0)/nx,(iy1-iy0)/ny
for iy in range(ny):
 for ix in range(nx):slab(f'Field slab | {iy:02d}.{ix:02d}',ix0+(ix+.5)*dx,iy0+(iy+.5)*dy,dx-joint,dy-joint,stone)
# Perimeter stones are also individually cut, rather than four metres-long bars.
for side,y in [('front',ymin+edge/2),('back',ymax-edge/2)]:
 for i in range(nx):slab(f'Border | {side} {i:02d}',xmin+(i+.5)*(xmax-xmin)/nx,y,(xmax-xmin)/nx-joint,edge-joint,border)
for side,x in [('left',xmin+edge/2),('right',xmax-edge/2)]:
 for i in range(ny):slab(f'Border | {side} {i:02d}',x,iy0+(i+.5)*dy,edge-joint,dy-joint,border)
slab('Joint bed | recessed',(xmin+xmax)/2,(ymin+ymax)/2,xmax-xmin,ymax-ymin,grout,top=1.062,bottom=.941,bevel=0)
report={'fieldSlabs':nx*ny,'borderSlabs':2*nx+2*ny,'parts':len(parts),'jointMeters':joint,'arrisRadiusMeters':.0025,'topMeters':1.07,'jointBedMeters':1.062,'boundsNative':[xmin,xmax,ymin,ymax,.94,1.07],'textureMeters':1.6,'materials':3}
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/主殿石铺地.blend'))
for mat in [stone,border,grout]:
 selected=[o for o in list(bpy.data.objects) if o.type=='MESH' and o.data.materials[0]==mat];bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=mat.name
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'sanctuary-floor.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(A/'sanctuary-floor.json').write_text(json.dumps(report,indent=2));print('SANCTUARY FLOOR',report,flush=True)
