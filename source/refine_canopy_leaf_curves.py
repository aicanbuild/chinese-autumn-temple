"""Replace native pyramid leaf fans with the browser's shared curved profile."""
import bpy,json,hashlib,shutil
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'source/听秋寺院.blend';backup=path.with_name('听秋寺院-before-curved-canopies.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path));canopies=[o for o in bpy.data.objects if o.name.startswith('Specimen leaf canopy ')];assert len(canopies)==3
profile=json.loads((R/'source/canopy-leaf-profile.json').read_text());P=np.array(profile['position']).reshape(-1,3);N=np.array(profile['normal']).reshape(-1,3);UV=np.array(profile['uv']).reshape(-1,2);F=np.array(profile['index']).reshape(-1,3)
def signature(o):
 h=hashlib.sha256(np.asarray(o.matrix_world).tobytes())
 if o.type=='MESH':
  for coll,prop,width,dtype in [(o.data.vertices,'co',3,np.float32),(o.data.loops,'vertex_index',1,np.int32),(o.data.polygons,'loop_total',1,np.int32)]:
   values=np.empty(len(coll)*width,dtype=dtype);coll.foreach_get(prop,values);h.update(values.tobytes())
  for uv in o.data.uv_layers:
   values=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',values);h.update(values.tobytes())
  h.update(str([m.name if m else None for m in o.data.materials]).encode())
 return h.hexdigest()
protected={o.name:signature(o) for o in bpy.data.objects if o not in canopies};report=[]
for o in canopies:
 if o.get('botanical_curve_version')==2:continue
 old=o.data;assert o.get('botanical_fold_version')==1
 co=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,3)
 ids=np.empty(len(old.loops),np.int32);old.loops.foreach_get('vertex_index',ids);ids=ids.reshape(-1,4,3)
 assert np.all(ids[:,:,2]==ids[:,0,2,None]);assert np.all(ids[:,0,1]==ids[:,1,0]);assert np.all(ids[:,1,1]==ids[:,2,0]);assert np.all(ids[:,2,1]==ids[:,3,0]);assert np.all(ids[:,3,1]==ids[:,0,0])
 c0,c1,c2,c3=[co[v] for v in [ids[:,0,0],ids[:,0,1],ids[:,1,1],ids[:,2,1]]];origin=(c0+c1+c2+c3)/4;u=c1-c0;v=c3-c0;lu=np.linalg.norm(u,axis=1);lv=np.linalg.norm(v,axis=1);assert np.min(lu)>.05 and np.min(lv)>.05
 w=np.cross(u,v);w/=np.linalg.norm(w,axis=1)[:,None];w*=lv[:,None]
 points=origin[:,None,:]+u[:,None,:]*P[None,:,0,None]+v[:,None,:]*P[None,:,1,None]+w[:,None,:]*P[None,:,2,None]
 normals=u[:,None,:]/lu[:,None,None]**2*N[None,:,0,None]+v[:,None,:]/lv[:,None,None]**2*N[None,:,1,None]+w[:,None,:]/lv[:,None,None]**2*N[None,:,2,None];normals/=np.linalg.norm(normals,axis=2)[:,:,None]
 count=len(ids);faces=(F[None,:,:]+np.arange(count)[:,None,None]*len(P)).reshape(-1,3)
 me=bpy.data.meshes.new(old.name+' curved');me.from_pydata(points.reshape(-1,3),[],faces);me.update()
 for m in old.materials:me.materials.append(m)
 uv=me.uv_layers.new();uv.data.foreach_set('uv',UV[faces.ravel()%len(P)].astype(np.float32).ravel())
 for poly in me.polygons:poly.use_smooth=True
 me.normals_split_custom_set_from_vertices(normals.reshape(-1,3).tolist());o.data=me;o['botanical_curve_version']=2
 assert np.isfinite(points).all() and np.isfinite(normals).all()
 assert np.max(np.linalg.norm(points[:,1,:]-(origin-v*.5),axis=1))<1e-5
 report.append({'object':o.name,'leaves':count,'triangles':len(faces),'vertices':len(me.vertices),'stemAnchorsPreserved':True});print('CURVED CANOPY',report[-1],flush=True)
assert protected=={name:signature(bpy.data.objects[name]) for name in protected}
bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert protected=={name:signature(bpy.data.objects[name]) for name in protected}
for o in bpy.data.objects:
 if not o.name.startswith('Specimen leaf canopy '):continue
 assert o.get('botanical_curve_version')==2 and len(o.data.vertices)%9==0 and len(o.data.polygons)==len(o.data.vertices)//9*8
 assert o.data.has_custom_normals
(R/'evidence/canopy-curves-native.json').write_text(json.dumps({'canopies':report,'protectedObjects':len(protected),'fullObjects':len(bpy.data.objects)},indent=2));print('CURVED CANOPIES VERIFIED',len(protected),flush=True)
