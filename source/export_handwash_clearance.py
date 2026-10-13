import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/入口手水钵.blend'))
points=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.get('handwashAssembly')!='ladle':continue
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  points.append([round(p.x+3.58,6),round(p.z-1.505,6),round(-p.y-15.88,6)])
assert len(points)>1000
report={'vertices':points,'railSegments':[[[-4.43,1.36,15.88],[-2.97,1.36,15.88]],[[-4.43,1.36,16.01],[-2.97,1.36,16.01]]],'railRadius':.026,'rest':[-3.58,1.505,15.88]}
(R/'source/handwash-clearance.json').write_text(json.dumps(report,separators=(',',':')))
print('Exported',len(points),'actual native ladle vertices for collision verification',flush=True)
