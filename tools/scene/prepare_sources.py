#!/usr/bin/env python3
"""Download pinned development scenery. Authorized template bundle stays private."""
import json,hashlib,zipfile,shutil,subprocess,os
from pathlib import Path
from urllib.request import Request,urlopen
root=Path(__file__).resolve().parents[2];cache=root/'.cache';cache.mkdir(exist_ok=True)
def download(url,path,sha=None,headers=None):
 with urlopen(Request(url,headers=headers or {}),timeout=90) as r,path.open('wb') as f:shutil.copyfileobj(r,f)
 if sha and hashlib.sha256(path.read_bytes()).hexdigest()!=sha:raise ValueError('Source checksum mismatch: '+path.name)
lock=json.loads((root/'BuildData/scene-source.lock.json').read_text());archive=cache/'courtyard-source.zip';download(lock['url'],archive,lock['sha256'])
dest=cache/'scene-source';dest.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
 assert set(z.namelist())=={'courtyard.glb','courtyard.json','sky.hdr','CREDITS.md'}
 z.extractall(dest)
engine=json.loads((root/'BuildData/engine.lock.json').read_text());manifest=cache/'engine-dependencies.xml'
download('https://api.github.com/repos/EpicGames/UnrealEngine/contents/Engine/Build/Commit.gitdeps.xml?ref='+engine['source_commit'],manifest,headers={'Authorization':'Bearer '+os.environ['UE_REGISTRY_TOKEN'],'Accept':'application/vnd.github.raw+json'})
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='af1404ab27b7c0c529e33fcd3d0e8a217b857ca97e4334e2f53c71f4670ee332'
stage=cache/'template-character'
subprocess.run(['python3',str(root/'tools/android/engine_deps.py'),'--mode','character','--manifest',str(manifest),'--engine-root',str(stage),'--report',str(root/'artifacts/gameplay-scene/character-dependencies.json')],check=True)
shutil.copytree(stage/'Templates/TemplateResources/High/Characters/Content',root/'Content/Characters',dirs_exist_ok=True)
print('SCENE_SOURCES_READY licensed template characters are internal test art, not final characters',flush=True)

subprocess.run(['python3',str(root/'tools/characters/fetch_conditioned.py')],check=True)

subprocess.run(['python3',str(root/'tools/scene/fetch_county.py')],check=True)

subprocess.run(['python3',str(root/'tools/story/fetch_county_voices.py')],check=True)

subprocess.run(['python3',str(root/'tools/story/fetch_main_voices.py')],check=True)
