#!/usr/bin/env python3
"""Pinned CC0 plant sources; gltfpack reduces the tree before Blender imports it."""
import json,sys,subprocess,argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from art_pack import fetch_file,safe_path,validate_model
root=Path(__file__).resolve().parents[2]
a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args();args.output.mkdir(parents=True,exist_ok=True)
lock=json.loads((root/'BuildData/scene-extra-art.lock.json').read_text())
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch_file,[(args.source/o['id']/safe_path(f['path']),f) for o in lock['assets'] for f in o['files']]))
for asset in lock['assets']:print(validate_model(args.source/asset['id'],asset),flush=True)
subprocess.run(['gltfpack','-i',str(args.source/'tree_small_02/tree_small_02.gltf'),'-o',str(args.output/'tree_small_02.glb'),'-si','0.035','-noq','-kn','-km','-v'],check=True)
subprocess.run(['blender','-b','-t','2','--python-exit-code','1','--python',str(root/'tools/scene/condition_extra_art.py'),'--',str(args.source),str(args.output)],check=True)
