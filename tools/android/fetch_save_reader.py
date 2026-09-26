#!/usr/bin/env python3
"""Pinned MIT CI-only GVAS reader. Never bundled into the game."""
from pathlib import Path
from urllib.request import urlopen
import json,hashlib,tarfile,io,os
ROOT=Path(__file__).resolve().parents[2]
def main():
 lock=json.loads((ROOT/'BuildData/uesave-tool.lock.json').read_text());out=ROOT/'.cache/save-reader';out.mkdir(parents=True,exist_ok=True)
 with urlopen(lock['url'],timeout=90) as r:data=r.read()
 assert len(data)==lock['bytes'] and hashlib.sha256(data).hexdigest()==lock['sha256']
 found=False
 with tarfile.open(fileobj=io.BytesIO(data),mode='r:xz') as tar:
  for entry in tar:
   if not entry.isfile():continue
   name=Path(entry.name).name
   if name=='uesave' or name.startswith('LICENSE'):
    raw=tar.extractfile(entry).read();assert len(raw)<32*1024**2;(out/name).write_bytes(raw)
    if name=='uesave':os.chmod(out/name,0o755);found=True
 assert found
 print('PINNED_SAVE_READER_READY',lock['version'],flush=True)
if __name__=='__main__':main()
