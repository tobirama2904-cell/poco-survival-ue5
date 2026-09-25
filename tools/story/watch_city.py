#!/usr/bin/env python3
"""Observe actual external runs; chain only verified matching content into INTERNAL packaging.
No claim of final art approval or device performance. Credentials are never stored in reports.
"""
import argparse,io,json,os,time,zipfile
from pathlib import Path
import requests
p=argparse.ArgumentParser();p.add_argument('--scene',type=int,required=True);p.add_argument('--native',type=int,required=True);p.add_argument('--branch',default='gameplay/city-story');p.add_argument('--observe-only',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--token-file',type=Path,required=True);args=p.parse_args()
args.output.mkdir(parents=True,exist_ok=True);statefile=args.output/'watch-state.json'
state=json.loads(statefile.read_text()) if statefile.exists() else {'scene':args.scene,'native':args.native,'artifacts':[],'cook_dispatch':None}
assert state['scene']==args.scene and state['native']==args.native
s=requests.Session();s.headers['Authorization']='Bearer '+args.token_file.read_text().strip();base='https://api.github.com/repos/tobirama2904-cell/poco-survival-ue5'
def get(path):
 r=s.get(base+path,timeout=35);r.raise_for_status();return r.json()
def save():
 temp=statefile.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2));temp.replace(statefile)
def evidence(run):
 for a in get(f'/actions/runs/{run}/artifacts')['artifacts']:
  if a['id'] in state['artifacts'] or a['expired']:continue
  assert a['size_in_bytes']<50*1024**2
  r=s.get(a['archive_download_url'],timeout=120);r.raise_for_status()
  with zipfile.ZipFile(io.BytesIO(r.content)) as z:
   assert sum(x.file_size for x in z.infolist())<90*1024**2
   for x in z.infolist():
    path=Path(x.filename);assert not path.is_absolute() and '..' not in path.parts
    if not x.is_dir() and path.suffix in ['.png','.jpg','.json','.log','.txt']:
     dest=args.output/str(run)/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(x))
  state['artifacts'].append(a['id']);save();print('EVIDENCE_READY',run,a['name'],flush=True)
last={};deadline=time.monotonic()+6*3600
while time.monotonic()<deadline:
 try:
  runs=[get(f'/actions/runs/{args.scene}'),get(f'/actions/runs/{args.native}')]
  for r in runs:
   active=[x['name'] for j in get(f"/actions/runs/{r['id']}/jobs")['jobs'] for x in j['steps'] if x['status']=='in_progress']
   entry={'status':r['status'],'conclusion':r['conclusion'],'active':active}
   if last.get(r['id'])!=entry:print(r['id'],json.dumps(entry),flush=True);last[r['id']]=entry
   state[str(r['id'])]=entry;evidence(r['id'])
  save()
  if any(r['status']=='completed' and r['conclusion']!='success' for r in runs):print('STOP: measured failure; inspect evidence, no packaging dispatch',flush=True);break
  if all(r['conclusion']=='success' for r in runs):
   if args.observe_only:print('READY_FOR_VISUAL_REVIEW: no cook dispatched',flush=True);break
   if state['cook_dispatch'] is None:
    # A subsequent native/reflected/config change requires a new matching native run.
    compare=get(f"/compare/{runs[1]['head_sha']}...{args.branch}")
    assert not any(x['filename'].startswith(('Source/','Config/')) or x['filename'].endswith('.uproject') for x in compare.get('files',[])), 'Branch changed native/config after verified build'
    state['cook_dispatch']='submitting';save()
    r=s.post(base+'/actions/workflows/android-cook.yml/dispatches',json={'ref':args.branch,'inputs':{'scene_run':str(args.scene),'native_run':str(args.native),'package_after_cook':True}},timeout=35)
    state['cook_dispatch']={'http_status':r.status_code,'accepted':r.status_code==204,'final_game':False};save();r.raise_for_status()
    print('MATCHED_CITY_COOK_DISPATCHED: internal APK chain, not final release',flush=True)
   break
 except Exception as e:
  print('WATCH_ERROR',type(e).__name__,str(e).split('https://')[0][:200],flush=True)
  if isinstance(e,AssertionError):break
 time.sleep(45)
