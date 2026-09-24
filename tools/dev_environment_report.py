#!/usr/bin/env python3
"""Measured workspace capacity, not a claim of engine/game availability."""
import json,os,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];cache=root/'.cache';cache.mkdir(exist_ok=True)
mem=os.sysconf('SC_PHYS_PAGES')*os.sysconf('SC_PAGE_SIZE')
limits=[]
for path in ['/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory/memory.limit_in_bytes']:
 try:
  value=int(Path(path).read_text().strip())
  if 0<value<2**60:limits.append(value)
 except (OSError,ValueError):pass
smoke=cache/'blender-smoke.log'
disk=shutil.disk_usage(root)
result={'kind':'resource-workshop-verification','logical_cpus':os.cpu_count(),'host_memory_bytes':mem,'effective_memory_ceiling_bytes':min([mem]+limits),'workspace_disk_total_bytes':disk.total,'workspace_disk_free_bytes':disk.free,'blender_smoke_passed':smoke.exists() and 'BLENDER_SMOKE_PASS' in smoke.read_text(),'unreal_installed':False,'unreal_android_packaging_tested':False,'physical_poco_f4_tested':False,'gpu_acceleration_claimed':False}
(cache/'environment-report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
