"""Apply the reviewed proximal branch shape to both native projects."""
import bpy,sys,json,hashlib,shutil
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from tree_bark_uv import authored_paths
from branch_cambers import cambers
A=R/'dist/assets';layout=json.loads((A/'garden-trees.json').read_text());paths,anchors=authored_paths(layout['trees']);assert np.max(np.abs(np.asarray(anchors)-np.asarray(layout['anchors'])))<1e-7
names={f'Garden tree {i:02d} fused trunk' for i in range(15)}
def signatures():
 result={}
 for o in bpy.data.objects:
  h=hashlib.sha256(np.asarray(o.matrix_world).tobytes())
  if o.type=='MESH':
   fields=[(o.data.loops,'vertex_index',1,np.int32),(o.data.polygons,'loop_total',1,np.int32),(o.data.polygons,'material_index',1,np.int32)]
   if o.name not in names:fields.append((o.data.vertices,'co',3,np.float32))
   for coll,prop,width,dtype in fields:
    a=np.empty(len(coll)*width,dtype=dtype);coll.foreach_get(prop,a);h.update(a.tobytes())
   h.update(str([m.name if m else None for m in o.data.materials]).encode())
   for uv in o.data.uv_layers:
    a=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',a);h.update(a.tobytes())
   attr=o.data.attributes.get('_BARK_BLEND')
   if attr:
    a=np.empty(len(attr.data)*3,dtype=np.float32);attr.data.foreach_get('vector',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result

def coords(mesh):
 a=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',a);return a.reshape(-1,3)
def audit(mesh,old,paths):
 new=coords(mesh);mesh.calc_loop_triangles();idx=np.asarray([t.vertices[:] for t in mesh.loop_triangles]);a=old[idx];b=new[idx]
 an=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);bn=np.cross(b[:,1]-b[:,0],b[:,2]-b[:,0]);alen=np.linalg.norm(an,axis=1);blen=np.linalg.norm(bn,axis=1);mask=alen>1e-10
 alignment=np.sum(an[mask]*bn[mask],axis=1)/(alen[mask]*blen[mask]);ratio=blen[mask]/alen[mask]
 assert alignment.min()>.3,alignment.min();assert ratio.min()>.4,ratio.min()
 volume=np.einsum('nd,nd->n',b[:,0],np.cross(b[:,1],b[:,2])).sum()/6;assert volume>0
 shift=np.linalg.norm(new-old,axis=1);attachment_shift=0
 for points,_,_ in paths[8:]:
  for p in [points[7],points[10],points[13],points[-1]]:
   near=np.linalg.norm(old-np.asarray(p),axis=1)<.12
   if near.any():attachment_shift=max(attachment_shift,float(shift[near].max()))
 assert attachment_shift<.002,attachment_shift
 assert np.array_equal(new[old[:,2]<1.35],old[old[:,2]<1.35])
 return {'minFaceNormalAlignment':float(alignment.min()),'minTriangleAreaRatio':float(ratio.min()),'positiveVolume':float(volume),'maxTwigAttachmentDisplacement':attachment_shift}

back=R/'evidence/tree-cambers-original';back.mkdir(exist_ok=True)
for name in ['garden-trees.glb','garden-trees-distant.glb']:
 if not (back/name).exists():shutil.copy2(A/name,back/name)
reports=[];newcoords={}
for filename in ['庭院曲枝树木.blend','听秋寺院.blend']:
 file=R/'source'/filename;backup=file.with_name(file.stem+'-before-branch-cambers.blend')
 if not backup.exists():shutil.copy2(file,backup)
 bpy.ops.wm.open_mainfile(filepath=str(file));before=signatures();stats=[]
 for i in range(15):
  o=bpy.data.objects[f'Garden tree {i:02d} fused trunk']
  if o.get('branch_cambers_revision')!=1:
   old=coords(o.data);report=cambers(o.data,paths[i],i);report.update(audit(o.data,old,paths[i]));o['branch_cambers_revision']=1;o['branch_cambers_audit']=json.dumps(report)
  stats.append(json.loads(o['branch_cambers_audit']))
  if filename=='庭院曲枝树木.blend':newcoords[o.name]=coords(o.data)
  else:assert np.array_equal(coords(o.data),newcoords[o.name])
 assert before==signatures()
 bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.wm.open_mainfile(filepath=str(file));assert before==signatures()
 for name in names:assert np.array_equal(coords(bpy.data.objects[name].data),newcoords[name])
 reports.append({'file':filename,'preservedObjects':len(before),'topologyUVBlendChartsMaterialsAndTransformsPreserved':True,'branchAudits':stats})
 if filename=='庭院曲枝树木.blend':
  shell=bpy.data.materials.new('Specimen bark | runtime shared maps');shell.use_nodes=True
  for o in bpy.data.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(shell)
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'garden-trees.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_attributes=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(R/'evidence/tree-cambers-native.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print('BRANCH CAMBERS VERIFIED',[(r['file'],r['preservedObjects']) for r in reports],flush=True)
