"""Original seamless citrus peel; deterministic pores at a roughly submillimetre scale."""
from pathlib import Path
import numpy as np
from PIL import Image
A=Path(__file__).resolve().parents[1]/'dist/assets';N=1024;rng=np.random.default_rng(5431)
y,x=np.mgrid[0:N,0:N];u=x/N;v=y/N
# Periodic coordinates keep the longitude seam continuous.
coarse=(np.sin(u*np.pi*6+.6*np.sin(v*np.pi*4))+np.cos(u*np.pi*10-v*np.pi*6))*.5
h=np.zeros((N,N));pores=np.zeros((N,N))
for k in range(14000):
 px=rng.integers(N);py=rng.integers(N);r=rng.uniform(.55,1.3);rad=4;ox=np.arange(-rad,rad+1);oy=ox[:,None];bump=np.exp(-(ox*ox+oy*oy)/(2*r*r));yy=(py+oy)%N;xx=(px+ox)%N
 pores[yy,xx]+=bump;h[yy,xx]-=bump*rng.uniform(.4,.8)
noise=rng.normal(0,.08,(N,N));h+=noise
color=np.zeros((N,N,3))+[232,124,20];color+=coarse[...,None]*[7,13,5];color-=np.clip(pores,0,2)[...,None]*[5,10,3];color+=noise[...,None]*3
Image.fromarray(np.uint8(np.clip(color,0,255))).save(A/'citrus-peel.jpg',quality=94)
dx=(np.roll(h,-1,1)-np.roll(h,1,1))*.27;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*.27;n=np.stack([-dx,dy,np.ones_like(h)],-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
Image.fromarray(np.uint8((n*.5+.5)*255)).save(A/'citrus-peel-normal.jpg',quality=95,subsampling=0)
rough=np.clip(.60+pores*.05+coarse*.03,.48,.78);Image.fromarray(np.uint8(rough*255)).save(A/'citrus-peel-rough.jpg',quality=93)
print('CITRUS original 1K color/normal/roughness generated')
