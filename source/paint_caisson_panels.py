"""Original layered temple polychrome motifs; no reference pixels are reused."""
from PIL import Image, ImageDraw
from pathlib import Path
import math
R=Path(__file__).resolve().parents[1];S=2;W,H=1536,512
im=Image.new('RGB',(W*S,H*S),'#173f43');d=ImageDraw.Draw(im)
gold='#c5a469';pale='#e1d3a6';red='#963e34';blue='#15314a';green='#20584f';ink='#102c35'
def line(pts,fill=gold,width=2):d.line([(x*S,y*S) for x,y in pts],fill=fill,width=max(1,int(width*S)),joint='curve')
def box(b,fill,outline=None,width=1):d.rectangle(tuple(v*S for v in b),fill=fill,outline=outline,width=width*S)
def ellipse(b,fill,outline=None,width=1):d.ellipse(tuple(v*S for v in b),fill=fill,outline=outline,width=width*S)
def petal(cx,cy,r,a,color):
 pts=[]
 for side in [1,-1]:
  for j in range(25):
   t=(j/24 if side==1 else 1-j/24);rr=r*(.10+.90*t);w=r*.22*math.sin(math.pi*t)**.65*side
   pts.append((cx+rr*math.cos(a)-w*math.sin(a),cy+rr*math.sin(a)+w*math.cos(a)))
 d.polygon([(x*S,y*S) for x,y in pts],fill=color);line(pts+[pts[0]],gold,1.6)
 line([(cx+r*t*math.cos(a),cy+r*t*math.sin(a)) for t in [.18,.35,.5,.68,.82]],pale,1)
def flower(x,y,r,n=8):
 for k in range(n):petal(x,y,r,k*math.tau/n,red if k%2 else '#617f70')
 for k in range(n):petal(x,y,r*.60,(k+.5)*math.tau/n,'#dac797')
 ellipse((x-r*.14,y-r*.14,x+r*.14,y+r*.14),gold,ink,2)
def scroll(x,y,scale,flip=1):
 pts=[]
 for j in range(85):
  t=j/84;angle=-math.pi*.3+t*math.tau*1.25;r=scale*(1-t*.87);pts.append((x+flip*r*math.cos(angle),y+r*math.sin(angle)))
 line(pts,gold,2.2)
 for j in [12,26,42]:
  px,py=pts[j];a=math.atan2(pts[j+1][1]-py,pts[j+1][0]-px)-flip*.8;petal(px,py,scale*.34,a,'#507c68')
# Interlocking border, double gold pinstripes and vermilion ground.
box((3,3,W-4,H-4),None,gold,3)
for y in [12,H-47]:
 box((12,y,W-13,y+34),red)
 for x in range(15,W-32,36):line([(x,y+27),(x,y+6),(x+27,y+6),(x+27,y+25),(x+10,y+25),(x+10,y+15),(x+19,y+15)],pale,2)
for y in [52,H-53]:
 line([(10,y),(W-10,y)],gold,2)
 for x in range(18,W-12,15):ellipse((x-2,y+6-2,x+2,y+6+2),gold)
# Two complete interstitial coffers sit between the real radial brackets.
for cx in [W*.34,W*.66]:
 b=(cx-170,77,cx+170,H-78);box(b,blue,gold,4);box((cx-157,88,cx+157,H-89),green,pale,1)
 for x in [cx-147,cx+147]:
  for y in [100,H-101]:
   sx=1 if x<cx else -1;sy=1 if y<H/2 else -1
   line([(x+sx*31,y),(x,y),(x,y+sy*31),(x+sx*10,y+sy*31),(x+sx*10,y+sy*10),(x+sx*23,y+sy*10)],gold,2)
 ellipse((cx-125,131,cx+125,381),blue,gold,3);ellipse((cx-116,140,cx+116,372),None,pale,1)
 for k in range(32):
  a=k*math.tau/32;x=cx+110*math.cos(a);y=256+110*math.sin(a);ellipse((x-2,y-2,x+2,y+2),gold)
 flower(cx,256,96,12)
 for x,flip in [(cx-139,1),(cx+139,-1)]:
  for y in [148,361]:scroll(x,y,20,flip)
# Flowing, fine stems along the otherwise bare interstices.
for x in [84,230,768,1306,1452]:
 for y,flip in [(148,1),(358,-1)]:scroll(x,y,57,flip)
 flower(x,256,28,6)
# Subtle pigment variation without coarse timber grain.
import numpy as np
arr=np.array(im).astype('float32');rng=np.random.default_rng(108);arr+=rng.normal(0,.55,arr.shape[:2])[...,None];im=Image.fromarray(np.clip(arr,0,255).astype('uint8'))
path=R/'dist/assets/caisson-polychrome.jpg';im.save(path,quality=94,subsampling=0)
# Square coffer border leaves its center free for the existing raised lotus.
sq=Image.new('RGB',(1024,1024),blue);sd=ImageDraw.Draw(sq)
for inset,color,width in [(12,gold,6),(30,red,17),(48,pale,2),(72,gold,3),(102,green,12)]:sd.rectangle((inset,inset,1023-inset,1023-inset),outline=color,width=width)
for k in range(24):
 p=126+k*33
 for a,b in [(p,83),(p,940),(83,p),(940,p)]:sd.ellipse((a-3,b-3,a+3,b+3),fill=gold)
for cx,cy in [(160,160),(864,160),(160,864),(864,864)]:
 for k in range(8):
  a=k*math.tau/8;pts=[(cx+math.cos(a)*r-math.sin(a)*s,cy+math.sin(a)*r+math.cos(a)*s) for r,s in [(8,0),(37,-10),(59,0),(37,10)]];sd.polygon(pts,fill=gold)
 for rr in [65,73]:sd.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=gold,width=2)
sq.save(R/'dist/assets/caisson-coffer-border.jpg',quality=94,subsampling=0)
print(path,path.stat().st_size)
