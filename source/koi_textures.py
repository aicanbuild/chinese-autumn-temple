"""Original koi skin atlases. Coherent pigment islands, overlapping scales, fin rays."""
from PIL import Image,ImageFilter
import numpy as np
from pathlib import Path
A=Path(__file__).resolve().parents[1]/'dist/assets/koi';A.mkdir(exist_ok=True)
W,H=2048,1024;y,x=np.mgrid[:H,:W];u=x/W;v=1-y/H
rng=np.random.default_rng(8307)
noise=np.zeros((H,W))
for size,amp in [(12,.55),(30,.27),(90,.12),(300,.06)]:
 ar=np.array(Image.fromarray(np.uint8(rng.random((size,size*2))*255)).resize((W,H),Image.Resampling.BICUBIC))/255
 noise+=(ar-.5)*amp
# Pigment follows the dorsal surface, wrapping around the upper sides.
dorsal=(1+np.sin(u*np.pi*2))*.5
for kind in ['kohaku','sanke','yamabuki','platinum']:
 col=np.zeros((H,W,3))+np.array([219,217,200] if kind!='yamabuki' else [208,166,57])
 col+=(noise*14)[...,None]
 col+=((1-dorsal)*10)[...,None]
 pigment=np.zeros((H,W))
 for cu,cv,ru,rv in [(.23,.25,.22,.13),(.29,.52,.24,.16),(.13,.70,.18,.10),(.25,.89,.19,.08)]:
  du=np.minimum(abs(u-cu),1-abs(u-cu));dist=(du/ru)**2+((v-cv)/rv)**2
  pigment=np.maximum(pigment,1-dist+noise*3)
 red=pigment>.08
 if kind in ['kohaku','sanke']:
  pigmentcol=np.stack([171+noise*47,44+noise*27,16+noise*12],-1)
  col=np.where(red[...,None],pigmentcol,col)
 if kind=='sanke':
  black=np.zeros((H,W))
  for cu,cv,ru,rv in [(.1,.34,.10,.06),(.39,.60,.09,.09),(.35,.77,.07,.06),(.11,.51,.07,.05)]:
   du=np.minimum(abs(u-cu),1-abs(u-cu));black=np.maximum(black,1-(du/ru)**2-((v-cv)/rv)**2+noise*3)
  col=np.where((black>.08)[...,None],np.stack([27+noise*15,30+noise*15,28+noise*15],-1),col)
 # Small scales fade over the head, where skin is smooth.
 row=np.floor(v*43);sx=np.mod(u*31+(row%2)*.5,1)-.5;sy=np.mod(v*43,1)
 arc=np.abs(sy-(.30+.66*np.sqrt(np.maximum(0,1-(sx*2)**2))))
 edge=np.exp(-arc*arc/.002);scaleweight=np.clip((.84-v)*16,0,1)*np.clip((v-.03)*15,0,1)
 ridge=edge*scaleweight
 col-=ridge[...,None]*np.array([20,19,15]);col+=(np.exp(-(arc-.045)**2/.001)*scaleweight)[...,None]*8
 Image.fromarray(np.uint8(np.clip(col,0,255))).save(A/f'{kind}.jpg',quality=94)
# Subtle normal relief, not embossed armor.
h=(ridge*.025+noise*.002);dy,dx=np.gradient(h);n=np.stack([-dx*34,-dy*18,np.ones_like(dx)],-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
Image.fromarray(np.uint8(n*127+128)).save(A/'scales-normal.jpg',quality=95)
Image.fromarray(np.uint8(np.clip(109+ridge*14+noise*5,0,255))).save(A/'scales-rough.jpg',quality=92)
# Thin translucent fin membranes have fine bifurcating rays, with softly faded rims.
W=512;H=512;y,x=np.mgrid[:H,:W];u=x/W;v=y/H
ray=np.power(.5+.5*np.cos(u*2*np.pi*17+np.sin(v*5)*.3),24)
rgba=np.zeros((H,W,4));rgba[:,:,:3]=np.array([202,191,155])+ray[...,None]*24
rgba[:,:,3]=np.clip(80+ray*110+(1-v)*42,0,255)
Image.fromarray(np.uint8(rgba)).save(A/'fin-membrane.png')
print('Four original koi skin atlases, scale relief and fin membranes generated.')
