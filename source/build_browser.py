"""Content-version browser modules and assets so updates cannot mix old helpers."""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];D=R/'dist';runtime=D/'runtime'
def digest(data):return hashlib.sha256(data).hexdigest()[:12]
modules=sorted(D.glob('*.js'));versions={}
for folder in ['assets','ambience']:
 for path in sorted((D/folder).rglob('*')):
  if path.is_file():versions[path.relative_to(D).as_posix()]=digest(path.read_bytes())
catalog=json.dumps(versions,sort_keys=True,separators=(',',':'))
version=digest(b''.join(p.name.encode()+p.read_bytes() for p in modules)+catalog.encode())
target=runtime/version;target.mkdir(parents=True,exist_ok=True)
for path in modules:
 text=path.read_text()
 if path.name=='asset-versions.js':text=text.replace('const assetVersions = {};','const assetVersions = '+catalog+';')
 (target/path.name).write_text(text)
manifest=runtime/'manifest.json';old=json.loads(manifest.read_text()) if manifest.exists() else {}
previous=old.get('version') if old.get('version')!=version else old.get('previous')
# Only this helper's derived, hash-named directories are eligible for cleanup.
for directory in runtime.iterdir():
 if directory.is_dir() and re.fullmatch('[0-9a-f]{12}',directory.name) and directory.name not in {version,previous}:shutil.rmtree(directory)
manifest.write_text(json.dumps({'version':version,'previous':previous,'assets':len(versions)},indent=2))
p=D/'index.html';html=p.read_text();html=re.sub(r'<script type="module" src="[^"]+"></script>',f'<script type="module" src="./runtime/{version}/app.js"></script>',html)
html=re.sub(r'href="\./style\.css(?:\?v=[^\"]+)?"',f'href="./style.css?v={digest((D/"style.css").read_bytes())}"',html)
match=re.search(r'<script type="importmap">(.*?)</script>',html);mapping=json.loads(match.group(1));mapping['imports']['three/addons/objects/Water2.js']='./vendor/three/addons/objects/Water2.js?v='+digest((D/'vendor/three/addons/objects/Water2.js').read_bytes())
html=html[:match.start(1)]+json.dumps(mapping,separators=(',',':'))+html[match.end(1):];p.write_text(html)
print(json.dumps({'runtime':version,'modules':len(modules),'versionedAssets':len(versions),'previous':previous}))
