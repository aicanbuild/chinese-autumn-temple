"""Original framed lacquer tabletop with mitred rails and restrained gold inlay."""
import bpy,bmesh,math
REGION=[-1.751,1.751,7.849,9.451,1.784,1.896]
def is_altar_top(o):return bool(o.get('crafted_altar_tabletop'))
def inside_old_top(p):return REGION[0]<p.x<REGION[1] and REGION[2]<p.y<REGION[3] and REGION[4]<p.z<REGION[5]
def build_altar_tabletop():
 parts=[];used={m for o in bpy.data.objects if o.get('sanctuary_interior') for m in getattr(o.data,'materials',[]) if m}
 def material(name):return next(m for m in used if m.name.startswith('Sanctuary | '+name))
 dark,wood,gold=[material(n) for n in ['carved rosewood','oxblood lacquer','hand burnished gold']]
 def prism(name,outline,bottom,top,mat,bevel,grain=0):
  n=len(outline);vs=[(x,y+8.65,z) for z in [bottom,top] for x,y in outline];faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
  data=bpy.data.meshes.new(name);data.from_pydata(vs,[],faces);data.update();o=bpy.data.objects.new('Altar tabletop | '+name,data);bpy.context.collection.objects.link(o);data.materials.append(mat)
  uv=data.uv_layers.new(name='Joinery grain')
  for p in data.polygons:
   second=1-grain if abs(p.normal.z)>.5 else 2
   first=grain if abs(p.normal[grain])<.8 else 1-grain
   for li in p.loop_indices:
    v=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(v[first]*.5+(0 if grain==0 else .23),v[second]*.7)
  if bevel:
   mod=o.modifiers.new('Hand softened joinery arris','BEVEL');mod.width=bevel;mod.segments=4
   bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
  # Weighted corner normals retain broad planar reflections across the flat top.
  for f in o.data.polygons:f.use_smooth=max(abs(c) for c in f.normal)<.999
  o['sanctuary_interior']=True;o['crafted_altar_tabletop']=True;parts.append(o);return o
 def rectangle(w,d):return [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
 prism('rounded solid cornice',rectangle(3.50,1.60),1.785,1.884,dark,.010)
 prism('inset lacquer panel',rectangle(3.298,1.398),1.883,1.895,wood,.001)
 outer=rectangle(3.50,1.60);inner=rectangle(3.30,1.40)
 for i in range(4):
  j=(i+1)%4
  prism('mitred rail %d'%i,[outer[i],outer[j],inner[j],inner[i]],1.883,1.895,dark,.001,0 if i%2==0 else 1)
 def inlay(name,w,d,z,radius,corner=.012):
  pts=[]
  for cx,cy,start in [(w/2-corner,d/2-corner,0),(-w/2+corner,d/2-corner,90),(-w/2+corner,-d/2+corner,180),(w/2-corner,-d/2+corner,270)]:
   for j in range(13):a=math.radians(start+j*90/12);pts.append((cx+corner*math.cos(a),8.65+cy+corner*math.sin(a),z))
  c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=radius;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(pts)-1);s.use_cyclic_u=True
  for p,v in zip(s.points,pts):p.co=(*v,1)
  o=bpy.data.objects.new('Altar tabletop | '+name,c);bpy.context.collection.objects.link(o);c.materials.append(gold);o['sanctuary_interior']=True;o['crafted_altar_tabletop']=True;parts.append(o)
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object
  uv=o.data.uv_layers.new(name='Gold grain')
  for f in o.data.polygons:
   for li in f.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.5,v.y*.5)
 inlay('fine perimeter inlay',3.45,1.55,1.8949,.001)
 inlay('lower cornice gilt bead',3.50,1.60,1.808,.0025)
 return parts,{'parts':len(parts),'top':1.895,'bottom':1.785,'width':3.5,'depth':1.6,'mitredRails':4,'inlayRadius':.001,'removeRegionNative':REGION}
