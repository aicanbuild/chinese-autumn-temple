"""Paired original ceremonial silk runners, placed on the existing side tables."""
import bpy,math
from pathlib import Path
A=Path(__file__).resolve().parents[1]/'dist/assets'
LENGTH=.58+math.pi*.025/2+.44

def build_altar_brocade():
 m=bpy.data.materials.get('Sanctuary | crimson silk and gilt thread') or bpy.data.materials.new('Sanctuary | crimson silk and gilt thread')
 m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');l.new(p.outputs[0],out.inputs[0]);p.inputs['Sheen Weight'].default_value=.16;p.inputs['Sheen Tint'].default_value=(.35,.065,.10,1);p.inputs['Sheen Roughness'].default_value=.5
 for filename,kind in [('altar-brocade-color.jpg','color'),('altar-brocade-orm.png','orm'),('altar-brocade-normal.png','normal')]:
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/filename),check_existing=True);t.extension='EXTEND'
  if kind=='color':l.new(t.outputs['Color'],p.inputs['Base Color'])
  else:
   t.image.colorspace_settings.name='Non-Color'
   if kind=='normal':
    bump=n.new('ShaderNodeNormalMap');bump.inputs['Strength'].default_value=.45;l.new(t.outputs['Color'],bump.inputs['Color']);l.new(bump.outputs[0],p.inputs['Normal'])
   else:
    sep=n.new('ShaderNodeSeparateColor');l.new(t.outputs['Color'],sep.inputs[0]);l.new(sep.outputs['Green'],p.inputs['Roughness']);l.new(sep.outputs['Blue'],p.inputs['Metallic'])
 lining=bpy.data.materials.get('Sanctuary | silk runner lining') or bpy.data.materials.new('Sanctuary | silk runner lining');lining.diffuse_color=(.085,.007,.012,1);lining.use_nodes=True;lp=lining.node_tree.nodes.get('Principled BSDF');lp.inputs['Base Color'].default_value=lining.diffuse_color;lp.inputs['Roughness'].default_value=.7
 parts=[]
 for side in [-1,1]:
  nx,ny=48,128;vs=[];faces=[]
  for j in range(ny+1):
   s=j/ny*LENGTH
   for i in range(nx+1):
    u=i/nx;fade=math.sin(math.pi*u)**.6
    if s<=.58:
     y=8.29-s;z=1.948+.0008*fade*math.sin(s*14+u*8)**2
    elif s<=.58+math.pi*.025/2:
     a=(s-.58)/.025;y=7.71-.025*math.sin(a);z=1.948-.025*(1-math.cos(a))
    else:
     t=(s-.58-math.pi*.025/2)/.44
     fold=(.014+.010*math.sin(u*math.tau*3+.3))*t*t
     y=7.685-fold;z=1.923-.44*t+.004*math.sin(u*math.tau*2+.5)*t*t
    x=side*2.16+(u-.5)*(.60-.012*max(0,(s-.65)/.41))
    vs.append((x,y,z))
  for j in range(ny):
   for i in range(nx):q=j*(nx+1)+i;faces.append((q,q+nx+1,q+nx+2,q+1))
  data=bpy.data.meshes.new('Tailored silk cloth');data.from_pydata(vs,[],faces);data.update();o=bpy.data.objects.new('Altar brocade | paired silk runner',data);bpy.context.collection.objects.link(o);data.materials.append(m);data.materials.append(lining)
  uv=data.uv_layers.new(name='Weave length')
  for f in data.polygons:
   f.use_smooth=True
   for k in f.loop_indices:
    index=data.loops[k].vertex_index;uv.data[k].uv=(index%(nx+1)/nx,1-(index//(nx+1))/ny)
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  mod=o.modifiers.new('Woven cloth and sewn edge thickness','SOLIDIFY');mod.thickness=.0008;mod.offset=-1;mod.material_offset=1;mod.material_offset_rim=1;mod.use_even_offset=True;bpy.ops.object.modifier_apply(modifier=mod.name)
  o['altar_brocade']=True;o['sanctuary_interior']=True;parts.append(o)
 return parts
