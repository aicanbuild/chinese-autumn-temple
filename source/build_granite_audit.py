"""Local-only full-scene material A/B inspection using the built runtime."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];version=json.loads((R/'dist/runtime/manifest.json').read_text())['version'];s=(R/f'dist/runtime/{version}/app.js').read_text();s=re.sub(r"from '([.]/[^']+)'",lambda m:f"from '../dist/runtime/{version}/"+m[1][2:]+"'",s)
s+='''
const auditBar=document.createElement('div');auditBar.style='position:fixed;z-index:100;left:20px;bottom:20px;padding:8px';document.body.append(auditBar);
let granitePairs;
async function oldGranite(){
 if(!sceneReady)return;
 if(!granitePairs){
  const textures=await Promise.all(['','-normal','-rough'].map(s=>new THREE.TextureLoader().loadAsync('../evidence/granite-before-fine-honing/cut-granite'+s+'.jpg')));
  const mats=new Set();scene.traverse(o=>{if(o.isMesh&&['Honed silver granite','Lantern | fine carved granite'].includes(o.material?.name))mats.add(o.material);});granitePairs=[];
  for(const m of mats)for(const [i,key] of ['map','normalMap','roughnessMap'].entries()){if(!m[key])continue;const before=m[key].clone();before.image=textures[i].image;before.needsUpdate=true;granitePairs.push({m,key,before,after:m[key]});}
 }
 for(const p of granitePairs){p.m[p.key]=p.before;p.m.needsUpdate=true;}
}
function newGranite(){for(const p of granitePairs||[]){p.m[p.key]=p.after;p.m.needsUpdate=true;}}
for(const [label,fn] of [['石灯近景',()=>{if(!sceneReady)return;controls.minDistance=.4;camera.position.set(14.5,1.4,10.5);controls.target.set(12.3,.63,8.3);camera.fov=43;camera.updateProjectionMatrix();controls.update();}],['原石材',oldGranite],['细磨石材',newGranite],['收起检查按钮',()=>auditBar.remove()]]){const b=document.createElement('button');b.textContent=label;b.style='padding:10px';b.onclick=fn;auditBar.append(b);}
'''
(R/'evidence/granite-audit.js').write_text(s)
h=(R/'dist/index.html').read_text().replace('<head>','<head><base href="../dist/">');h=re.sub(r'<script type="module" src="[^"]+"></script>','<script type="module" src="../evidence/granite-audit.js"></script>',h);(R/'evidence/granite-audit.html').write_text(h)
