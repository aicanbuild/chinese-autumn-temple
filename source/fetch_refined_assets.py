"""Pinned CC0 environment and clean hardwood maps for the restored temple."""
from pathlib import Path
import json,subprocess
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
def api(asset):return json.loads(subprocess.check_output(['curl','-sSL','--fail','--max-time','45','https://api.polyhaven.com/files/'+asset]))
def download(url,dest):subprocess.run(['curl','-sSL','--fail','--retry','2','--max-time','120',url,'-o',str(dest)],check=True)
data=api('rosewood_veneer_02')
for key,suffix in [('Diffuse',''),('nor_gl','-normal'),('Rough','-rough')]:
 dest=A/f'pbr-rosewood{suffix}.jpg';download(data[key]['2k']['jpg']['url'],dest)
 with Image.open(dest) as im:im.convert('RGB').save(dest,quality=92,optimize=True)
if not (A/'autumn-forest.hdr').exists():download(api('autumn_forest_01')['hdri']['2k']['hdr']['url'],A/'autumn-forest.hdr')
(R/'source/refined-asset-sources.json').write_text(json.dumps([{'asset':'autumn_forest_01','author':'Andreas Mischok','license':'CC0','url':'https://polyhaven.com/a/autumn_forest_01','resolution':'2k'},{'asset':'rosewood_veneer_02','author':'Jenelle van Heerden','license':'CC0','url':'https://polyhaven.com/a/rosewood_veneer_02','resolution':'2k'}],indent=2))
print('CC0 photographic environment and clean rosewood maps ready.')
