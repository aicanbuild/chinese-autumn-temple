"""Original restrained charcoal glaze, with submillimetre surface variation."""
from pathlib import Path
import numpy as np
from PIL import Image
A=Path(__file__).resolve().parents[1]/'dist/assets';n=1024;rng=np.random.default_rng(481)
y,x=np.mgrid[:n,:n]/n
def field(cycles):
 f=np.zeros((n,n))
 for _ in range(24):
  a,b=rng.integers(-cycles,cycles+1,2);f+=np.sin(2*np.pi*(a*x+b*y)+rng.uniform(0,6.28))
 return f/f.std()
wave=field(9);grain=field(150);fine=rng.standard_normal((n,n))
height=wave*.000010+grain*.0000015+fine*.0000003
dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.5/(.24/n);dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.5/(.24/n)
normal=np.stack([-dx,dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
color=np.stack([42+wave*1.2+grain*.3,49+wave*1.3+grain*.4,47+wave*1.2+grain*.3],-1)
rough=np.clip(.38+wave*.018+grain*.012,.30,.47)
Image.fromarray(np.uint8(np.clip(color,0,255))).save(A/'roof-glaze.jpg',quality=95)
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(A/'roof-glaze-normal.png')
Image.fromarray(np.uint8(rough*255)).save(A/'roof-glaze-rough.jpg',quality=95)
print('Original ceramic glaze maps written')
