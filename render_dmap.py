'''
Code for rendering the groundtruths of Doc3D dataset 
https://www3.cs.stonybrook.edu/~cvl/projects/dewarpnet/storage/paper.pdf (ICCV 2019)

This code renders the depth maps using the .blend files 
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
import string
from pathlib import Path


def select_object(ob):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def render():
    bpy.context.scene.camera = bpy.data.objects['Camera']
    bpy.data.scenes['Scene'].render.image_settings.color_depth='8'
    bpy.data.scenes['Scene'].render.image_settings.color_mode='RGB'
    # bpy.data.scenes['Scene'].render.image_settings.file_format='OPEN_EXR'
    bpy.data.scenes['Scene'].render.image_settings.compression=0
    bpy.ops.render.render(write_still=False)


def prepare_no_env_render():
    # Remove lamp
    for lamp in bpy.data.lights:
        bpy.data.lights.remove(lamp, do_unlink=True)

    world=bpy.data.worlds['World']
    world.use_nodes = True
    links = world.node_tree.links
    # clear default nodes
    for l in links:
        links.remove(l)
    scene=bpy.data.scenes['Scene']
    scene.cycles.samples=1
    scene.cycles.use_square_samples=True
    scene.view_settings.view_transform='Standard'


def get_depth_map(img_name):
    # no normalization or inversion use true z
    bpy.context.scene.camera = bpy.data.objects['Camera']
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    render_layers = tree.nodes.new('CompositorNodeRLayers')
    composite_node = tree.nodes.new("CompositorNodeComposite")
    file_output_node = tree.nodes.new("CompositorNodeOutputFile")
    file_output_node.format.file_format = 'OPEN_EXR'
    file_output_node.base_path = path_to_output_dmap
    file_output_node.file_slots[0].path = img_name

    links.new(render_layers.outputs['Depth'], file_output_node.inputs[0])    



strt=int(sys.argv[-2])
end=int(sys.argv[-1])
rridx=sys.argv[-3]
path_to_output_dmap = os.path.abspath('./dmap/{}/'.format(rridx))
blend_list = './blendlists/blendlist{}.csv'.format(rridx)

if not os.path.exists(path_to_output_dmap):
    os.makedirs(path_to_output_dmap)

with open(blend_list,'r') as b:
    blendlist = list(csv.reader(b))


for bfile in blendlist[strt:end]:
    bpy.ops.wm.read_factory_settings()
    bfname=bfile[0]
    fn=Path(bfname).stem
    bpy.ops.wm.open_mainfile(filepath=bfname)
    get_depth_map(fn)  
    render()