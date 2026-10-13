"""Build seated polychrome coffers, gilt flower relief and beaded borders.
All existing structural geometry is preserved; replaces only the sparse vine asset.
"""
import bpy,bmesh,sys,math,json,shutil,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def signatures():
 result={}
 for o in bpy.data.objects:
  if o.get('caisson_vines'):continue
  h=hashlib.sha256(array.array('f',[v for row in o.matrix_world for v in row]).tobytes())
  if o.type=='MESH':
   for data,prop,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i')]:
    a=array.array(kind,[0])*(len(data)*width);data.foreach_get(prop,a);h.update(a.tobytes())
   for uv in o.data.uv_layers:
    a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  result[o.name]=h.hexdigest()
 return result

def build():
 gold=next(m for m in bpy.data.materials if m.name=='Sanctuary | hand burnished gold')
 def paint(name,file):
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();p=n.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.68;p.inputs['Metallic'].default_value=0;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],o.inputs['Surface']);t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'dist/assets'/file),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);return m
 panel=paint('Caisson | mineral polychrome coffers','caisson-polychrome.jpg');square=paint('Caisson | painted square borders','caisson-coffer-border.jpg')
 parts=[]
 def mesh(name,vs,fs,mat,uvs=None):
  g=bpy.data.meshes.new(name);g.from_pydata(vs,[],fs);g.update();o=bpy.data.objects.new('Caisson enrichment | '+name,g);bpy.context.collection.objects.link(o);g.materials.append(mat);o['sanctuary_interior']=True;o['caisson_vines']=True;parts.append(o)
  uv=g.uv_layers.new(name='Painted motifs')
  for poly in g.polygons:
   poly.use_smooth=uvs is None
   for li in poly.loop_indices:
    i=g.loops[li].vertex_index;v=g.vertices[i].co;uv.data[li].uv=uvs[i] if uvs else (v.x*.5,v.y*.7)
  return o
 # Tube sections stay within their backing board; no free-floating gold shapes.
 def tube(vs,fs,points,normal,radius=.0018,closed=False):
  start=len(vs);sides=6;count=len(points)
  for j,p in enumerate(points):
   d=points[(j+1)%count]-points[(j-1)%count] if closed else points[min(j+1,count-1)]-points[max(0,j-1)];side=d.normalized().cross(normal).normalized()
   for k in range(sides):
    a=k*math.tau/sides;vs.append(p+radius*(normal*math.cos(a)+side*math.sin(a)))
  for j in range(count if closed else count-1):
   for k in range(sides):a=start+j*sides+k;b=start+j*sides+(k+1)%sides;c=start+((j+1)%count)*sides+(k+1)%sides;e=start+((j+1)%count)*sides+k;fs.append((a,b,c,e))
  if not closed:fs.extend([tuple(start+k for k in reversed(range(sides))),tuple(start+(count-1)*sides+k for k in range(sides))])
 levels=[(2.48,4.36),(2.15,4.61),(1.79,4.89),(1.43,5.16),(1.08,5.43)]
 for tier in range(4):
  r,z=levels[tier];r2,z2=levels[tier+1]
  for edge in range(8):
   a=math.pi/8+edge*math.tau/8;b=a+math.tau/8
   c=[Vector((rr*math.cos(t),7.1+rr*math.sin(t),zz)) for rr,zz,t in [(r,z,a),(r,z,b),(r2,z2,a),(r2,z2,b)]];normal=(c[1]-c[0]).cross(c[2]-c[0]).normalized()
   if normal.z>0:normal=-normal
   def point(u,v,h=.00065):return c[0].lerp(c[1],u).lerp(c[2].lerp(c[3],u),v)+normal*h
   mesh('tier %d panel %d'%(tier,edge),[point(.008,.015),point(.992,.015),point(.992,.985),point(.008,.985)],[(3,2,1,0)],panel,[(0,0),(1,0),(1,1),(0,1)])
   vs=[];fs=[]
   for u in [.34,.66]:
    # Real relief outlines sit on the painted cartouches.
    for du,dv in [(.110,.345),(.103,.323)]:tube(vs,fs,[point(u-du,.5-dv,.001),point(u+du,.5-dv,.001),point(u+du,.5+dv,.001),point(u-du,.5+dv,.001)],normal,.0014,True)
    tube(vs,fs,[point(u+.079*math.cos(j*math.tau/64),.5+.237*math.sin(j*math.tau/64),.0015) for j in range(64)],normal,.0015,True)
    # Eight cambered, closed gold petals form the centre of each painted flower.
    for k in range(8):
     angle=(k+.5)*math.tau/8;start=len(vs);nu,nv=12,4
     for front in [True,False]:
      for i in range(nu+1):
       t=i/nu;d=.036*(.1+.9*t);w=.009*max(.02,math.sin(math.pi*t)**.7)
       for j in range(nv+1):
        s=j*2/nv-1;x=d*math.cos(angle)-s*w*math.sin(angle);y=d*math.sin(angle)+s*w*math.cos(angle);h=.001+.005*math.sin(math.pi*t)*(1-.7*s*s) if front else -.0003;vs.append(point(u+x,.5+3*y,h))
     n=(nu+1)*(nv+1)
     for i in range(nu):
      for j in range(nv):
       q=start+i*(nv+1)+j;fs.extend([(q,q+1,q+nv+2,q+nv+1),(q+n,q+nv+1+n,q+nv+2+n,q+1+n)])
     rim=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1) for i in range(nu-1,0,-1)]
     for j,q in enumerate(rim):q2=rim[(j+1)%len(rim)];fs.append((start+q,start+q+n,start+q2+n,start+q2))
   # A continuous fine moulding along both terrace edges.
   for v in [.026,.972]:tube(vs,fs,[point(.018,v,.001),point(.982,v,.001)],normal,.0016)
   mesh('tier %d gilt relief %d'%(tier,edge),vs,fs,gold)
 # Painted square soffits: existing sculpted lotus flowers remain in front.
 for x in [-4.45,-3.05,3.05,4.45]:
  for y in [5.95,7.22,8.49,9.76]:
   mesh('square coffer',[(x-.653,y-.587,4.3042),(x+.653,y-.587,4.3042),(x+.653,y+.587,4.3042),(x-.653,y+.587,4.3042)],[(3,2,1,0)],square,[(0,0),(1,0),(1,1),(0,1)])
 # A pierced scroll necklace between the central lotus and the inner terrace.
 vs=[];fs=[];normal=Vector((0,0,-1))
 def ceiling_z(r):return 5.70+(5.59-5.70)*(r-.78)/(.99-.78) if r<=.99 else 5.59+(5.43-5.59)*(r-.99)/.09
 for k in range(16):
  base=k*math.tau/16+math.pi/16
  for sign in [-1,1]:
   pts=[]
   for j in range(65):
    t=j/64;a=-math.pi*.6+math.tau*1.2*t;spiral=.055*(1-.87*t);u=sign*(.045+spiral*math.cos(a));r=.91+spiral*math.sin(a);theta=base+u/.91;pts.append(Vector((r*math.cos(theta),7.1+r*math.sin(theta),ceiling_z(r)-.004)))
   tube(vs,fs,pts,normal,.0028)
 for r in [1.018,1.042]:
  tube(vs,fs,[Vector((r*math.cos(j*math.tau/192),7.1+r*math.sin(j*math.tau/192),ceiling_z(r)-.003)) for j in range(192)],normal,.0025,True)
 mesh('central paired scroll necklace',vs,fs,gold)
 # Fine embossed veins follow the exact cambered face of the existing large lotus.
 vs=[];fs=[]
 def petal_surface(a,t,s):
  r=.79;wave=math.sin(math.pi*t);d=r*(.075+.925*t);w=r*.235*max(.020,wave**.68);x=d*math.cos(a)-s*w*math.sin(a);y=7.1+d*math.sin(a)+s*w*math.cos(a);rr=math.hypot(x,y-7.1)
  back=5.74+(5.70-5.74)*rr/.78 if rr<=.78 else 5.70+(5.59-5.70)*(rr-.78)/.21
  relief=r*(.125*wave**.65*(1-.74*s*s)+.026*t**6);rim=r*.012*math.exp(-((abs(s)-.82)/.17)**2)*wave;veins=r*.006*wave*(math.exp(-(s/.12)**2)+.55*math.exp(-((abs(s)-.5)/.12)**2))
  return Vector((x,y,min(5.68,back+.002-.012)-.004-relief-rim+veins-.0007))
 for k in range(16):
  a=k*math.tau/16
  for sign in [-1,1]:
   tube(vs,fs,[petal_surface(a,.64+.28*j/48,sign*(.58*math.sin(j/48*math.pi)**.8)) for j in range(49)],normal,.0011)
  for sign in [-1,1]:
   for t in [.70,.79]:tube(vs,fs,[petal_surface(a,t-.055+j/24*.08,sign*j/24*.52) for j in range(25)],normal,.0009)
 mesh('central lotus fine veins',vs,fs,gold)
 # Corner fields carry a complete curling gold wreath around their existing lotus.
 vs=[];fs=[]
 for sx in [-1,1]:
  for sy in [-1,1]:
   for k in range(8):
    a=k*math.tau/8;cx=sx*1.92+.285*math.cos(a);cy=7.1+sy*1.92+.285*math.sin(a);pts=[]
    for j in range(49):
     t=j/48;b=a+t*math.tau*1.18;r=.047*(1-.86*t);pts.append(Vector((cx+r*math.cos(b),cy+r*math.sin(b),4.357)))
    tube(vs,fs,pts,normal,.0023)
   pts=[Vector((sx*x,7.1+sy*y,4.357)) for x,y in [(2.29,2.29),(1.11,2.29),(2.29,1.11)]];tube(vs,fs,pts,normal,.0022,True)
 mesh('corner wreaths and triangular inlay',vs,fs,gold)
 return parts
reports=[];backupdir=R/'evidence/caisson-enrichment-original';backupdir.mkdir(exist_ok=True)
asset=R/'dist/assets/caisson-vines.glb'
if not (backupdir/asset.name).exists():shutil.copy2(asset,backupdir/asset.name)
for filename in ['庄严内殿.blend','听秋寺院.blend']:
 path=R/'source'/filename;backup=path.with_name(path.stem+'-before-dense-polychrome.blend')
 if not backup.exists():shutil.copy2(path,backup)
 bpy.ops.wm.open_mainfile(filepath=str(path));before=signatures()
 for o in list(bpy.data.objects):
  if o.get('caisson_vines'):bpy.data.objects.remove(o,do_unlink=True)
 parts=build();bpy.context.view_layer.update();assert signatures()==before
 triangles=0
 for o in parts:
  assert all(math.isfinite(v) for vert in o.data.vertices for v in vert.co)
  o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));assert signatures()==before
 reports.append({'file':filename,'preservedObjects':len(before),'parts':len(parts),'paintedTerraces':32,'lotusCartouches':64,'squareCoffers':16,'giltPetals':512,'centralScrolls':32,'triangles':triangles})
 if filename=='庄严内殿.blend':
  groups={}
  for o in bpy.data.objects:
   if o.get('caisson_vines'):groups.setdefault(o.data.materials[0],[]).append(o)
  exports=[]
  for mat,group in groups.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in group:o.select_set(True)
   bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name='Caisson enrichment | '+mat.name;o['sourceMaterial']=mat.name;exports.append(o)
  bpy.ops.object.select_all(action='DESELECT')
  for o in exports:o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(asset),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=18,export_draco_normal_quantization=14)
(R/'evidence/caisson-enrichment-native.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2));print('DENSE CAISSON',reports,flush=True)
