"""Read-only, authored furniture bounds for smooth interior camera collision."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];path=R/'source/听秋寺院.blend';before=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();groups={}
for o in bpy.data.objects:
 if o.type not in {'MESH','CURVE'}:continue
 obj=o.evaluated_get(deps);points=[obj.matrix_world@Vector(v) for v in obj.bound_box];center=sum(points,Vector())/8;side='left' if center.x<0 else 'right';key=None
 if o.get('door_back'):key='door-leaf-'+str(o['door_index'])
 elif o.get('altar_sculpture'):key='buddha'
 elif o.get('wooden_fish'):key='wooden-fish-stand'
 elif o.get('incense_vessel') or o.get('native_incense_stick'):key='incense-vessel'
 elif o.get('crafted_altar_tabletop') or o.name.startswith('Altar | recessed front panel'):key='central-altar'
 elif o.name.startswith('Altar | side offering') or o.name.startswith('Altar | gilt tabletop') or o.name.startswith('Altar | square mortised') or o.name.startswith('Altar | cloud apron'):key=side+'-offering-table'
 elif o.get('crafted_candlestick'):key='candle-'+str(o['candlestick_index'])
 elif o.name.startswith('Candle | red wax'):key='candle-'+str(o['flame_index'])
 elif o.name.startswith('Offering | celadon lotus vase') or o.name.startswith('Vase |'):key=side+'-vase'
 elif o.get('lotus_bouquet'):key=side+'-bouquet'
 elif o.get('altar_fruit') or o.name.startswith('Offering | bronze fruit tazza'):key=side+'-fruit-offering'
 elif o.get('crafted_offering_cup'):key='offering-cup-'+str(o['cup_index'])
 if not key:continue
 mesh=obj.to_mesh();points=[obj.matrix_world@v.co for v in mesh.vertices];obj.to_mesh_clear()
 if not points:continue
 if key not in groups:groups[key]=[]
 groups[key].extend(points)
assert {'buddha','incense-vessel','central-altar','left-offering-table','right-offering-table','left-vase','right-vase'}.issubset(groups)
boxes=[]
for name,points in sorted(groups.items()):
 lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 boxes.append({'name':name,'min':[lo[0],lo[2],-hi[1]],'max':[hi[0],hi[2],-lo[1]]})
assert hashlib.sha256(path.read_bytes()).hexdigest()==before
result={'sourceSHA256':before,'sourceUnchanged':True,'cameraRadius':.16,'targetMin':[-5.15,1.55,-10.02],'targetMax':[5.15,5.6,-4.4],'cameraMin':[-5.08,1.92,-9.95],'cameraMax':[5.08,4,-4.02],'boxes':boxes}
(R/'dist/assets/hall-navigation.json').write_text(json.dumps(result,indent=2));print('HALL CAMERA',json.dumps(result),flush=True)
