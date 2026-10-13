"""Read-only check that the editable flowers and browser placements agree."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];layout=json.loads((R/'dist/assets/camellia-blossoms.json').read_text())
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));Ci=C.inverted();reports=[]
for filename in ['池岸山茶花.blend','听秋寺院.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'source'/filename));objects=[o for o in bpy.context.scene.objects if o.get('camellia_blossom')]
 assert len(objects)==180
 meshes={o.data for o in objects};assert len(meshes)==3
 for mesh in meshes:
  assert all(math.isfinite(x) for v in mesh.vertices for x in v.co)
  mesh.calc_loop_triangles();assert all(t.area>1e-12 for t in mesh.loop_triangles)
 for group in range(12):
  for k,j in enumerate(range(0,950,210)):
   found=[o for o in objects if o.name.startswith(f'Camellia flower {group:02d}-{j:03d} |')];assert len(found)==3
   for o in found:
    m=C@o.matrix_world@Ci;expected=layout['matrices'][group*5+k]
    assert max(abs(m[r][c]-expected[c*4+r]) for c in range(4) for r in range(4))<1e-5
 reports.append({'file':filename,'meshes':len(objects),'sharedMeshes':len(meshes),'triangles':sum(len(m.loop_triangles) for m in meshes)*60})
print('NATIVE BLOSSOMS VERIFIED',json.dumps(reports,ensure_ascii=False),flush=True)
