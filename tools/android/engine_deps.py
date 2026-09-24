#!/usr/bin/env python3
"""Install only Android files from the authorized pinned Epic GitDependencies manifest.
Verifies decompressed pack and individual blob SHA-1 values; never publishes data.
"""
import argparse,concurrent.futures,gzip,hashlib,json,os,tempfile,time
from pathlib import Path,PurePosixPath
from urllib.request import urlopen
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

def digest(path):
    h=hashlib.sha1()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def destination(root,name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe dependency path')
    result=root.joinpath(*p.parts)
    if not result.resolve().is_relative_to(root.resolve()):raise ValueError('Escaping dependency path')
    return result

def install_blob(raw,blob,entry,root):
    target=destination(root,entry['Name']);target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_name(target.name+'.ue-download')
    h=hashlib.sha1();remaining=int(blob['Size'])
    try:
        with raw.open('rb') as source,temporary.open('wb') as out:
            source.seek(int(blob['PackOffset']))
            while remaining:
                chunk=source.read(min(1024*1024,remaining))
                if not chunk:raise ValueError('Truncated dependency blob')
                remaining-=len(chunk);h.update(chunk);out.write(chunk)
        if h.hexdigest()!=entry['Hash']:raise ValueError('Blob checksum mismatch')
        temporary.chmod(0o755 if entry.get('IsExecutable','false').lower()=='true' else 0o644)
        os.replace(temporary,target)
    finally:
        temporary.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--engine-root',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
    x=ET.parse(a.manifest).getroot();base=x.attrib['BaseUrl'].rstrip('/')
    parsed=urlparse(base)
    if parsed.scheme!='https' or parsed.hostname!='cdn.unrealengine.com':raise ValueError('Unapproved engine dependency host')
    blobs={b.attrib['Hash']:b.attrib for b in x.find('Blobs')};packs={p.attrib['Hash']:p.attrib for p in x.find('Packs')}
    entries=[f.attrib for f in x.find('Files') if 'android' in f.attrib['Name'].lower() or 'arm64-v8a' in f.attrib['Name'].lower()]
    if not entries:raise ValueError('No Android dependency entries')
    groups={};existing=0
    for e in entries:
        target=destination(a.engine_root,e['Name']);b=blobs[e['Hash']]
        if target.is_file() and target.stat().st_size==int(b['Size']) and digest(target)==e['Hash']:
            existing+=1;continue
        groups.setdefault(b['PackHash'],[]).append(e)
    print('ANDROID_DEPENDENCIES',json.dumps({'selected_files':len(entries),'already_verified':existing,'packs_to_download':len(groups)}),flush=True)
    def process(pack_hash):
        pack=packs[pack_hash];remote=pack['RemotePath']
        if '..' in PurePosixPath(remote).parts or '://' in remote:raise ValueError('Unsafe pack path')
        url=base+'/'+remote+'/'+pack_hash
        for attempt in range(3):
            try:
                with tempfile.TemporaryDirectory(prefix='android-gitdeps-') as directory:
                    raw=Path(directory)/'pack';h=hashlib.sha1();size=0
                    with urlopen(url,timeout=60) as response,gzip.GzipFile(fileobj=response) as gz,raw.open('wb') as out:
                        while True:
                            chunk=gz.read(1024*1024)
                            if not chunk:break
                            size+=len(chunk)
                            if size>int(pack['Size']):raise ValueError('Pack larger than declared')
                            h.update(chunk);out.write(chunk)
                    if size!=int(pack['Size']) or h.hexdigest()!=pack_hash:raise ValueError('Pack checksum mismatch')
                    for e in groups[pack_hash]:install_blob(raw,blobs[e['Hash']],e,a.engine_root)
                return len(groups[pack_hash])
            except Exception:
                if attempt==2:raise
                time.sleep(2**attempt)
    installed=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for count in pool.map(process,groups):installed+=count
    report={'phase':'authorized-android-engine-dependencies','manifest_sha256':hashlib.sha256(a.manifest.read_bytes()).hexdigest(),'selected_files':len(entries),'previously_verified_files':existing,'installed_and_hash_verified_files':installed,'packs_verified':len(groups),'android_native_compiled':False,'apk_produced':False}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print('ANDROID_DEPENDENCIES_READY',json.dumps(report),flush=True)
if __name__=='__main__':main()
