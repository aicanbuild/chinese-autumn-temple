"""Original seamless gold leaf finish: 24 cm tile, three 8 cm leaves per axis."""
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';n=1024
rng=np.random.default_rng(912);y,x=np.mgrid[:n,:n]/n
def field(cycles):
 f=np.zeros((n,n))
 for _ in range(24):
  kx,ky=rng.integers(-cycles,cycles+1,2);f+=np.cos(2*np.pi*(kx*x+ky*y)+rng.uniform(0,2*np.pi))
 return f/(f.std()+1e-9)
cloud=field(5);hammer=field(70);fine=rng.standard_normal((n,n))
u=x+.0007*np.sin(y*np.pi*18);v=y+.0007*np.sin(x*np.pi*12)
du=np.abs((u*3+.5)%1-.5)/3;dv=np.abs((v*3+.5)%1-.5)/3
seam=np.maximum(np.exp(-(du/.0015)**2),np.exp(-(dv/.0015)**2))
height=hammer*.000006+fine*.0000005+seam*.000009
dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.5/(.24/n)
dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.5/(.24/n)
normal=np.stack([-dx,dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
variation=cloud*1.8+hammer*.8-seam*3
color=np.stack([220+variation,181+variation,104+variation],-1)
rough=np.clip(.29+cloud*.022+hammer*.014+seam*.035,.21,.40)
Image.fromarray(np.uint8(np.clip(color,0,255))).save(A/'sanctuary-gold-leaf.jpg',quality=95)
Image.fromarray(np.uint8(np.clip(normal*.5+.5,0,1)*255)).save(A/'sanctuary-gold-leaf-normal.png')
Image.fromarray(np.uint8(rough*255)).save(A/'sanctuary-gold-leaf-rough.jpg',quality=95)
print('Original gold leaf maps generated: 1024 square, 24 cm tile')
