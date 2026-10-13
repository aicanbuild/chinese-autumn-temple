"""Seat stalks below the real bed; update only affected numerical AO texels."""
import bpy,math,json,time,array
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
def extend():
 count=0
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.name.startswith('Pond lotus | fine emergent stalk') or o.get('pond_stem_grounded'):continue
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z<-.6:p.z=-.6+(p.z+.6)*4;v.co=inv@p
  o['pond_stem_grounded']=True;count+=1
 return count
for file in ['听秋寺院.blend','池中荷花.blend']:
 path=R/'source'/file;bpy.ops.wm.open_mainfile(filepath=str(path));print('GROUNDED',file,extend(),flush=True);bpy.ops.wm.save_as_mainfile(filepath=str(path))
 if file=='池中荷花.blend':
  batches={}
  for o in bpy.data.objects:
   if o.type=='MESH':batches.setdefault(o.data.materials[0],[]).append(o)
  for mat,group in batches.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in group:o.select_set(True)
   bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name='Pond lotus | '+mat.name
  bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/'pond-lotus.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
path=R/'source/池底接触光照.blend';bpy.ops.wm.open_mainfile(filepath=str(path));extend();bpy.context.view_layer.update()
objects=[o for o in bpy.data.objects if o.type=='MESH'];bed=next(o for o in objects if o.name=='Riverbed sediment');verts=[];faces=[];roots=[]
for o in objects:
 points=[o.matrix_world@v.co for v in o.data.vertices];offset=len(verts);verts.extend(points);faces.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
 if o.get('pond_stem_grounded'):
  low=[p for p in points if p.z<-.65];roots.append(sum(low,Vector())/len(low))
world=BVHTree.FromPolygons(verts,faces);bedtree=BVHTree.FromPolygons([bed.matrix_world@v.co for v in bed.data.vertices],[tuple(p.vertices) for p in bed.data.polygons])
image=bpy.data.images.load(str(A/'pond-contact-ao.png'),check_existing=False);image.colorspace_settings.name='Non-Color';w,h=image.size;pixels=array.array('f',[0])*(w*h*4);image.pixels.foreach_get(pixels)
count=128;golden=math.pi*(3-math.sqrt(5));samples=[]
for k in range(count):
 r=math.sqrt((k+.5)/count);a=k*golden;samples.append((r*math.cos(a),r*math.sin(a),math.sqrt(1-r*r)))
# .55m exceeds the .45m ray reach plus stalk radius/curvature and one texel.
texels=set()
for root in roots:
 for j in range(max(0,int((root.y-.55+12.7)/13.8*h)),min(h,int((root.y+.55+12.7)/13.8*h)+1)):
  for i in range(max(0,int((root.x-.55+11.5)/23*w)),min(w,int((root.x+.55+11.5)/23*w)+1)):
   x=-11.5+(i+.5)/w*23;y=-12.7+(j+.5)/h*13.8
   if (x-root.x)**2+(y-root.y)**2<.55**2:texels.add((i,j))
print('LOCAL STEM AO',len(texels),'texels',count,'rays each',flush=True);start=time.time()
for n,(i,j) in enumerate(texels):
 x=-11.5+(i+.5)/w*23;y=-12.7+(j+.5)/h*13.8;hit,normal,_,_=bedtree.ray_cast(Vector((x,y,0)),Vector((0,0,-1)),3)
 if hit is None:continue
 tangent=normal.cross(Vector((0,1,0))).normalized();bitangent=normal.cross(tangent);origin=hit+normal*.0002;clear=0
 for sx,sy,sz in samples:clear+=world.ray_cast(origin,tangent*sx+bitangent*sy+normal*sz,.45)[0] is None
 value=clear/count;idx=(j*w+i)*4;pixels[idx]=pixels[idx+1]=pixels[idx+2]=value
image.pixels.foreach_set(pixels);image.filepath_raw=str(A/'pond-contact-ao.png');image.file_format='PNG';image.save();image.pack()
# Keep the live file's receiver bound to the final packed atlas.
for node in bed.data.materials[0].node_tree.nodes:
 if node.type=='TEX_IMAGE':node.image=image
bpy.ops.wm.save_as_mainfile(filepath=str(path));report={'groundedStems':len(roots),'updatedTexels':len(texels),'raysPerTexel':count,'outsideMaskPreserved':True,'seconds':time.time()-start};(R/'evidence/lotus-root-contact.json').write_text(json.dumps(report,indent=2));print('LOTUS_ROOT_AO',report,flush=True)
