"""Full-scene comparison of curved leaves with the original pyramid card."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1];version=json.loads((R/'dist/runtime/manifest.json').read_text())['version'];s=(R/f'dist/runtime/{version}/app.js').read_text();s=re.sub(r"from '([.]/[^']+)'",lambda m:f"from '../dist/runtime/{version}/"+m[1][2:]+"'",s)
s+='''
const originalCanopy=new THREE.BufferGeometry();originalCanopy.setAttribute('position',new THREE.Float32BufferAttribute([-.5,-.5,0,.5,-.5,.01,.5,.5,.035,-.5,.5,0,0,.05,.10],3));originalCanopy.setAttribute('uv',new THREE.Float32BufferAttribute([0,0,1,0,1,1,0,1,.5,.55],2));originalCanopy.setIndex([0,1,4,1,2,4,2,3,4,3,0,4]);originalCanopy.computeVertexNormals();originalCanopy.computeBoundingSphere();originalCanopy.computeBoundingBox();
const auditBar=document.createElement('div');auditBar.style='position:fixed;z-index:100;left:20px;bottom:20px;padding:8px';document.body.append(auditBar);
function selectCanopy(geometry){for(const m of canopyBatches){m.geometry=geometry;m.computeBoundingSphere();m.boundingSphere.radius+=.032;}renderer.shadowMap.needsUpdate=true;}
function leafCamera(){let best=Infinity,center=new THREE.Vector3(),target=new THREE.Vector3(12,2,6),matrix=new THREE.Matrix4(),point=new THREE.Vector3();for(const batch of canopyBatches.filter(m=>m.name.includes('maple')))for(let i=0;i<batch.count;i++){batch.getMatrixAt(i,matrix);point.setFromMatrixPosition(matrix);const d=point.distanceToSquared(target);if(d<best){best=d;center.copy(point);}}controls.minDistance=.1;controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(.35,.25,.6));camera.fov=43;camera.updateProjectionMatrix();controls.update();}
for(const [label,fn] of [['岸边树冠',()=>{if(!sceneReady)return;controls.minDistance=.4;camera.position.set(14.5,1.4,10.5);controls.target.set(4,-.4,5);camera.fov=43;camera.updateProjectionMatrix();controls.update();}],['枫叶近景',leafCamera],['原折面',()=>selectCanopy(originalCanopy)],['曲面叶片',()=>selectCanopy(canopyGeom)],['收起检查按钮',()=>auditBar.remove()]]){const b=document.createElement('button');b.textContent=label;b.style='padding:10px';b.onclick=fn;auditBar.append(b);}
'''
(R/'evidence/canopy-curve-audit.js').write_text(s)
h=(R/'dist/index.html').read_text().replace('<head>','<head><base href="../dist/">');h=re.sub(r'<script type="module" src="[^"]+"></script>','<script type="module" src="../evidence/canopy-curve-audit.js"></script>',h);(R/'evidence/canopy-curve-audit.html').write_text(h)
