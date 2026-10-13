"""Local-only real-scene comparison of old/new incident-water attenuation."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1];version=json.loads((R/'dist/runtime/manifest.json').read_text())['version'];s=(R/f'dist/runtime/{version}/app.js').read_text();s=re.sub(r"from '([.]/[^']+)'",lambda m:f"from '../dist/runtime/{version}/"+m[1][2:]+"'",s)
s='const mediumComparison={value:1};\n'+s
needle='pondOptics=installPondOptics(scene,pondLightMaps,canopyUniform,sun);'
assert needle in s
s=s.replace(needle,needle+'''const mediumMaterials=new Set();scene.traverse(o=>{if(o.isMesh&&o.material&&!mediumMaterials.has(o.material)){const m=o.material;mediumMaterials.add(m);const previous=m.onBeforeCompile,key=m.customProgramCacheKey();m.onBeforeCompile=function(shader,r){previous.call(this,shader,r);if(shader.fragmentShader.includes('pondBeamTransmittance(path)*focus')){shader.uniforms.mediumComparison=mediumComparison;shader.fragmentShader='uniform float mediumComparison;\\n'+shader.fragmentShader.replace('pondBeamTransmittance(path)*focus','mix(exp(-vec3(.25,.075,.045)*path),pondBeamTransmittance(path),mediumComparison)*focus');}};m.customProgramCacheKey=()=>key+'|medium-audit';m.needsUpdate=true;}});''')
s+='''
const auditBar=document.createElement('div');auditBar.style='position:fixed;z-index:100;left:20px;bottom:20px;padding:8px';document.body.append(auditBar);
for(const [label,fn] of [['池岸水景',()=>{if(!sceneReady)return;controls.minDistance=.4;camera.position.set(14.5,1.4,10.5);controls.target.set(4,-.4,5);camera.fov=43;camera.updateProjectionMatrix();controls.update();}],['俯看池底',()=>{if(!sceneReady)return;camera.position.set(7,7,12);controls.target.set(4,-.5,6);camera.fov=43;camera.updateProjectionMatrix();controls.update();}],['原透光',()=>mediumComparison.value=0],['一致透光',()=>mediumComparison.value=1],['收起检查按钮',()=>auditBar.remove()]]){const b=document.createElement('button');b.textContent=label;b.style='padding:10px';b.onclick=fn;auditBar.append(b);}
'''
(R/'evidence/water-medium-audit.js').write_text(s)
h=(R/'dist/index.html').read_text().replace('<head>','<head><base href="../dist/">');h=re.sub(r'<script type="module" src="[^"]+"></script>','<script type="module" src="../evidence/water-medium-audit.js"></script>',h);(R/'evidence/water-medium-audit.html').write_text(h)
