"""Add matching thin diffuse foliage lobes to editable Blender source materials.
Runtime uses shadowed punctual lighting; Cycles also transports environment light.
Does not export GLB: portable original PBR material/geometry remains unchanged.
"""
import bpy,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
report=[]
def amount(name):
 if 'Understory | waxed evergreen leaf' in name:return .16
 if name.startswith('Woodland | green'):return .20
 if name.startswith(('Woodland | ginkgo','Woodland | maple')):return .25
 if 'fern_02' in name:return .27
 return None
def install(m,f):
 if m.get('thin_foliage_v1'):return False
 nodes=m.node_tree.nodes;links=m.node_tree.links
 p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
 assert output.inputs['Surface'].is_linked,m.name
 original=output.inputs['Surface'].links[0].from_socket
 trans=nodes.new('ShaderNodeBsdfTranslucent');trans.label='薄叶漫透射';trans.location=(p.location.x,p.location.y-360)
 color=p.inputs['Base Color'];normal=p.inputs['Normal']
 if color.is_linked:links.new(color.links[0].from_socket,trans.inputs['Color'])
 else:trans.inputs['Color'].default_value=color.default_value
 if normal.is_linked:links.new(normal.links[0].from_socket,trans.inputs['Normal'])
 transmitted=trans.outputs[0]
 alpha=p.inputs['Alpha']
 if alpha.is_linked or alpha.default_value<1:
  clear=nodes.new('ShaderNodeBsdfTransparent');mask=nodes.new('ShaderNodeMixShader');mask.label='保留原叶片裁切';links.new(clear.outputs[0],mask.inputs[1]);links.new(transmitted,mask.inputs[2])
  if alpha.is_linked:links.new(alpha.links[0].from_socket,mask.inputs[0])
  else:mask.inputs[0].default_value=alpha.default_value
  transmitted=mask.outputs[0]
 mix=nodes.new('ShaderNodeMixShader');mix.label='反射 / 透射能量分配';mix.inputs[0].default_value=f;links.new(original,mix.inputs[1]);links.new(transmitted,mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface'])
 m['thin_foliage_v1']=f;return True
for name in ['听秋寺院','山林地被','林下灌木','池岸蕨类','山林地形']:
 path=R/'source'/(name+'.blend');backup=path.with_name(name+'-before-foliage-light.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path))
 before={o.name:(o.data.as_pointer() if o.type=='MESH' else 0,tuple(v for row in o.matrix_world for v in row)) for o in bpy.data.objects}
 used={m for o in bpy.data.objects if o.type=='MESH' for m in o.data.materials if m};changed=[]
 for m in used:
  f=amount(m.name)
  if f is not None:
   install(m,f);changed.append([m.name,f])
 assert changed,(name,'No target materials')
 after={o.name:(o.data.as_pointer() if o.type=='MESH' else 0,tuple(v for row in o.matrix_world for v in row)) for o in bpy.data.objects};assert before==after
 bpy.ops.wm.save_as_mainfile(filepath=str(path));report.append({'file':str(path),'materials':changed,'objectsPreserved':len(before)});print('FOLIAGE SAVED',name,len(changed),flush=True)
(R/'evidence/foliage-lighting-native.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('FOLIAGE COMPLETE',flush=True)
