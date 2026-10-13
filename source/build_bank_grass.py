"""Original curved sedge-like bank planting, shared by Blender and Three.js."""
import bpy,bmesh,math,random,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'dist/assets';rng=random.Random(73103)

def allowed(x,y,r=.35):
    if abs(x)<2.7+r or y>-.1-r:return False
    if (x/11.5)**2+((y+5.8)/6.9)**2<1.11:return False
    for cx,cy,w,d in [(-6,-14,4.5,1.8),(6,-14,4.5,1.8)]:
        if abs(x-cx)<w/2+r+.12 and abs(y-cy)<d/2+r+.12:return False
    for side in [-1,1]:
        for j in range(27):
            px=side*(13+.65*math.sin(j*.17));py=-10+j*.75
            if abs(x-px)<.725+r+.08 and abs(y-py)<.363+r+.08:return False
    return True

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials=[]
for name,color in [('fresh jade',(.095,.20,.045)),('olive green',(.15,.22,.065)),('old straw',(.28,.24,.11))]:
    m=bpy.data.materials.new('Bank sedge | '+name);m.use_nodes=True;m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.69
    v=m.node_tree.nodes.new('ShaderNodeVertexColor');v.layer_name='Leaf pigment';m.node_tree.links.new(v.outputs['Color'],p.inputs['Base Color'])
    m.use_backface_culling=False;materials.append(m)
centers=[]
for patch in range(60):
    a=patch/60*math.tau;r=rng.uniform(1.12,1.24);cx=11.5*math.cos(a)*r;cy=-5.8+6.9*math.sin(a)*r
    for i in range(rng.randint(2,5)):
        x=cx+rng.uniform(-.48,.48);y=cy+rng.uniform(-.35,.35)
        if allowed(x,y) and all(math.hypot(x-q[0],y-q[1])>.17 for q in centers):centers.append((x,y))
parts=[];blade_count=0;max_radius=0
for i,(x,y) in enumerate(centers):
    vs=[];fs=[];colors=[];uvs=[];mis=[];height=rng.uniform(.18,.37)
    for blade in range(rng.randint(29,44)):
        angle=rng.random()*math.tau;length=height*rng.uniform(.65,1.3);reach=rng.uniform(.12,.25)
        width=rng.uniform(.006,.012);bx=rng.uniform(-.038,.038);by=rng.uniform(-.038,.038)
        kind=2 if rng.random()<.09 else rng.randrange(2);base=materials[kind].diffuse_color[:3];shade=rng.uniform(.8,1.18);offset=len(vs)
        # Three rails form a shallow central rib; 12 segments arc and droop.
        for step in range(13):
            t=step/12;w=width*(1-t)**.72*(.62+.38*math.sin(t*math.pi))
            bend=reach*t*t;z=.15+length*(1.42*t-.50*t*t-.22*t**4)
            for side in [-1,0,1]:
                xx=x+bx+math.cos(angle)*bend-math.sin(angle)*w*side;yy=y+by+math.sin(angle)*bend+math.cos(angle)*w*side
                vs.append((xx,yy,z+(1-abs(side))*w*.28));uvs.append(((side+1)/2,t))
                fade=(.62+.38*t)*shade*(1.08 if side else .93)
                colors.append(tuple(c*fade for c in base)+(1,));max_radius=max(max_radius,math.hypot(xx-x,yy-y))
        for step in range(12):
            for side in range(2):
                q=offset+step*3+side;fs.append((q,q+1,q+4,q+3));mis.append(kind)
        blade_count+=1
    mesh=bpy.data.meshes.new(f'Sedge tuft {i:03}');mesh.from_pydata(vs,[],fs);mesh.update()
    for m in materials:mesh.materials.append(m)
    pigment=mesh.color_attributes.new(name='Leaf pigment',type='FLOAT_COLOR',domain='POINT')
    for v,c in zip(pigment.data,colors):v.color=c
    uv=mesh.uv_layers.new()
    for p,mi in zip(mesh.polygons,mis):
        p.material_index=mi;p.use_smooth=True
        for li in p.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
    o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o);o['bank_grass']=True;parts.append(o)
assert max_radius<.35
prototype=R/'source/池岸细叶草.blend';bpy.ops.wm.save_as_mainfile(filepath=str(prototype))
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=str(A/'bank-grass.glb'),export_format='GLB',use_selection=True,export_yup=True,export_materials='EXPORT')

full=R/'source/听秋寺院.blend';backup=R/'source/听秋寺院-before-bank-grass.blend'
if not backup.exists():shutil.copy2(full,backup)
bpy.ops.wm.open_mainfile(filepath=str(full));preserved={tag:sum(bool(o.get(tag)) for o in bpy.data.objects) for tag in ['altar_sculpture','incense_vessel','sanctuary_interior','fern_cutout_restored']}
for o in list(bpy.data.objects):
    if o.get('bank_grass'):bpy.data.objects.remove(o,do_unlink=True)
removed=0
for o in bpy.data.objects:
    if o.type!='MESH' or not any(m and m.name=='Soft forest moss' for m in o.data.materials):continue
    bm=bmesh.new();bm.from_mesh(o.data);erase=[]
    for f in bm.faces:
        pts=[o.matrix_world@v.co for v in f.verts];zs=[p.z for p in pts]
        if len(pts)==4 and sum(abs(z-.18)<.00002 for z in zs)==2 and .30<max(zs)<.72:erase.append(f)
    removed+=len(erase);bmesh.ops.delete(bm,geom=erase,context='FACES');bm.to_mesh(o.data);bm.free()
with bpy.data.libraries.load(str(prototype),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
    if o:bpy.context.collection.objects.link(o)
for tag,count in preserved.items():assert sum(bool(o.get(tag)) for o in bpy.data.objects)==count
bpy.ops.wm.save_as_mainfile(filepath=str(full))
meta={'tufts':len(centers),'blades':blade_count,'segmentsPerBlade':12,'maxRadius':max_radius,'centersNative':centers,'removedLegacyQuads':removed,'preserved':preserved}
(A/'bank-grass.json').write_text(json.dumps(meta,indent=2));print('BANK_GRASS',json.dumps({k:v for k,v in meta.items() if k!='centersNative'}))
