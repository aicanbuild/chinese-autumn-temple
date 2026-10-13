"""Original lotus/cloud weaving maps; no photographic or museum texture copied."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import math
A=Path(__file__).resolve().parents[1]/'dist/assets';W,H=1536,2560
mask=Image.new('L',(W,H));d=ImageDraw.Draw(mask)
def path(points,width=5,fill=255):d.line([(int(x*W),int(y*H)) for x,y in points],fill=fill,width=width,joint='curve')
def petal(cx,cy,angle,length,width):
 pts=[]
 for side in [1,-1]:
  for t in (np.linspace(0,1,55) if side==1 else np.linspace(1,0,55)):
   u=length*t;v=side*width*math.sin(math.pi*t)**.8
   pts.append((cx+u*math.cos(angle)-v*math.sin(angle),cy+(u*math.sin(angle)+v*math.cos(angle))*.56))
 path(pts+[pts[0]],5)
 for delta in [-.22,0,.22]:
  path([(cx+length*t*math.cos(angle)-delta*width*math.sin(math.pi*t)*math.sin(angle),cy+(length*t*math.sin(angle)+delta*width*math.sin(math.pi*t)*math.cos(angle))*.56) for t in np.linspace(.13,.86,35)],2,185)
# Woven double border, fine running stitch and restrained cloud scrolls.
for inset,width in [(.034,7),(.055,2)]:d.rectangle((inset*W,inset*H,(1-inset)*W,(1-inset)*H),outline=235,width=width)
for i in range(86):
 y=.075+i*.01
 for x in [.044,.956]:path([(x,y),(x,y+.004)],2,180)
for cx in [.14,.86]:
 for cy in np.arange(.15,.95,.13):
  path([(cx+.045*math.cos(t)*(1-t/8),cy+.025*math.sin(t)*(1-t/8)) for t in np.linspace(0,6,100)],3,185)
# Front medallion: interlaced lotus petals, seed heart, and sweeping foliage.
cx,cy=.5,.80
for phase,length,width in [(0,.23,.060),(math.pi/8,.145,.048)]:
 for k in range(8):petal(cx,cy,k*math.tau/8+phase,length,width)
for r in [.032,.042]:d.ellipse(((cx-r)*W,(cy-r*.56)*H,(cx+r)*W,(cy+r*.56)*H),outline=230,width=3)
for side in [-1,1]:
 path([(cx+side*(.06+.24*t),cy+.17*t-.025*math.sin(t*math.tau)) for t in np.linspace(0,1,100)],5,220)
 for i in range(3):petal(cx+side*(.105+.062*i),cy+.035+.04*i,(math.pi*.25 if side>0 else math.pi*.75),.08,.028)
m=np.asarray(mask.filter(ImageFilter.GaussianBlur(.45)),dtype=np.float32)/255
Y,X=np.mgrid[:H,:W].astype(np.float32)
# Submillimetre satin weave, with alternating over/under yarn highlights in the albedo.
weave=(np.sin(X*math.pi*.8)*np.sin(Y*math.pi*.4))
thread=.96+.04*weave
red=np.array([91,13,22],np.float32);gold=np.array([180,131,54],np.float32)
base=(red[None,None,:]*(1-m[:,:,None])+gold[None,None,:]*m[:,:,None])*thread[:,:,None]
Image.fromarray(np.uint8(np.clip(base,0,255))).save(A/'altar-brocade-color.jpg',quality=95,subsampling=0)
# Metal is limited to the gilt thread; crimson silk remains dielectric.
rough=.62*(1-m)+.36*m;metal=.82*m
orm=np.stack([np.ones_like(m),rough,metal],axis=-1)
Image.fromarray(np.uint8(orm*255)).save(A/'altar-brocade-orm.png',optimize=True)
height=m*.00020+weave*.000015
gy,gx=np.gradient(height,1.07/H,.6/W);normal=np.stack([-gx,gy,np.ones_like(m)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
Image.fromarray(np.uint8(np.clip(normal*.5+.5,0,1)*255)).save(A/'altar-brocade-normal.png',optimize=True)
print('Brocade maps',W,H,'gilt coverage',float((m>.1).mean()))
