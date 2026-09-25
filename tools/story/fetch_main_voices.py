#!/usr/bin/env python3
"""Fetch only hash-pinned authored PCM speech; no credentials or engine assets."""
import hashlib,json,zipfile,shutil
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[2]
def main():
 out=ROOT/'BuildData/mainvoices';lock=json.loads((out/'archive.lock.json').read_text());integrity=json.loads((out/'integrity.json').read_text());expected={f['name']:f for f in integrity['files']}
 def valid(name):
  p=out/name;return p.is_file() and p.stat().st_size==expected[name]['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==expected[name]['sha256']
 if all(valid(n) for n in expected):return
 cache=ROOT/'.cache/main-dialogue.zip';cache.parent.mkdir(exist_ok=True)
 with urlopen(lock['url'],timeout=120) as r,cache.open('wb') as f:shutil.copyfileobj(r,f)
 assert cache.stat().st_size==lock['bytes'] and hashlib.sha256(cache.read_bytes()).hexdigest()==lock['sha256']
 with zipfile.ZipFile(cache) as z:
  assert len(z.infolist())==len(expected)==96 and set(z.namelist())==set(expected)
  assert sum(i.file_size for i in z.infolist())<40*1024**2
  for i in z.infolist():
   name=Path(i.filename);assert len(name.parts)==1 and name.suffix=='.wav' and not name.is_absolute();data=z.read(i);assert len(data)==expected[i.filename]['bytes'];assert hashlib.sha256(data).hexdigest()==expected[i.filename]['sha256'];(out/name).write_bytes(data)
 print('MAIN_VOICE_CORPUS_VERIFIED',len(expected),integrity['total_seconds'],flush=True)
if __name__=='__main__':main()
