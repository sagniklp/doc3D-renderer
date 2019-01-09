import cv2
import numpy as np
from hdf5storage import savemat

def saveasmat(file_path, dst_path):
    img = cv2.imread(file_path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_UNCHANGED)
    savemat(dst_path, {'uv': img})
    
import os
import multiprocessing
pool = multiprocessing.Pool(processes=2)

src_dir = '/media/hilab/sagniksSSD/Sagnik/DewarpNet/swat3d/uv/1/'
dst_dir = '/media/hilab/sagniksSSD/Sagnik/DewarpNet/swat3d/uvmat/1/'

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