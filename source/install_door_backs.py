import bpy,bmesh,sys,hashlib,array,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from door_backs import build_door_backs,CENTERS

def signatures():
 result={}
 for o in bpy.data.objects:
  if o.get('door_back'):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for data,prop,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
    a=array.array(kind,[0])*(len(data)*width);data.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result
reports=[]
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-door-backs.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures()
 for o in list(bpy.data.objects):
  if o.get('door_back'):bpy.data.objects.remove(o,do_unlink=True)
 parts=build_door_backs();bpy.context.view_layer.update();assert signatures()==before
 tris=0
 for o in parts:
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),(o.name,'open mesh');assert bm.calc_volume(signed=True)>0,(o.name,'volume');bm.free()
  o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
  vs=[o.matrix_world@v.co for v in o.data.vertices];x=CENTERS[o['door_index']]
  assert all(x-.66-1e-5<=v.x<=x+.66+1e-5 and 5.162<=v.y<=5.245 and 1.094<=v.z<=3.966 for v in vs),(o.name,'outside backing')
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signatures()==before
 reports.append({'file':filename,'preservedObjects':len(before),'parts':len(parts),'triangles':tris,'closedSolids':True});print('VERIFIED',reports[-1],flush=True)
exec(compile((R/'source/export_door_backs.py').read_text(),str(R/'source/export_door_backs.py'),'exec'))
(R/'evidence/door-backs-native.json').write_text(json.dumps(reports,indent=2,ensure_ascii=False))
