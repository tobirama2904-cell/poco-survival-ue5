#!/usr/bin/env python3
"""Extract a verified private archive stream only into Android intermediate paths."""
import argparse,hashlib,json,os,sys,tarfile
from pathlib import Path,PurePosixPath

def allowed(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:return False
    parts=p.parts
    if parts[:5]==('home','ue4','UnrealEngine','Engine','Intermediate'):
        return parts[5:7]==('Build','Android')
    if parts[:5]==('home','ue4','UnrealEngine','Engine','Binaries'):
        return parts[5:6]==('Android',)
    if parts[:2] in [('project','Intermediate'),('project','Binaries')]:
        return (parts[1:4]==('Intermediate','Build','Android') or parts[1:3]==('Binaries','Android'))
    if parts[:5]==('home','ue4','UnrealEngine','Engine','Plugins'):rest=parts[5:]
    elif parts[:2]==('project','Plugins'):rest=parts[2:]
    else:return False
    return any(rest[i:i+3]==('Intermediate','Build','Android') for i in range(1,len(rest)-2))

def extract(stream,root=Path('/'),byte_limit=32*1024**3):
    root=root.resolve();total=0;count=0
    with tarfile.open(fileobj=stream,mode='r|gz') as archive:
        for member in archive:
            count+=1
            if count>300000 or not allowed(member.name) or not(member.isfile() or member.isdir()):raise ValueError('Unsafe private cache entry')
            destination=(root/member.name).resolve()
            if not destination.is_relative_to(root) or not allowed(destination.relative_to(root).as_posix()):raise ValueError('Cache symlink escape')
            total+=member.size
            if total>byte_limit:raise ValueError('Cache larger than declared')
            member.uid=os.getuid();member.gid=os.getgid();member.uname='';member.gname='';member.mode &= 0o777
            # Paths, types, links and sizes are checked above, including on Python
            # 3.10 where tarfile's newer data filter is not available.
            archive.extract(member,path=root,set_attrs=True)
    return {'files_and_directories':count,'restored_bytes':total}

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);a=p.parse_args();j=json.loads(a.manifest.read_text())
    lock=json.loads(Path('/project/content/engine.lock.json').read_text())
    if j.get('engine_reference')!=lock['reference'] or j.get('configuration')!='Android arm64 Development':raise ValueError('Cache compatibility mismatch')
    result=extract(sys.stdin.buffer,byte_limit=int(j['uncompressed_bytes']));print('PRIVATE_NATIVE_CACHE_RESTORED',json.dumps(result),flush=True)
if __name__=='__main__':main()
