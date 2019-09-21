'''
Code for rendering the groundtruths of Doc3D dataset 
https://www3.cs.stonybrook.edu/~cvl/projects/dewarpnet/storage/paper.pdf (ICCV 2019)

This code renders the normals using the .blend files 
saved from render_mesh.py 

Written by: Sagnik Das
Stony Brook University, New York
January 2019
'''


import sys
import csv
import os
import bpy
import bmesh
import random
import math
from mathutils import Vector, Euler
import string


def select_object(ob):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = None
    ob.select=True
    bpy.context.scene.objects.active = ob


def render():
    bpy.context.scene.camera = bpy.data.objects['Camera']
    bpy.data.scenes['Scene'].render.image_settings.color_depth='8'
    bpy.data.scenes['Scene'].render.image_settings.color_mode='RGB'
    bpy.data.scenes['Scene'].render.image_settings.compression=0
    bpy.ops.render.render(write_still=False)


def color_norm_material(obj,mat_name):
    # Remove lamp
    for lamp in bpy.data.lamps:
        bpy.data.lamps.remove(lamp, do_unlink=True)

    select_object(obj)
    # Add a new material
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
    links.new(geo_node.outputs[3],em_node.inputs[0])
    links.new(em_node.outputs[0],mat_node.inputs[0])


def get_normal_img(img_name):
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
    file_output_node_0.base_path = path_to_output_norms
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
    scene=bpy.data.scenes['Scene']
    scene.cycles.samples=1
    scene.cycles.use_square_samples=True
    scene.view_settings.view_transform='Default'


# read args
strt=int(sys.argv[-2])
end=int(sys.argv[-1])
rridx=sys.argv[-3]

blend_list = './blendlists/blendlist{}.csv'.format(rridx)
path_to_output_norms= './norm/{}/'.format(rridx)

if not os.path.exists(path_to_output_norms):
    os.makedirs(path_to_output_norms)

with open(blend_list,'r') as b:
    blendlist = list(csv.reader(b))


for bfile in blendlist[strt:end]:
    bpy.ops.wm.read_factory_settings()
    bfname=bfile[0]
    #load blend file 
    bpy.ops.wm.open_mainfile(filepath=bfname)
    fn=bfname.split('/')[-1][:-6]
    mesh=bpy.data.objects[bpy.data.meshes[0].name]

    # render world coordinates
    prepare_no_env_render()
    color_norm_material(mesh,'nColor')
    get_normal_img(fn)
    render()
 
