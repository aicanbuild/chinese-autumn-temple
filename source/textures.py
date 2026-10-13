from PIL import Image, ImageDraw, ImageFilter
import numpy as np, random, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'dist/assets'
ROOT.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(427)
N=1024
def noise(n=N):
    out=np.zeros((n,n))
    for k,a in [(4,.30),(8,.24),(16,.18),(32,.13),(64,.08),(128,.045),(512,.025)]:
        im=Image.fromarray(np.uint8(rng.random((k,k))*255)).resize((n,n),Image.Resampling.BICUBIC)
        out+=np.array(im)/255*a
    return out
def save(name,color,h,rough=.8):
    Image.fromarray(np.uint8(np.clip(color,0,255))).save(ROOT/f'{name}.jpg',quality=93)
    dx,dy=np.gradient(h)
    v=np.stack([-dy*7,-dx*7,np.ones_like(h)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(v*127+128)).save(ROOT/f'{name}-normal.jpg',quality=94)
    Image.fromarray(np.uint8(np.clip(rough*255+(h-h.mean())*32,0,255))).save(ROOT/f'{name}-rough.jpg',quality=90)
y,x=np.mgrid[:N,:N]/N
n=noise(); fine=rng.random((N,N))
grain=np.sin(x*720+np.sin(y*7+x*8)*9+n*26)*.5+.5
grain2=np.sin(x*2500+n*60)*.5+.5
h=.48*n+.16*grain+.06*grain2+.035*fine
col=np.stack([63+h*69,36+h*43,21+h*27],-1)
save('wood',col,h,.77)
n=noise();h=n+.045*fine
col=np.stack([91+n*74,93+n*73,83+n*72],-1)
save('stone',col,h,.89)
n=noise();h=n+.10*fine
col=np.stack([30+n*46,40+n*48,40+n*49],-1)
save('tile',col,h,.76)
n=noise();h=n+.12*fine
col=np.stack([23+n*55,34+n*64,12+n*29],-1)
save('moss',col,h,.95)
n=noise();h=n+.045*fine
col=np.stack([88+n*65,101+n*63,87+n*42],-1)
save('sand',col,h,.96)
# Fine, periodic ripples; seamless across both directions.
for ix in (0,1):
    h=np.zeros((N,N))
    for k in range(16):
        a,b=rng.integers(-14,15,2); h+=np.sin((x*a+y*b)*math.tau+rng.random()*6)*.16/(k+1)
    dx,dy=np.gradient(h)
    v=np.stack([-dy*14,-dx*14,np.ones_like(h)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(v*127+128)).save(ROOT/f'water-normal-{ix}.jpg',quality=96)
# A leaf's actual silhouette and its branching venation, with translucent ragged edges.
for name,base in [('maple',(176,64,22)),('ginkgo',(222,166,34)),('green',(94,113,42))]:
    sz=512; im=Image.new('RGBA',(sz,sz));d=ImageDraw.Draw(im)
    if name=='maple':
        pts=[(256,468),(222,362),(106,387),(137,316),(37,261),(120,249),(79,142),(181,191),(194,83),(230,120),(256,18),(283,119),(319,81),(330,190),(430,139),(391,248),(477,260),(376,315),(408,388),(292,361)]
    elif name=='ginkgo':
        pts=[(256,467),(235,363),(140,319),(62,245),(35,152),(94,73),(185,41),(249,77),(276,44),(375,63),(460,145),(476,211),(419,289),(310,361)]
    else: pts=[(256,475),(154,366),(107,208),(152,82),(256,26),(353,104),(396,237),(336,374)]
    d.polygon(pts,fill=(*base,255))
    d.line([(256,488),(256,65)],fill=(115,77,26,255),width=4)
    ends=pts[1:-1:2] if name!='green' else [(131,210),(164,320),(359,230),(330,343)]
    for ex,ey in ends:
        start=(256,399 if name=='ginkgo' else 305)
        d.line([start,(ex,ey)],fill=tuple(min(255,c+36) for c in base)+(235,),width=2)
        for t in [.35,.5,.65,.8]:
            px=start[0]+(ex-start[0])*t;py=start[1]+(ey-start[1])*t
            d.line([(px,py),(px+(ex-256)*.2,py-26)],fill=(*[min(255,c+17) for c in base],180),width=1)
    ar=np.array(im).astype(float);tex=noise(512); variation=(tex-.5)*72+rng.random((512,512))*12
    ar[:,:,:3]+=variation[:,:,None]
    Image.fromarray(np.uint8(np.clip(ar,0,255))).save(ROOT/f'{name}-leaf.png')
print('Generated original PBR material sets and leaf atlases.')
