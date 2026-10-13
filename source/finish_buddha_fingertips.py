"""Blend terminal phalanges into rounded pads, removing overlapping-sphere collars."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/主殿佛像-衔接候选.blend'))
o=next(o for o in bpy.data.objects if o.name.startswith('Tang sculpture'))
reports=json.loads((R/'evidence/integrated-hands.json').read_text());caps=[]
for r in reports[:2]:
 side=-1 if r['gesture']=='giving' else 1;palm=Vector(r['palm'])
 for j in range(4):
  fx=(j-1.5)*.0255;length=([.086,.100,.094,.075] if side>0 else [.072,.089,.096,.083])[j]+.011
  start=palm+Vector((fx*.82,0,side*(.013+.004*(1-abs(j-1.5)))))
  bend=.009 if side>0 else .018
  end=start+Vector((fx*.29,-.006-bend,side*length))
  axis=Vector((fx*.11,-.006-2*bend,side*length)).normalized()
  radius=(.0122-.0007*abs(j-1.3))*.75
  caps.append((end,axis,radius,.88))
 caps.append((palm+Vector((-side*.073,-.016,side*.042)),Vector((-side*.049,0,side*.057)).normalized(),.0093,.88))
if '--thumbs-only' in sys.argv:caps=caps[4::5]
modified=0
for v in o.data.vertices:
 for end,axis,r,flatten in caps:
  delta=v.co-end;h=delta.dot(axis)
  if not -2.3*r<h<.006:continue
  across=Vector((1,0,0));across=(across-axis*across.dot(axis)).normalized();depth=axis.cross(across).normalized()
  x=delta.dot(across);y=delta.dot(depth);radial=math.sqrt(x*x+(y/flatten)**2)
  if radial>r*1.7:continue
  if radial<.00005:
   v.co=end+axis*min(h,-.00003);modified+=1;break
  h_new=min(h,-.00003)
  radius=r if h_new<=-r else r*math.sqrt(max(.000001,1-((h_new+r)/r)**2))
  weight=min(1,max(0,(h+2.3*r)/(1.3*r)));weight=weight*weight*(3-2*weight)
  target=radial*(1-weight)+radius*weight
  v.co=end+axis*h_new+across*(x*target/radial)+depth*(y*target/radial)
  modified+=1;break
# Remove the duplicate sliver triangle reported by the exporter; no sculpted surface changes.
cleaned=o.data.validate(clean_customdata=False);o.data.update()
assert not o.data.validate(clean_customdata=False)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/主殿佛像-衔接候选.blend'))
print('FINGERTIP_FINISH',modified,'vertices; removed duplicate face:',cleaned,flush=True)
