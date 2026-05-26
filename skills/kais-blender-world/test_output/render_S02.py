import bpy, sys, mathutils
sys.stderr.write('[blender-layout] Starting...\\n')
def get_aabb(obj):
    cs = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    xs=[c.x for c in cs]; ys=[c.y for c in cs]; zs=[c.z for c in cs]
    return mathutils.Vector((min(xs),min(ys),min(zs))), mathutils.Vector((max(xs),max(ys),max(zs)))

def scene_aabb(exclude={'Floor'}):
    mn=mx=None
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','ARMATURE') and o.name not in exclude:
            a,b=get_aabb(o)
            if mn is None: mn,mx=a,b
            else:
                mn=mathutils.Vector((min(mn.x,a.x),min(mn.y,a.y),min(mn.z,a.z)))
                mx=mathutils.Vector((max(mx.x,b.x),max(mx.y,b.y),max(mx.z,b.z)))
    return mn,mx

def look_at(cam, target):
    d=mathutils.Vector(target)-cam.location
    cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()

bpy.ops.wm.open_mainfile(filepath=r'D:\BlenderAgent\cache\full_scene.blend')
sys.stderr.write('[blender-layout] Scene loaded\\n')
# ── Scale sofa to match character proportions ──
sofa_scale = 1.0
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and 'sofa_02' in obj.name.lower():
        obj.scale = (sofa_scale, sofa_scale, sofa_scale)
bpy.context.view_layer.update()

# ── Assemble sofa components ──
base=next((o for o in bpy.context.scene.objects if o.type=='MESH' and 'sofa_02_base' in o.name.lower()),None)
seat=next((o for o in bpy.context.scene.objects if o.type=='MESH' and 'sofa_02_seat' in o.name.lower()),None)
if base and seat:
    b_mn,b_mx=get_aabb(base); s_mn,s_mx=get_aabb(seat)
    if s_mn.z < b_mx.z - 0.01:
        seat.location.z += b_mx.z - s_mn.z
        bpy.context.view_layer.update()
        sys.stderr.write(f'  Assembled seat onto base\\n')

# ── Character 1 ──
for obj in list(bpy.context.scene.objects):
    if obj.type=='ARMATURE' or obj.name=='Human':
        bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.import_scene.fbx(filepath=r'D:\BlenderAgent\animations\motions\fighting_idle.fbx', use_anim=True)
arm = next((o for o in bpy.context.scene.objects if o.type=='ARMATURE'), None)
if arm and arm.animation_data:
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()

for m in bpy.context.scene.objects:
    if m.type=='MESH' and m.name=='Beta_Joints':
        m.hide_render=True; m.hide_viewport=True

c_mn,c_mx=get_aabb(arm)
for m in bpy.context.scene.objects:
    if m.type=='MESH' and m.parent and m.parent.type=='ARMATURE':
        mn,mx=get_aabb(m)
        for ax in range(3):
            if mn[ax]<c_mn[ax]: c_mn[ax]=mn[ax]
            if mx[ax]>c_mx[ax]: c_mx[ax]=mx[ax]
ch=c_mx.z-c_mn.z
sys.stderr.write(f'  Char1: z=[{c_mn.z:.2f},{c_mx.z:.2f}] h={ch:.2f}\\n')

# ── Character 2 ──
for obj in list(bpy.context.scene.objects):
    if obj.type=='ARMATURE' or obj.name=='Human':
        bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.import_scene.fbx(filepath=r'D:\BlenderAgent\animations\motions\roaring_inplace.fbx', use_anim=True)
arm = next((o for o in bpy.context.scene.objects if o.type=='ARMATURE'), None)
if arm and arm.animation_data:
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()

for m in bpy.context.scene.objects:
    if m.type=='MESH' and m.name=='Beta_Joints':
        m.hide_render=True; m.hide_viewport=True

c_mn,c_mx=get_aabb(arm)
for m in bpy.context.scene.objects:
    if m.type=='MESH' and m.parent and m.parent.type=='ARMATURE':
        mn,mx=get_aabb(m)
        for ax in range(3):
            if mn[ax]<c_mn[ax]: c_mn[ax]=mn[ax]
            if mx[ax]>c_mx[ax]: c_mx[ax]=mx[ax]
ch=c_mx.z-c_mn.z
sys.stderr.write(f'  Char2: z=[{c_mn.z:.2f},{c_mx.z:.2f}] h={ch:.2f}\\n')

# ── HDRI ──
world=bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world=world
world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
if bg:
    env=world.node_tree.nodes.new(type='ShaderNodeTexEnvironment')
    env.image=bpy.data.images.load(r'D:\BlenderAgent\assets\polyhaven\hdris\\night_roads_02_4k.hdr')
    world.node_tree.links.new(env.outputs[0],bg.inputs[0])
    bg.inputs[1].default_value=1.0

# ── Camera + Render ──
cam=next((o for o in bpy.context.scene.objects if o.type=='CAMERA'),None)
if not cam:
    cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
    bpy.context.scene.collection.objects.link(cam)
bpy.context.scene.camera=cam
mn,mx=scene_aabb()
ctr=(mn+mx)/2

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='GPU'
scene.render.resolution_x=1920
scene.render.resolution_y=1080
scene.cycles.samples=128

cam.location=ctr+mathutils.Vector((-2.0,-2.5,1.8))
look_at(cam,ctr)
scene.render.filepath=r'D:\BlenderAgent\outputs\dungeon\S02\\scene_medium.png'
bpy.ops.render.render(write_still=True)
sys.stderr.write(f'[OK] medium\\n')

cam.location=ctr+mathutils.Vector((-1.0,-1.2,1.1))
look_at(cam,ctr)
scene.render.filepath=r'D:\BlenderAgent\outputs\dungeon\S02\\scene_otw_over_shoulder.png'
bpy.ops.render.render(write_still=True)
sys.stderr.write(f'[OK] otw_over_shoulder\\n')

cam.location=ctr+mathutils.Vector((-1.2,-1.6,1.3))
look_at(cam,ctr)
scene.render.filepath=r'D:\BlenderAgent\outputs\dungeon\S02\\scene_closeup.png'
bpy.ops.render.render(write_still=True)
sys.stderr.write(f'[OK] closeup\\n')

print('DONE')