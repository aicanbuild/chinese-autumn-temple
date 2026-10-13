"""Pack the revised continuous sediment finish into the existing native material."""
import bpy,shutil,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';path=R/'source/听秋寺院.blend';backup=path.with_name('听秋寺院-before-continuous-sediment.blend')
if not backup.exists():shutil.copy2(path,backup)
bpy.ops.wm.open_mainfile(filepath=str(path));before={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects}
material=bpy.data.materials.get('Riverbed sediment');assert material
changed=[]
for node in material.node_tree.nodes:
 if node.type!='TEX_IMAGE' or not node.image:continue
 stem=Path(bpy.path.abspath(node.image.filepath)).stem
 if stem not in ['sand','sand-normal','sand-rough']:continue
 image=bpy.data.images.load(str(A/(stem+'.jpg')),check_existing=False);image.colorspace_settings.name='sRGB' if stem=='sand' else 'Non-Color';image.pack();node.image=image;changed.append(stem)
assert sorted(changed)==['sand','sand-normal','sand-rough'];assert before=={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects}
bpy.ops.wm.save_as_mainfile(filepath=str(path));print('SEDIMENT NATIVE',{'images':changed,'objectsPreserved':len(before)},flush=True)
