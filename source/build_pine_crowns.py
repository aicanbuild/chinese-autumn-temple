"""Original three-dimensional pine shoots attached to the six existing pruned trees."""
import bpy,bmesh,math,random,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';rng=random.Random(81132)
layout=json.loads((A/'garden-trees.json').read_text());pines=layout['pines']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
needle=bpy.data.materials.new('Pine | waxy green needles');needle.use_nodes=True;needle.use_backface_culling=False
p=needle.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.56
color=needle.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name='Needle pigment';needle.node_tree.links.new(color.outputs['Color'],p.inputs['Base Color'])
wood=bpy.data.materials.new('Pine | fine cinnamon twigs');wood.use_nodes=True;p=wood.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.095,.048,.019,1);p.inputs['Roughness'].default_value=.87

def batch():return [[],[],[]]
def tube(data,points,r0,r1,sides=5):
    vs,fs,cs=data;offset=len(vs)
    for j,p in enumerate(points):
        tangent=(points[min(j+1,len(points)-1)]-points[max(0,j-1)]).normalized();q=tangent.to_track_quat('Z','Y');r=r0+(r1-r0)*j/(len(points)-1)
        for k in range(sides):vs.append(tuple(p+q@Vector((math.cos(k*math.tau/sides)*r,math.sin(k*math.tau/sides)*r,0))));cs.append((1,1,1,1))
    for j in range(len(points)-1):
        for k in range(sides):a=offset+j*sides+k;b=offset+j*sides+(k+1)%sides;fs.append((a,b,b+sides,a+sides))

def pine_needle(data,base,end,bend,radius,pigment):
    vs,fs,cs=data;offset=len(vs);axis=(end-base).normalized();q=axis.to_track_quat('Z','Y')
    for t in [0,.53]:
        c=base.lerp(end,t)+bend*math.sin(t*math.pi);r=radius*(1-.4*t)
        for k in range(3):vs.append(tuple(c+q@Vector((math.cos(k*math.tau/3)*r,math.sin(k*math.tau/3)*r,0))));cs.append(tuple(v*(.72+.28*t) for v in pigment)+(1,))
    vs.append(tuple(end));cs.append(tuple(v*1.04 for v in pigment)+(1,))
    for k in range(3):a=offset+k;b=offset+(k+1)%3;fs.extend([(a,b,b+3,a+3),(a+3,b+3,offset+6)])

def object_mesh(name,data,mat):
    vs,fs,cs=data;me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);o['pine_crown']=True
    if mat==needle:
        ca=me.color_attributes.new(name='Needle pigment',type='FLOAT_COLOR',domain='POINT')
        for v,c in zip(ca.data,cs):v.color=c
    for f in me.polygons:f.use_smooth=True
    return o

near=[];far=[];attachments=[];needle_count=0
for ti,(x,y,h) in enumerate(pines):
    for level in range(6):
        a=level*2.35;reach=(1-level*.10)*1.45;z=.8+level*h*.14
        origin=Vector((x+math.cos(a)*reach,y+math.sin(a)*reach,z+.23));attachments.append(tuple(origin))
        nd=batch();fd=batch();twigs=batch()
        # An open fan of curved branches, with upright needle-bearing shoots.
        for fan in range(7):
            angle=a+(fan-3)*.49+rng.uniform(-.08,.08);direction=Vector((math.cos(angle),math.sin(angle),0));span=rng.uniform(.49,.78)*(1-level*.033)
            end=origin+direction*span+Vector((0,0,rng.uniform(.05,.17)))
            points=[origin.lerp(end,t/8)+Vector((0,0,-.07*math.sin(t/8*math.pi))) for t in range(9)];tube(twigs,points,.012,.003)
            for shoot in range(7):
                root=points[2+shoot];az=angle+(1 if shoot%2 else -1)*rng.uniform(.5,1.25)
                d=Vector((math.cos(az)*.66,math.sin(az)*.66,rng.uniform(.40,.8))).normalized();length=rng.uniform(.19,.32)
                tip=root+d*length;curve=[root.lerp(tip,t/5)+Vector((0,0,-.025*math.sin(t/5*math.pi))) for t in range(6)];tube(twigs,curve,.004,.0016,4)
                u=d.cross(Vector((0,0,1))).normalized();v=d.cross(u).normalized()
                for pair in range(12):
                    t=.18+pair*.069;base=root.lerp(tip,t)+Vector((0,0,-.025*math.sin(t*math.pi)));rot=pair*2.399+rng.uniform(-.12,.12)
                    radial=u*math.cos(rot)+v*math.sin(rot)
                    for fascicle in [0,1]:
                        radial2=radial if fascicle==0 else -radial
                        for side in [-1,1]:
                            # Longer, slightly broader paired needles keep the foliage mass
                            # legible from the pond without adding vertices or draw calls.
                            direction=(d*.52+radial2*.82+u*side*.10).normalized();ll=rng.uniform(.14,.22)*(1-.18*t)
                            e=base+direction*ll;bend=Vector((0,0,rng.uniform(.006,.016)));radius=rng.uniform(.0023,.0031)
                            shade=rng.uniform(.75,1.2);pigment=(.052*shade+.034*t,.132*shade+.053*t,.031*shade+.015*t)
                            pine_needle(nd,base,e,bend,radius,pigment)
                            if pair%3==0:pine_needle(fd,base,e,bend,radius*1.8,pigment)
                            needle_count+=1
        near.extend([(f'Pine {ti} crown {level} needles',nd,needle),(f'Pine {ti} crown {level} twigs',twigs,wood)])
        far.extend([(f'Pine {ti} crown {level} needles',fd,needle),(f'Pine {ti} crown {level} twigs',twigs,wood)])
for name,data,mat in near:object_mesh(name,data,mat)
prototype=R/'source/庭院立体松针.blend';bpy.ops.wm.save_as_mainfile(filepath=str(prototype))
def export_batches(filename):
    # Per-tree geometry preserves spatial culling; only two materials per tree.
    for i in range(6):
        for kind in ['needles','twigs']:
            bpy.ops.object.select_all(action='DESELECT');objs=[o for o in bpy.context.scene.objects if o.name.startswith(f'Pine {i} crown') and o.name.endswith(kind)]
            for o in objs:o.select_set(True)
            bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();bpy.context.object.name=f'Pine {i} {kind}'
    bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(A/filename),export_format='GLB',use_selection=True,export_yup=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6)
export_batches('pine-crowns.glb')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for name,data,mat in far:object_mesh(name,data,mat)
export_batches('pine-crowns-distant.glb')

full=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-pine-crowns.blend'
if not backup.exists():shutil.copy2(full,backup)
bpy.ops.wm.open_mainfile(filepath=str(full));removed=0
preserved={tag:sum(bool(o.get(tag)) for o in bpy.data.objects) for tag in ['altar_sculpture','incense_vessel','sanctuary_interior','fern_cutout_restored','bank_grass']}
for o in list(bpy.data.objects):
    if o.get('pine_crown'):bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
    if o.type!='MESH' or not any(m and m.name=='Deep green pine needles' for m in o.data.materials):continue
    bm=bmesh.new();bm.from_mesh(o.data);old=[f for f in bm.faces if all((o.matrix_world@v.co).y<2 for v in f.verts)];removed+=len(old);bmesh.ops.delete(bm,geom=old,context='FACES');bm.to_mesh(o.data);bm.free()
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
    if o:bpy.context.collection.objects.link(o)
for tag,n in preserved.items():assert sum(bool(o.get(tag)) for o in bpy.data.objects)==n
bpy.ops.wm.save_as_mainfile(filepath=str(full))
previous=json.loads((A/'pine-crowns.json').read_text()) if (A/'pine-crowns.json').exists() else {}
meta={'pines':pines,'crowns':36,'needleCount':needle_count,'parts':72,'batches':12,'distantNeedles':needle_count//3,'attachmentPointsNative':attachments,'removedOldNeedleFaces':removed or previous.get('removedOldNeedleFaces',0),'preserved':preserved}
(A/'pine-crowns.json').write_text(json.dumps(meta,indent=2));print('PINE_CROWNS',json.dumps({k:v for k,v in meta.items() if k!='attachmentPointsNative'}))
