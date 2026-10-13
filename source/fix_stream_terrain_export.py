"""Restore the existing terrain's active color semantic after Blender 4.5 export.
The full source file has an unexportable color-node chain; glTF adds a white
COLOR_0 ahead of the authored Color attribute. Keep the authored channel.
"""
from pathlib import Path
import json,struct

def fix(path):
 b=Path(path).read_bytes();length=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+length]);tail=b[20+length:]
 for m in j['meshes']:
  for p in m['primitives']:
   if 'COLOR_1' in p['attributes']:
    p['attributes']['COLOR_0']=p['attributes'].pop('COLOR_1');d=p.get('extensions',{}).get('KHR_draco_mesh_compression',{}).get('attributes',{})
    if 'COLOR_1' in d:d['COLOR_0']=d.pop('COLOR_1')
 for m in j['materials']:
  if m['name']=='Landscape | forest floor':
   p=m['pbrMetallicRoughness'];p.pop('metallicRoughnessTexture',None);p['roughnessFactor']=.91
 data=json.dumps(j,separators=(',',':')).encode();data+=b' '*((-len(data))%4);Path(path).write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
if __name__=='__main__':fix(Path(__file__).resolve().parents[1]/'dist/assets/terrain.glb')
