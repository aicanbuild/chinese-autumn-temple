"""Adapt vmccurley's CC BY 4.0 Chinatown Lion Statue scan for the temple.
https://zenodo.org/records/10335910 ; crop, scale, mirror, clean and rematerial.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];A=R/'dist/assets'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'source/reference-assets/guardians/10335910/249b684b29234e26b1a09038bcf1023c.glb'))
obs=[o for o in bpy.data.objects if o.type=='MESH']
for o in obs:
 o.data.transform(o.matrix_world);o.parent=None;o.matrix_world=Matrix.Identity(4)
bpy.ops.object.select_all(action='DESELECT')
for o in obs:o.select_set(True)
bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object
# Keep the scanned feet, ball and a thin integral stone seat, remove the tall
# scanned roadside plinth so the existing temple pedestals remain in place.
cut=.97;bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=(0,0,cut),plane_no=(0,0,1),clear_inner=True)
# Only cap the new planar cut, leaving actual carved openings untouched.
border=[e for e in bm.edges if e.is_boundary and all(abs(v.co.z-cut)<.00001 for v in e.verts)]
bmesh.ops.holes_fill(bm,edges=border,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
lo=Vector([min(v.co[k] for v in o.data.vertices) for k in range(3)]);hi=Vector([max(v.co[k] for v in o.data.vertices) for k in range(3)])
scale=1.46/(hi.z-lo.z);center=(hi+lo)*.5
o.data.transform(Matrix.Diagonal((scale,scale,scale,1))@Matrix.Translation((-center.x,-center.y,-lo.z)))
# Mild reduction removes oversampled scan triangles while preserving silhouette.
bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Conservative scan reduction','DECIMATE');mod.ratio=.56;bpy.ops.object.modifier_apply(modifier=mod.name)
# Decimation can move extremal vertices by microns; restore exact contact and height.
low=min(v.co.z for v in o.data.vertices);high=max(v.co.z for v in o.data.vertices)
o.data.transform(Matrix.Diagonal((1.46/(high-low),)*3+(1,))@Matrix.Translation((0,0,-low)))
for p in o.data.polygons:p.use_smooth=True
mat=o.data.materials[0];mat.name='Guardian | scanned pale carved stone';nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.78
tex=next(n for n in nodes if n.type=='TEX_IMAGE');tex.image.name='Guardian stone | original CC BY scan albedo';tex.image.scale(2048,2048);tex.image.pack()
# Additional fine roughness variation follows the original stone luminance.
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.68,.68,.68,1);ramp.color_ramp.elements[1].color=(.84,.84,.84,1);links.new(tex.outputs['Color'],ramp.inputs[0]);links.new(ramp.outputs[0],p.inputs['Roughness'])
# glTF does not export arbitrary ramps: bake an authored roughness image from
# the scan's actual image pixels, retaining exactly the existing UV layout.
import numpy as np
pixels=np.array(tex.image.pixels[:],dtype=np.float32).reshape(-1,4);gray=pixels[:,:3]@np.array([.2126,.7152,.0722]);rough=np.zeros_like(pixels);rough[:,:3]=(.68+.16*gray[:,None]);rough[:,3]=1
ri=bpy.data.images.new('Guardian stone | measured-tone roughness',width=2048,height=2048);ri.colorspace_settings.name='Non-Color';ri.pixels.foreach_set(rough.ravel());ri.pack();rn=nodes.new('ShaderNodeTexImage');rn.image=ri;links.new(rn.outputs[0],p.inputs['Roughness'])
o.name='Guardian | east scanned lion';o['guardian_scan']=True;o['attribution']='Chinatown Lion Statue — vmccurley — CC BY 4.0 — https://zenodo.org/records/10335910; cropped, rescaled and mirrored';o.location=(3.6,2.25,.925)
left=o.copy();left.data=o.data.copy();bpy.context.collection.objects.link(left);left.name='Guardian | west mirrored lion';left.location.x=-3.6;left.data.transform(Matrix.Diagonal((-1,1,1,1)));left.data.flip_normals()
for other in list(bpy.data.objects):
 if other not in [o,left]:bpy.data.objects.remove(other,do_unlink=True)
bpy.context.view_layer.update()
report={'source':'https://zenodo.org/records/10335910','creator':'vmccurley','license':'CC BY 4.0','adaptation':'cropped roadside plinth, reduced scan, scaled, mirrored, resized albedo and authored roughness','count':2,'trianglesPerLion':sum(len(p.vertices)-2 for p in o.data.polygons),'height':1.46,'pedestalTop':.925,'bounds':[[min((obj.matrix_world@v.co)[k] for v in obj.data.vertices) for k in range(3)] for obj in [o,left]]}
bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/门前石狮.blend'));bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(A/'guardian-lions.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_extras=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
(A/'guardian-lions.json').write_text(json.dumps(report,indent=2));print('GUARDIANS',report,flush=True)
# Asset-only three-quarter inspection.
bpy.ops.object.light_add(type='AREA',location=(0,-2,6));bpy.context.object.data.energy=500;bpy.context.object.data.size=4
bpy.context.scene.world.color=(.35,.35,.35);bpy.ops.object.camera_add(location=(6.6,-2.75,3.2));cam=bpy.context.object;cam.rotation_euler=(Vector((3.6,2.25,1.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.2
sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=640;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.filepath=str(R/'evidence/guardian-asset.png');bpy.ops.render.render(write_still=True)
