"""Independent closed-mesh and bed-contact audit of the saved gravel source."""
import bpy,bmesh,json,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from pond_basin import basin_height
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(R/'source/自然池岸.blend'));bpy.context.view_layer.update()
layout=json.loads((R/'dist/assets/pond-stones.json').read_text())['placements'];parts=[o for o in bpy.data.objects if o.get('pond_stone')];assert len(parts)==len(layout)==617
meshes={o.data for o in parts};assert len(meshes)==8
for me in meshes:
 bm=bmesh.new();bm.from_mesh(me);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>1;bm.free()
smallHeight=0;contact=[];oldTop={}
for o in parts:
 i=int(o.name.rsplit(' ',1)[1]);p=layout[i];assert (o.location-Vector(p[1:4])).length<1e-6;assert (o.scale-Vector(p[4:7])).length<1e-6;assert abs(o.rotation_euler.z-p[7])<1e-6
 if o.get('pond_zone')!='bed':continue
 points=[o.matrix_world@v.co for v in o.data.vertices];gaps=[v.z-basin_height(v.x,v.y) for v in points];support=min(gaps);assert abs(support+(.004 if i>=257 else .010))<2e-6;contact.append(support)
 if i>=257:smallHeight=max(smallHeight,max(gaps))
 else:oldTop[o.name]=max(v.z for v in points)
assert smallHeight<.09,smallHeight
bpy.ops.wm.open_mainfile(filepath=str(R/'source/自然池岸-before-gravel.blend'));bpy.context.view_layer.update();maxTopChange=-999
for o in bpy.data.objects:
 if o.name in oldTop:
  change=oldTop[o.name]-max((o.matrix_world@v.co).z for v in o.data.vertices);maxTopChange=max(maxTopChange,change)
assert maxTopChange<.001,maxTopChange
report={'closedMeshes':8,'placementsAligned':617,'bedContacts':len(contact),'maxAddedHeightAboveSediment':smallHeight,'maxOriginalStoneTopChange':maxTopChange,'supportMin':min(contact),'supportMax':max(contact)}
(R/'evidence/gravel-native-audit.json').write_text(json.dumps(report,indent=2));print('GRAVEL AUDIT',report,flush=True)
