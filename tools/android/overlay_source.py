#!/usr/bin/env python3
"""Complete the slim image from authorized, digest-matched source checkout.
Never publishes source. Preserve original binary build/version identity files.
"""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
SOURCE=Path('/project/.cache/engine-source');DEST=Path('/home/ue4/UnrealEngine')
PRESERVE={'Engine/Build/Build.version','Engine/Source/Runtime/Launch/Resources/Version.h'}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.digest()
def main():
    metadata=json.loads(Path('/project/.cache/engine-source-checkout.json').read_text());lock=json.loads(Path('/project/content/engine.lock.json').read_text())
    if metadata['commit']!=lock['source_commit']:raise ValueError('Engine source revision mismatch')
    added=updated=unchanged=0
    for source in (SOURCE/'Engine').rglob('*'):
        if not source.is_file() or source.is_symlink():continue
        relative=source.relative_to(SOURCE).as_posix();target=DEST/relative
        if relative in PRESERVE and target.exists():continue
        if not target.resolve().is_relative_to(DEST.resolve()):raise ValueError('Escaping engine source path')
        if target.is_file() and target.stat().st_size==source.stat().st_size and sha(target)==sha(source):unchanged+=1;continue
        existed=target.exists();target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        os.utime(target,(metadata['commit_timestamp'],metadata['commit_timestamp']))
        if existed:updated+=1
        else:added+=1
    report={'phase':'authorized-matching-engine-source-overlay','source_commit':metadata['commit'],'files_added':added,'files_updated':updated,'files_unchanged':unchanged,'preserved_binary_identity':sorted(PRESERVE),'android_native_compiled':False,'apk_produced':False}
    Path('/project/artifacts/android-build/source-overlay.json').write_text(json.dumps(report,indent=2)+'\n');print('ENGINE_SOURCE_COMPLETED',json.dumps(report),flush=True)
    shutil.rmtree(SOURCE)
if __name__=='__main__':main()
