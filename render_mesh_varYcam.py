import bpy
import bmesh
import random
import math
from mathutils import Vector, Euler
import os
import string

rridx = 2

path_to_output_images='/nfs/bigdisk/sagnik/swat3d/img/' + str(rridx) + '/'
path_to_output_uv = '/nfs/bigdisk/sagnik/swat3d/uv/' + str(rridx) + '/'
path_to_output_wc = '/nfs/bigdisk/sagnik/swat3d/wc/' + str(rridx) + '/'
path_to_output_blends='/nfs/bigdisk/sagnik/swat3d/bld/' + str(rridx) + '/'

for fd in [path_to_output_images, path_to_output_uv, path_to_output_blends]:
    if not os.path.exists(fd):
        os.makedirs(fd)

# path_to_input_meshes='/nfs/bigdisk/kema/data/docwarp/dobj/'
def reset_blend():
    # bpy.ops.wm.read_factory_settings()
    bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)

    # for scene in bpy.data.scenes:
    #     for obj in scene.objects:
    #         scene.objects.unlink(obj)

    # only worry about data in the startup scene
    for bpy_data_iter in (
            bpy.data.meshes,
            bpy.data.lamps,
            bpy.data.images,
            bpy.data.materials
            ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data, do_unlink=True)



from bpy_extras.object_utils import world_to_camera_view

def isVisible(mesh, cam):    
    bm = bmesh.new()   # create an empty BMesh
    bm.from_mesh(mesh.data) 
    cam_direction = cam.matrix_world.to_quaternion() * Vector((0.0, 0.0, -1.0))
    cam_pos = cam.location
    # print(cam_direction)
    mat_world = mesh.matrix_world
    ct1 = 0
    ct2 = 0
    for v in bm.verts:
        co_ndc = world_to_camera_view(bpy.context.scene, cam, mat_world * v.co)
        nm_ndc = cam_direction.angle(v.normal)
        # v1 = v.co - cam_pos
        # nm_ndc = v1.angle(v.normal)
        if (co_ndc.x < 0.03 or co_ndc.x > 0.97 or co_ndc.y < 0.03 or co_ndc.y > 0.97):
            bm.free()
            print('out of view')
            return False
        # normal may be in two directions
        if nm_ndc < math.radians(120):
            ct1 += 1
        if nm_ndc > math.radians(60):
            ct2 += 1
    if min(ct1, ct2) / 10000. > 0.03:
        bm.free()
        print('ct1: {}, ct2: {}\n'.format(ct1, ct2))
        return False
    bm.free()
    return True

def select_object(ob):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = None
    ob.select=True
    bpy.context.scene.objects.active = ob


def prepare_scene():
    # bpy.ops.wm.read_factory_settings()
    reset_blend()

    scene=bpy.data.scenes['Scene']
    scene.render.engine='CYCLES'
    scene.cycles.samples=128
    scene.cycles.use_square_samples=False    
    scene.display_settings.display_device='sRGB'
    if random.random() > 0.5:
        bpy.data.scenes['Scene'].view_settings.view_transform='Filmic'
    else:
        bpy.data.scenes['Scene'].view_settings.view_transform='Default'


def prepare_rendersettings():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.scenes['Scene'].cycles.device='CPU'
    bpy.data.scenes['Scene'].render.resolution_x=448
    bpy.data.scenes['Scene'].render.resolution_y=448
    bpy.data.scenes['Scene'].render.resolution_percentage=100

def position_object(mesh_name):
    mesh=bpy.data.objects[mesh_name]
    # mesh.select=True
    select_object(mesh)
    # bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
    mesh.rotation_euler=[0.0,0.0,0.0]
    # mesh.scale=(45,45,45)

    # mdim = mesh.dimensions
    # s = 10. / max(mdim.x, mdim.y)
    # mesh.scale=(s,s,s)
    return mesh

def add_lighting():
    world=bpy.data.worlds['World']
    world.use_nodes = True
    wnodes=world.node_tree.nodes
    wlinks=world.node_tree.links
    bg_node=wnodes['Background']
    # hdr lighting
    # remove old node
    for node in wnodes:
        if node.type in ['OUTPUT_WORLD', 'BACKGROUND']:
            continue
        else:
            wnodes.remove(node)
    # hdr world lighting
    if random.random() > 0.3:
        texcoord = wnodes.new(type='ShaderNodeTexCoord')
        mapping = wnodes.new(type='ShaderNodeMapping')
        mapping.rotation[2] = random.uniform(0, 6.28)
        wlinks.new(texcoord.outputs[0], mapping.inputs[0])
        envnode=wnodes.new(type='ShaderNodeTexEnvironment')
        wlinks.new(mapping.outputs[0], envnode.inputs[0])
        # envnode.image=bpy.data.images.load('D:/9C4A0034-a460e29cd9.exr')
        idx = random.randint(0, len(envlist) - 1)
        envp = envlist[idx]
        # envp = ['D:/9C4A0003-e05009bcad.exr', 100]
        # envp = ['D:/0001.hdr', 1]
        envnode.image = bpy.data.images.load(envp[0])
        envstr = int(envp[1])
        bg_node.inputs[1].default_value=random.uniform(0.4 * envstr, 0.6 * envstr)
        wlinks.new(envnode.outputs[0], bg_node.inputs[0])
    else:
        # point light
        bg_node.inputs[1].default_value=0

        d = random.uniform(3, 5)
        litpos = Vector((0, d, 0))
        eul = Euler((0, 0, 0), 'XYZ')
        eul.rotate_axis('Z', random.uniform(0, 3.1415))
        eul.rotate_axis('X', random.uniform(math.radians(45), math.radians(135)))
        litpos.rotate(eul)

        bpy.ops.object.add(type='LAMP', location=litpos)
        lamp = bpy.data.lamps[0]
        lamp.use_nodes = True
        nodes=lamp.node_tree.nodes
        links=lamp.node_tree.links
        for node in nodes:
            if node.type=='OUTPUT':
                output_node=node
            elif node.type=='EMISSION':
                lamp_node=node
        strngth=random.uniform(200,500)
        lamp_node.inputs[1].default_value=strngth
        #Change warmness of light to simulate more natural lighting
        bbody=nodes.new(type='ShaderNodeBlackbody')
        color_temp=random.uniform(2700,10200)
        bbody.inputs[0].default_value=color_temp
        links.new(bbody.outputs[0],lamp_node.inputs[0])

    # bpy.ops.object.lamp_add(type='AREA')
    # lamp=bpy.data.objects[bpy.data.lamps[0].name]
    # select_object(lamp)
    # lamp.location=(0,0,10)
    # xt=random.uniform(-7.0,7.0)
    # yt=random.uniform(-7.0,7.0)
    # zt=random.uniform(-2.0,2.0)
    # bpy.ops.transform.translate( value=(xt,yt,zt))
    # bpy.ops.object.constraint_add(type='DAMPED_TRACK')
    # # bpy.data.objects[0].constraints['Damped Track'].target=bpy.data.objects['Empty']
    # lamp.constraints['Damped Track'].track_axis='TRACK_NEGATIVE_Z'
    # lamp=bpy.data.lamps[bpy.data.lamps[0].name]
    # lamp.shape='RECTANGLE'
    # size_x=random.uniform(10,12)
    # size_y=random.uniform(1,3)
    # lamp.size=size_x
    # lamp.size_y=size_y
    # lamp.use_nodes=True
    # nodes=lamp.node_tree.nodes
    # links=lamp.node_tree.links
    # for node in nodes:
    #     if node.type=='OUTPUT':
    #         output_node=node
    #     elif node.type=='EMISSION':
    #         lamp_node=node
    # strngth=random.uniform(500,600)
    # lamp_node.inputs[1].default_value=strngth
    
    # #Change warmness of light to simulate more natural lighting
    # bbody=nodes.new(type='ShaderNodeBlackbody')
    # color_temp=random.uniform(4000,9500)
    # bbody.inputs[0].default_value=color_temp
    # links.new(bbody.outputs[0],lamp_node.inputs[0])

    # world=bpy.data.worlds['World']
    # world.use_nodes = True
    # wnodes=world.node_tree.nodes
    # wlinks=world.node_tree.links

    # #add random environment lighting
    # # env=random.uniform(0,1)
    # env = 0.9
    # if  env>=0.4 and env<0.6:
    #     bg_node=wnodes['Background']
    #     h=random.uniform(0,1)
    #     s=random.uniform(0,0.2)
    #     v=random.uniform(0.1,0.4)
    #     for node in wnodes:
    #         if node.type=='COMBHSV':
    #             wnodes.remove(node)
    #     hsvnode=wnodes.new(type='ShaderNodeCombineHSV')
    #     hsvnode.inputs[0].default_value=h
    #     hsvnode.inputs[1].default_value=s
    #     hsvnode.inputs[2].default_value=v
    #     bg_node.inputs[1].default_value=random.uniform(0.2,0.7)
    #     wlinks.new(hsvnode.outputs[0], bg_node.inputs[0])
    # else:
    #     print('no env')
    #     for node in wnodes:
    #         if node.type=='OUTPUT_WORLD':
    #             continue
    #         elif node.type=='BACKGROUND':
    #             continue
    #         else:
    #             wnodes.remove(node)
    #     bg_node=wnodes['Background']
    #     # bg_node.inputs[1].default_value=random.uniform(0.2,0.4)
    #     if env>=0.6:
    #         # hdr lighting
    #         envnode=wnodes.new(type='ShaderNodeTexEnvironment')
    #         # envnode.image=bpy.data.images.load('D:/9C4A0034-a460e29cd9.exr')
    #         # idx = random.randint(0, len(envlist) - 1)
    #         # envp = envlist[idx]
    #         envp = ['D:/9C4A0034-a460e29cd9.exr', 50]
    #         # envp = ['D:/0001.hdr', 1]
    #         envnode.image = bpy.data.images.load(envp[0])
    #         bg_node.inputs[1].default_value=random.uniform(0.7 * envp[1], 1.3 * envp[1])
    #         wlinks.new(envnode.outputs[0], bg_node.inputs[0])

def reset_camera_varY(mesh):
    bpy.ops.object.select_all(action='DESELECT')
    camera=bpy.data.objects['Camera']
    camera.select=True
    # sample camera config until find a valid one
    id = 0
    vid = False
    # focal length
    bpy.data.cameras['Camera'].lens = random.randint(25, 35)
    # cam position
    d = random.uniform(2.3, 3.0)
    campos = Vector((0, 0, d))
    eul = Euler((0, 0, -1.570), 'XYZ')

    camera.rotation_euler=eul
    camera.location=campos

    camera.constraints.new(type='DAMPED_TRACK')
    camera.constraints['Damped Track'].target=mesh
    camera.constraints['Damped Track'].track_axis='TRACK_NEGATIVE_Z'
    # xt=random.uniform(-5.0,3.0)
    yt=random.uniform(-1.3,1.3)
    if yt <= 0.6 and yt >= -0.6 :
        if yt < 0:
            yt-=0.6
        else:
            yt+=0.6
    bpy.ops.transform.translate(value=(0,yt,0))

    while id < 50:
        if isVisible(mesh, camera):
            vid = True
            break

        else:
            d+=0.1
            campos = Vector((0, 0, d))
            camera.location=campos
            bpy.context.scene.update()

        id += 1
    print(d)
    return vid


def reset_camera(mesh):
    bpy.ops.object.select_all(action='DESELECT')
    camera=bpy.data.objects['Camera']

    # sample camera config until find a valid one
    id = 0
    vid = False
    # focal length
    bpy.data.cameras['Camera'].lens = random.randint(25, 35)
    # cam position
    d = random.uniform(2.3, 3.3)
    campos = Vector((0, d, 0))
    eul = Euler((0, 0, 0), 'XYZ')
    eul.rotate_axis('Z', random.uniform(0, 3.1415))
    eul.rotate_axis('X', random.uniform(math.radians(60), math.radians(120)))
    
    campos.rotate(eul)
    camera.location=campos

    while id < 50:
        # look at pos
        st = (d - 2.3) / 1.0 * 0.2 + 0.3
        lookat = Vector((random.uniform(-st, st), random.uniform(-st, st), 0))
        eul = Euler((0, 0, 0), 'XYZ')
        
        eul.rotate_axis('X', math.atan2(lookat.y - campos.y, campos.z))
        eul.rotate_axis('Y', math.atan2(campos.x - lookat.x, campos.z))
        st = (d - 2.3) / 1.0 * 15 + 5.
        eul.rotate_axis('Z', random.uniform(math.radians(-90 - st), math.radians(-90 + st)))
        
        camera.rotation_euler = eul
        bpy.context.scene.update()

        if isVisible(mesh, camera):
            vid = True
            break

        id += 1
    return vid

def page_texturing(mesh, texpath):
    select_object(mesh)
    bpy.ops.object.mode_set(mode="OBJECT")
    #for material in bpy.data.materials:
    #    bpy.data.materials.remove(material, do_unlink=True)
    bpy.ops.object.material_slot_add()
    bpy.data.materials.new('Material.001')
    mesh.material_slots[0].material=bpy.data.materials['Material.001']
    mat = bpy.data.materials['Material.001']
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    # clear default nodes
    for n in nodes:
        nodes.remove(n)
    out_node=nodes.new(type='ShaderNodeOutputMaterial')
    bsdf_node=nodes.new(type='ShaderNodeBsdfDiffuse')
    texture_node=nodes.new(type='ShaderNodeTexImage')
    
    texture_node.image=bpy.data.images.load(texpath)

    links=mat.node_tree.links
    links.new(bsdf_node.outputs[0],out_node.inputs[0])
    links.new(texture_node.outputs[0],bsdf_node.inputs[0])

    bsdf_node.inputs[0].show_expanded=True
    texture_node.extension='EXTEND'
    texturecoord_node=nodes.new(type='ShaderNodeTexCoord')
    links.new(texture_node.inputs[0],texturecoord_node.outputs[2])

# def get_image(objpath, texpath):
#     bpy.context.scene.use_nodes = True
#     tree = bpy.context.scene.node_tree
#     links = tree.links

#     # clear default nodes
#     for n in tree.nodes:
#         tree.nodes.remove(n)

#     # create input render layer node
#     render_layers = tree.nodes.new('CompositorNodeRLayers')
#     file_output_node_0 = tree.nodes.new("CompositorNodeOutputFile")
#     file_output_node_0.base_path = path_to_output_images

#     # change output image name to obj file name + texture name + random three
#     # characters (upper lower alphabet and digits)
#     id_name = objpath.split('/')[-1][:-4] + '-' + texpath.split('/')[-1][:-4] + '-' + \
#         ''.join(random.sample(string.ascii_letters + string.digits, 3))

#     file_output_node_0.file_slots[0].path = id_name

#     links.new(render_layers.outputs[0], file_output_node_0.inputs[0])
#     return id_name

def color_wc_material(obj,mat_name):
    # Remove lamp
    for lamp in bpy.data.lamps:
        bpy.data.lamps.remove(lamp, do_unlink=True)

    select_object(obj)
    # Add a new material
    # bpy.ops.object.material_slot_remove()
    # bpy.ops.object.material_slot_add()
    bpy.data.materials.new(mat_name)
    obj.material_slots[0].material=bpy.data.materials[mat_name]
    mat=bpy.data.materials[mat_name]
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # clear default nodes
    for n in nodes:
        nodes.remove(n)

    # Add an material output node
    mat_node=nodes.new(type='ShaderNodeOutputMaterial')
    # Add an emission node
    em_node=nodes.new(type='ShaderNodeEmission')
    # Add a geometry node
    geo_node=nodes.new(type='ShaderNodeNewGeometry')
    
    # Connect each other
    tree=mat.node_tree
    links=tree.links
    links.new(geo_node.outputs[0],em_node.inputs[0])
    links.new(em_node.outputs[0],mat_node.inputs[0])


def get_worldcoord_img(img_name):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    render_layers = tree.nodes.new('CompositorNodeRLayers')

    file_output_node_0 = tree.nodes.new("CompositorNodeOutputFile")
    file_output_node_0.format.file_format = 'OPEN_EXR'
    file_output_node_0.base_path = path_to_output_wc
    file_output_node_0.file_slots[0].path = img_name

    links.new(render_layers.outputs[0], file_output_node_0.inputs[0])

def prepare_no_env_render():
    # Remove lamp
    for lamp in bpy.data.lamps:
        bpy.data.lamps.remove(lamp, do_unlink=True)

    world=bpy.data.worlds['World']
    world.use_nodes = True
    links = world.node_tree.links
    # clear default nodes
    for l in links:
        links.remove(l)


def render_pass(obj,objpath, texpath):
    # change output image name to obj file name + texture name + random three
#     # characters (upper lower alphabet and digits)
    fn = objpath.split('/')[-1][:-4] + '-' + texpath.split('/')[-1][:-4] + '-' + \
        ''.join(random.sample(string.ascii_letters + string.digits, 3))

    scene=bpy.data.scenes['Scene']
    scene.render.layers['RenderLayer'].use_pass_uv=True
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    render_layers = tree.nodes.new('CompositorNodeRLayers')

    file_output_node_img = tree.nodes.new('CompositorNodeOutputFile')
    file_output_node_img.format.file_format = 'PNG'
    file_output_node_img.base_path = path_to_output_images
    file_output_node_img.file_slots[0].path = fn
    imglk = links.new(render_layers.outputs[0], file_output_node_img.inputs[0])
    scene.cycles.samples=128
    bpy.ops.render.render(write_still=False)

    # remove img link
    links.remove(imglk)
    file_output_node_uv = tree.nodes.new('CompositorNodeOutputFile')
    file_output_node_uv.format.file_format = 'OPEN_EXR'
    file_output_node_uv.base_path = path_to_output_uv
    file_output_node_uv.file_slots[0].path = fn
    uvlk = links.new(render_layers.outputs[4], file_output_node_uv.inputs[0])
    scene.cycles.samples = 1
    bpy.ops.render.render(write_still=False)

    # save_blend_file
    bpy.ops.wm.save_mainfile(filepath=path_to_output_blends+fn+'.blend')

    # render world coordinates
    prepare_no_env_render()
    color_wc_material(obj,'wcColor')
    get_worldcoord_img(fn)
    bpy.ops.render.render(write_still=False)

    return fn

def render_img(objpath, texpath):
    prepare_scene()
    prepare_rendersettings()

    bpy.ops.import_scene.obj(filepath=objpath)
    mesh_name=bpy.data.meshes[0].name
    mesh=position_object(mesh_name)

    add_lighting()
    v = reset_camera_varY(mesh)
    if not v:
        return 1
    else:
        #add texture
        page_texturing(mesh, texpath)
        # plane_texturing(plane)
        fn = render_pass(mesh,objpath, texpath)
        # render()

        # return 0

    # idx+=1

# def check_mesh(obj_name):
#     prepare_scene()
#     prepare_rendersettings()
#     bpy.ops.import_scene.obj(filepath=obj_name)
#     # bpy.ops.import_scene.obj(filepath=obj_name)
#     mesh_name=bpy.data.meshes[0].name
#     mesh=position_object(mesh_name, flip=False)

#     v = reset_camera(mesh)
#     if not v:
#         return 0
#     else:
#         return 1

import sys
import csv
# dst_dir = '/nfs/bigmind/kema/exp/dun/vm/'
# oid = sys.argv[-1]

# with open(os.path.join(dst_dir, '{}.csv'.format(oid)), 'w') as csvfile:
#     writer = csv.writer(csvfile, delimiter=',')
#     for k in range(1, 209):
#         print(k)
#         objfn = '{}_{}.obj'.format(oid, k)
#         f = check_mesh(objfn)
#         writer.writerow([objfn, f])

        

# idx=1
# if __name__ == '__main__':
#     for ii in range(1, 101):
#         for jj in range(1, 209):
#             obj_name=str(x)+'_'+str(y)+'.obj'
#             f = check_meshes(obj_name)
#             if f:


env_list = '/home/kema/code/dun/env.csv'
envlist = []
with open(env_list, 'r') as f:
    envlist = list(csv.reader(f))

tex_list = '/home/kema/code/dun/page_tex.csv'
obj_list = '/home/kema/code/dun/ma.csv'

id1 = int(sys.argv[-2])
id2 = int(sys.argv[-1])

with open(tex_list, 'r') as t, open(obj_list, 'r') as m:
    texlist = list(csv.reader(t))
    objlist = list(csv.reader(m))
    print(objlist)
    for k in range(id1, id2):
        print(k)
        objpath = objlist[k][0]
        idx = random.randint(0, len(texlist))
        texpath=texlist[idx][0]
        print(objpath)
        print(texpath)

        render_img(objpath, texpath)


# render_img('I:/kema/data/docwarp/sobj/C/1/1_1_1.obj', 'D:/scan/vibrance/25.png')



# # import sys
# # import multiprocessing
# # pool = multiprocessing.Pool(processes=24)
# import csv
# def render_batch(objlist, sid):
#     with open('/home/kema/code/dun/page_tex.csv') as csv_file:
#         csv_reader = csv.reader(csv_file)
#         texlist = list(csv_reader)
#     id = sid
