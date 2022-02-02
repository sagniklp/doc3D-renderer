'''
Code for rendering the groundtruths of Doc3D dataset 
https://www3.cs.stonybrook.edu/~cvl/projects/dewarpnet/storage/paper.pdf (ICCV 2019)

This code renders the albedo maps using the .blend files 
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
from pathlib import Path

def select_object(ob):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def prepare_rendersettings():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.scenes['Scene'].cycles.device='CPU'
    bpy.data.scenes['Scene'].render.resolution_x=448
    bpy.data.scenes['Scene'].render.resolution_y=448
    bpy.data.scenes['Scene'].render.resolution_percentage=100


def render():
    bpy.context.scene.camera = bpy.data.objects['Camera']
    bpy.data.scenes['Scene'].render.image_settings.color_depth='8'
    bpy.data.scenes['Scene'].render.image_settings.color_mode='RGB'
    # bpy.data.scenes['Scene'].render.image_settings.file_format='OPEN_EXR'
    bpy.data.scenes['Scene'].render.image_settings.compression=0
    bpy.ops.render.render(write_still=False)


def get_albedo_img(img_name):
    bpy.context.view_layer.use_pass_diffuse_color=True
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    render_layers = tree.nodes.new('CompositorNodeRLayers')

    file_output_node = tree.nodes.new('CompositorNodeOutputFile')
    comp_node = tree.nodes.new('CompositorNodeComposite')

    # file_output_node_0.format.file_format = 'OPEN_EXR'
    out_path=path_to_output_alb
    if not os.path.exists(out_path):
        os.makedirs(out_path)
	
    file_output_node.base_path = out_path
    file_output_node.file_slots[0].path = img_name
    links.new(render_layers.outputs['DiffCol'], file_output_node.inputs[0])
    links.new(render_layers.outputs['DiffCol'], comp_node.inputs[0])

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
    scene.view_settings.view_transform='Standard'


rridx=sys.argv[-3]
strt=int(sys.argv[-2])
end=int(sys.argv[-1])
path_to_output_alb = os.path.abspath('./alb/'+ str(rridx) + '/')
blend_list = './blendlists/blendlist'+ str(rridx) +'.csv'

if not os.path.exists(path_to_output_alb):
    os.makedirs(path_to_output_alb)

with open(blend_list,'r') as b:
    blendlist = list(csv.reader(b))

for bfile in blendlist[strt:end]:
    bfname=bfile[0]
    fn=Path(bfname).stem
    #load blend file 
    bpy.ops.wm.open_mainfile(filepath=bfname)
    prepare_rendersettings()
    prepare_no_env_render()
    get_albedo_img(fn)
    render()
