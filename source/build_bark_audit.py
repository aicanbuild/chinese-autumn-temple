"""Full-scene pond maple camera using the production runtime."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];version=json.loads((R/'dist/runtime/manifest.json').read_text())['version'];s=(R/f'dist/runtime/{version}/app.js').read_text()
s=re.sub(r"from '([.]/[^']+)'",lambda m:f"from '../dist/runtime/{version}/"+m[1][2:]+"'",s)
s+='''
const auditBar=document.createElement('div');auditBar.style='position:fixed;z-index:100;left:20px;bottom:20px;padding:8px';document.body.append(auditBar);
for(const [label,fn] of [['查看池边红枫',()=>{if(!sceneReady)return;camera.position.set(11.8,2.3,12);controls.target.set(10.6,2.15,10);camera.fov=43;camera.updateProjectionMatrix();controls.update();}],['收起检查按钮',()=>auditBar.remove()]]){const b=document.createElement('button');b.textContent=label;b.style='padding:10px';b.onclick=fn;auditBar.append(b);}
'''
(R/'evidence/bark-fork-audit.js').write_text(s)
h=(R/'dist/index.html').read_text().replace('<head>','<head><base href="../dist/">');h=re.sub(r'<script type="module" src="[^"]+"></script>','<script type="module" src="../evidence/bark-fork-audit.js"></script>',h);(R/'evidence/bark-fork-audit.html').write_text(h)
