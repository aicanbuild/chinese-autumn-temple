"""Restore the missing CC0 fern cutout and export a portable, embedded RGBA asset.

Poly Haven Fern 02: Rico Cilliers / Rob Tuytel, https://polyhaven.com/a/fern_02
The upstream glTF references an RGB JPEG even though it declares alphaMode MASK.
Use the original separate alpha image, never infer the silhouette from RGB color.
"""
import bpy, json, shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
A=R/'dist/assets/fern'

def repair(m):
    nodes=m.node_tree.nodes; links=m.node_tree.links
    p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    for n in nodes:
        if n.type=='TEX_IMAGE' and n.image:
            for kind in ['diff','nor_gl','arm']:
                if f'fern_02_{kind}_1k' in n.image.filepath:
                    n.image=bpy.data.images.load(str(A/f'textures/fern_02_{kind}_2k.jpg'),check_existing=True)
                    if kind!='diff': n.image.colorspace_settings.name='Non-Color'
    alpha=nodes.get('Original fern alpha') or nodes.new('ShaderNodeTexImage')
    alpha.name='Original fern alpha'
    alpha.image=bpy.data.images.load(str(A/'textures/fern_02_alpha_2k.png'),check_existing=True)
    alpha.image.colorspace_settings.name='Non-Color'
    clip=nodes.get('Leaf cutout threshold') or nodes.new('ShaderNodeMath')
    clip.name='Leaf cutout threshold';clip.operation='ROUND'
    links.new(alpha.outputs['Color'],clip.inputs[0])
    links.new(clip.outputs[0],p.inputs['Alpha'])
    m.surface_render_method='DITHERED'
    m.use_backface_culling=False
    m['gltf_alpha_mode']='MASK'
    m['gltf_alpha_cutoff']=.5
    return m

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(A/'fern.gltf'))
parts=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(parts)==4
for m in set(o.active_material for o in parts):repair(m)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/池岸蕨类.blend'))
bpy.ops.export_scene.gltf(filepath=str(A/'fern-cutout.glb'),export_format='GLB',export_image_format='AUTO',export_extras=True)

# Update shared materials only: no changes to the planted positions or other assets.
full=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-fern-cutout.blend'
if not backup.exists():shutil.copy2(full,backup)
bpy.ops.wm.open_mainfile(filepath=str(full))
ferns=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m and m.name.startswith('fern_02') for m in o.data.materials)]
assert len(ferns)==96,len(ferns)
for m in set(m for o in ferns for m in o.data.materials if m):repair(m)
for o in ferns:o['fern_cutout_restored']=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(full))
print(json.dumps({'fern_objects':len(ferns),'variants':len(parts),'alpha':'original 2K grayscale, non-color','native_updated':True}))
