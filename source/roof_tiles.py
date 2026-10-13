"""Recover existing five-panel roof strips and make closed, smooth ceramic shells."""
import bpy,math,random
from mathutils import Vector
from pathlib import Path
A=Path(__file__).resolve().parents[1]/'dist/assets'
def refine_roof_mesh(o):
 if o.get('roof_shell_revision'):return dict(o['roof_report'])
 old=o.data;uv=old.uv_layers.active;verts=[];faces=[];uvs=[];colors=[];smooth=[];rng=random.Random(774)
 def surface(points,coords,indices,tint,soft=False):
  start=len(verts);verts.extend(points);uvs.extend(coords);colors.extend([(tint,tint,tint,1)]*len(points))
  faces.extend([tuple(start+k for k in face) for face in indices]);smooth.extend([soft]*len(indices))
 def is_strip(index):
  if index+5>len(old.polygons):return False
  for j in range(5):
   p=old.polygons[index+j]
   if len(p.vertices)!=4:return False
   us=[uv.data[k].uv.x for k in p.loop_indices]
   if any(abs(a-b)>1e-5 for a,b in zip(us,[j/5,(j+1)/5,(j+1)/5,j/5])):return False
  return True
 tiles=0;preserved=0;i=0
 while i<len(old.polygons):
  if not is_strip(i):
   p=old.polygons[i];points=[tuple(old.vertices[k].co) for k in p.vertices];coords=[tuple(uv.data[k].uv) for k in p.loop_indices];surface(points,coords,[tuple(range(len(points)))],1,p.use_smooth);preserved+=1;i+=1;continue
  a,b,c,d=[old.vertices[k].co.copy() for k in [old.polygons[i].vertices[0],old.polygons[i+4].vertices[1],old.polygons[i+4].vertices[2],old.polygons[i].vertices[3]]]
  nx=12;ny=2;thickness=.008;tint=.95+rng.random()*.05;offset=rng.random()*8
  width=(b-a).length;length=(d-a).length;reverse=(b-a).cross(d-a).z<0
  def point(u,v,bottom=False):
   p=a.lerp(b,u).lerp(d.lerp(c,u),v);p.z+=math.sin(u*math.pi)*.055+v*.014-(thickness if bottom else 0);return tuple(p)
  for bottom in [False,True]:
   pts=[point(j/nx,k/ny,bottom) for k in range(ny+1) for j in range(nx+1)]
   coords=[(j/nx*width/.24+offset,k/ny*length/.24+offset*.37) for k in range(ny+1) for j in range(nx+1)]
   quads=[]
   for k in range(ny):
    for j in range(nx):
     z=k*(nx+1)+j;q=(z,z+1,z+nx+2,z+nx+1);quads.append(q[::-1] if reverse!=bottom else q)
   surface(pts,coords,quads,tint,True)
  # End faces expose the real eight millimetre ceramic lip at overlapping courses.
  for v in [0,1]:
   pts=[];coords=[];quads=[]
   for j in range(nx+1):
    for bottom in [False,True]:pts.append(point(j/nx,v,bottom));coords.append((j/nx*width/.24+offset,float(bottom)*thickness/.24))
   for j in range(nx):
    q=(j*2,j*2+2,j*2+3,j*2+1);quads.append(q[::-1] if (v==0)!=reverse else q)
   surface(pts,coords,quads,tint,False)
  for u in [0,1]:
   pts=[];coords=[];quads=[]
   for k in range(ny+1):
    for bottom in [False,True]:pts.append(point(u,k/ny,bottom));coords.append((k/ny*length/.24,float(bottom)*thickness/.24))
   for k in range(ny):
    q=(k*2,k*2+2,k*2+3,k*2+1);quads.append(q[::-1] if (u==1)!=reverse else q)
   surface(pts,coords,quads,tint)
  tiles+=1;i+=5
 assert tiles>2800,(tiles,preserved)
 mesh=bpy.data.meshes.new('Twelve-segment closed ceramic tiles');mesh.from_pydata(verts,[],faces);mesh.update()
 mesh.uv_layers.new(name='UVMap');mesh.color_attributes.new(name='Kiln tint',type='FLOAT_COLOR',domain='CORNER')
 # Adding a corner attribute may reallocate Blender CustomData. Acquire both
 # RNA handles only after the full layout exists, or UV writes can corrupt color.
 layer=mesh.uv_layers['UVMap'];color=mesh.color_attributes['Kiln tint']
 for p in mesh.polygons:
  p.use_smooth=smooth[p.index]
  for li in p.loop_indices:
   vi=mesh.loops[li].vertex_index;layer.data[li].uv=uvs[vi];color.data[li].color=colors[vi]
 m=bpy.data.materials.new('Charcoal glazed ceramic | refined shells');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Metallic'].default_value=0;p.inputs['Coat Weight'].default_value=.25;p.inputs['Coat Roughness'].default_value=.28
 for suffix,slot in [('', 'Base Color'),('-normal','Normal'),('-rough','Roughness')]:
  t=n.new('ShaderNodeTexImage');ext='png' if suffix=='-normal' else 'jpg';t.image=bpy.data.images.load(str(A/f'roof-glaze{suffix}.{ext}'),check_existing=True)
  if suffix:t.image.colorspace_settings.name='Non-Color'
  if slot=='Normal':
   normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.5;l.new(t.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs[slot])
  elif slot=='Base Color':
   vc=n.new('ShaderNodeVertexColor');vc.layer_name='Kiln tint';mix=n.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;l.new(t.outputs['Color'],mix.inputs[6]);l.new(vc.outputs['Color'],mix.inputs[7]);l.new(mix.outputs[2],p.inputs[slot])
  else:l.new(t.outputs['Color'],p.inputs[slot])
 mesh.materials.append(m);o.data=mesh;o['roof_shell_revision']=1
 report={'tiles':tiles,'preservedNonRoofFaces':preserved,'crossSections':12,'thicknessMeters':thickness,'toeRiseMeters':.014,'vertices':len(verts),'faces':len(faces)};o['roof_report']=report;return report
