from subprocess import Popen
import os
import sys


# number of meshes
id1 = int(sys.argv[-2])
id2 = int(sys.argv[-1])

# number of processors
nnum_proc = 24

# split the task
import numpy as np
tlist = np.linspace(id1, id2, nnum_proc + 1)
for k in range(nnum_proc):
    cmd = ['blender', '--background', '--python', 'render_mesh_fixcam.py', '--', 
    '{}'.format(int(round(tlist[k]))), '{}'.format(int(round(tlist[k + 1])))]
    pp = Popen(cmd)
