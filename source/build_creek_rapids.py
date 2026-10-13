"""Bake rock-registered hydraulic relief and breaking zones from the actual Blender stones."""
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
rocks=json.loads((R/'source/creek-rock-surfaces.json').read_text());w,h=256,1536;x,z=np.meshgrid(np.linspace(12,18,w),np.linspace(-18,20,h));base=np.zeros_like(x);energy=np.zeros_like(x);foam=np.zeros_like(x);jets=[]
for i,r in enumerate(rocks):
 top=r['top'];rx,rz=r['rx'],r['rz'];dx=x-r['x'];dz=z-r['z'];q2=(dx/(rx*1.07))**2+(dz/(rz*1.07))**2
 # The lowest stones become spill lips. Taller ones retain dry crowns.
 overflow=top<.155
 if overflow:
  solid=-.15+(top+.15)*np.sqrt(np.maximum(0,1-q2))
  base=np.maximum(base,np.where(q2<1,np.maximum(0,solid+.025+.055),0))
  jets.append({**r,'top':top,'lipY':top+.047,'lipZ':r['z']+rz*.40,'width':rx*.72,'length':.42+rx*.38,'seed':i*.71})
 pressure=np.exp(-(dx/(rx*.85))**2-((dz+rz*.85)/(.28+rz*.12))**2)*.075
 base=np.maximum(base,pressure)
 downstream=np.maximum(0,dz-rz*.6);wake=np.exp(-downstream/1.6)*np.exp(-(dx/(rx*.70+downstream*.25))**2)*np.clip((dz-rz*.35)/.30,0,1)
 shoulders=np.exp(-((abs(dx)-rx*.91)/.16)**2-(dz/(rz*1.4))**2)
 energy=np.maximum(energy,wake*.92+shoulders*.3);foam=np.maximum(foam,wake*.95+shoulders*.32)
 # Keep overflow sheets above solid stone instead of oscillating through it.
 if overflow:energy*=np.where(q2<.9,.07,1)
cx=15+.7*np.cos((z+9)*.22);width=(1.07+.17*np.sin(z*.51)+.11*np.sin(z*1.12))*np.minimum(1,np.minimum(.14+(z+72)/3,.14+(20-z)/2))*np.exp(np.minimum(0,(z+14)/28));bank=np.clip((.94-abs(x-cx)/width)/.22,0,1);bank=bank*bank*(3-2*bank)
bank*=np.clip((z+18)/.6,0,1)*np.clip((20-z)/.6,0,1)
base*=bank;energy*=bank;foam*=bank
rgba=np.stack([base/.55,energy,foam,bank],-1);Image.fromarray(np.uint8(np.clip(rgba,0,1)*255)).save(A/'creek-rapids.png')
(A/'creek-rapids.json').write_text(json.dumps({'bounds':[12,18,-18,20],'heightRange':.55,'jets':jets,'rocks':len(rocks),'maxRelief':float(base.max()),'description':'Rock-registered overflow lips, shoulder surges, downstream breaking rollers'},indent=2))
print(json.dumps({'overflowLips':len(jets),'rocks':len(rocks),'height':float(base.max()),'profile':[w,h]}))
