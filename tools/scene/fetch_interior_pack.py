#!/usr/bin/env python3
"""Restore the pinned CC0-only prop pack; original source art is separate."""
import hashlib,json,zipfile,shutil
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[2]
def main():
 lock=json.loads((ROOT/'BuildData/interior-pack.lock.json').read_text());out=ROOT/'.cache/interior-pack';out.mkdir(parents=True,exist_ok=True);archive=ROOT/'.cache/interior-art.zip'
 with urlopen(lock['url'],timeout=120) as response,archive.open('wb') as f:shutil.copyfileobj(response,f)
 assert archive.stat().st_size==lock['bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==lock['sha256']
 expected={f['name']:f for f in lock['files']}
 with zipfile.ZipFile(archive) as z:
  assert len(z.infolist())==len(expected) and set(z.namelist())==set(expected);assert sum(i.file_size for i in z.infolist())<50*1024**2
  for item in z.infolist():
   name=Path(item.filename);assert len(name.parts)==1 and not name.is_absolute() and item.file_size==expected[item.filename]['bytes'];data=z.read(item);assert hashlib.sha256(data).hexdigest()==expected[item.filename]['sha256'];(out/name).write_bytes(data)
 print('INTERIOR_PACK_VERIFIED',len(lock['models']),flush=True)
if __name__=='__main__':main()
