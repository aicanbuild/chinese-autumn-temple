"""Bake depth-dependent photon density in RGB, using the actual courtyard sun.

Original procedural wave field, 4,194,304 rays per layer, periodic splatting.
RGB stores depths .25/.875/1.6 m in linear density / 6, not coloured light.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from water_optics import wavefield,SURFACE_SLOPE_SCALE
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
SIZE=1024;RAYS=2048;SPAN=4.;DEPTHS=[.25,.875,1.6]
daylight=json.loads((A/'daylight.json').read_text())
direction=np.array(daylight['sunTarget'],dtype=np.float64)-np.array(daylight['sunPosition']);direction/=np.linalg.norm(direction)
# wavefield coordinates are world x/z, with the third axis vertically upwards.
ray=direction[[0,2,1]];eta=1/1.333
x=np.arange(RAYS,dtype=np.float32)[None,:]*(SPAN/RAYS);y=x.T
reports=[]
for index,seed in enumerate([719,2031]):
 h,gx,gy,_=wavefield(RAYS,seed);h*=SURFACE_SLOPE_SCALE;gx*=SURFACE_SLOPE_SCALE;gy*=SURFACE_SLOPE_SCALE;length=np.sqrt(1+gx*gx+gy*gy);nx=-gx/length;ny=-gy/length;nz=1/length
 dot=ray[0]*nx+ray[1]*ny+ray[2]*nz;factor=eta*dot+np.sqrt(1-eta*eta*(1-dot*dot))
 rx=eta*ray[0]-factor*nx;ry=eta*ray[1]-factor*ny;rz=eta*ray[2]-factor*nz
 channels=[];layers=[]
 for depth in DEPTHS:
  travel=(-depth-h)/rz
  px=np.remainder((x+rx*travel)/SPAN*SIZE,SIZE);py=np.remainder((y+ry*travel)/SPAN*SIZE,SIZE)
  ix=px.astype(np.int32);iy=py.astype(np.int32);fx=px-ix;fy=py-iy
  density=np.zeros(SIZE*SIZE,np.float64)
  for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
   ids=(((iy+dy)%SIZE)*SIZE+(ix+dx)%SIZE).ravel();density+=np.bincount(ids,weights=weight.ravel(),minlength=SIZE*SIZE)
  density=density.reshape(SIZE,SIZE)/(RAYS/SIZE)**2
  energy=float(density.mean());assert abs(energy-1)<1e-6
  # Small periodic low-pass for finite emitter size; no dark texture-border seam.
  density=(density*4+np.roll(density,1,0)+np.roll(density,-1,0)+np.roll(density,1,1)+np.roll(density,-1,1))/8
  density=np.minimum(density,5);density/=density.mean();assert density.max()<6
  channel=np.round(density/6*255).astype('uint8');decoded=channel.astype(np.float64)*6/255
  assert abs(decoded.mean()-1)<.002
  channels.append(channel);layers.append({'depth':depth,'photonEnergy':energy,'encodedMean':float(decoded.mean()),'peak':float(decoded.max()),'standardDeviation':float(decoded.std())})
 Image.fromarray(np.stack(channels,axis=-1)).save(A/f'pond-caustics-{index}.png',optimize=True)
 reports.append({'seed':seed,'depths':layers});print(reports[-1],flush=True)
result={'revision':3,'surfaceSlopeScale':SURFACE_SLOPE_SCALE,'spanMeters':SPAN,'depthsMeters':DEPTHS,'densityDecodeScale':6,'raysPerLayer':RAYS*RAYS,'resolution':SIZE,'sunTravelDirectionWorld':direction.tolist(),'imageFlipY':False,'layers':reports}
(A/'pond-caustic-transport.json').write_text(json.dumps(result,indent=2))
