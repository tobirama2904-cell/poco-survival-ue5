#!/usr/bin/env python3
"""Bounded CI repair window; reuses the already-pulled licensed editor.
Only accepts a changed main commit in relevant project source, never a PR.
No autonomous authoring: a reviewed corrective commit must actually arrive.
"""
import subprocess,time,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
def git(*args):return subprocess.check_output(['git','-c','safe.directory='+str(root),'-C',str(root),*args],text=True).strip()
before=git('rev-parse','HEAD')
refs=git('for-each-ref','--format=%(refname:short)','--points-at='+before,'refs/remotes/origin').splitlines()
refs=[r for r in refs if r!='origin/HEAD']
if len(refs)!=1:raise RuntimeError('Cannot unambiguously identify the checked-out repair branch')
branch=refs[0].removeprefix('origin/')
deadline=time.monotonic()+480
while time.monotonic()<deadline:
 git('fetch','--quiet','origin',branch);after=git('rev-parse','FETCH_HEAD')
 if before!=after:
  changed=git('diff','--name-only',before,after).splitlines()
  if any(p.startswith(('Source/','tools/scene/','Config/')) for p in changed):
   if any(p in changed for p in ['BuildData/engine.lock.json','BuildData/scene-source.lock.json']):raise RuntimeError('Pinned engine/art changed; a fresh preparation is required')
   git('reset','--hard',after)
   (root/'artifacts/gameplay-scene/effective-source.json').write_text(json.dumps({'initial_source':before,'corrected_source':after,'reason':'measured failure; editor reused during bounded repair window'},indent=2)+'\n')
   print('CORRECTIVE_SOURCE_READY',after,flush=True);break
 print('WAITING_FOR_MEASURED_CORRECTION',before,flush=True);time.sleep(20)
else:raise RuntimeError('No corrective code commit in the bounded repair window')
