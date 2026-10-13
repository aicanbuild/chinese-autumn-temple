"""Export a non-destructive tree-shape proposal from the current native trees."""
import bpy,sys,json,hashlib
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'source'))
from tree_bark_uv import authored_paths
from branch_cambers import cambers
layout=json.loads((R/'dist/assets/garden-trees.json').read_text());paths,anchors=authored_paths(layout['trees']);assert np.max(np.abs(np.asarray(anchors)-np.asarray(layout['anchors'])))<1e-7
file=R/'source/庭院曲枝树木-before-branch-cambers.blend'
if not file.exists():file=R/'source/庭院曲枝树木.blend'
before=hashlib.sha256(file.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(file));stats=[]
for i in range(15):stats.append(cambers(bpy.data.objects[f'Garden tree {i:02d} fused trunk'].data,paths[i],i))
shell=bpy.data.materials.new('Specimen bark | runtime shared maps');shell.use_nodes=True
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(shell)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'evidence/tree-cambers-proposal.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_attributes=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
assert hashlib.sha256(file.read_bytes()).hexdigest()==before
(R/'evidence/tree-cambers-proposal.json').write_text(json.dumps(stats,indent=2));print('PROPOSAL',stats,flush=True)
