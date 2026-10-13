"""Continuous koi contours and sub-millimetre scale surface maps; no new skins."""
from pathlib import Path
import math
PROFILE=[(0,.022),(.10,.034),(.27,.097),(.49,.158),(.66,.166),(.79,.138),(.90,.097),(.97,.052),(1,.006)]
D=[(b[1]-a[1])/(b[0]-a[0]) for a,b in zip(PROFILE,PROFILE[1:])]
S=[D[0]]
for i in range(1,len(PROFILE)-1):
 h0=PROFILE[i][0]-PROFILE[i-1][0];h1=PROFILE[i+1][0]-PROFILE[i][0]
 S.append(0 if D[i-1]*D[i]<=0 else (3*(h0+h1))/((2*h1+h0)/D[i-1]+(h1+2*h0)/D[i]))
S.append(D[-1])
def radius(t):
 for i,((a,r),(b,q)) in enumerate(zip(PROFILE,PROFILE[1:])):
  if a<=t<=b:
   h=b-a;u=(t-a)/h
   return (2*u**3-3*u*u+1)*r+(u**3-2*u*u+u)*h*S[i]+(-2*u**3+3*u*u)*q+(u**3-u*u)*h*S[i+1]
 return PROFILE[0][1] if t<0 else PROFILE[-1][1]
def old_radius(t):
 for (a,r),(b,q) in zip(PROFILE,PROFILE[1:]):
  if a<=t<=b:
   f=(t-a)/(b-a);return r+(q-r)*f*f*(3-2*f)
 return .006

def maps():
 import numpy as np
 from PIL import Image
 A=Path(__file__).resolve().parents[1]/'dist/assets/koi';W,H=2048,1024
 y,x=np.mgrid[:H,:W];u=x/W;v=1-y/H
 row=np.floor(v*43);sx=np.mod(u*31+(row%2)*.5,1)-.5;sy=np.mod(v*43,1)
 arc=sy-(.30+.66*np.sqrt(np.maximum(0,1-(sx*2)**2)))
 weight=np.clip((.84-v)*16,0,1)*np.clip((v-.03)*15,0,1)
 # Match the already authored pigment atlas's scale arcs. Fine relief changes
 # reflection rather than drawing additional dark scales into the skin.
 crest=np.exp(-arc*arc/.0032)*weight
 h=.00014*crest+weight*.000003*np.sin(u*math.tau*93)*np.sin(v*math.tau*127)
 # UV U travels around the body; V follows its 1.25 m length. Cylindrical metric
 # avoids the previous pixel-resolution-dependent normal amplitude.
 circumference=np.array([max(.16,math.tau*radius(float(t))) for t in v[:,0]])[:,None]
 dhdu=(np.roll(h,-1,axis=1)-np.roll(h,1,axis=1))*W/2/circumference
 dhdv=-np.gradient(h,axis=0)*H/1.25
 n=np.stack([-dhdu,-dhdv,np.ones_like(h)],-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
 rough=.33+.035*weight+.105*crest+.012*weight*np.sin(u*math.tau*31)*np.cos(v*math.tau*43)
 # Keep smooth head skin and the silver/gold pigments of all four variants.
 for filename,data in [('scales-normal.jpg',np.uint8(np.clip(n*127.5+127.5,0,255))),('scales-rough.jpg',np.uint8(np.clip(rough*255,0,255)))]:Image.fromarray(data).save(A/filename,quality=97,subsampling=0)
 return {'normalSize':[W,H],'reliefPeakMeters':.00014,'roughnessRange':[float(rough.min()),float(rough.max())]}
if __name__=='__main__':print(maps())
