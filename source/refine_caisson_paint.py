"""Synchronize restored mineral paint in native projects and glTF metadata.
Geometry, encoded mesh streams and embedded images are kept byte-identical.
"""
import bpy,array,hashlib,json,shutil,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'source'))
from caisson_paint import apply_refined_paint
NAMES={'Sanctuary | azurite painted wood','Sanctuary | malachite painted wood'}
def signature():
 h=hashlib.sha256()
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  h.update(o.name.encode());h.update(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for coll,prop,width,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    a=array.array(typ,[0])*(len(coll)*width);coll.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
 return h.hexdigest()
reports=[]
for name in ['庄严内殿','听秋寺院']:
 path=R/'source'/f'{name}.blend';backup=path.with_name(name+'-before-refined-paint.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signature();changed=[]
 changed=apply_refined_paint(bpy.data.materials)
 assert signature()==before
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signature()==before
 for name in changed:
  m=bpy.data.materials[name];p=m.node_tree.nodes.get('Principled BSDF');assert not p.inputs['Roughness'].is_linked;assert abs(p.inputs['Roughness'].default_value-.68)<1e-6;assert m.node_tree.nodes['Refined paint grain scale'].inputs['Scale'].default_value[:]==(6,6,6)
 reports.append({'file':path.name,'objects':len(bpy.data.objects),'geometryUVTransformsUnchanged':True,'materials':changed})
original=R/'evidence/paint-original';original.mkdir(exist_ok=True)
for name in ['sanctuary.glb','fine-caisson.glb']:
 path=R/'dist/assets'/name;backup=original/name
 if not backup.exists():shutil.copy2(path,backup)
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);tail=b[20+n:];assert struct.unpack_from('<I',b,16)[0]==0x4e4f534a
 before=json.dumps({k:v for k,v in j.items() if k not in ['materials','extensionsUsed']},sort_keys=True)
 changed=[]
 for m in j['materials']:
  if m['name'] not in NAMES:continue
  p=m['pbrMetallicRoughness'];p.pop('metallicRoughnessTexture',None);p['roughnessFactor']=.68;p['metallicFactor']=0
  m['normalTexture']['scale']=.075;m['normalTexture'].setdefault('extensions',{})['KHR_texture_transform']={'scale':[6,6]}
  m.setdefault('extras',{})['refined_paint_revision']=1;changed.append(m['name'])
 assert set(changed)==NAMES
 if 'KHR_texture_transform' not in j.setdefault('extensionsUsed',[]):j['extensionsUsed'].append('KHR_texture_transform')
 assert json.dumps({k:v for k,v in j.items() if k not in ['materials','extensionsUsed']},sort_keys=True)==before
 data=json.dumps(j,separators=(',',':'),ensure_ascii=False).encode();data+=b' '*((-len(data))%4)
 out=struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail;path.write_bytes(out)
 assert out[20+len(data):]==backup.read_bytes()[20+struct.unpack_from('<I',backup.read_bytes(),12)[0]:]
 reports.append({'file':name,'encodedMeshesAndImagesUnchanged':True,'binarySHA256':hashlib.sha256(tail).hexdigest(),'materials':changed})
(R/'evidence/caisson-paint-native.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print(json.dumps(reports,ensure_ascii=False),flush=True)
