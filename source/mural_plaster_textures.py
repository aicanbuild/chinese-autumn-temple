"""Original numerical mineral-plaster relief, one metre square, no painted-image edits."""
from pathlib import Path
import numpy as np
from PIL import Image
A=Path(__file__).resolve().parents[1]/'dist/assets';N=1024;rng=np.random.default_rng(8117)
y,x=np.mgrid[:N,:N]/N
def field(cycles,terms=16):
 f=np.zeros((N,N),np.float32)
 for _ in range(terms):
  a,b=rng.integers(-cycles,cycles+1,2);f+=np.sin(2*np.pi*(a*x+b*y)+rng.uniform(0,2*np.pi))
 return f/f.std()
broad=field(5);fine=field(150,28);grain=field(360,24)
height=broad*.00007+fine*.000012+grain*.000002
# Tangent-space +Y is up in the image, hence the sign reversal for raster rows.
dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.5*N;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.5*N
normal=np.stack([-dx,dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
rough=np.clip(.84+broad*.015+fine*.025,.74,.94)
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(A/'sanctuary-plaster-normal.png')
Image.fromarray(np.uint8(rough*255)).save(A/'sanctuary-plaster-rough.jpg',quality=94)
print('Plaster maps: 1m repeat, 70 micron broad relief, 12 micron grain, roughness .74-.94')
