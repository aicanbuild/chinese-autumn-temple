"""Cross-fade transported branch charts only around fused trunk/limb forks."""
import math
import numpy as np
from tree_bark_uv import BranchProjection

def add_bark_blend(mesh,paths):
 projections=[BranchProjection(*p) for p in paths]
 centers=np.asarray([p.center[:] for p in mesh.polygons]);normals=np.asarray([p.normal[:] for p in mesh.polygons]);scores=[]
 for projection in projections:
  error,_,_,unit=projection.project(centers);scores.append(error+.025*(1-np.einsum('nd,nd->n',unit,normals)))
 scores=np.asarray(scores);chosen=np.argmin(scores,axis=0)
 positions=np.asarray([v.co[:] for v in mesh.vertices]);vn=np.asarray([v.normal[:] for v in mesh.vertices]);lookup=[p.project(positions) for p in projections]
 vertex_scores=[v[0]+.025*(1-np.einsum('nd,nd->n',v[3],vn)) for v in lookup]
 uv=mesh.uv_layers.get('BarkBlendUV') or mesh.uv_layers.new(name='BarkBlendUV')
 attribute=mesh.attributes.get('_BARK_BLEND') or mesh.attributes.new('_BARK_BLEND','FLOAT_VECTOR','CORNER')
 # Adding a corner attribute can invalidate the RNA UV-layer reference.
 uv=mesh.uv_layers['BarkBlendUV']
 blended=0
 for fi,(face,primary) in enumerate(zip(mesh.polygons,chosen)):
  secondary=0 if primary>=8 else int(np.argmin(scores[8:,fi]))+8
  ids=np.asarray([mesh.loops[li].vertex_index for li in face.loop_indices]);_,theta,along,_=lookup[secondary];angles=theta[ids].copy()
  if np.ptp(angles)>math.pi:angles[angles<math.pi]+=math.tau
  width=.055
  t=np.clip(.5+.5*(vertex_scores[primary][ids]-vertex_scores[secondary][ids])/width,0,1);weights=t*t*(3-2*t)
  if 1<=primary<8:weights[:]=0
  circumference=math.tau*max(paths[secondary][1:])*1.3
  for li,vi,a,w in zip(face.loop_indices,ids,angles,weights):
   coord=(a/math.tau*circumference,along[vi]*.65);uv.data[li].uv=coord;attribute.data[li].vector=(*coord,float(w));blended+=w>.001
 mesh.uv_layers.active_index=0;mesh.update()
 return {'loops':len(mesh.loops),'blendedLoops':int(blended),'transitionWidthMetres':.055}

def configure_native_bark(material,asset_dir,primary_uv):
 import bpy
 nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
 output=nodes.new('ShaderNodeOutputMaterial');bsdf=nodes.new('ShaderNodeBsdfPrincipled');links.new(bsdf.outputs[0],output.inputs[0])
 attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='_BARK_BLEND';split=nodes.new('ShaderNodeSeparateXYZ');links.new(attr.outputs['Vector'],split.inputs[0]);weight=split.outputs['Z']
 uvnodes=[]
 for name in [primary_uv,'BarkBlendUV']:
  uv=nodes.new('ShaderNodeUVMap');uv.uv_map=name;uvnodes.append(uv)
 def images(filename,noncolor=False):
  image=bpy.data.images.load(str(asset_dir/filename),check_existing=True);image.colorspace_settings.name='Non-Color' if noncolor else 'sRGB';pair=[]
  for uv in uvnodes:
   n=nodes.new('ShaderNodeTexImage');n.image=image;n.extension='REPEAT';links.new(uv.outputs[0],n.inputs['Vector']);pair.append(n.outputs['Color'])
  return pair
 def mix(pair):
  n=nodes.new('ShaderNodeMixRGB');links.new(weight,n.inputs[0]);links.new(pair[0],n.inputs[1]);links.new(pair[1],n.inputs[2]);return n.outputs[0]
 links.new(mix(images('pbr-bark.jpg')),bsdf.inputs['Base Color'])
 rough=nodes.new('ShaderNodeMath');rough.operation='MULTIPLY';rough.inputs[1].default_value=.91;links.new(mix(images('pbr-bark-rough.jpg',True)),rough.inputs[0]);links.new(rough.outputs[0],bsdf.inputs['Roughness'])
 normals=[]
 for image,uvname in zip(images('pbr-bark-normal.jpg',True),[primary_uv,'BarkBlendUV']):
  n=nodes.new('ShaderNodeNormalMap');n.uv_map=uvname;n.inputs['Strength'].default_value=.38;links.new(image,n.inputs['Color']);normals.append(n.outputs[0])
 normalize=nodes.new('ShaderNodeVectorMath');normalize.operation='NORMALIZE';links.new(mix(normals),normalize.inputs[0]);links.new(normalize.outputs[0],bsdf.inputs['Normal']);material['bark_junction_revision']=1
