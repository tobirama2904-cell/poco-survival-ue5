#!/usr/bin/env python3
"""Acquire first-party CC0 props and pin every byte; no engine content."""
import requests,json,hashlib,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'.cache/interior-sources'
ASSETS=['medical_box','medical_tape','wheelchair_01','old_bed_frame','wooden_bookshelf_worn','metal_office_desk','SchoolChair_01','SchoolDesk_01','portable_cassette_player']
def fetch(name):
 r=requests.get('https://api.polyhaven.com/files/'+name,timeout=60);r.raise_for_status();entry=r.json()['gltf']['1k']['gltf'];files=[]
 for relative,item in {name+'.gltf':entry,**entry['include']}.items():
  p=OUT/name/relative;assert p.resolve().is_relative_to((OUT/name).resolve());p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():
   r=requests.get(item['url'],timeout=120);r.raise_for_status();p.write_bytes(r.content)
  data=p.read_bytes();assert len(data)==item['size'] and hashlib.md5(data).hexdigest()==item['md5'].zfill(32)
  files.append({'file':relative,'url':item['url'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 print('INTERIOR_SOURCE_VERIFIED',name,flush=True)
 return {'id':name,'license':'CC0-1.0','source':'https://polyhaven.com/a/'+name,'license_url':'https://polyhaven.com/license','files':files}
def main():
 lock=ROOT/'BuildData/interior-sources.lock.json'
 if lock.exists():
  for asset in json.loads(lock.read_text())['assets']:
   base=OUT/asset['id']
   for item in asset['files']:
    p=base/item['file'];assert p.resolve().is_relative_to(base.resolve());p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():
     r=requests.get(item['url'],timeout=120);r.raise_for_status();p.write_bytes(r.content)
    data=p.read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
   print('PINNED_INTERIOR_SOURCE_VERIFIED',asset['id'],flush=True)
  return
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,ASSETS))
 lock.write_text(json.dumps({'schema':1,'assets':records},indent=2)+'\n')
if __name__=='__main__':main()
