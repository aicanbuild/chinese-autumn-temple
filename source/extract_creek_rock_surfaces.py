import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/寺旁清溪.blend'))
o=next(o for o in bpy.data.objects if o.get('streamAssembly')=='river stones and submerged pebbles');rocks=json.loads((R/'dist/assets/temple-stream.json').read_text())['rocks'];out=[]
for i,r in enumerate(rocks):
 verts=[o.matrix_world@v.co for v in o.data.vertices[i*108:(i+1)*108]]
 assert abs(sum(v.x for v in verts)/len(verts)-r['x'])<.02
 out.append({**r,'top':max(v.z for v in verts)})
(R/'source/creek-rock-surfaces.json').write_text(json.dumps(out,indent=2));print('Extracted',len(out),'actual stone surfaces')
