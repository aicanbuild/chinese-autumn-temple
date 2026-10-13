from pathlib import Path
import re
R=Path(__file__).resolve().parents[1];s=(R/'dist/app.js').read_text()
s=re.sub(r' // BEGIN hall contact scale.*? // END hall contact scale\n','',s,flags=re.S)
s=re.sub(r"from '([.]/[^']+)'",lambda m:"from '../dist/"+m[1][2:]+"'",s)
s="let waterMaskAudit;\n"+s
s=s.replace('waterAOMask=installWaterAOMask(ao,water);','waterAOMask=installWaterAOMask(ao,water);waterMaskAudit=waterAOMask;waterMaskAudit.enabled=false;')
s+='''
const auditBar=document.createElement('div');auditBar.style='position:fixed;z-index:100;left:20px;top:130px;background:#222;padding:8px;color:white';document.body.append(auditBar);
for(const [label,fn] of [['池岸近景',()=>{if(!sceneReady)return;camera.position.set(12,3.5,11);controls.target.set(7,0,5);camera.fov=43;camera.updateProjectionMatrix();controls.update();}],['桥与池底',()=>{camera.position.set(6,5,8);controls.target.set(0,0,6);controls.update();}],['庭院全景',()=>{camera.position.set(14,8.5,26);controls.target.set(0,2,0);controls.update();}],['原接触阴影',()=>{ao.enabled=true;ao.kernelRadius=.45;ao.minDistance=.001;ao.maxDistance=.07;ao.invalidated=true;}],['实际距离阴影',()=>{ao.enabled=true;ao.kernelRadius=.45;ao.minDistance=.008/(camera.far-camera.near);ao.maxDistance=.9/(camera.far-camera.near);ao.invalidated=true;}],['无接触阴影',()=>{ao.enabled=false;}],['水面遮罩开关',()=>{waterMaskAudit.enabled=!waterMaskAudit.enabled;}]]){const b=document.createElement('button');b.textContent=label;b.onclick=fn;auditBar.append(b);}
'''
(R/'evidence/pond-contact-audit.js').write_text(s)
h=(R/'dist/index.html').read_text().replace('<head>','<head><base href="../dist/">');h=re.sub(r'<script type="module" src="[^"]+"></script>','<script type="module" src="../evidence/pond-contact-audit.js"></script>',h);(R/'evidence/pond-contact-audit.html').write_text(h)
