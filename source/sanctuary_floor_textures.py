"""Original seamless honed limestone maps; 1.6 metres across the texture."""
from pathlib import Path
import numpy as np
from PIL import Image
A=Path(__file__).resolve().parents[1]/'dist/assets';N=2048;rng=np.random.default_rng(7088)
y,x=np.mgrid[:N,:N]/N
def field(cycles,terms=14):
 f=np.zeros((N,N),np.float32)
 for _ in range(terms):
  a,b=rng.integers(-cycles,cycles+1,2);f+=np.sin(2*np.pi*(a*x+b*y)+rng.uniform(0,np.pi*2))
 return f/max(f.std(),.001)
broad=field(3);cloud=field(12);grain=field(320,20);fine=rng.normal(0,1,(N,N));ribbon=np.sin(2*np.pi*(2*x+3*y)+broad*.65+cloud*.07)
vein=np.exp(-((ribbon+.18)/.034)**2);density=np.clip(.5+broad*.18,0,1)
color=np.zeros((N,N,3))+[158,157,145];color+=(broad*.8+cloud*.55)[...,None]*[3.3,3.1,2.7];color+=grain[...,None]*1.2+fine[...,None]*.55;color-=vein[...,None]*density[...,None]*[7,6,4]
# Honing removes relief: only micrometre mineral variation remains.
height=cloud*.0000015+grain*.000002+fine*.00000035-vein*.000001
dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.5/(1.6/N);dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.5/(1.6/N)
normal=np.stack([-dx,dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
rough=np.clip(.36+cloud*.017+grain*.011+vein*.024,.29,.46)
Image.fromarray(np.uint8(np.clip(color,0,255))).save(A/'sanctuary-stone.jpg',quality=95)
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(A/'sanctuary-stone-normal.png')
Image.fromarray(np.uint8(rough*255)).save(A/'sanctuary-stone-rough.jpg',quality=94)
print('Original limestone maps: 2K, 1.6m repeat, micron relief')
