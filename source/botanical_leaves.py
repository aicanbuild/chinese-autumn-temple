"""Original botanical leaf surfaces, with serration, branching veins and thickness."""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from granite_finish import refresh_glb
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';N=1024
rng=np.random.default_rng(5217)

def noise(scale):
 data=rng.random((scale,scale))*255
 return np.array(Image.fromarray(data.astype('uint8')).resize((N,N),Image.Resampling.BICUBIC))/255

def leaf(kind):
 mask=Image.new('L',(N,N));d=ImageDraw.Draw(mask);vein=Image.new('L',(N,N));v=ImageDraw.Draw(vein)
 if kind=='maple':
  points=[(507,957),(476,737),(78,635),(281,582),(103,333),(337,465),(282,89),(430,354),(514,33),(603,370),(768,129),(713,478),(958,367),(794,595),(935,689),(550,743),(524,957)]
  serrated=[]
  for i,a in enumerate(points):
   b=points[(i+1)%len(points)];length=math.dist(a,b);steps=max(1,int(length/11));dx=(b[0]-a[0])/length;dy=(b[1]-a[1])/length
   for j in range(steps):
    t=j/steps;serrated.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t))
    if 1<=i<=14 and steps>3:
     t=(j+.48)/steps;tooth=3.4*math.sin(math.pi*t)**.4;serrated.append((a[0]+(b[0]-a[0])*t-dy*tooth,a[1]+(b[1]-a[1])*t+dx*tooth))
  d.polygon(serrated,fill=255);root=np.array([516.,710.]);tips=[points[i] for i in [2,4,6,8,10,12,14]]
  for tip in tips:
   tip=np.array(tip);delta=tip-root
   for j in range(35):
    t=j/35;v.line([tuple(root+delta*t),tuple(root+delta*(j+1)/35)],fill=220,width=max(1,int(5*(1-t))))
   for t in np.arange(.22,.9,.105):
    origin=root+delta*t
    for side in [-1,1]:
     end=origin+delta*.16+np.array([-delta[1],delta[0]])*side*.10*(1-t*.5)
     v.line([tuple(origin),tuple(end)],fill=105,width=2)
     for q in [.45,.7]:
      p=origin+(end-origin)*q;branch=p+delta*.04+np.array([-delta[1],delta[0]])*side*.045
      v.line([tuple(p),tuple(branch)],fill=55,width=1)
  base=np.array([169,62,24]);warm=np.array([46,26,8]);v.line([(516,710),(516,954)],fill=230,width=5)
 elif kind=='ginkgo':
  root=(512,777);outline=[(505,951),(497,758)]
  for t in np.linspace(0,1,320):
   a=math.radians(204+132*t);radius=660-94*math.exp(-((t-.50)/.046)**2)+8*math.sin(t*math.pi*30)+4*math.sin(t*math.pi*73)
   outline.append((512+radius*math.cos(a)*.74,777+radius*math.sin(a)))
  outline.extend([(530,754),(523,952)]);d.polygon(outline,fill=255)
  for t in np.linspace(.02,.98,65):
   a=math.radians(204+132*t);end=np.array([512+660*math.cos(a)*.74,777+660*math.sin(a)]);start=np.array(root)
   mid=start+(end-start)*.52;mid[0]+=(t-.5)*12
   v.line([root,tuple(mid),tuple(end)],fill=120,width=2)
   fork=mid+(end-mid)*.22;v.line([tuple(fork),tuple(end+np.array([7 if t>.5 else -7,0]))],fill=70,width=1)
  v.line([(512,777),(514,950)],fill=230,width=6);base=np.array([212,159,30]);warm=np.array([23,38,9])
 else:
  outline=[]
  for t in np.linspace(0,math.tau,280,endpoint=False):
   radius=math.sin(t);width=289*(.94+.06*math.cos(t*3))
   outline.append((512+radius*width+(2 if int(t*70)%2 else -2),487-math.cos(t)*430))
  d.polygon(outline,fill=255);d.line([(510,870),(521,969)],fill=255,width=8);v.line([(512,61),(512,895),(521,969)],fill=230,width=6)
  for y in range(220,830,70):
   width=math.sqrt(max(0,1-((y-487)/430)**2))*270
   for side in [-1,1]:
    start=(512,y+45);end=(512+side*width,y-67);v.line([start,end],fill=115,width=3)
    for t in [.4,.6,.8]:
     p=(512+(end[0]-512)*t,start[1]+(end[1]-start[1])*t);v.line([p,(p[0]+side*width*.19,p[1]-50)],fill=60,width=1)
  base=np.array([77,102,35]);warm=np.array([27,20,5])
 alpha=np.array(mask);veins=np.array(vein.filter(ImageFilter.GaussianBlur(.65)))/255
 broad=noise(9);fine=noise(160);micro=noise(480)
 erosion=np.array(mask.filter(ImageFilter.MinFilter(7)))/255;edge=(alpha/255-erosion)
 pigment=np.clip((broad-.24)*1.6,0,1);color=base+pigment[:,:,None]*warm+(fine[:,:,None]-.5)*15+(micro[:,:,None]-.5)*5
 color+=veins[:,:,None]*np.array([32,28,10]);color-=edge[:,:,None]*np.array([20,12,3])
 # RGB exists outside the silhouette too, avoiding dark mipmap fringes.
 rgba=np.dstack([np.uint8(np.clip(color,0,255)),alpha]);Image.fromarray(rgba).save(A/f'{kind}-leaf.png')
 h=veins*.001+(fine-.5)*.00011+(broad-.5)*.00035
 dy,dx=np.gradient(h);normal=np.stack([-dx/(.18/N),dy/(.18/N),np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255))).save(A/f'{kind}-leaf-normal.png')
 transmission=np.clip(.77-veins*.61-edge*.2+(broad-.5)*.15,.10,.92)
 roughness=np.clip(.73+veins*.12+(fine-.5)*.13,.5,.92)
 surface=np.stack([transmission,roughness,np.ones_like(h)],-1);Image.fromarray(np.uint8(surface*255)).save(A/f'{kind}-leaf-surface.png')
 return {'species':kind,'opaquePixels':int((alpha>127).sum()),'normalReliefMillimeters':1,'surfaceChannels':'R: thin-sheet transmission, G: roughness'}

if __name__=='__main__':
 report=[leaf(k) for k in ['maple','ginkgo','green']]
 exec(compile((R/'source/woodland_textures.py').read_text(),str(R/'source/woodland_textures.py'),'exec'))
 report.append(refresh_glb(A/'woodland.glb',{f'{k}-{variant}':A/f'{k}-{variant}.png' for k in ['maple','ginkgo','green'] for variant in ['leaf','spray']}))
 (R/'evidence/botanical-leaves-verification.json').write_text(json.dumps(report,indent=2));print(report)
