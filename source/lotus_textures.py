"""Original parametric petal pigment and radial leaf veins; no photo copying."""
from pathlib import Path
import numpy as np
from PIL import Image
A=Path(__file__).resolve().parents[1]/'dist/assets';N=1024
v,u=np.mgrid[0:N,0:N]/(N-1);t=1-v
rng=np.random.default_rng(619)
def save(name,c,h,strength):
 Image.fromarray(np.uint8(np.clip(c,0,255))).save(A/(name+'.jpg'),quality=93)
 dy,dx=np.gradient(h);normal=np.stack([-dx*strength,dy*strength,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 Image.fromarray(np.uint8((normal*.5+.5)*255)).save(A/(name+'-normal.png'))
veins=np.exp(-np.sin((u-.5)*(22-8*t)+.35*np.sin(t*6))**2*60)
noise=rng.normal(0,1,(N,N));pink=np.clip(t**2*.80+abs(u-.5)**2*.6,0,1)
c=np.array([242,225,202])[None,None,:]*(1-pink[...,None])+np.array([220,86,139])[None,None,:]*pink[...,None]
c-=veins[...,None]*np.array([1.5,7,4])+noise[...,None]*.55
save('lotus-petal',c,veins*.12+noise*.002,12)
x=(u-.5)*2;y=(v-.5)*2;r=np.sqrt(x*x+y*y);a=np.arctan2(y,x)
primary=np.exp(-np.sin(a*7)**2*180)*np.clip(r*8,0,1)
secondary=np.exp(-np.sin(a*28+r*31)**2*100)*.3
h=primary*.12+secondary*.018+noise*.001
mottle=np.sin(x*18+y*9)*np.sin(y*14-x*7)*2
c=np.zeros((N,N,3))+np.array([66,100,59]);c+=primary[...,None]*np.array([19,25,8]);c+=secondary[...,None]*np.array([9,12,3]);c+=mottle[...,None]+noise[...,None]*.6
save('lotus-leaf',c,h,18)
print('LOTUS: four original 1024px pigment/normal maps')
