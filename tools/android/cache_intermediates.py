#!/usr/bin/env python3
"""Checkpoint licensed intermediates to split files for a PRIVATE release only."""
import hashlib,io,json,os,tarfile
from pathlib import Path
ENGINE=Path('/home/ue4/UnrealEngine/Engine');PROJECT=Path('/project')
OUTPUT=PROJECT/'.cache/private-engine-cache';LIMIT=1900*1024*1024
class Parts(io.RawIOBase):
    def __init__(self):self.stream=None;self.size=0;self.hash=None;self.parts=[];self.total=0
    def writable(self):return True
    def finish_part(self):
        if self.stream:
            self.stream.close();self.parts.append({'file':self.name,'bytes':self.size,'sha256':self.hash.hexdigest()});self.stream=None
    def write(self,data):
        count=len(data);view=memoryview(data)
        while view:
            if self.stream is None:
                self.name='android-cache.tar.gz.part%03d'%len(self.parts);self.stream=(OUTPUT/self.name).open('wb');self.size=0;self.hash=hashlib.sha256()
            n=min(len(view),LIMIT-self.size);self.stream.write(view[:n]);self.hash.update(view[:n]);self.size+=n;self.total+=n;view=view[n:]
            if self.size==LIMIT:self.finish_part()
        return count
    def tell(self):return self.total

def main():
    roots=[ENGINE/'Intermediate/Build/Android',ENGINE/'Binaries/Android',PROJECT/'Intermediate/Build/Android',PROJECT/'Binaries/Android']
    for plugin_root in [ENGINE/'Plugins',PROJECT/'Plugins']:
        if plugin_root.exists():roots.extend(plugin_root.glob('**/Intermediate/Build/Android'))
    roots=[p for p in roots if p.exists()]
    total=sum(f.stat().st_size for p in roots for f in p.rglob('*') if f.is_file() and not f.is_symlink())
    if total<1024*1024:
        print('NO_USEFUL_NATIVE_CACHE_YET',total,flush=True);return
    OUTPUT.mkdir(parents=True,exist_ok=True)
    def checked(info):
        if not (info.isfile() or info.isdir()):return None
        if not info.name.startswith(('home/ue4/UnrealEngine/Engine/','project/')):raise ValueError('Unexpected cache path')
        return info
    parts=Parts()
    with tarfile.open(fileobj=parts,mode='w|gz',compresslevel=1) as archive:
        for p in roots:archive.add(p,arcname=p.relative_to('/').as_posix(),filter=checked)
    parts.finish_part()
    lock=json.loads((PROJECT/'content/engine.lock.json').read_text())
    report={'schema':1,'private_licensed_engine_cache':True,'engine_reference':lock['reference'],'configuration':'Android arm64 Development','source_commit':os.environ.get('GAME_SOURCE_SHA'),'uncompressed_bytes':total,'parts':parts.parts,'build_exit_code':int(os.environ.get('NATIVE_BUILD_EXIT','-1')),'not_an_apk':True}
    (OUTPUT/'android-cache-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('PRIVATE_NATIVE_CACHE_READY',total,len(parts.parts),flush=True)
if __name__=='__main__':main()
