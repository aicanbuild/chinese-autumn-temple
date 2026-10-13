"""Read-only inspection of retained legacy gilded components at the rear murals."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
o=bpy.data.objects['Satin gilded bronze'];mesh=o.data;world=[o.matrix_world@v.co for v in mesh.vertices]
adj=[set() for _ in world]
for edge in mesh.edges:
 a,b=edge.vertices;adj[a].add(b);adj[b].add(a)
result=[]
for x in [-2.8,2.8]:
 center=Vector((x,10.13,3.75));seed=min(range(len(world)),key=lambda i:(world[i]-center).length_squared);seen={seed};todo=[seed]
 while todo:
  for n in adj[todo.pop()]:
   if n not in seen:seen.add(n);todo.append(n)
 lo=[min(world[i][k] for i in seen) for k in range(3)];hi=[max(world[i][k] for i in seen) for k in range(3)]
 result.append({'near':list(center),'vertices':len(seen),'faces':sum(any(i in seen for i in p.vertices) for p in mesh.polygons),'lo':lo,'hi':hi})
(R/'evidence/mural-intrusions-inspection.json').write_text(json.dumps(result,indent=2));print('MURAL INTRUSIONS',result,flush=True)
