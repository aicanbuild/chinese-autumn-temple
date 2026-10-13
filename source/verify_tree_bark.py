"""Measure actual branch UV anisotropy and check arc-length projection."""
import bpy,sys,json
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from tree_bark_uv import BranchProjection

for direction in [np.array([1.,0,0]),np.array([0.,0,1]),np.array([1.,2,3])/np.sqrt(14)]:
 axis=np.cross(direction,[0,1,0]);axis/=np.linalg.norm(axis)
 projection=BranchProjection([direction*i for i in range(4)],.2,.2)
 _,theta,arc,_=projection.project(np.asarray([direction*s+axis*.2 for s in [.3,1.2,2.6]]))
 assert np.allclose(arc,[.3,1.2,2.6],atol=1e-7)
 assert np.ptp(theta)<1e-7

def distortion(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));ratios=[];areas=[];triangles=0
 for o in bpy.data.objects:
  if 'fused trunk' not in o.name:continue
  mesh=o.data;mesh.calc_loop_triangles();vertices=np.asarray([v.co[:] for v in mesh.vertices]);indices=np.asarray([p.vertices[:] for p in mesh.loop_triangles]);loops=np.asarray([p.loops[:] for p in mesh.loop_triangles]);uv=np.asarray([v.uv[:] for v in mesh.uv_layers.active.data]);tri=vertices[indices];centers=tri.mean(axis=1)
  # Only above-root lateral branches, measured on the unchanged real topology.
  a=tri[:,1]-tri[:,0];b=tri[:,2]-tri[:,0];length=np.linalg.norm(a,axis=1);x=np.sum(a*b,axis=1)/np.maximum(length,1e-12);y=np.sqrt(np.maximum(0,np.sum(b*b,axis=1)-x*x));area=length*y/2
  mask=(centers[:,2]>1.4)&(np.linalg.norm(centers[:,:2],axis=1)>.65)&(area>1e-9)
  du=uv[loops[:,1]]-uv[loops[:,0]];dv=uv[loops[:,2]]-uv[loops[:,0]]
  dx=du[mask]/length[mask,None];dy=(dv[mask]-dx*x[mask,None])/y[mask,None]
  jacobian=np.stack([dx,dy],axis=2);singular=np.linalg.svd(jacobian,compute_uv=False)
  ratio=singular[:,0]/np.maximum(singular[:,1],1e-9);ratios.extend(ratio);areas.extend(area[mask]);triangles+=int(mask.sum())
 ratios=np.asarray(ratios);areas=np.asarray(areas);order=np.argsort(ratios);cdf=np.cumsum(areas[order])/sum(areas)
 return {'branchTriangles':triangles,'areaWeightedMedianAnisotropy':float(np.interp(.5,cdf,ratios[order])),'areaWeightedP95Anisotropy':float(np.interp(.95,cdf,ratios[order])),'areaAbove20x':float(sum(areas[ratios>20])/sum(areas))}

before=distortion(R/'source/庭院曲枝树木-before-bark-uv.blend');after=distortion(R/'source/庭院曲枝树木.blend')
assert before['branchTriangles']==after['branchTriangles']
assert after['areaWeightedMedianAnisotropy']<before['areaWeightedMedianAnisotropy']
assert after['areaAbove20x']<before['areaAbove20x']
result={'projectionDirections':3,'before':before,'after':after};(R/'evidence/tree-bark-uv-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
