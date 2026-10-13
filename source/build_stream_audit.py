from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1];version=json.loads((R/'dist/runtime/manifest.json').read_text())['version'];s=(R/'dist/app.js').read_text();s=re.sub(r"from './([^']+)'",lambda m:f"from '../dist/runtime/{version}/{m[1]}'",s)
s+='''
const auditControls=document.createElement('div');auditControls.style.cssText='position:fixed;bottom:12px;left:12px;z-index:999;display:flex;gap:5px';
for(const [name,position,target] of [['手水钵',[-2.35,2.45,18.05],[-3.7,1.1,15.6]],['溪边',[18.5,2.4,14],[14.6,.2,5]],['浅滩',[16.4,1.65,4.8],[14.5,-.05,-1.8]],['寺院与溪流',[26,10,22],[6,1,0]],['上游',[18,2.8,-8],[15,-.05,-15]]]){const b=document.createElement('button');b.textContent=name;b.onclick=()=>{camera.position.fromArray(position);controls.target.fromArray(target);controls.minDistance=1;controls.update();auditControls.style.display="none";};auditControls.append(b);}
document.body.append(auditControls);document.addEventListener("keydown",e=>{if(e.code==="F8")auditControls.style.display="flex";});
const report=document.createElement('output');report.id='audit-state';report.style.display='none';document.body.append(report);setInterval(()=>{report.textContent=JSON.stringify({ready:sceneReady,handwash:handwash?.stats,camera:camera.position.toArray(),target:controls.target.toArray()});},300);
'''
(R/'evidence/stream-app.js').write_text(s)
html=(R/'dist/index.html').read_text();html=html.replace('<head>','<head><base href="../dist/">');html=re.sub(r'<script type="module" src="[^"]+"></script>',f'<script type="module" src="../evidence/stream-app.js?v={version}"></script>',html);(R/'evidence/stream-audit.html').write_text(html)
