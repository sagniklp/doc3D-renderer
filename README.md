
# doc3D-renderer
Doc3D is the first 3D dataset focused on document unwarping with realistic paper warping and renderings.
<p align="center">
  <img src="data.gif">
</p>
This repository contains all the rendering codes of doc3D. 
The download scripts of the dataset is available in [doc3D-dataset](https://github.com/cvlab-stonybrook/doc3D-dataset) repo. 

### Instructions to render your own data:
- Step 1: We need a few assets to start the rendering.
	- a) Meshes
	- b) HDR environment maps for lighting
	- c) Textures
For your convenience, we already provide some sample meshes (`/obj`), HDR maps (`/env`) and textures (`/tex`). Each line is a path to a mesh, HDR map  and a texture.

- Step 2: List the assets in `objs.csv`,`envs.csv`, and `texs.csv`.
- Step 3a : Run the rendering code (for images, UVs, 3D coordinates):
	- `blender --background --python render_mesh.py -- <folder-id> <start-mesh> <end-mesh>`
	This command renders the images (`/img`), 3D coordinates (`/wc`) and UV (`/uv`) in folder `<folder-id>`. `<start-mesh>` and `<end-mesh>` refers to line numbers in `objs.csv` specifying the meshes to be used while rendering.
	Additionally,  `render_mesh.py` also saves the Blender model (`.blend`) files for further rendering process (`albedo`, `norm` etc.). Toggle it using the `save_blend_file=False` flag in the code.
	- For faster rendering you can use the multiprocessing code `batch_render.py`. Run `python batch_render.py <folder-id> <start-mesh> <end-mesh>`. Remember to modify the processor counts using `nproc`.
- Step 3b : Run the rendering code (for checkerboards, albedos, depth etc.):
	- Run `blendnames.py` to list the available `.blend` files, `python blendnames.py <folder-id>`. Remember to do this step!
	- Albedos (`/alb`): `blender --background --python render_alb.py -- <folder-id> <start-mesh> <end-mesh>`
	- Normals (`/norm`): `blender --background --python render_norm.py -- <folder-id> <start-mesh> <end-mesh>`
	- Depths (`/dmap`): `blender --background --python render_dmap.py -- <folder-id> <start-mesh> <end-mesh>`
	- Checkerboard (`/norm`): `blender --background --python render_recon.py -- <folder-id> <start-mesh> <end-mesh>`
- Step 4: If you want to create the backward mappings from UV:
	- `/uv2backwardmap` contains the necessary scripts. We use MatLab to do this.
	- `python exr2mat.py <folder-id>`, converts the `.exr` files to `.mat` files.
	- Edit the `src_dir` and `dst_dir` accordingly and run `fm2bm.m`. 

### Citation:
If you use the dataset or this code, please consider citing our work-
```
@inproceedings{SagnikKeICCV2019, 
Author = {Sagnik Das*, Ke Ma*, Zhixin Shu, Dimitris Samaras, Roy Shilkrot}, 
Booktitle = {Proceedings of International Conference on Computer Vision}, 
Title = {DewarpNet: Single-Image Document Unwarping With Stacked 3D and 2D Regression Networks}, 
Year = {2019}}   
```
#### Acknowlegement: 
Thanks to the awesome software, [Blender](https://www.blender.org/), thanks to it's developers and also to the super awesome [community](https://blender.stackexchange.com/).

