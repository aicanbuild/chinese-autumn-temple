"""Compare original shrub faces and curved replacement in the real garden."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];version=json.loads((R/'dist/runtime/manifest.json').read_text())['version'];s=(R/f'dist/runtime/{version}/app.js').read_text();s=re.sub(r"from '([.]/[^']+)'",lambda m:f"from '../dist/runtime/{version}/"+m[1][2:]+"'",s)
s="import {extractRegion as extractCamelliaRegion} from '../dist/runtime/"+version+"/rituals.js';\nlet originalCamellias,replacementCamellias;\n"+s
s=s.replace('const camellias=installCamellias(','''const shrubCopy=new THREE.Group();model.updateMatrixWorld(true);model.traverse(o=>{if(o.isMesh&&o.material.name==='Clipped garden foliage'){const copy=new THREE.Mesh(o.geometry.clone(),o.material);copy.matrix.copy(o.matrixWorld);copy.matrixAutoUpdate=false;shrubCopy.add(copy);}});originalCamellias=extractCamelliaRegion(shrubCopy,()=>true,p=>p.y<1.35,points=>points.every(p=>p.y<1.35));shrubCopy.traverse(o=>o.geometry?.dispose());originalCamellias.visible=false;scene.add(originalCamellias);const camellias=installCamellias(''')
s=s.replace('renderer.domElement.dataset.camellias=JSON.stringify(camellias.stats);','renderer.domElement.dataset.camellias=JSON.stringify(camellias.stats);replacementCamellias=camellias.batches;')
s+='''
const auditBar=document.createElement('div');auditBar.style='position:fixed;z-index:100;left:20px;bottom:20px;padding:8px';document.body.append(auditBar);
function showNew(value){originalCamellias.visible=!value;for(const m of replacementCamellias)m.visible=value;}
for(const [label,fn] of [['池岸灌木',()=>{if(!sceneReady)return;controls.minDistance=.4;camera.position.set(14.5,1.4,10.5);controls.target.set(12.3,.63,8.3);camera.fov=43;camera.updateProjectionMatrix();controls.update();}],['叶片近景',()=>{if(!sceneReady)return;controls.minDistance=.4;camera.position.set(12.8,.92,9.1);controls.target.set(12.3,.65,8.3);camera.fov=43;camera.updateProjectionMatrix();controls.update();}],['原叶片',()=>showNew(false)],['曲面叶片',()=>showNew(true)],['收起检查按钮',()=>auditBar.remove()]]){const b=document.createElement('button');b.textContent=label;b.style='padding:10px';b.onclick=fn;auditBar.append(b);}
'''
(R/'evidence/camellia-audit.js').write_text(s)
h=(R/'dist/index.html').read_text().replace('<head>','<head><base href="../dist/">');h=re.sub(r'<script type="module" src="[^"]+"></script>','<script type="module" src="../evidence/camellia-audit.js"></script>',h);(R/'evidence/camellia-audit.html').write_text(h)
