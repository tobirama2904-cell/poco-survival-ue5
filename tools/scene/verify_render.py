#!/usr/bin/env python3
"""Require an actual PNG and input/floor runtime evidence, not a green optional step."""
import argparse,json
from frame_character import character_presence
from render_health import material_failures
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--exit-code',type=int,required=True);a=p.parse_args()
root=Path('/project/artifacts/gameplay-scene');images=[]
for f in root.glob('*.png'):
    with f.open('rb') as stream:
        header=stream.read(24)
    if header[:8]!=b'\x89PNG\r\n\x1a\n' or len(header)!=24:raise ValueError('Invalid screenshot PNG')
    width=int.from_bytes(header[16:20],'big');height=int.from_bytes(header[20:24],'big')
    if width<480 or height<270:raise ValueError('Screenshot unexpectedly small')
    images.append({'name':f.name,'bytes':f.stat().st_size,'width':width,'height':height,'character_presence':character_presence(f)})
movement=json.loads((root/'runtime-movement.json').read_text()) if (root/'runtime-movement.json').exists() else {}
construction=json.loads((root/'scene-ready.json').read_text()) if (root/'scene-ready.json').exists() else {}
county=json.loads((root/'county-runtime.json').read_text()) if (root/'county-runtime.json').exists() else {}
companion=json.loads((root/'companion-runtime.json').read_text()) if (root/'companion-runtime.json').exists() else {}
support=json.loads((root/'companion-support.json').read_text()) if (root/'companion-support.json').exists() else {}
forest=json.loads((root/'forest-runtime.json').read_text()) if (root/'forest-runtime.json').exists() else {}
errors=material_failures((root/'rendered-game.log').read_text(errors='replace')) if (root/'rendered-game.log').exists() else ['Missing actual renderer log']
passed=forest.get('passed') is True and support.get('passed') is True and companion.get('passed') is True and not errors and county.get('passed') is True and len(images)>=4 and construction.get('all_construction_steps_succeeded') is True and a.exit_code==0 and bool(images) and movement.get('passed') is True and movement.get('human_avatar_loaded') is True and any(f['character_presence']['passed'] for f in images)
report={'forest_runtime':forest,'companion_support':support,'companion_runtime':companion,'material_failures':errors,'county_runtime':county,'construction':construction,'renderer':'software Vulkan / llvmpipe; NOT hardware or POCO performance','renderer_exit_code':a.exit_code,'screenshots':images,'runtime_movement':movement,'gate_passed':passed,'visual_quality_review':'requires human/image inspection separately','physical_device_tested':False}
(root/'render-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
raise SystemExit(0 if passed else 1)
