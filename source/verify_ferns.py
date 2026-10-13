"""Validate actual embedded pixels, not only the glTF alphaMode declaration."""
import json,struct,io
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import numpy as np
R=Path(__file__).resolve().parents[1];A=R/'dist/assets/fern'
b=(A/'fern-cutout.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0]
d=json.loads(b[20:20+n]);binary=b[28+n:]
assert len(d['meshes'])==4
m=d['materials'][0]
assert m['alphaMode']=='MASK' and m.get('alphaCutoff',.5)==.5
assert m['doubleSided']
idx=d['textures'][m['pbrMetallicRoughness']['baseColorTexture']['index']]['source']
v=d['bufferViews'][d['images'][idx]['bufferView']]
im=Image.open(io.BytesIO(binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]))
assert im.mode=='RGBA' and im.size==(2048,2048)
alpha=im.getchannel('A');original=Image.open(A/'textures/fern_02_alpha_2k.png')
# The official mask is 16-bit; PIL convert('L') would clip instead of rescale it.
original=Image.fromarray(np.rint(np.asarray(original,dtype=float)/257).astype('uint8'))
delta=ImageStat.Stat(ImageChops.difference(alpha,original)).mean[0]
assert delta<1,delta
h=alpha.histogram();assert sum(h[:128])>im.width*im.height*.30
assert sum(h[128:])>im.width*im.height*.10
assert all('TEXCOORD_0' in p['attributes'] for mesh in d['meshes'] for p in mesh['primitives'])
assert all('bufferView' in image for image in d['images'])
report={'variants':4,'embeddedImages':len(d['images']),'rgbaSize':list(im.size),'alphaMeanError':delta,'transparentPixelFraction':sum(h[:128])/(im.width*im.height),'sizeBytes':len(b)}
(R/'evidence/fern-cutout-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
