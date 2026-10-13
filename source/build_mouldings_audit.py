"""Responsive asset comparison; local-only inspection controls."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'source/caisson-joinery-fixture.html').read_text()
s=s.replace('renderer.setSize(1280,720)','renderer.setSize(innerWidth,innerHeight)').replace('66,1280/720','66,innerWidth/innerHeight')
s=s.replace("'../dist/assets/fine-caisson.glb?joinery=cloud2'","new URLSearchParams(location.search).has('before')?'../evidence/mouldings-original/fine-caisson.glb':'../dist/assets/fine-caisson.glb?joinery=profile1'")
s=s.replace('<button id="whole">','<button id="before">修改前</button><button id="after">细线脚</button><button id="whole">')
s=s.replace("view(false);\n</script>","document.querySelector('#before').onclick=()=>location.search='?before=1';document.querySelector('#after').onclick=()=>location.search='?after=1';view(false);\n</script>")
s=s.replace("camera.position.set(detail?1.9:0,detail?3.75:2.7,detail?-6.25:-7.1)","camera.position.set(detail?.9:0,detail?3.3:1.5,detail?-3.5:-7.1)")
s=s.replace("camera.lookAt(detail?1.95:0,detail?4.6:5,detail?-6.5:-7.1)","camera.lookAt(detail?.9:0,detail?4.4:5,detail?-4.7:-7.1)")
(R/'evidence/caisson-mouldings-audit.html').write_text(s)
