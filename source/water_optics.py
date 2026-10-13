"""Bake periodic refracted photon density and matching ripples, without source imagery."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
SIZE=1024;RAYS=2048;SPAN=4.;DEPTH=.875
# Atlas encodes .65 of the analytical XY slopes; the water shader applies .42.
SURFACE_SLOPE_SCALE=.65*.42

def wavefield(n,seed):
 rng=np.random.default_rng(seed);x=np.arange(n,dtype=np.float32)[None,:]*(SPAN/n);y=x.T
 h=np.zeros((n,n),np.float32);gx=h.copy();gy=h.copy();waves=[]
 for i in range(48):
  while True:
   k=rng.integers(-12,13,size=2)
   if 4<=np.linalg.norm(k)<=12:break
  kx,ky=k*2*np.pi/SPAN;phase=rng.uniform(0,2*np.pi)
  amp=.0042*(4/np.linalg.norm(k))**.8*rng.uniform(.65,1.2)
  theta=x*kx+y*ky+phase;c=np.cos(theta)*amp
  h+=np.sin(theta)*amp;gx+=c*kx;gy+=c*ky
  waves.append([int(k[0]),int(k[1]),float(amp),float(phase)])
 return h,gx,gy,waves

def bake(seed,index):
 h,gx,gy,waves=wavefield(RAYS,seed)
 # Air-to-water refraction at the analytical wave normal (Snell's law).
 length=np.sqrt(1+gx*gx+gy*gy);nx=-gx/length;ny=-gy/length;nz=1/length
 ray=np.array([15.,10.,-24.]);ray/=np.linalg.norm(ray);eta=1/1.333
 dot=ray[0]*nx+ray[1]*ny+ray[2]*nz;factor=eta*dot+np.sqrt(1-eta*eta*(1-dot*dot))
 rx=eta*ray[0]-factor*nx;ry=eta*ray[1]-factor*ny;rz=eta*ray[2]-factor*nz
 travel=(-DEPTH-h)/rz
 x=np.arange(RAYS,dtype=np.float32)[None,:]*(SPAN/RAYS);y=x.T
 px=np.remainder((x+rx*travel)/SPAN*SIZE,SIZE);py=np.remainder((y+ry*travel)/SPAN*SIZE,SIZE)
 ix=px.astype(np.int32);iy=py.astype(np.int32);fx=px-ix;fy=py-iy
 density=np.zeros(SIZE*SIZE,np.float64)
 # Bilinear photon splatting avoids point-sample holes in low-density regions.
 for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
  ids=(((iy+dy)%SIZE)*SIZE+(ix+dx)%SIZE).ravel()
  density+=np.bincount(ids,weights=weight.ravel(),minlength=SIZE*SIZE)
 density=density.reshape(SIZE,SIZE)/(RAYS/SIZE)**2
 energy=float(density.mean());assert abs(energy-1)<1e-6
 # Highlights are stored in linear space, with a finite sun-sized soft core.
 highlights=np.clip((density-.8)/5,0,1)
 image=Image.fromarray(np.round(highlights*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.55))
 # Caustic RGB transport maps are generated below by caustic_transport.py.
 _,sx,sy,_=wavefield(SIZE,seed);length=np.sqrt(1+sx*sx+sy*sy)
 rgb=np.stack([-.65*sx/length,-.65*sy/length,1/length],axis=-1)*.5+.5
 Image.fromarray(np.round(np.clip(rgb,0,1)*255).astype('uint8')).save(A/f'pond-ripples-{index}.png',optimize=True)
 return {'seed':seed,'waves':waves,'photonEnergy':energy,'peakDensity':float(density.max()),'highlightFraction':float((highlights>.3).mean())}

if __name__=='__main__':
 result={'spanMeters':SPAN,'depthMeters':DEPTH,'raysPerLayer':RAYS*RAYS,'resolution':SIZE,'layers':[bake(719,0),bake(2031,1)]}
 (A/'pond-optics.json').write_text(json.dumps(result,separators=(',',':')))
 print({k:v for k,v in result.items() if k!='layers'});print([{k:v for k,v in l.items() if k!='waves'} for l in result['layers']])

 # Keep the current depth-dependent caustics after a full optics rebuild.
 import caustic_transport
