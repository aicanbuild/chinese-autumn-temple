"""Refresh packed granite images without changing native geometry or other assets."""
import bpy,json,shutil,hashlib
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];reports=[]
def signature(o):
 h=hashlib.sha256(np.asarray(o.matrix_world).tobytes())
 if o.type=='MESH':
  for coll,prop,width,dtype in [(o.data.vertices,'co',3,np.float32),(o.data.loops,'vertex_index',1,np.int32),(o.data.polygons,'loop_total',1,np.int32)]:
   values=np.empty(len(coll)*width,dtype=dtype);coll.foreach_get(prop,values);h.update(values.tobytes())
  for uv in o.data.uv_layers:
   values=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',values);h.update(values.tobytes())
  for attr in o.data.attributes:
   if attr.data_type=='FLOAT':
    values=np.empty(len(attr.data),dtype=np.float32);attr.data.foreach_get('value',values);h.update(attr.name.encode()+values.tobytes())
  h.update(str([m.name if m else None for m in o.data.materials]).encode())
 return h.hexdigest()
for name in ['雕刻石灯笼.blend','听秋寺院.blend']:
 path=R/'source'/name;backup=path.with_name(path.stem+'-before-fine-honing.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path))
 before={o.name:signature(o) for o in bpy.data.objects}
 updated=[]
 for image in list(bpy.data.images):
  source=Path(bpy.path.abspath(image.filepath)).name
  if source not in ['cut-granite.jpg','cut-granite-normal.jpg','cut-granite-rough.jpg']:continue
  # Load fresh pixels; replace links instead of reloading a stale packed buffer.
  replacement=bpy.data.images.load(str(R/'dist/assets'/source),check_existing=False)
  replacement.colorspace_settings.name=image.colorspace_settings.name;replacement.pack()
  image.user_remap(replacement);updated.append(source)
 assert set(updated)=={'cut-granite.jpg','cut-granite-normal.jpg','cut-granite-rough.jpg'}
 assert before=={o.name:signature(o) for o in bpy.data.objects}
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path))
 bpy.ops.wm.open_mainfile(filepath=str(path));assert before=={o.name:signature(o) for o in bpy.data.objects}
 for image in bpy.data.images:
  source=Path(bpy.path.abspath(image.filepath)).name
  if source in set(updated) and image.users:
   assert image.packed_file and hashlib.sha256(image.packed_file.data).digest()==hashlib.sha256((R/'dist/assets'/source).read_bytes()).digest(),source
 reports.append({'file':name,'preservedObjects':len(before),'updatedImages':sorted(set(updated))})
(R/'evidence/granite-native-verification.json').write_text(json.dumps(reports,indent=2));print(reports)
