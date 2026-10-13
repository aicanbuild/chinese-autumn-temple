"""Merge finished tree assets only after preserving and validating the existing temple."""
import bpy,math,random,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
layout=json.loads((A/'garden-trees.json').read_text());trees=layout['trees'];pines=layout['pines'];anchors=layout['anchors']
backup=R/'source/听秋寺院-树木更新前.blend'
if not backup.exists():shutil.copy2(R/'source/听秋寺院.blend',backup)
assert backup.stat().st_size>100_000_000
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
protected={o.name for o in bpy.data.objects if not (o.get('garden_tree') or o.name in ['Autumn maple foliage','Golden ginkgo foliage','Forest green foliage'] or (o.type=='MESH' and any(m and m.name=='Ridged maple bark' for m in o.data.materials)))}
assert bpy.data.objects.get('Reflecting pond')
assert len([o for o in bpy.data.objects if o.get('bridge_asset')])==843
assert len([o for o in bpy.data.objects if o.get('pond_stone')])==257
assert len([o for o in bpy.data.objects if o.get('stone_lantern')])==736
for o in list(bpy.data.objects):
 if o.get('garden_tree') or o.name in ['Autumn maple foliage','Golden ginkgo foliage','Forest green foliage'] or (o.type=='MESH' and any(m and m.name=='Ridged maple bark' for m in o.data.materials)):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(R/'source/庭院曲枝树木.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:bpy.context.collection.objects.link(o)
def mesh(name,vs,fs,uv):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);layer=me.uv_layers.new()
 for face in me.polygons:
  for li in face.loop_indices:layer.data[li].uv=uv[me.loops[li].vertex_index]
 o['garden_tree']=True;return o
# Editable native leaf surfaces follow the same compact anchor layout as the web.
for kind,name in enumerate(['maple','ginkgo','green']):
 vs=[];fs=[];uv=[];rr=random.Random(8801+kind)
 for x,y,z,k,r,dx,dy,dz in anchors:
  if k!=kind:continue
  for j in range(64):
   a=rr.random()*math.tau;radius=math.sqrt(rr.random())*r;p=Vector((x+math.cos(a)*radius,y+math.sin(a)*radius,z+(rr.random()+rr.random()-1)*r*.58));size=rr.uniform(.115,.20)*(1.12 if kind==2 else 1);az=rr.random()*math.tau;tilt=rr.uniform(-.85,.85);u=Vector((math.cos(az),math.sin(az),0))*size*.44;v=Vector((-math.sin(az)*math.cos(tilt),math.cos(az)*math.cos(tilt),math.sin(tilt)))*size*.5
   base=len(vs);vs.extend([tuple(p-u-v),tuple(p+u-v),tuple(p+u+v),tuple(p-u+v)]);fs.append((base,base+1,base+2,base+3));uv.extend([(0,0),(1,0),(1,1),(0,1)])
 o=mesh('Specimen leaf canopy '+name,vs,fs,uv);m=bpy.data.materials.new('Specimen leaf '+name);m.use_nodes=True;n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(A/f'{name}-leaf.png'),check_existing=True);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.8;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(n.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED';o.data.materials.append(m)
assert protected.issubset({o.name for o in bpy.data.objects}),'Non-tree object removed during merge'
assert len([o for o in bpy.data.objects if o.get('garden_tree')])==39
assert len([o for o in bpy.data.objects if o.get('landscape_asset')])==1241
assert any(o.get('detailed_koi') for o in bpy.data.objects)
assert any(o.get('altar_sculpture') for o in bpy.data.objects)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/听秋寺院.blend'))
(R/'evidence/trees-native-verification.json').write_text(json.dumps({'trees':15,'pines':6,'meshes':39,'preservedObjects':len(protected),'backup':str(backup)},indent=2))
print('CURVED TREES COMPLETE',len(trees),len(pines),len(anchors),flush=True)
