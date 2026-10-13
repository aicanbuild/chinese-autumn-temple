from pathlib import Path
import re
R=Path(__file__).resolve().parents[1];s=(R/'dist/app.js').read_text()
s=re.sub(r' // BEGIN hall contact scale.*? // END hall contact scale\n','',s,flags=re.S)
s=re.sub(r"from '([.]/[^']+)'",lambda m:"from '../dist/"+m[1][2:]+"'",s)
s+='''
const auditBar=document.createElement('div');auditBar.style='position:fixed;z-index:100;left:20px;top:130px;background:#222;padding:8px;color:white';document.body.append(auditBar);
for(const [label,fn] of [['查看藻井',()=>{if(!sceneReady)return;if(!rituals.inside){rituals.enter();return;}camera.position.set(0,3,-4.02);controls.target.set(0,4.6,-7.1);camera.fov=66;camera.updateProjectionMatrix();controls.update();}],['原接触阴影',()=>{ao.enabled=true;ao.kernelRadius=.45;ao.minDistance=.001;ao.maxDistance=.07;ao.invalidated=true;}],['近距离接触阴影',()=>{ao.enabled=true;ao.kernelRadius=.14;ao.minDistance=.004/(camera.far-camera.near);ao.maxDistance=.28/(camera.far-camera.near);ao.invalidated=true;}],['不显示接触阴影',()=>{ao.enabled=false;}]]){const b=document.createElement('button');b.textContent=label;b.onclick=fn;auditBar.append(b);}
'''
(R/'evidence/paint-contact-audit.js').write_text(s)
h=(R/'dist/index.html').read_text().replace('<head>','<head><base href="../dist/">');h=re.sub(r'<script type="module" src="[^"]+"></script>','<script type="module" src="../evidence/paint-contact-audit.js"></script>',h);(R/'evidence/paint-contact-audit.html').write_text(h)
