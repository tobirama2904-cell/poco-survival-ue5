#!/usr/bin/env python3
import json,hashlib,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[2];lock=json.loads((root/'BuildData/characters/conditioned.lock.json').read_text());out=root/'.cache/characters';out.mkdir(parents=True,exist_ok=True)
for f in lock['files']:
 p=out/f['name']
 if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']:continue
 with urllib.request.urlopen(f['url'],timeout=90) as r:p.write_bytes(r.read())
 assert p.stat().st_size==f['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],f['name']
print('VERIFIED_CHARACTER_SOURCES',len(lock['files']))
