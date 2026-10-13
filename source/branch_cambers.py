"""Local living-wood camber, anchored before the first twig attachment.
The deformation transports existing UV charts rather than rebuilding the tree.
"""
import numpy as np
from tree_bark_uv import BranchProjection

def cambers(mesh,paths,tree_index):
 positions=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',positions);positions=positions.reshape(-1,3).astype(float)
 normals=np.asarray([v.normal[:] for v in mesh.vertices]);projections=[BranchProjection(*p) for p in paths];lookups=[p.project(positions) for p in projections]
 scores=np.asarray([error+.025*(1-np.einsum('nd,nd->n',unit,normals)) for error,_,_,unit in lookups])
 weights=np.exp(-(scores-scores.min(axis=0))/.045);weights/=weights.sum(axis=0)
 delta=np.zeros_like(positions);max_extent=0
 for index in range(8,15):
  projection=projections[index];along=lookups[index][2];extent=projection.arc[6];max_extent=max(max_extent,float(extent))
  s=np.clip(along/extent,0,1);bump=np.sin(np.pi*s)**2
  # Species/branch variation is deterministic; no foliage or planting RNG changes.
  phase=tree_index*1.71+(index-8)*2.399
  lift=(.042+.018*np.sin(phase))*min(1.25,projection.arc[-1]/2.4)
  direction=projection.direction[0].copy();side=np.array([-direction[1],direction[0],0]);side/=max(np.linalg.norm(side),1e-8)
  rise=np.array([0.,0.,lift])+side*(.018*np.cos(phase))
  segment=np.clip(np.searchsorted(projection.arc,along,side='right')-1,0,len(projection.length)-1)
  t=np.clip((along-projection.arc[segment])/projection.length[segment],0,1)
  center=projection.a[segment]+projection.delta[segment]*t[:,None];radial=positions-center
  # A restrained collar rolls out of the trunk and quickly returns to the old bark.
  collar=.12*np.exp(-((s-.18)/.17)**2)*(1-s)**2
  contribution=rise[None,:]*bump[:,None]+radial*collar[:,None]
  delta+=contribution*weights[index,:,None]
 # Reject numerical spill outside the authored proximal branch regions.
 delta[np.linalg.norm(delta,axis=1)<1e-6]=0
 assert np.isfinite(delta).all();assert np.max(np.linalg.norm(delta,axis=1))<.20
 assert np.all(delta[positions[:,2]<1.35]==0),'Root region must stay fixed'
 updated=(positions+delta).astype(np.float32);mesh.vertices.foreach_set('co',updated.ravel());mesh.update()
 return {'vertices':len(positions),'changedVertices':int(np.count_nonzero(np.linalg.norm(delta,axis=1)>0)),'maxDisplacement':float(np.max(np.linalg.norm(delta,axis=1))),'proximalExtent':max_extent}
