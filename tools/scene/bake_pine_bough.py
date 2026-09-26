#!/usr/bin/env python3
"""Composite real CC0 twig photographs into one branch cutout, reducing layers.
This is an authored texture atlas, not a new photograph or a scanned tree.
"""
from pathlib import Path
import math,json,hashlib
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'.cache/conifer-sources'
def main():
 twig=Image.open(SRC/'pine_needles_rgba.png').convert('RGBA');w,h=twig.size;canvas=Image.new('RGBA',(1024,1024),(0,0,0,0))
 draw=ImageDraw.Draw(canvas);draw.line([(512,996),(512,135)],fill=(71,65,38,255),width=7)
 count=0
 def stamp(cx,cy,angle,length):
  scale=length/h;c=math.cos(math.radians(angle));s=math.sin(math.radians(angle));rx=.58*w;ry=.98*h
  coefficients=(c/scale,s/scale,rx-(c*cx+s*cy)/scale,-s/scale,c/scale,ry+(s*cx-c*cy)/scale)
  layer=twig.transform(canvas.size,Image.Transform.AFFINE,coefficients,Image.Resampling.BICUBIC);canvas.alpha_composite(layer)
 for i in range(6):
  y=905-i*114;length=490-i*34
  for sign in [-1,1]:stamp(512,y,sign*(66-i*4),length);count+=1
 stamp(512,344,0,310);count+=1
 data=np.array(canvas);mask=data[:,:,3]>40;_,indices=distance_transform_edt(~mask,return_indices=True);rgb=data[:,:,:3];filled=rgb[tuple(indices)];filled[mask]=rgb[mask];data[:,:,:3]=filled
 out=SRC/'pine_needles_bough_rgba.png';Image.fromarray(data).save(out)
 (SRC/'bough-bake.json').write_text(json.dumps({'source':'pine_tree_01 twig photograph, CC0','source_cutout_sha256':hashlib.sha256((SRC/'pine_needles_rgba.png').read_bytes()).hexdigest(),'source_sprigs_per_bough':count,'atlas_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'alpha_coverage_fraction':float(mask.mean()),'generated_composite_not_photograph':True},indent=2))
 print('PINE_BOUGH_BAKED',count,float(mask.mean()),flush=True)
if __name__=='__main__':main()
