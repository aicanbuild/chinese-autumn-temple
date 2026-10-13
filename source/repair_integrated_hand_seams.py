import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/主殿佛像-衔接候选.blend'))
o=next(o for o in bpy.data.objects if o.name.startswith('Tang sculpture'))
def patch(p):return ((-.510<p.x<-.300 and -.27<p.y<.080 and .60<p.z<1.055) or (.160<p.x<.400 and -.33<p.y<-.045 and .83<p.z<1.290))
b=bmesh.new();b.from_mesh(o.data)
def count():return sum(e.is_boundary and patch((e.verts[0].co+e.verts[1].co)*.5) for e in b.edges)
log=[count()]
for tolerance in [.00005,.00015,.00030,.0006,.001,.0015]:
 boundary_vs={v for e in b.edges if e.is_boundary and all(patch(v.co) for v in e.verts) for v in e.verts}
 vs=list({v for a in boundary_vs for e in a.link_edges for v in e.verts if patch(v.co)})
 bmesh.ops.remove_doubles(b,verts=vs,dist=tolerance)
 es=[e for e in b.edges if all(patch(v.co) for v in e.verts)]
 bmesh.ops.dissolve_degenerate(b,edges=es,dist=.00001)
 boundaries=[e for e in b.edges if e.is_boundary and all(patch(v.co) for v in e.verts)]
 bmesh.ops.holes_fill(b,edges=boundaries,sides=32)
 log.append(count())
 print('SEAMS_REPAIR',tolerance,log[-1],flush=True)
 if log[-1]<=15:break
bmesh.ops.recalc_face_normals(b,faces=list(b.faces));b.to_mesh(o.data);b.free();o.data.update()
for p in o.data.polygons:p.use_smooth=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/主殿佛像-衔接候选.blend'))
print('SEAMS_RESULT',log,flush=True)
