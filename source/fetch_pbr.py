"""Fetch cited CC0 material maps from Poly Haven's asset API (not arbitrary URLs)."""
from pathlib import Path
import subprocess,json,concurrent.futures
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
assets={'wood':'weathered_brown_planks','stone':'mossy_rock','bark':'bark_brown_02','earth':'forest_floor'}
def get(alias,asset):
 result=subprocess.run(['curl','-sSL','--fail','--max-time','45',f'https://api.polyhaven.com/files/{asset}'],capture_output=True,check=True)
 data=json.loads(result.stdout)
 for choices,suffix in [(['Diffuse','diff'],''),(['nor_gl'],'-normal'),(['Rough','rough'],'-rough')]:
  key=next(k for k in choices if k in data);entry=data[key]['2k']['jpg'];dest=ROOT/'dist/assets'/f'pbr-{alias}{suffix}.jpg'
  subprocess.run(['curl','-sSL','--fail','--retry','2','--max-time','100',entry['url'],'-o',str(dest)],check=True)
 for dest in (ROOT/'dist/assets').glob(f'pbr-{alias}*.jpg'):
  Image.open(dest).convert('RGB').save(dest,quality=92,optimize=True)
 print(asset,'downloaded',flush=True)
 return {'asset':asset,'url':f'https://polyhaven.com/a/{asset}','license':'CC0','resolution':'2k'}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
 records=list(executor.map(lambda item:get(*item),assets.items()))
(ROOT/'source/pbr-sources.json').write_text(json.dumps(records,indent=2))
