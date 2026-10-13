"""Mirror courtyard moss material in the editable terrain and full temple files.
Runtime retains the original GLB geometry and blends the same maps in Three.js.
"""
import bpy,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
for filename in ['山林地形.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-garden-moss.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path))
 m=next(m for m in bpy.data.materials if m.name=='Landscape | forest floor');nodes=m.node_tree.nodes;links=m.node_tree.links
 if nodes.get('Maintained garden moss'):
  for image in list(bpy.data.images):
   name=Path(bpy.path.abspath(image.filepath)).name
   if name not in ['garden-moss.jpg','garden-moss-normal.jpg','garden-moss-rough.jpg']:continue
   fresh=bpy.data.images.load(str(A/name),check_existing=False);fresh.colorspace_settings.name=image.colorspace_settings.name;fresh.pack();image.user_remap(fresh)
  bpy.ops.wm.save_as_mainfile(filepath=str(path));print('MOSS MAP REFRESH',filename,flush=True);continue
 p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');base=p.inputs['Base Color'].links[0].from_socket
 normal=next(n for n in nodes if n.type=='NORMAL_MAP');old_normal=normal.inputs['Color'].links[0].from_socket
 uv=nodes.new('ShaderNodeTexCoord');scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=7;links.new(uv.outputs['UV'],scale.inputs[0])
 sep=nodes.new('ShaderNodeSeparateXYZ');links.new(scale.outputs[0],sep.inputs[0]);x=sep.outputs['X'];y=sep.outputs['Y']
 def math(op,a,b=None):
  n=nodes.new('ShaderNodeMath');n.operation=op
  for i,value in enumerate([a,b]):
   if value is None:continue
   if isinstance(value,(int,float)):n.inputs[i].default_value=value
   else:links.new(value,n.inputs[i])
  return n.outputs[0]
 radius=nodes.new('ShaderNodeVectorMath');radius.operation='DISTANCE';radius.inputs[1].default_value=(0,-2,0);links.new(scale.outputs[0],radius.inputs[0])
 edge=math('MULTIPLY',math('MULTIPLY',math('SINE',math('MULTIPLY',x,.37)),math('COSINE',math('MULTIPLY',y,.31))),.7)
 ramp=nodes.new('ShaderNodeMapRange');ramp.interpolation_type='SMOOTHSTEP';ramp.clamp=True;ramp.inputs['From Min'].default_value=18;ramp.inputs['From Max'].default_value=28;ramp.inputs['To Min'].default_value=1;ramp.inputs['To Max'].default_value=0;links.new(math('ADD',radius.outputs['Value'],edge),ramp.inputs['Value'])
 cover=ramp.outputs['Result'];texscale=nodes.new('ShaderNodeVectorMath');texscale.operation='SCALE';texscale.inputs[3].default_value=7/1.2;links.new(uv.outputs['UV'],texscale.inputs[0])
 maps=[]
 for suffix in ['', '-normal','-rough']:
  n=nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(A/f'garden-moss{suffix}.jpg'),check_existing=True);n.image.colorspace_settings.name='Non-Color' if suffix else 'sRGB';n.image.pack();links.new(texscale.outputs[0],n.inputs['Vector']);maps.append(n.outputs['Color'])
 tone=math('ADD',.78,math('ADD',math('MULTIPLY',.12,math('SINE',math('ADD',math('MULTIPLY',x,.8),math('SINE',math('MULTIPLY',y,.54))))),math('MULTIPLY',.08,math('COSINE',math('MULTIPLY',y,1.3)))))
 tint=nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;links.new(maps[0],tint.inputs[1]);links.new(tone,tint.inputs[2])
 def mix(a,b,name):
  n=nodes.new('ShaderNodeMixRGB');n.name=name;links.new(cover,n.inputs[0]);links.new(a,n.inputs[1]);links.new(b,n.inputs[2]);return n.outputs[0]
 links.new(mix(base,tint.outputs[0],'Maintained garden moss'),p.inputs['Base Color'])
 links.new(mix(old_normal,maps[1],'Moss and forest surface normals'),normal.inputs['Color'])
 rough=nodes.new('ShaderNodeValue');rough.outputs[0].default_value=.94;links.new(mix(rough.outputs[0],maps[2],'Moss surface roughness'),p.inputs['Roughness'])
 bpy.ops.wm.save_as_mainfile(filepath=str(path));print('MOSS SYNC',filename,flush=True)
