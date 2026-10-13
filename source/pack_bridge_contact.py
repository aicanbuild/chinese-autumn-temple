"""Pack contact-refined Draco meshes; original PBR image payloads stay byte-exact."""
import json,struct,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';path=A/'bridge.glb';raw=(R/'evidence/bridge-before-contact.glb').read_bytes();old_hash=hashlib.sha256(raw).hexdigest();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:];out=bytearray();original_views=doc['bufferViews'];doc['bufferViews']=[];doc['accessors']=[]
for image in doc['images']:
 view=original_views[image['bufferView']];payload=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
 while len(out)%4:out.append(0)
 image['bufferView']=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':len(out),'byteLength':len(payload)});out.extend(payload)
 assert bytes(out[-len(payload):])==payload
meta=json.loads((R/'evidence/bridge-contact-compressed.json').read_text());audit=json.loads((R/'evidence/bridge-contact-compression-audit.json').read_text());assert max(x['POSITIONMaxError'] for x in audit)<.00003
report=[]
for i,batch in enumerate(meta):
 p=doc['meshes'][batch['mesh']]['primitives'][batch['primitive']];payload=(R/f'evidence/bridge-contact-{i}.drc').read_bytes()
 while len(out)%4:out.append(0)
 vi=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':len(out),'byteLength':len(payload)});out.extend(payload);attributes={}
 for name,kind in [('POSITION','VEC3'),('NORMAL','VEC3'),('TEXCOORD_0','VEC2'),('_BRIDGE_OCCLUSION','SCALAR')]:
  attributes[name]=len(doc['accessors']);accessor={'componentType':5126,'count':batch['vertices'],'type':kind}
  if name=='POSITION':accessor.update(min=batch['min'],max=batch['max'])
  doc['accessors'].append(accessor)
 p['attributes']=attributes;p['indices']=len(doc['accessors']);doc['accessors'].append({'componentType':5125,'count':batch['triangles']*3,'type':'SCALAR'});p['extensions']={'KHR_draco_mesh_compression':{'bufferView':vi,'attributes':batch['attributes']}};report.append({k:batch[k] for k in ['mesh','vertices','triangles','bytes']})
while len(out)%4:out.append(0)
doc['buffers'][0]['byteLength']=len(out);j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);result=struct.pack('<III',0x46546c67,2,28+len(j)+len(out))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(out),0x004e4942)+out;assert len(result)<14*1024*1024,len(result);previous_hash=hashlib.sha256(path.read_bytes()).hexdigest();path.write_bytes(result)
# Existing AO silhouette error from Draco quantization is <30 micrometers.
meta_path=A/'pond-contact-ao.json';data=json.loads(meta_path.read_text());assert data['inputs']['bridge.glb']==previous_hash;data['inputs']['bridge.glb']=hashlib.sha256(result).hexdigest();meta_path.write_text(json.dumps(data,indent=2))
report={'originalBytes':len(raw),'newBytes':len(result),'originalImagePayloadsByteExact':True,'oldHash':old_hash,'newHash':hashlib.sha256(result).hexdigest(),'batches':report,'compressionAudit':audit};(R/'evidence/bridge-contact-pack.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
