"""Original bronze casting and incense-ash microstructure, in physical scale."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
A=Path(__file__).resolve().parents[1]/'dist/assets';n=1024;rng=np.random.default_rng(8726)
y,x=np.mgrid[:n,:n]/n
noise=rng.random((n,n))
def blurred(a,r):return np.asarray(Image.fromarray(np.uint8(a*255)).filter(ImageFilter.GaussianBlur(r)),dtype=float)/255
cloud=blurred(rng.random((n,n)),11);cloud=(cloud-cloud.mean())/(cloud.std()+1e-8)
fine=blurred(noise,.55);pore=(noise>.989)*rng.random((n,n))
h=.035*fine-.075*blurred(pore,1.1)
tarnish=np.clip((cloud-.5)*.09,0,.27)
col=np.stack([164+cloud*5+fine*8,115+cloud*4+fine*6,61+cloud*3+fine*4],-1)*(1-tarnish[...,None])
def save(name,color,height,rough,strength=2):
 Image.fromarray(np.uint8(np.clip(color,0,255))).save(A/f'{name}.jpg',quality=93)
 dy,dx=np.gradient(height);normal=np.stack([-dx*strength,-dy*strength,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 Image.fromarray(np.uint8(np.clip(normal*127.5+127.5,0,255))).save(A/f'{name}-normal.png')
 Image.fromarray(np.uint8(np.clip(rough,0,1)*255)).save(A/f'{name}-rough.jpg',quality=92)
save('incense-bronze',col,h,.37+tarnish*.5+fine*.08,4)
# 0.64 m across: discrete grains and fine carbon remain sub-millimetre to 2 mm.
grains=rng.random((n,n));h=blurred(grains,.45)*.24;soot=np.zeros((n,n))
for px,py in [(-.095,-.03),(0,.07),(.095,-.03)]:
 d=((x-.5)*.64-px)**2+((y-.5)*.64-py)**2;soot+=np.exp(-d/.00019)*.22
base=173+(h-.12)*160-soot*120
color=np.stack([base+9,base+6,base-3],-1)
save('incense-ash',color,h,np.ones((n,n))*.97,4)
print('Original bronze and ash texture sets generated.')
