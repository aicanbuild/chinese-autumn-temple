"""Delivery-only encoding, retaining 2K resolution and the original normal map."""
from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';report={}
for name,quality in [('garden-moss',97),('garden-moss-rough',95)]:
 source=A/(name+'.jpg');target=A/(name+'-runtime.jpg');im=Image.open(source)
 im.save(target,format='JPEG',quality=quality,subsampling=0,optimize=True)
 delta=np.abs(np.asarray(im,dtype=np.float32)-np.asarray(Image.open(target),dtype=np.float32))
 report[name]={'sourceBytes':source.stat().st_size,'runtimeBytes':target.stat().st_size,'quality':quality,'resolution':im.size,'mode':im.mode,'meanAbsoluteError8bit':float(delta.mean()),'p99Error8bit':float(np.quantile(delta,.99)),'maxError8bit':float(delta.max())}
report['normalMap']='Unchanged original garden-moss-normal.jpg'
(R/'evidence/garden-ground-encoding-pixels.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
