from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'source/caisson-joinery-fixture.html').read_text().replace('renderer.setSize(1280,720)','renderer.setSize(innerWidth,innerHeight)').replace('66,1280/720','66,innerWidth/innerHeight')
s=s.replace("'../dist/assets/fine-caisson.glb?joinery=cloud2'","'../dist/assets/fine-caisson.glb?ornament=1'")
s=s.replace('function view(detail)',"const decor=await loader.loadAsync('../dist/assets/caisson-vines.glb?ornament=1');decor.scene.traverse(o=>{if(o.isMesh){o.castShadow=o.receiveShadow=true;o.material.envMapIntensity=o.material.metalness>.6?.68:.32;if(o.material.map)o.material.map.anisotropy=8;}});scene.add(decor.scene);\nfunction view(detail)")
s=s.replace('detail?3.75:2.7','detail?3.75:1.5')
(R/'evidence/enriched-caisson-audit.html').write_text(s)
