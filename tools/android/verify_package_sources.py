#!/usr/bin/env python3
"""Refuse stale native C++ / mismatched cooked definitions before APK assembly."""
import json,os,re,subprocess
from pathlib import Path
REPO='tobirama2904-cell/poco-survival-ue5'
def command(*args):return subprocess.check_output(args,text=True).strip()
def require_matching(current,native,cooked):
    for key in ['source_tree','engine_lock','project_descriptor']:
        if current[key]!=native[key] or current[key]!=cooked[key]:
            raise ValueError('Incompatible APK inputs: '+key+' differs; rebuild rather than mix binaries and reflection data')
    if current['configuration_tree']!=cooked['configuration_tree']:
        raise ValueError('Cooked configuration differs from packaging configuration')
def identity(commit):
    if not re.fullmatch('[0-9a-f]{40}',commit):raise ValueError('Invalid source commit')
    command('git','fetch','--depth=1','origin',commit)
    paths={'source_tree':'Source','engine_lock':'BuildData/engine.lock.json','project_descriptor':'PocoSurvival.uproject','configuration_tree':'Config'}
    return {'commit':commit,**{k:command('git','rev-parse',commit+':'+v) for k,v in paths.items()}}
def run(run_id,workflow):
    if not re.fullmatch('[0-9]+',run_id):raise ValueError('Invalid run ID')
    r=json.loads(command('gh','api','repos/'+REPO+'/actions/runs/'+run_id))
    if r['conclusion']!='success' or r['path']!='.github/workflows/'+workflow:
        raise ValueError('Successful matching workflow required for '+run_id)
    return r
if __name__=='__main__':
    n=run(os.environ['NATIVE_RUN'],'android-native.yml');c=run(os.environ['COOK_RUN'],'android-cook.yml')
    native=identity(n['head_sha']);cooked=identity(c['head_sha']);current=identity(command('git','rev-parse','HEAD'))
    manifest=json.loads(Path('.cache/native-restore/android-cache-manifest.json').read_text())
    if manifest['source_commit']!=native['commit']:raise ValueError('Private native cache does not match its source workflow')
    require_matching(current,native,cooked)
    report={'package_run':os.environ.get('GITHUB_RUN_ID',''),'native_run':n['id'],'cook_run':c['id'],'native':native,'cooked':cooked,'packaging':current,'matching_game_source_verified':True}
    Path('artifacts/android-build/package-source-provenance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
