"""Rock-aware world-space velocity atlas: RG velocity, B downstream whitewater."""
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];a=R/'dist/assets';layout=json.loads((a/'temple-stream.json').read_text());w,h=256,4096
x,z=np.meshgrid(np.linspace(12,18,w),np.linspace(layout['z0'],layout['z1'],h));cx=15+.7*np.cos((z+9)*.22)
u=.45;vx=-.154*np.sin((z+9)*.22)*u;vz=np.ones_like(x)*u;foam=np.zeros_like(x)
for rock in layout['rocks']:
 dx=x-rock['x'];dz=z-rock['z'];r=rock['radius'];r2=np.maximum(dx*dx+dz*dz,r*r);fade=np.exp(-r2/(r*r*18));
 vx+=-2*u*r*r*dx*dz/(r2*r2)*fade;vz+=u*r*r*(dx*dx-dz*dz)/(r2*r2)*fade
 wake=np.exp(-np.maximum(0,dz-r*.65)/(r*4))*np.exp(-(dx/(r*.45+np.maximum(0,dz)*.19))**2)*(dz>r*.4)
 foam=np.maximum(foam,wake*.88)
vz*=.85+.15*np.sin(z*.9+x*1.7);vx=np.clip(vx,-1.2,1.2);vz=np.clip(vz,.08,1.2)
rgb=np.stack([vx/2.4+.5,vz/2.4+.5,foam],axis=-1)
Image.fromarray(np.uint8(np.clip(rgb,0,1)*255)).save(a/'stream-flow.png')
print(json.dumps({'size':[w,h],'speedRange':[float(np.hypot(vx,vz).min()),float(np.hypot(vx,vz).max())],'maxWake':float(foam.max())}))
