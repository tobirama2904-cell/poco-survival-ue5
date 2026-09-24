#!/usr/bin/env python3
"""Fetch pinned CC0 sources, validate glTF dependencies, package without padding.
Only listed resources enter an archive; credentials and the engine never do.
"""
import argparse, hashlib, json, os, shutil, time, urllib.request, zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]

def sha(path, algo='sha256'):
 h=hashlib.new(algo)
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def safe_path(name):
 decoded=unquote(name)
 p=PurePosixPath(decoded)
 if not decoded or p.is_absolute() or '..' in p.parts or '\\' in decoded or ':' in decoded:raise ValueError('Unsafe relative path')
 return Path(*p.parts)

def fetch_file(item):
 dest,record=item
 url=record['url'];u=urlsplit(url)
 if u.scheme!='https' or u.hostname!='dl.polyhaven.org':raise ValueError('Unapproved asset source')
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists() and dest.stat().st_size==record['size'] and sha(dest,'md5')==record['md5']:return
 for attempt in range(3):
  tmp=dest.with_name(dest.name+'.partial')
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'PocoSurvivalArtPipeline/0.1'})
   with urllib.request.urlopen(req,timeout=120) as response,tmp.open('wb') as out:shutil.copyfileobj(response,out)
   if tmp.stat().st_size!=record['size'] or sha(tmp,'md5')!=record['md5']:raise ValueError('Asset integrity mismatch: '+dest.name)
   tmp.replace(dest);return
  except Exception:
   tmp.unlink(missing_ok=True)
   if attempt==2:raise
   time.sleep(2**attempt)

def validate_model(folder,asset):
 document=json.loads((folder/asset['entrypoint']).read_text())
 assert document['asset']['version']=='2.0'
 listed={f['path'] for f in asset['files']}
 for group in ('buffers','images'):
  for item in document.get(group,[]):
   uri=item.get('uri','')
   if not uri or uri.startswith('data:'):continue
   assert unquote(uri) in listed,(asset['id'],'unlisted dependency',uri)
   path=folder/safe_path(uri);assert path.is_file()
   if group=='buffers':assert path.stat().st_size>=item['byteLength']
 accessors=document.get('accessors',[])
 triangles=0;vertices=0
 for mesh in document.get('meshes',[]):
  for p in mesh['primitives']:
   assert 'POSITION' in p['attributes'];v=accessors[p['attributes']['POSITION']]['count'];assert v>0
   vertices+=v
   if p.get('mode',4)==4:triangles+=(accessors[p['indices']]['count'] if 'indices' in p else v)//3
 assert vertices>0 and triangles>0
 return {'id':asset['id'],'vertices':vertices,'triangles':triangles,'materials':len(document.get('materials',[])),'source_valid':True}

def zip_tree(folder,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(folder.rglob('*')):
   if p.is_file() and not p.is_symlink():z.write(p,p.relative_to(folder))
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path)}

def acquire(work):
 lock=json.loads((ROOT/'BuildData/assets.lock.json').read_text());source=work/'source';source.mkdir(parents=True,exist_ok=True)
 jobs=[(source/a['id']/safe_path(f['path']),f) for a in lock['assets'] for f in a['files']]
 with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch_file,jobs))
 models=[validate_model(source/a['id'],a) for a in lock['assets']]
 manifest=[]
 for a in lock['assets']:
  for f in a['files']:
   p=source/a['id']/safe_path(f['path']);manifest.append({'path':str(p.relative_to(source)),'bytes':p.stat().st_size,'sha256':sha(p),'url':f['url'],'license':a['license']})
 (source/'SHA256-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
 (source/'SOURCE-LOCK.json').write_text(json.dumps(lock,indent=2))
 credits=['# Source art pack — not a game\n','All listed art assets: CC0-1.0. See https://polyhaven.com/license.\n','Unreal Engine is NOT included. No framerate or Unreal import validation is claimed.\n']
 for a in lock['assets']:credits.append('\n## '+a['id']+'\n'+a['source_page']+'\nAuthors: '+', '.join(a['authors'])+'\nPurpose: '+a['role']+'\n')
 (source/'CREDITS.md').write_text('\n'.join(credits))
 report={'phase':'source-art-validation','source_asset_count':len(models),'models':models,'all_source_files_verified':True,'source_bytes':sum(x['bytes'] for x in manifest),'runner_ram_bytes':os.sysconf('SC_PHYS_PAGES')*os.sysconf('SC_PAGE_SIZE'),'runner_disk_free_bytes':shutil.disk_usage(work).free,'unreal_import_tested':False,'android_build_produced':False,'poco_f4_performance_tested':False}
 (work/'source-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

def package(work,output):
 report=json.loads((work/'source-report.json').read_text())
 condition=json.loads((work/'mobile'/'conditioning-report.json').read_text())
 assert len(condition['assets'])==report['source_asset_count']
 archives=[zip_tree(work/'source',output/'environment-source-v0.1.0.zip'),zip_tree(work/'mobile',output/'environment-mobile-candidates-v0.1.0.zip')]
 report.update(archives=archives,conditioning=condition)
 output.mkdir(parents=True,exist_ok=True)
 (output/'art-build-report.json').write_text(json.dumps(report,indent=2))
 (output/'SHA256SUMS.txt').write_text(''.join(f"{a['sha256']}  {a['file']}\n" for a in archives))
 print(json.dumps({'archives':archives},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['fetch','package']);p.add_argument('--work',type=Path,default=ROOT/'.cache/art');p.add_argument('--output',type=Path,default=ROOT/'artifacts');a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
 if a.command=='fetch':acquire(a.work)
 else:package(a.work,a.output)
