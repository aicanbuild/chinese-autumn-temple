"""Check shipped ripple normals against the photon bake's nominal slope field."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
from water_optics import wavefield,SURFACE_SLOPE_SCALE
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';meta=json.loads((A/'pond-caustic-transport.json').read_text());assert meta['surfaceSlopeScale']==SURFACE_SLOPE_SCALE
results=[]
for i,seed in enumerate([719,2031]):
 _,gx,gy,_=wavefield(1024,seed)
 rgb=np.asarray(Image.open(A/f'pond-ripples-{i}.png'),dtype=np.float64)/255
 decoded=np.stack([(.42*(rgb[:,:,0]*2-1)),rgb[:,:,2]*2-1,.42*(rgb[:,:,1]*2-1)],axis=-1);decoded/=np.linalg.norm(decoded,axis=-1,keepdims=True)
 expected=np.stack([-gx*SURFACE_SLOPE_SCALE,np.ones_like(gx),-gy*SURFACE_SLOPE_SCALE],axis=-1).astype(np.float64);expected/=np.linalg.norm(expected,axis=-1,keepdims=True)
 angle=np.arccos(np.clip(np.sum(decoded*expected,axis=-1),-1,1))*180/math.pi;assert angle.max()<.25,angle.max()
 caustic=np.asarray(Image.open(A/f'pond-caustics-{i}.png'),dtype=np.float64)*6/255
 means=caustic.mean(axis=(0,1));assert np.max(abs(means-1))<.002;assert caustic.max()<6
 results.append({'seed':seed,'maxNormalAngleErrorDegrees':float(angle.max()),'meanNormalAngleErrorDegrees':float(angle.mean()),'densityMeanByDepth':means.tolist(),'densityStdByDepth':caustic.std(axis=(0,1)).tolist(),'rmsNominalSlope':float(np.sqrt(np.mean((gx*SURFACE_SLOPE_SCALE)**2+(gy*SURFACE_SLOPE_SCALE)**2)))})
(R/'evidence/calm-water-audit.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
