import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(R/'source/寺旁清溪.blend'),link=False) as (a,b):b.objects=a.objects
for o in b.objects:
 if o and o.type=='MESH' and o.get('streamAssembly') not in ['water surface','headwater surface']:bpy.context.scene.collection.objects.link(o)
layout=json.loads((R/'dist/assets/creek-rapids.json').read_text());tex=bpy.data.images.load(str(R/'dist/assets/creek-rapids.png'));tex.colorspace_settings.name='Non-Color';pixels=np.array(tex.pixels[:],dtype=np.float32).reshape(tex.size[1],tex.size[0],4)[::-1]
# PNG array row zero is world z=-18, matching the runtime flipY=false sampler.
def profile(x,z):
 u=np.clip((x-12)/6*(tex.size[0]-1),0,tex.size[0]-1);v=np.clip((z+18)/38*(tex.size[1]-1),0,tex.size[1]-1);a=int(u);b=int(v);aa=min(a+1,tex.size[0]-1);bb=min(b+1,tex.size[1]-1);s=u-a;t=v-b
 return pixels[b,a]*(1-s)*(1-t)+pixels[b,aa]*s*(1-t)+pixels[bb,a]*(1-s)*t+pixels[bb,aa]*s*t
water=bpy.data.materials.new('Clear moving water with broken aerated crests');water.use_nodes=True;n=water.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.52,.69,.62,1);p.inputs['Roughness'].default_value=.08;p.inputs['IOR'].default_value=1.333;p.inputs['Transmission Weight'].default_value=.9
attr=n.new('ShaderNodeAttribute');attr.attribute_name='foam';ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.10;ramp.color_ramp.elements[1].position=.65;water.node_tree.links.new(attr.outputs['Fac'],ramp.inputs['Fac'])
foam=n.new('ShaderNodeBsdfPrincipled');foam.inputs['Base Color'].default_value=(.77,.88,.83,1);foam.inputs['Roughness'].default_value=.33;mix=n.new('ShaderNodeMixShader');water.node_tree.links.new(ramp.outputs['Color'],mix.inputs[0]);water.node_tree.links.new(p.outputs['BSDF'],mix.inputs[1]);water.node_tree.links.new(foam.outputs['BSDF'],mix.inputs[2]);water.node_tree.links.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
vs=[];faces=[];coords=[];fields=[];nx=36;nz=760
for k in range(nz+1):
 z=-18+38*k/nz;cx=15+.7*math.cos((z+9)*.22);w=(1.07+.17*math.sin(z*.51)+.11*math.sin(z*1.12))*math.exp(min(0,(z+14)/28))*min(1,.14+(z+72)/3,.14+(20-z)/2)*.94
 for i in range(nx+1):
  x=cx+(i/nx*2-1)*w;coords.append((x,z));fields.append(profile(x,z));vs.append((x,-z,-.025))
for k in range(nz):
 for i in range(nx):a=k*(nx+1)+i;b=a+nx+1;faces.extend([(a,b,a+1),(a+1,b,b+1)])
m=bpy.data.meshes.new('Subdivided surface');m.from_pydata(vs,[],faces);m.update();o=bpy.data.objects.new('Actual displaced rapid surface',m);bpy.context.scene.collection.objects.link(o);m.materials.append(water);color=m.color_attributes.new(name='foam',type='FLOAT_COLOR',domain='POINT')
for poly in m.polygons:poly.use_smooth=True
sheetmat=water.copy();sheetmat.name='Thin clear overflow film';sn=sheetmat.node_tree.nodes;sp=sn.get('Principled BSDF');transparent=sn.new('ShaderNodeBsdfTransparent');smix=sn.new('ShaderNodeMixShader');smix.inputs[0].default_value=.42;sheetmat.node_tree.links.new(transparent.outputs[0],smix.inputs[1]);sheetmat.node_tree.links.new(sp.outputs[0],smix.inputs[2]);sheetmat.node_tree.links.new(smix.outputs[0],sn.get('Material Output').inputs['Surface'])
jets=[]
for j in layout['jets']:
 v=[];f=[]
 for k in range(25):
  for i in range(9):v.append((0,0,0))
 for k in range(24):
  for i in range(8):a=k*9+i;b=a+9;f.extend([(a,b,a+1),(a+1,b,b+1)])
 g=bpy.data.meshes.new('Water lip');g.from_pydata(v,[],f);obj=bpy.data.objects.new('Overflow '+str(j['seed']),g);bpy.context.scene.collection.objects.link(obj);g.materials.append(sheetmat);g.color_attributes.new(name='foam',type='FLOAT_COLOR',domain='POINT');jets.append((j,g))
 for poly in g.polygons:poly.use_smooth=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.world=bpy.data.worlds.new('Daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.42,.55,.64,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
ld=bpy.data.lights.new('Sun','SUN');ld.energy=3;ld.angle=.09;lo=bpy.data.objects.new('Sun',ld);scene.collection.objects.link(lo);lo.rotation_euler=(.6,-.4,-.5)
cd=bpy.data.cameras.new('Rapid inspection');cam=bpy.data.objects.new('Rapid inspection',cd);scene.collection.objects.link(cam);cam.location=(18.4,-7.0,2.5);target=Vector((15.1,-2.0,0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=44;scene.camera=cam;scene.render.resolution_x=1000;scene.render.resolution_y=760;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
for frame,t in enumerate([0.,.12]):
 for i,((x,z),f) in enumerate(zip(coords,fields)):
  crest=.5+.5*math.sin(z*7.8-t*19.8+math.sin(x*4.1)*.65);h=f[0]*.55+f[1]*(.19*crest**3-.034+.023*math.sin(z*13.4-t*34+x*5.3))+f[3]*.012*math.sin(z*5-t*13+x*3);m.vertices[i].co.z=-.025+h
  xx=x-.12*t;zz=z-2.54*t;cells=math.sin(xx*47+math.sin(zz*23))*math.sin(zz*39+math.sin(xx*31));density=f[2]*(.12+.75*max(0,min(1,(crest-.48)/.46)))*(.26+.74*max(0,min(1,(cells+.28)/.83)));color.data[i].color=(density,density,density,1)
 for j,g in jets:
  for k in range(25):
   v=k/24
   for i in range(9):
    u=i/8*2-1;x=j['x']+u*j['width']*(.5-.28*v+.055*math.sin(v*11+j['seed']))+.026*math.sin(v*5-t*5+j['seed'])*v;y=j['lipY']+.15*v-((j['lipY']+.025)+.15)*v*v+.012*math.sin(v*34-t*31+u*6+j['seed'])*math.sin(math.pi*v);z=j['lipZ']+j['length']*(.92+.08*math.sin(t*7.1+j['seed']))*v;g.vertices[k*9+i].co=(x,-z,y)
  g.update()
 m.update();scene.render.filepath=str(R/f'evidence/creek-rapids-native-{frame}.png');bpy.ops.render.render(write_still=True)
scene['note']='Offline geometry QA using the runtime relief and sheet equations; browser material differs.';bpy.ops.wm.save_as_mainfile(filepath=str(R/'evidence/溪流急浪形态检查.blend'))
