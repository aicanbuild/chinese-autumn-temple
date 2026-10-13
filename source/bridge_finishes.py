"""Original, seamless fine chased-copper finish; a 24 cm physical texture tile."""
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';n=1024;size=.24
rng=np.random.default_rng(3409);y,x=np.mgrid[:n,:n]/n
# Smooth periodic casting variation and finer hammer planishing, without grime blobs.
def field(cycles):
 f=np.zeros((n,n))
 for _ in range(22):
  kx,ky=rng.integers(-cycles,cycles+1,2);f+=np.cos(2*np.pi*(kx*x+ky*y)+rng.uniform(0,2*np.pi))
 return f/(f.std()+1e-9)
cloud=field(10);hammer=field(80);fine=rng.standard_normal((n,n))
# Micron-scale finishing scratches: long horizontal bands interrupted in U.
brushed=np.zeros((n,n))
for _ in range(180):
 line=rng.uniform();width=rng.uniform(.0005,.0013);dist=np.abs((y-line+.5)%1-.5)
 gate=(.5+.5*np.cos(2*np.pi*(rng.integers(1,5)*x+rng.uniform())))**6
 brushed+=np.exp(-dist**2/(2*width**2))*gate
height=hammer*.000009+fine*.0000015-brushed*.000012
# Normal from metric slope; OpenGL +Y tangent normal with image rows top-to-bottom.
dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.5/(size/n)
dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.5/(size/n)
normal=np.stack([-dx,dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
shade=np.clip(238+cloud*3+hammer*1.5-brushed*5,212,250)
color=np.stack([shade,shade-2,shade-6],-1)
rough=np.clip(.61+cloud*.035+brushed*.05+fine*.005,.49,.78)
Image.fromarray(np.uint8(color)).save(A/'bridge-copper.jpg',quality=94)
Image.fromarray(np.uint8(np.clip(normal*.5+.5,0,1)*255)).save(A/'bridge-copper-normal.png')
Image.fromarray(np.uint8(rough*255)).save(A/'bridge-copper-rough.jpg',quality=95)
print('Bridge copper maps: 1024² / 0.24 m, micron relief, periodic derivatives')
