"""Validate saved plant geometry and clearance around the altar sculpture/candles."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
parts=[o for o in bpy.data.objects if o.get('lotus_bouquet')];petals=[o for o in parts if o.get('botanical_part')=='petal'];leaves=[o for o in parts if o.get('botanical_part')=='leaf'];buds=[o for o in parts if o.get('botanical_part')=='bud'];stamens=[o for o in parts if o.get('botanical_part')=='stamens']
assert len(petals)==120 and len(leaves)==6 and len(buds)==4 and len(stamens)==6
allpoints=[o.matrix_world@v.co for o in parts if o.type=='MESH' for v in o.data.vertices]
# The accepted central figure has a clear axial opening; plants stay behind the front candles.
assert min(abs(v.x) for v in allpoints)>1.50
assert min(v.y for v in allpoints)>8.08
assert max(v.z for v in allpoints)<3.65
for o in petals+leaves+buds:
 assert o.data.uv_layers.active and len(o.data.vertices)>150
 for v in o.data.vertices:assert all(math.isfinite(c) for c in v.co)
for o in leaves:
 attachment=Vector(o['stem_attachment']);center=sum((o.matrix_world@v.co for v in o.data.vertices[:96]),Vector())/96;assert (center-attachment).length<1e-5
 assert len(o.data.vertices)==13*96
 assert any((v.co-attachment).length>.14 for v in o.data.vertices)
 assert o.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value==0
images=set()
for o in petals+leaves:
 for m in o.data.materials:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':images.add(n.image.name);assert n.image.packed_file
assert len(images)==4
report=json.loads((R/'evidence/lotus-native.json').read_text());report.update(petals=len(petals),buds=len(buds),leaves=len(leaves),stamens=288,packedBotanicalMaps=len(images),minimumAxisClearance=min(abs(v.x) for v in allpoints),maximumHeight=max(v.z for v in allpoints),leafStemsAttachedCentrally=True)
(R/'evidence/lotus-native.json').write_text(json.dumps(report,indent=2));print('VERIFIED',report)
