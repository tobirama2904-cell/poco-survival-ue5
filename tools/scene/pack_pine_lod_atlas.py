#!/usr/bin/env python3
"""Assemble original/baked CC0-derived cutouts with transparent-border RGB dilation."""
import json,struct,io
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[2];folder=ROOT/'.cache/pine-lod'
raw=(ROOT/'.cache/county-pack/Pine.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);blob=raw[28+n:]
image=next(i for i in d['images'] if 'pine_needles' in i.get('name',''));v=d['bufferViews'][image['bufferView']];needle=Image.open(io.BytesIO(blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])).convert('RGBA')
def crop(image):
 a=np.array(image.getchannel('A'));yy,xx=np.where(a>20);box=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1));return image.crop(box),box
full=Image.open(folder/'tree.png').convert('RGBA');tree,box=crop(full)
bough,_=crop(Image.open(folder/'bough.png').convert('RGBA').crop((0,0,1024,450)))
dense=Image.new('RGBA',(1024,640),(0,0,0,0));branch=bough.resize((980,280),Image.Resampling.LANCZOS)
for y,pic in [(20,branch),(180,ImageOps.flip(branch)),(340,branch)]:dense.alpha_composite(pic,(0,y))
bough,_=crop(dense)
atlas=Image.new('RGBA',(2048,2048),(0,0,0,0));atlas.paste(needle.resize((508,1020),Image.Resampling.LANCZOS),(2,2));atlas.paste(bough.resize((1020,1020),Image.Resampling.LANCZOS),(2,1026));atlas.paste(tree.resize((1020,2044),Image.Resampling.LANCZOS),(1026,2))
a=np.array(atlas);mask=a[:,:,3]>30;_,idx=distance_transform_edt(~mask,return_indices=True);rgb=a[:,:,:3];filled=rgb[tuple(idx)];filled[mask]=rgb[mask];a[:,:,:3]=filled;Image.fromarray(a).save(folder/'pine_lod_atlas.png')
meta=json.loads((folder/'bake.json').read_text());unit=meta['tree_ortho_scale']/meta['tree_pixels'];metadata={'tree_width':(box[2]-box[0])*unit,'tree_height':(box[3]-box[1])*unit,'tree_center_x':((box[0]+box[2])/2-512)*unit,'tree_bottom_z':meta['tree_camera_center_z']+(512-box[3])*unit,'needle_uv':[2/2048,1026/2048,510/2048,2046/2048],'bough_uv':[2/2048,2/2048,1022/2048,1022/2048],'tree_uv':[1026/2048,2/2048,2046/2048,2046/2048]};(folder/'atlas.json').write_text(json.dumps(metadata,indent=2));print('PINE_LOD_ATLAS_READY',metadata)
