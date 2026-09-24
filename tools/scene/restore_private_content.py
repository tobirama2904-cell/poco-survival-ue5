#!/usr/bin/env python3
"""Verify owner-private content archive and safely restore only project Content."""
import hashlib,tarfile
from pathlib import Path,PurePosixPath
root=Path('/project');source=root/'.cache/private-scene';archive=source/'game-content.tar.gz'
expected=(source/'SHA256SUMS').read_text().split()[0];h=hashlib.sha256()
with archive.open('rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
if h.hexdigest()!=expected:raise ValueError('Private Content SHA256 mismatch')
size=0;count=0
with tarfile.open(archive,'r|gz') as tar:
    for m in tar:
        p=PurePosixPath(m.name);count+=1;size+=m.size
        if not p.parts or p.parts[0]!='Content' or p.is_absolute() or '..' in p.parts or '\\' in m.name or ':' in m.name or not(m.isdir() or m.isfile()):raise ValueError('Unsafe Content entry')
        target=(root/m.name).resolve()
        if not target.is_relative_to(root/'Content'):raise ValueError('Content path escape')
        if count>30000 or size>3*1024**3:raise ValueError('Content archive exceeds limit')
        m.mode&=0o777
        tar.extract(m,path=root,set_attrs=False)
if not(root/'Content/Worlds/CanalDistrict.umap').is_file():raise ValueError('Real district map missing')
print('PRIVATE_CONTENT_RESTORED',count,size,flush=True)
