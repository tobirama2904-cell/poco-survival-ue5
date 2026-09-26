#!/usr/bin/env python3
"""Verified photo inputs and deterministic cutout derived from their real needle atlas."""
from pathlib import Path
import json,hashlib,requests
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[2]
def main():
 lock=json.loads((ROOT/'BuildData/woodland-inputs.lock.json').read_text())
 for group in lock['inputs']:
  out=ROOT/'.cache'/group['directory'];out.mkdir(parents=True,exist_ok=True)
  for f in group['provenance']['files']:
   p=out/f['name']
   if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:
    r=requests.get(f['url'],timeout=120);r.raise_for_status();assert len(r.content)==f['bytes'] and hashlib.sha256(r.content).hexdigest()==f['sha256'];p.write_bytes(r.content)
  (out/'license-lock.json').write_text(json.dumps(group['provenance'],indent=2))
 src=ROOT/'.cache/conifer-sources';crop=Image.open(src/'pine_tree_01_twig_diff_1k.jpg').convert('RGB').crop((6,35,211,447));rgb=np.array(crop);mask=Image.new('L',crop.size,0)
 ImageDraw.Draw(mask).polygon([(15,10),(161,0),(204,130),(198,235),(163,350),(148,410),(101,410),(95,335),(7,233),(0,76)],fill=255)
 alpha=np.clip((rgb.max(2).astype(float)-14)*255/20,0,255).astype('uint8');alpha=np.minimum(alpha,np.array(mask));fg=alpha>40
 _,indices=distance_transform_edt(~fg,return_indices=True);filled=rgb[tuple(indices)];filled[fg]=rgb[fg]
 Image.fromarray(np.dstack((filled,alpha))).save(src/'pine_needles_rgba.png')
 print('WOODLAND_TEXTURE_INPUTS_VERIFIED',flush=True)
if __name__=='__main__':main()
