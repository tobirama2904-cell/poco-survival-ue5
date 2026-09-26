#!/usr/bin/env python3
import json,hashlib,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'.cache/cmu-motion';out.mkdir(parents=True,exist_ok=True)
for f in json.loads((ROOT/'BuildData/characters/cmu-boxing.lock.json').read_text())['files']:
 p=out/f['file'];assert p.parent==out and p.suffix in ('.asf','.amc')
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:
  with urllib.request.urlopen(f['url'],timeout=120) as r:data=r.read()
  assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256'];p.write_bytes(data)
print('CMU_MOTION_SOURCES_VERIFIED')
