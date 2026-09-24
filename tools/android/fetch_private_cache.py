#!/usr/bin/env python3
"""Runner-side helper. GH_TOKEN is used by gh only; never passed into the engine."""
import hashlib,json,re,shutil,subprocess
from pathlib import Path
REPO='tobirama2904-cell/poco-ue5-engine-cache'
OUTPUT=Path('.cache/native-restore')

def gh(*args):return subprocess.check_output(['gh',*args],text=True)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def main():
    if json.loads(gh('api','repos/'+REPO))['private'] is not True:raise ValueError('Cache repository must be private')
    engine=json.loads(Path('content/engine.lock.json').read_text())
    releases=json.loads(gh('api','repos/'+REPO+'/releases?per_page=30'))
    candidates=[r for r in releases if r['tag_name'].startswith('android-'+engine['engine_version']+'-dev-') and not r['draft']]
    for release in candidates:
        shutil.rmtree(OUTPUT,ignore_errors=True);OUTPUT.mkdir(parents=True)
        if not any(a['name']=='android-cache-manifest.json' for a in release['assets']):continue
        gh('release','download',release['tag_name'],'--repo',REPO,'--pattern','android-cache-manifest.json','--dir',str(OUTPUT))
        manifest=OUTPUT/'android-cache-manifest.json';j=json.loads(manifest.read_text())
        if j.get('schema')!=1 or j.get('engine_reference')!=engine['reference'] or j.get('configuration')!='Android arm64 Development':continue
        parts=j['parts']
        if not 0<len(parts)<=64:raise ValueError('Invalid cache part count')
        names=[];compressed=0
        for i,p in enumerate(parts):
            if p['file']!='android-cache.tar.gz.part%03d'%i or not re.fullmatch('[0-9a-f]{64}',p['sha256']) or not 0<p['bytes']<2**31:raise ValueError('Invalid cache part metadata')
            names.append(p['file']);compressed+=p['bytes']
        needed=compressed+int(j['uncompressed_bytes'])+8*1024**3
        if needed>shutil.disk_usage('.').free:
            print('PRIVATE_CACHE_SKIPPED_INSUFFICIENT_DISK',needed,flush=True);shutil.rmtree(OUTPUT);return
        for part in parts:
            gh('release','download',release['tag_name'],'--repo',REPO,'--pattern',part['file'],'--dir',str(OUTPUT))
            path=OUTPUT/part['file']
            if path.stat().st_size!=part['bytes'] or sha(path)!=part['sha256']:raise ValueError('Private cache checksum mismatch')
        print('PRIVATE_CACHE_DOWNLOADED_AND_VERIFIED',release['tag_name'],len(parts),compressed,flush=True);return
    shutil.rmtree(OUTPUT,ignore_errors=True)
    print('PRIVATE_NATIVE_CACHE_MISS',flush=True)
if __name__=='__main__':main()
