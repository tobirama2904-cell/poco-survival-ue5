#!/usr/bin/env python3
"""Restore verified binary/cooked inputs, not all compiler intermediates.
Private archives remain private. Reject links/traversal even for skipped members.
"""
import argparse,hashlib,json,os,sys,tarfile
from pathlib import Path,PurePosixPath
ROOT=Path('/project')
def extract(stream,prefix,root,limit):
    total=count=0
    with tarfile.open(fileobj=stream,mode='r|gz') as t:
        for m in t:
            p=PurePosixPath(m.name)
            if p.is_absolute() or '..' in p.parts or '\\' in m.name or ':' in m.name or not(m.isfile() or m.isdir()):raise ValueError('Unsafe private archive member')
            if p.parts[:len(prefix)]!=prefix:continue
            destination=(root/m.name).resolve()
            if not destination.is_relative_to(root.joinpath(*prefix)):raise ValueError('Archive path escape')
            total+=m.size;count+=1
            if total>limit or count>50000:raise ValueError('Package inputs exceed limit')
            m.mode&=0o777;t.extract(m,path=root,set_attrs=False)
    if count==0:raise ValueError('Requested archive subtree is empty')
    return {'entries':count,'bytes':total}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['native','cooked']);a=p.parse_args()
    if a.kind=='native':
        m=json.loads((ROOT/'.cache/native-restore/android-cache-manifest.json').read_text());lock=json.loads((ROOT/'BuildData/engine.lock.json').read_text())
        assert m['engine_reference']==lock['reference'] and m['build_exit_code']==0 and m['configuration']=='Android arm64 Development'
        result=extract(sys.stdin.buffer,('project','Binaries','Android'),Path('/'),4*1024**3)
        from inspect_elf import inspect
        outputs=[inspect(f) for f in (ROOT/'Binaries/Android').glob('*.so')];assert outputs
        result.update(native_source_commit=m['source_commit'],elf_outputs=outputs)
    else:
        folder=ROOT/'.cache/private-cook';archive=folder/'cooked-and-host.tar.gz';expected=(folder/'SHA256SUMS').read_text().split()[0]
        actual=sha(archive)
        if actual!=expected:raise ValueError('Cook archive SHA256 mismatch')
        with archive.open('rb') as f:result=extract(f,('project','Saved','Cooked'),Path('/'),8*1024**3)
        maps=list((ROOT/'Saved/Cooked').glob('Android*/PocoSurvival/Content/Worlds/CanalDistrict.umap'));assert maps
        result.update(archive_sha256=actual,cooked_maps=[{'path':str(f.relative_to(ROOT)),'sha256':sha(f)} for f in maps])
    (ROOT/f'artifacts/android-build/restored-{a.kind}.json').write_text(json.dumps(result,indent=2)+'\n');print('REAL_PACKAGE_INPUT_RESTORED',a.kind,json.dumps(result),flush=True)
if __name__=='__main__':main()
