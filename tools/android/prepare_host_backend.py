#!/usr/bin/env python3
"""Selectively compile missing Android host modules; preserve installed Linux libs.
Edits ONLY the disposable licensed engine checkout. No licensed text is exported.
"""
import hashlib,json,re
from pathlib import Path
engine=Path('/home/ue4/UnrealEngine/Engine');binary=engine/'Binaries/Linux'
names=['AndroidDeviceDetection','AndroidTargetPlatformSettings','AndroidTargetPlatformControls','AndroidTargetPlatform']
missing=[name for name in names if not any(binary.rglob('libUnrealEditor-'+name+'.so'))]
report={'already_present':[name for name in names if name not in missing],'selected_missing_modules':missing,'engine_installed_marker_preserved':(engine/'Build/InstalledBuild.txt').exists(),'overrides':[],'host_backend_compiled':False}
for name in missing:
    matches=list((engine/'Source').rglob(name+'.Build.cs'))
    if len(matches)!=1:raise RuntimeError('Expected exactly one module rule: '+name)
    path=matches[0];original=path.read_text()
    pattern=r'(public\s+'+name+r'\s*\(\s*ReadOnlyTargetRules\s+Target\s*\)\s*:\s*base\s*\(\s*Target\s*\)\s*\{)'
    changed,count=re.subn(pattern,r'\1\n        bUsePrecompiled = false; // disposable selective host augmentation',original,count=1)
    if count!=1:raise RuntimeError('Unrecognized pinned module constructor: '+name)
    path.write_text(changed)
    report['overrides'].append({'module':name,'path':str(path.relative_to(engine)),'before_sha256':hashlib.sha256(original.encode()).hexdigest(),'after_sha256':hashlib.sha256(changed.encode()).hexdigest()})
if missing:
    target=Path('/project/Source/PocoSurvivalEditor.Target.cs');text=target.read_text();anchor='ExtraModuleNames.Add("PocoSurvival");'
    if text.count(anchor)!=1:raise RuntimeError('Unexpected project editor target')
    extra='\n        ExtraModuleNames.AddRange(new string[] { '+', '.join('"'+n+'"' for n in missing)+' });'
    target.write_text(text.replace(anchor,anchor+extra))
Path('/project/artifacts/android-build/host-backend-selection.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
