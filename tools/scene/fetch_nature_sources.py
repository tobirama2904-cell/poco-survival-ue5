#!/usr/bin/env python3
"""Fetch licensed CC0 nature inputs with the publisher's digest, then pin SHA256.
Source art is cached, never padded or confused with final packaged game content.
"""
import concurrent.futures,hashlib,json
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'.cache/nature-sources'
ASSETS=['pine_sapling_small','island_tree_02','fern_02','rock_moss_set_01','tree_stump_01','dead_tree_trunk']
def fetch(asset):
 d=requests.get('https://api.polyhaven.com/files/'+asset,timeout=60);d.raise_for_status();entry=d.json()['gltf']['1k']['gltf'];base=OUT/asset;base.mkdir(parents=True,exist_ok=True)
 entries={asset+'.gltf':entry,**entry['include']};records=[]
 for name,item in entries.items():
  path=base/name;assert path.resolve().is_relative_to(base.resolve());path.parent.mkdir(parents=True,exist_ok=True)
  if not path.exists():
   r=requests.get(item['url'],timeout=180);r.raise_for_status();path.write_bytes(r.content)
  data=path.read_bytes();assert len(data)==item['size'];assert hashlib.md5(data).hexdigest()==item['md5'].zfill(32)
  records.append({'file':name,'url':item['url'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 print('VERIFIED_NATURE_SOURCE',asset,sum(r['bytes'] for r in records),flush=True)
 return {'id':asset,'license':'CC0-1.0','license_url':'https://polyhaven.com/license','source':'https://polyhaven.com/a/'+asset,'files':records}
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,ASSETS))
 (OUT/'sources.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
