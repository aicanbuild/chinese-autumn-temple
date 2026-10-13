"""Original periodic sediment maps; replace images without changing temple geometry."""
from pathlib import Path
import numpy as np
from PIL import Image
import json,shutil,hashlib
from granite_finish import refresh_glb
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';E=R/'evidence';rng=np.random.default_rng(1742);N=1024
for name in ['temple.glb','sand.jpg','sand-normal.jpg','sand-rough.jpg']:
 backup=E/('calm-wave-before-'+name)
 if not backup.exists():shutil.copy2(A/name,backup)
# Fourier low-pass fields have periodic values and derivatives in both axes.
f=np.fft.fftfreq(N);fy,fx=np.meshgrid(f,f,indexing='ij');frequency=fx*fx+fy*fy
def field(radius):
 a=np.fft.ifft2(np.fft.fft2(rng.standard_normal((N,N)))*np.exp(-2*np.pi*np.pi*radius*radius*frequency)).real;a-=a.mean();return a/a.std()
coarse=.65*field(72)+.25*field(28)+.10*field(9);fine=field(.8);mid=field(2.8)
original=np.asarray(Image.open(E/'calm-wave-before-sand.jpg'),dtype=float);mean=original.mean(axis=(0,1))
color=mean+coarse[:,:,None]*np.array([3.8,3.7,2.8])+fine[:,:,None]*.8
# Half-millimetre sediment relief at the existing native physical UV pitch.
h=.00018*mid+.00011*fine
sx=(np.roll(h,-1,1)-np.roll(h,1,1))/(2*(30/7/N));sy=(np.roll(h,-1,0)-np.roll(h,1,0))/(2*(18/7/N))
normal=np.stack([-sx,sy,np.ones_like(h)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
rough=.95+.010*coarse+.012*fine
for suffix,pixels in [('',color),('-normal',(normal*.5+.5)*255),('-rough',rough*255)]:
 Image.fromarray(np.uint8(np.clip(np.round(pixels),0,255))).save(A/f'sand{suffix}.jpg',quality=95,subsampling=0)
# Only opaque sediment images change; AO factors depend on the byte-exact
# preserved geometry, not these receiver colors/normal/roughness maps.
oldHash=hashlib.sha256((A/'temple.glb').read_bytes()).hexdigest()
report=refresh_glb(A/'temple.glb',{name:A/(name+'.jpg') for name in ['sand','sand-normal','sand-rough']})
for name in ['hall-contact-ao.json','mural-contact-ao.json']:
 p=A/name;meta=json.loads(p.read_text());assert meta['inputs']['temple.glb']==oldHash;meta['inputs']['temple.glb']=report['sha256'];p.write_text(json.dumps(meta,indent=2))
checks=[]
for name in ['sand.jpg','sand-normal.jpg','sand-rough.jpg']:
 old=np.asarray(Image.open(E/('calm-wave-before-'+name)),dtype=float);new=np.asarray(Image.open(A/name),dtype=float)
 def edges(a):
  return [float(np.abs(a[0]-a[-1]).mean()),float(np.abs(a[:,0]-a[:,-1]).mean())]
 checks.append({'image':name,'beforeEdgeMeanDifference':edges(old),'afterEdgeMeanDifference':edges(new)})
report['seams']=checks;report['meanColorBefore']=mean.tolist();report['meanColorAfter']=np.asarray(Image.open(A/'sand.jpg'),dtype=float).mean(axis=(0,1)).tolist();report['nativeTileMeters']=[30/7,18/7]
assert max(checks[0]['afterEdgeMeanDifference'])<2
(E/'pond-sediment-finish.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
