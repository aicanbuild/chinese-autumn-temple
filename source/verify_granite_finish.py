"""Verify image-only GLB changes before refreshing dependent contact-map bindings."""
from pathlib import Path
import json,struct,hashlib
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';B=R/'evidence/granite-before-fine-honing'
def read(path):
 data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+n]);binary=data[28+n:];return doc,[binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']] for v in doc['bufferViews']]
reports=[]
for name in ['temple.glb','stone-lantern.glb']:
 old,ob=read(B/name);new,nb=read(A/name)
 assert len(ob)==len(nb)
 # Accessors, nodes, transforms, materials, occlusion attributes and compressed
 # mesh descriptors must remain exact, as must all non-granite image payloads.
 assert {k:v for k,v in old.items() if k not in ['images','buffers','bufferViews']}=={k:v for k,v in new.items() if k not in ['images','buffers','bufferViews']}
 assert old['images']==new['images']
 changed={image['bufferView'] for image in old['images'] if image.get('name','').startswith('cut-granite')};assert len(changed)==3
 for i in range(len(ob)):
  if i not in changed:assert ob[i]==nb[i],(name,i)
  else:assert ob[i]!=nb[i],(name,i)
 reports.append({'file':name,'unchangedBuffers':len(ob)-3,'changedImages':3,'meshAndMaterialMetadataPreserved':True})
old_hash=hashlib.sha256((B/'temple.glb').read_bytes()).hexdigest();new_hash=hashlib.sha256((A/'temple.glb').read_bytes()).hexdigest()
# The earlier mineral-paint refinement also changed only material shading.
# Verify its actual pre-change binary instead of trusting a stale binding.
paint_before=R/'evidence/paint-original/sanctuary.glb';po,pob=read(paint_before);pn,pnb=read(A/'sanctuary.glb')
assert pob==pnb
assert {k:v for k,v in po.items() if k not in ['materials','extensionsUsed']}=={k:v for k,v in pn.items() if k not in ['materials','extensionsUsed']}
for m in po['materials']:
 if m['name'] not in ['Sanctuary | azurite painted wood','Sanctuary | malachite painted wood']:continue
 p=m['pbrMetallicRoughness'];p.pop('metallicRoughnessTexture',None);p['roughnessFactor']=.68;p['metallicFactor']=0
 m['normalTexture']['scale']=.075;m['normalTexture'].setdefault('extensions',{})['KHR_texture_transform']={'scale':[6,6]};m.setdefault('extras',{})['refined_paint_revision']=1
assert po['materials']==pn['materials']
paint_old_hash=hashlib.sha256(paint_before.read_bytes()).hexdigest();paint_new_hash=hashlib.sha256((A/'sanctuary.glb').read_bytes()).hexdigest()
for name in ['hall-contact-ao.json','mural-contact-ao.json']:
 path=A/name;metadata=json.loads(path.read_text());assert metadata['inputs']['temple.glb'] in [old_hash,new_hash]
 assert metadata['inputs']['sanctuary.glb'] in [paint_old_hash,paint_new_hash]
 metadata['inputs']['temple.glb']=new_hash;metadata['inputs']['sanctuary.glb']=paint_new_hash;path.write_text(json.dumps(metadata,indent=2)+'\n')
reports.append({'file':'sanctuary.glb','priorPaintUpdateVerified':True,'geometryAndImagesExact':True,'occlusionUnchanged':True})
(R/'evidence/granite-buffer-verification.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
