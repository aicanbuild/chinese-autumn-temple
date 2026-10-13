"""Fetch unmodified CC0 ambientCG Moss002 color, OpenGL normal and roughness maps."""
from pathlib import Path
from zipfile import ZipFile
import subprocess,tempfile,json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
url='https://ambientcg.com/get?file=Moss002_2K-JPG.zip'
with tempfile.TemporaryDirectory() as folder:
 archive=Path(folder)/'moss.zip';subprocess.run(['curl','--fail','-sSL','--max-time','120',url,'-o',str(archive)],check=True)
 with ZipFile(archive) as z:
  for key,suffix in [('Color',''),('NormalGL','-normal'),('Roughness','-rough')]:
   name=f'Moss002_2K-JPG_{key}.jpg';(A/f'garden-moss{suffix}.jpg').write_bytes(z.read(name))
print('Downloaded original 2K JPG maps from',url)
