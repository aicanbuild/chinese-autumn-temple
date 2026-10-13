import bpy,array,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def signatures():
 d={}
 for o in bpy.data.objects:
  if o.get('temple_stream') or o.get('handwash') or o.name=='Sculpted woodland terrain':continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for seq,field,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i')]:
    a=array.array(kind,[0])*(len(seq)*width);seq.foreach_get(field,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  d[o.name]=h.hexdigest()
 return d
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院-before-stream.blend'));before=signatures()
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'));after=signatures();assert before==after,'Unrelated geometry changed'
report={'preservedGeometryAndUVs':len(before),'assemblies':{}}
for key,name in [('temple_stream','寺旁清溪'),('handwash','入口手水钵')]:
 objects=[o for o in bpy.data.objects if o.get(key)];sc=bpy.data.scenes.new(name)
 for o in objects:sc.collection.objects.link(o)
 bpy.data.libraries.write(str(R/'source'/(name+'.blend')),{sc},fake_user=True)
 triangles=0
 for o in objects:
  if o.type=='MESH':
   o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 report['assemblies'][name]={'objects':len(objects),'triangles':triangles}
(R/'evidence/water-native-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report,flush=True)
