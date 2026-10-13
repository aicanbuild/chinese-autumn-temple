import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/主殿佛像.blend'))
body=next(o for o in bpy.data.objects if o.name.startswith('Tang sculpture'))
vs=[body.matrix_world@v.co-Vector((0,8.6,1.915)) for v in body.data.vertices]
# Dense sections around the exposed forearms; report actual front surface.
report={}
for side in [-1,1]:
 out=[]
 for z in [.82,.88,.94,1.,1.06,1.12,1.18]:
  pts=[p for p in vs if .20<side*p.x<.51 and abs(p.z-z)<.009 and p.y<-.08]
  if pts:out.append({'z':z,'bounds':[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)]})
 report[str(side)]=out
(R/'evidence/wrist-sections.json').write_text(json.dumps(report,indent=2))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.world.color=(.15,.15,.15)
for loc,energy,size in [((2,5,6),500,4),((-3,8,5),700,3)]:
 d=bpy.data.lights.new('Inspection area','AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new('Inspection area',d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,8.4,3))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Inspection camera');cam=bpy.data.objects.new('Inspection camera',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.ortho_scale=1.1
for name,loc,target in [('front',(0,5,3),(0,8.35,2.99)),('side',(3,8.1,3),(0,8.35,2.99))]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(R/f'evidence/wrists-before-{name}.png');bpy.ops.render.render(write_still=True)
print('WRIST_SECTIONS',json.dumps(report),flush=True)
