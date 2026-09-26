#!/usr/bin/env python3
"""Restore only the public, hash-pinned, CC0/original county art pack."""
import hashlib,json,zipfile,shutil,argparse
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[2]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lock',type=Path,default=ROOT/'BuildData/county-pack.lock.json');args=parser.parse_args();lock=json.loads(args.lock.read_text());dst=ROOT/'.cache/county-pack';dst.mkdir(parents=True,exist_ok=True);archive=ROOT/'.cache/county-pack.zip'
 with urlopen(lock['url'],timeout=120) as response,archive.open('wb') as f:shutil.copyfileobj(response,f)
 assert archive.stat().st_size==lock['bytes'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==lock['sha256']
 with zipfile.ZipFile(archive) as z:
  assert sum(a.file_size for a in z.infolist())<150*1024**2
  for item in z.infolist():
   path=Path(item.filename);assert not path.is_absolute() and len(path.parts)==1 and '..' not in path.parts
   z.extract(item,dst)
 for file in lock['files']:
  path=dst/file['name'];assert hashlib.sha256(path.read_bytes()).hexdigest()==file['sha256']
 print('COUNTY_ART_VERIFIED',len(lock['files']))
if __name__=='__main__':main()
