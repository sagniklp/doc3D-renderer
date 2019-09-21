'''
Code for rendering the groundtruths of Doc3D dataset 
https://www3.cs.stonybrook.edu/~cvl/projects/dewarpnet/storage/paper.pdf (ICCV 2019)

This code runs the rendering codes in multiple threads

Written by: Ke Ma
Stony Brook University, New York
January 2019
'''
from subprocess import Popen
import os
import sys
import numpy as np

# number of meshes
id1 = int(sys.argv[-2])
id2 = int(sys.argv[-1])

# folder id
folder = sys.argv[-3]

# number of processors
nnum_proc = 1

# split the task
tlist = np.linspace(id1, id2, nnum_proc + 1)
for k in range(nnum_proc):
    cmd = ["blender", "--background", "--python", "render_mesh.py", "--", folder,
    '{}'.format(int(round(tlist[k]))), '{}'.format(int(round(tlist[k + 1])))]
    
    #### In MacOS ####
    #cmd = ["blender", "--background", "--python", "/full/path/to/render_mesh.py", "--", folder,
    #'{}'.format(int(round(tlist[k]))), '{}'.format(int(round(tlist[k + 1])))]
    pp = Popen(cmd)
