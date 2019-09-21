'''
Code for rendering the groundtruths of Doc3D dataset 
https://www3.cs.stonybrook.edu/~cvl/projects/dewarpnet/storage/paper.pdf (ICCV 2019)

This code converts the .exr files to .mat, 
run it before running the fm2bm.m 

Written by: Sagnik Das
Stony Brook University, New York
January 2019
'''

import cv2
import numpy as np
from hdf5storage import savemat

rridx=sys.argv[-1]

def saveasmat(file_path, dst_path):
    img = cv2.imread(file_path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_UNCHANGED)
    savemat(dst_path, {'uv': img})
    
import os
import multiprocessing
pool = multiprocessing.Pool(processes=2)

src_dir = '../uv/{}/'.format(rridx)
dst_dir = '../uvmat/{}/'.format(rridx)

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

for fname in os.listdir(src_dir):
    if '.exr' in fname:
        file_name = os.path.join(src_dir, fname)
        if not os.path.isfile(file_name):
            continue 
        # t = os.path.join(dst_dir, str(fid))
        t=dst_dir
        if not os.path.exists(t):
            os.makedirs(t)
        dst_name = os.path.join(t, fname[:-4])
        pool.apply_async(saveasmat, (file_name, dst_name))

pool.close()
pool.join()