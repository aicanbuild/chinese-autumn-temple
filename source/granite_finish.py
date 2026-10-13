"""Tileable honed granite: connected mineral grains, shallow relief, matched roughness.

Refresh only embedded granite images in existing GLBs; every geometry buffer is
preserved byte-for-byte. No Blender scene regeneration is involved.
"""
from pathlib import Path
import hashlib,json,struct

R=Path(__file__).resolve().parents[1];A=R/'dist/assets'

def crystal_field(size,cells,seed):
 import numpy as np
 rng=np.random.default_rng(seed)
 jitter=rng.uniform(.12,.88,(cells,cells,2)).astype(np.float32)
 values=rng.random((cells,cells,4),dtype=np.float32)
 y,x=np.mgrid[:size,:size].astype(np.float32)*cells/size
 ix=np.floor(x).astype(int);iy=np.floor(y).astype(int)
 best=np.full((size,size),np.inf,np.float32);second=best.copy()
 result=np.zeros((size,size,4),np.float32)
 for dy in [-1,0,1]:
  for dx in [-1,0,1]:
   gx=ix+dx;gy=iy+dy;j=jitter[gy%cells,gx%cells]
   dist=(gx+j[:,:,0]-x)**2+(gy+j[:,:,1]-y)**2
   hit=dist<best;second=np.where(hit,best,np.minimum(second,dist));best=np.minimum(best,dist)
   result[hit]=values[gy%cells,gx%cells][hit]
 return result,np.sqrt(second)-np.sqrt(best)

def build_maps():
 import numpy as np
 from PIL import Image
 n=1024;grain,edge=crystal_field(n,230,718);fine,_=crystal_field(n,410,724)
 rng=np.random.default_rng(91);noise=rng.random((n,n)).astype(np.float32)
 kind=grain[:,:,0];shade=grain[:,:,1];quartz=kind<.55;mica=kind>.955
 # A light silver stone, with grey translucent quartz and sparse dark mica.
 colors=np.where(quartz[:,:,None],np.array([180,184,179]),np.array([201,198,187])).astype(float)
 colors=np.where(mica[:,:,None],np.array([109,114,107]),colors)
 colors+=(shade[:,:,None]-.5)*24+(fine[:,:,1,None]-.5)*12+(noise[:,:,None]-.5)*6
 # Tight grain boundaries are subtle, not thick artificial polygon outlines.
 boundary=np.exp(-edge*130);colors-=boundary[:,:,None]*5
 # Honing leaves a nearly flat surface with shallow mineral relief and tiny pits.
 h=(shade-.5)*.000085+(fine[:,:,2]-.5)*.00004-boundary*.00002
 pores=(fine[:,:,0]>.992)*np.maximum(0,noise-.25);h-=pores*.00008;colors-=pores[:,:,None]*15
 dx=(np.roll(h,-1,1)-np.roll(h,1,1))*.5/(.77/n)
 dy=(np.roll(h,-1,0)-np.roll(h,1,0))*.5/(.77/n)
 normal=np.stack([-dx,dy,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 rough=np.where(mica,.63,np.where(quartz,.70,.78))+(fine[:,:,3]-.5)*.05+boundary*.02
 for suffix,data in [('',colors),('-normal',(normal*.5+.5)*255),('-rough',rough*255)]:
  Image.fromarray(np.uint8(np.clip(data,0,255))).save(A/f'cut-granite{suffix}.jpg',quality=95,subsampling=0)
 return {'resolution':n,'tileMeters':.77,'typicalGrainMillimeters':round(.77/230*1000,2),'micaFraction':float(mica.mean()),'seed':718}

def refresh_glb(path,image_files=None):
 data=path.read_bytes();length=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+length]);binary=data[28+length:]
 replacements={image['bufferView']:image for image in doc['images'] if (image.get('name','') in image_files if image_files is not None else image.get('name','').startswith('cut-granite'))}
 original=[binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']] for v in doc['bufferViews']]
 rebuilt=bytearray();changed=[]
 for i,view in enumerate(doc['bufferViews']):
  while len(rebuilt)%4:rebuilt.append(0)
  payload=original[i]
  if i in replacements:
   image=replacements[i];source=image_files[image['name']] if image_files is not None else A/(image['name']+'.jpg');payload=source.read_bytes();image['mimeType']='image/png' if source.suffix=='.png' else 'image/jpeg';changed.append(image['name'])
  view['byteOffset']=len(rebuilt);view['byteLength']=len(payload);rebuilt.extend(payload)
 while len(rebuilt)%4:rebuilt.append(0)
 doc['buffers'][0]['byteLength']=len(rebuilt)
 # Repack offsets only. Compressed mesh payloads and all other images stay exact.
 for i,view in enumerate(doc['bufferViews']):
  if i not in replacements:assert rebuilt[view['byteOffset']:view['byteOffset']+view['byteLength']]==original[i]
 encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
 output=struct.pack('<III',0x46546C67,2,28+len(encoded)+len(rebuilt))+struct.pack('<II',len(encoded),0x4E4F534A)+encoded+struct.pack('<II',len(rebuilt),0x004E4942)+rebuilt
 assert len(output)<25*1024*1024,'Keep each source asset under hosting limit'
 temp=path.with_suffix('.glb.tmp');temp.write_bytes(output);temp.replace(path)
 return {'file':path.name,'updatedImages':changed,'otherBuffersVerifiedUnchanged':True,'bytes':len(output),'sha256':hashlib.sha256(output).hexdigest()}

if __name__=='__main__':
 report={'material':build_maps(),'models':[refresh_glb(A/name) for name in ['temple.glb','stone-lantern.glb']]}
 (R/'evidence/granite-material-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
