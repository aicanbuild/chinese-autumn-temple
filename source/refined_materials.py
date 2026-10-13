"""Original fine-grained finishes for the restored temple, deterministic and tileable."""
from PIL import Image
import numpy as np
from pathlib import Path
A=Path(__file__).resolve().parents[1]/'dist/assets'
n=1024; y,x=np.mgrid[:n,:n]/n; rng=np.random.default_rng(108)
def save(name,col,h,rough):
 Image.fromarray(np.uint8(np.clip(col,0,255))).save(A/f'{name}.jpg',quality=92)
 dx,dy=np.gradient(h);v=np.stack([-dy*3,-dx*3,np.ones_like(h)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
 Image.fromarray(np.uint8(v*127+128)).save(A/f'{name}-normal.jpg',quality=91)
 Image.fromarray(np.uint8(np.clip(rough*255+h*5,0,255))).save(A/f'{name}-rough.jpg',quality=90)
grain=np.sin(y*1600+np.sin(x*6.283)*4+np.sin(y*6.283)*18)*.5+.5
fine=rng.random((n,n));h=grain*.07+fine*.025
save('lacquer',np.stack([70+grain*15+fine*3,39+grain*9+fine*2,22+grain*6+fine*2],-1),h,.49)
speck=rng.normal(0,1,(n,n));cloud=np.sin(x*6.283)*np.cos(y*12.566)*1.2
h=speck*.015
save('cut-granite',np.stack([179+speck*9+cloud,177+speck*8+cloud,165+speck*8+cloud],-1),h,.68)
h=fine*.025+np.sin(x*6.283)*.015
save('glazed-tile',np.stack([31+fine*5,39+fine*5,38+fine*5],-1),h,.34)
print('Restored lacquer, honed granite and glazed ceramic textures written.')
