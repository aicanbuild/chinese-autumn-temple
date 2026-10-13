"""Portable mineral-plaster materials and proportion-preserving mural UVs."""
import bpy
from pathlib import Path
A=Path(__file__).resolve().parents[1]/'dist/assets'
def apply_mural_finishes():
 panels=[o for o in bpy.data.objects if o.get('sanctuary_interior') and ('celestial garden assembly' in o.name or 'continuous lotus paradise' in o.name)]
 assert len(panels)==4
 rear=next(o.data.materials[0] for o in panels if 'Rear wall' in o.name)
 side=next((m for m in bpy.data.materials if m.name=='Sanctuary | mineral procession mural'),None)
 if side is None:side=bpy.data.materials.new('Sanctuary | mineral procession mural')
 for material,filename,w,h in [(rear,'sanctuary-mural.png',3.10,1.99),(side,'sanctuary-procession.jpg',4.34,2.18)]:
  material.use_nodes=True;n=material.node_tree.nodes;l=material.node_tree.links;n.clear()
  out=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');l.new(p.outputs[0],out.inputs[0]);p.inputs['Metallic'].default_value=0
  image=n.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(A/filename),check_existing=True);image.extension='EXTEND';l.new(image.outputs['Color'],p.inputs['Base Color'])
  uv=n.new('ShaderNodeUVMap');uv.uv_map='Plaster metres'
  for filename,slot in [('sanctuary-plaster-normal.png','Normal'),('sanctuary-plaster-rough.jpg','Roughness')]:
   t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/filename),check_existing=True);t.image.colorspace_settings.name='Non-Color';t.extension='REPEAT';l.new(uv.outputs[0],t.inputs['Vector'])
   if slot=='Normal':
    normal=n.new('ShaderNodeNormalMap');normal.uv_map='Plaster metres';normal.inputs['Strength'].default_value=.7;l.new(t.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs[slot])
   else:l.new(t.outputs['Color'],p.inputs[slot])
  material['mural_surface_revision']=1
 for o in panels:
  is_side='Side wall' in o.name;material=side if is_side else rear;w,h=(4.34,2.18) if is_side else (3.10,1.99)
  o.data.materials.clear();o.data.materials.append(material)
  image=next(n.image for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image.colorspace_settings.name=='sRGB');aspect=image.size[0]/image.size[1];target=w/h
  scale_u=min(1,target/aspect);scale_v=min(1,aspect/target)
  if not o.data.uv_layers:o.data.uv_layers.new(name='Paint composition')
  paint=o.data.uv_layers[0];paint.name='Paint composition'
  if not o.data.uv_layers.get('Plaster metres'):o.data.uv_layers.new(name='Plaster metres')
  # Reacquire RNA UV handles after changing layer allocation.
  paint=o.data.uv_layers['Paint composition'];plaster=o.data.uv_layers['Plaster metres']
  xs=[v.co.y if is_side else v.co.x for v in o.data.vertices];zs=[v.co.z for v in o.data.vertices];xmin,zmin=min(xs),min(zs)
  for loop in o.data.loops:
   v=o.data.vertices[loop.vertex_index].co;u=((v.y if is_side else v.x)-xmin)/w;t=(v.z-zmin)/h
   paint.data[loop.index].uv=((u-.5)*scale_u+.5,(t-.5)*scale_v+.5);plaster.data[loop.index].uv=(u*w,t*h)
  o.data.uv_layers.active_index=0;paint.active_render=True
 return side
