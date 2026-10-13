import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/听秋寺院.blend'))
parts=[o for o in bpy.data.objects if o.get('sanctuary_interior')]
meta=json.loads((R/'dist/assets/sanctuary.json').read_text())
assert len(parts)==meta['components']
assert len([o for o in bpy.data.objects if o.get('altar_sculpture')])==38
assert len([o for o in bpy.data.objects if o.get('incense_vessel')])==196
assert len([o for o in parts if o.name.startswith('Candle | red wax')])==4
assert len([o for o in parts if o.name.startswith('Offering | celadon water cup')])==7
assert len([o for o in parts if 'celestial garden assembly' in o.name or 'continuous lotus paradise' in o.name])==4
assert any(o.get('detailed_koi') for o in bpy.data.objects)
assert bpy.data.objects.get('Reflecting pond')
clusters={}
for o in parts:
 if 'dougong_cluster' in o:clusters.setdefault(o['dougong_cluster'],[]).append(o)
assert len(clusters)==96
edge_offsets=[]
for cluster,objects in clusters.items():
 assert len([o for o in objects if 'cloud gong' in o.name or 'radial arm' in o.name or 'crossing gong' in o.name])==3
 base=next(o for o in objects if 'seated dou block' in o.name)
 center=sum((base.matrix_world@Vector(v) for v in base.bound_box),Vector())/8
 level=cluster//24;r=[2.48,2.15,1.79,1.43][level]
 import math
 corners=[Vector((r*math.cos(math.pi/8+i*math.tau/8),7.1+r*math.sin(math.pi/8+i*math.tau/8))) for i in range(8)]
 point=Vector((center.x,center.y));distances=[]
 for i in range(8):
  a=corners[i];d=corners[(i+1)%8]-a;t=max(0,min(1,(point-a).dot(d)/d.length_squared));distances.append((point-a-t*d).length)
 edge_offsets.append(min(distances));assert abs(min(distances)-.073)<.002,(cluster,min(distances))
 for o in objects:
  if o.type!='MESH':continue
  assert o.data.uv_layers.active
  for face in o.data.polygons:
   uv=[o.data.uv_layers.active.data[i].uv for i in face.loop_indices]
   area=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(uv,uv[1:]+uv[:1])))*.5
   assert area>1e-10,(o.name,face.index,area)
# The central ceiling opening must not be capped by the former low grid.
hits=[]
for o in parts:
 if o.type!='MESH':continue
 inv=o.matrix_world.inverted();origin=inv@Vector((.025,7.10,4.0));direction=inv.to_3x3()@Vector((0,0,1));hit,p,n,i=o.ray_cast(origin,direction)
 if hit:
  p=o.matrix_world@p
  if p.z>4:hits.append((p.z,o.name))
assert hits and min(hits)[0]>5.3,min(hits)
roof_clearances=[]
old_roof=[o for o in bpy.data.objects if o.type=='MESH' and not o.get('sanctuary_interior') and any(m and 'cedar' in m.name.lower() for m in o.data.materials)]
for x in [-.7,.025,.7]:
 for y in [6.4,7.1,7.8]:
  old=[];new=[]
  for objects,out in [(old_roof,old),(parts,new)]:
   for o in objects:
    if o.type!='MESH':continue
    inv=o.matrix_world.inverted();hit,p,n,i=o.ray_cast(inv@Vector((x,y,4.45)),inv.to_3x3()@Vector((0,0,1)))
    if hit:out.append((o.matrix_world@p).z)
  assert old and new and min(old)>min(new),(x,y,old,new)
  roof_clearances.append(min(old)-min(new))
result={'editableComponents':len(parts),'murals':4,'redCandles':4,'waterCups':7,'dougongClusters':len(clusters),'bracketEdgeOffsets':[min(edge_offsets),max(edge_offsets)],'bracketUVsValid':True,'ceilingCenterClearHeight':min(hits)[0],'minimumTestedRoofClearance':min(roof_clearances),'sculptureAndIncensePreserved':True,'pondAndKoiPreserved':True}
(R/'evidence/sanctuary-native-verification.json').write_text(json.dumps(result,indent=2));print('VERIFIED',result)
