"""Area/volume witnesses that shading refinement has not enlarged the bridge."""
import json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
coarse=json.loads((R/'evidence/bridge-contact-coarse.json').read_text());fine=json.loads((R/'evidence/bridge-contact-samples.json').read_text());report=[]
def metrics(batch):
 p=np.array(batch['positions']).reshape(-1,3);tri=np.array(batch['indices']).reshape(-1,3);a,b,c=(p[tri[:,i]] for i in range(3));cross=np.cross(b-a,c-a);return {'area':float(np.linalg.norm(cross,axis=1).sum()*.5),'signedVolume':float(np.einsum('ij,ij->i',a,np.cross(b,c)).sum()/6),'min':p.min(axis=0),'max':p.max(axis=0)}
for a,b in zip(coarse,fine):
 before,after=metrics(a),metrics(b);area=abs(before['area']-after['area'])/before['area'];volume=abs(before['signedVolume']-after['signedVolume']);bounds=max(float(np.abs(before[k]-after[k]).max()) for k in ['min','max']);assert area<1e-5 and volume<1e-5 and bounds<1e-6,(area,volume,bounds);report.append({'material':a['material'],'relativeAreaError':area,'volumeErrorCubicMeters':volume,'boundsErrorMeters':bounds})
(R/'evidence/bridge-contact-shape-audit.json').write_text(json.dumps(report,indent=2));print(report)
