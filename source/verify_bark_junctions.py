"""Read-only audit against recoverable pre-blend native projects."""
import bpy,hashlib,json,sys
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from tree_bark_uv import authored_paths
from branch_cambers import cambers
paths,_=authored_paths(json.loads((R/'dist/assets/garden-trees.json').read_text())['trees'])
names={f'Garden tree {i:02d} fused trunk' for i in range(15)}
def signature():
 result={}
 for o in bpy.data.objects:
  h=hashlib.sha256(np.asarray(o.matrix_world).tobytes())
  if o.type=='MESH':
   for coll,prop,width,dtype in [(o.data.vertices,'co',3,np.float32),(o.data.loops,'vertex_index',1,np.int32),(o.data.polygons,'loop_total',1,np.int32),(o.data.polygons,'material_index',1,np.int32)]:
    v=np.empty(len(coll)*width,dtype=dtype);coll.foreach_get(prop,v);h.update(v.tobytes())
   if o.name not in names:h.update(str([m.name if m else None for m in o.data.materials]).encode())
   for uv in o.data.uv_layers:
    if uv.name=='BarkBlendUV':continue
    v=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',v);h.update(v.tobytes())
  result[o.name]=h.hexdigest()
 return result
report=[]
for stem in ['庭院曲枝树木','听秋寺院']:
 file=R/'source'/f'{stem}.blend';bpy.ops.wm.open_mainfile(filepath=str(file));revised={n for n in names if bpy.data.objects[n].get('branch_cambers_revision')==1}
 bpy.ops.wm.open_mainfile(filepath=str(R/'source'/f'{stem}-before-bark-blend.blend'))
 for i in range(15):
  name=f'Garden tree {i:02d} fused trunk'
  if name in revised:cambers(bpy.data.objects[name].data,paths[i],i)
 before=signature()
 file=R/'source'/f'{stem}.blend';filehash=hashlib.sha256(file.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(file));assert before==signature();charts=[]
 for name in sorted(names):
  o=bpy.data.objects[name];a=o.data.attributes['_BARK_BLEND'];assert a.domain=='CORNER';v=np.empty(len(a.data)*3,dtype=np.float32);a.data.foreach_get('vector',v);v=v.reshape(-1,3);assert np.isfinite(v).all();assert (v[:,2]>=0).all() and (v[:,2]<=1).all();assert np.any(v[:,2]>.01);assert np.any(v[:,2]==0)
  uv=np.empty(len(o.data.uv_layers['BarkBlendUV'].data)*2,dtype=np.float32);o.data.uv_layers['BarkBlendUV'].data.foreach_get('uv',uv);assert np.array_equal(uv.reshape(-1,2),v[:,:2]);assert o.data.materials[0].get('bark_junction_revision')==1
  charts.append({'name':name,'loops':len(v),'blendedLoops':int((v[:,2]>.001).sum())})
 assert hashlib.sha256(file.read_bytes()).hexdigest()==filehash
 report.append({'file':file.name,'objects':len(before),'expectedGeometryPrimaryUVTransformsAndOtherMaterialsPreserved':True,'reviewedBranchCambersAccountedFor':len(revised),'sourceUnchanged':True,'charts':charts})
(R/'evidence/bark-junction-native.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('NATIVE BARK VERIFIED',[(r['file'],r['objects']) for r in report],flush=True)
