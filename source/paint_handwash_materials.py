from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
A=Path(__file__).resolve().parents[1]/'dist/assets';rng=np.random.default_rng(1059);n=1024
y,x=np.mgrid[0:n,0:n];grain=np.sin(x*.22+2.8*np.sin(y*.013)+np.sin(y*.041+x*.01))+.45*np.sin(x*.83+1.2*np.sin(y*.024))
wood=np.array([201,165,108])+grain[:,:,None]*np.array([7,7,5])+rng.normal(0,1.1,(n,n,1));Image.fromarray(np.uint8(np.clip(wood,0,255))).save(A/'handwash-hinoki.jpg',quality=93)
noise=rng.normal(0,1,(n,n));large=np.asarray(Image.fromarray(np.uint8(np.clip(127+noise*38,0,255))).filter(ImageFilter.GaussianBlur(12)),dtype=float)-127
fine=np.asarray(Image.fromarray(np.uint8(np.clip(127+noise*40,0,255))).filter(ImageFilter.GaussianBlur(.7)),dtype=float)-127
h=fine*.014+large*.02;stone=np.array([112,116,110])+fine[:,:,None]*.62+large[:,:,None]*5
quartz=rng.random((n,n));stone[quartz>.993]+=57;stone[quartz<.008]-=40
Image.fromarray(np.uint8(np.clip(stone,0,255))).save(A/'handwash-granite.jpg',quality=94)
dy,dx=np.gradient(h);normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);Image.fromarray(np.uint8((normal*.5+.5)*255)).save(A/'handwash-granite-normal.png')
