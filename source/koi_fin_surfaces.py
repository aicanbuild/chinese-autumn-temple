"""Original koi fin membrane maps with fine branching rays and a soft rim."""
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'dist/assets/koi';N=1024
y,x=np.mgrid[:N,:N];u=x/(N-1);v=1-y/(N-1);rays=np.zeros_like(u)
for k in range(17):
 center=(k+.5)/17+.001*np.sin(v*3+k*.73)*v
 split=.48+.12*np.sin(k*1.31);branch=np.clip((v-split)/(1-split),0,1)
 width=.0019-.0011*v;trunk=np.exp(-((u-center)/width)**2)
 fork=np.maximum(np.exp(-((u-center-.007*branch)/(width*.67))**2),np.exp(-((u-center+.007*branch)/(width*.67))**2))
 blend=np.clip((v-split)*20,0,1);rays=np.maximum(rays,trunk*(1-blend)+fork*blend)
# Pigment and thickness vary gently; ray reinforcement remains subtle ivory.
grain=np.sin(u*173+v*41)*np.sin(v*211-u*57)*.5
rim=np.clip((1-v)/.025,0,1);rim=rim*rim*(3-2*rim)
alpha=(.19+.39*(1-v)**.8+.25*rays+.012*grain)*rim
color=np.zeros((N,N,3))+np.array([201.,203.,186.]);color+=rays[...,None]*np.array([12,10,5]);color+=(1-v)[...,None]*np.array([7,1,-4]);color+=grain[...,None]*2
rgba=np.concatenate([np.clip(color,0,255),np.clip(alpha*255,0,255)[...,None]],axis=2)
Image.fromarray(np.uint8(rgba)).save(A/'fin-membrane.png')
h=.000065*rays*(.25+.75*v)+.000008*np.sin(u*89+v*8)*np.sin(v*np.pi)
dy,dx=np.gradient(h);normal=np.stack([-dx*N/.24,dy*N/.32,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
Image.fromarray(np.uint8(np.clip(normal*127.5+127.5,0,255))).save(A/'fin-normal.jpg',quality=96,subsampling=0)
print({'resolution':N,'rays':17,'finNormalReliefMeters':.000065,'alphaRange':[float(alpha.min()),float(alpha.max())]})
