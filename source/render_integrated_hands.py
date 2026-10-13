import bpy,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/主殿佛像-衔接候选.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.15,.15,.15,1)
s.view_settings.view_transform='AgX'
for loc,energy,size in [((2,5,6),500,4),((-3,8,5),700,3)]:
 d=bpy.data.lights.new('Inspection area','AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new('Inspection area',d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,8.4,3))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Inspection camera');cam=bpy.data.objects.new('Inspection camera',d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO'
views=[('front',(0,5,3),(0,8.4,3),1.20),('side',(3,8.05,3),(0,8.35,3),1.20),('giving',(-.4,6.8,2.72),(-.413,8.56,2.725),.34),('raised',(.27,6.8,3.02),(.267,8.345,3.01),.36),('raised-side',(1.7,8.3,3),(.274,8.35,2.985),.46)]
if '--preview' in sys.argv:
 views=[v for v in views if v[0] in ['raised','giving']];s.cycles.samples=16;s.render.resolution_x=700;s.render.resolution_y=700
for name,loc,target,scale in views:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;s.render.filepath=str(R/f'evidence/hands-integrated-{name}.png');bpy.ops.render.render(write_still=True)
