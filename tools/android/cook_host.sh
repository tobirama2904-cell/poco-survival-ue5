#!/usr/bin/env bash
set -euo pipefail
cd /project
ENGINE=/home/ue4/UnrealEngine
mkdir -p artifacts/android-build
python3 tools/engine_inventory.py
"$JAVA_HOME/bin/java" tools/android/TrustStoreProbe.java | tee artifacts/android-build/java-trust-store.log
python3 tools/scene/restore_private_content.py
# Recursive inventory proved these host backends ALREADY SHIP in Linux/Android.
# Do not overlay 70k unnecessary source files/plugins or rebuild engine modules.
python3 - <<'PYHOST'
from pathlib import Path
import json
engine=Path('/home/ue4/UnrealEngine/Engine');root=engine/'Binaries/Linux'
names=['AndroidDeviceDetection','AndroidTargetPlatformSettings','AndroidTargetPlatformControls','AndroidTargetPlatform','TextureFormatASTC','TextureFormatETC2']
found={name:[str(p.relative_to(engine)) for p in root.rglob('libUnrealEditor-'+name+'.so')] for name in names}
assert all(found.values()),found
Path('artifacts/android-build/host-backend-selection.json').write_text(json.dumps({'strategy':'reuse actual shipped host modules, no engine-source overlay','modules':found,'engine_modules_rebuilt':False},indent=2)+'\n')
PYHOST
set +e
timeout --foreground 35m "$ENGINE/Engine/Build/BatchFiles/Linux/Build.sh" \
  PocoSurvivalEditor Linux Development -Project=/project/PocoSurvival.uproject \
  -MaxParallelActions=2 -NoUBA -NoHotReloadFromIDE -Verbose \
  2>&1 | tee artifacts/android-build/host-backend-build.log
RESULT=${PIPESTATUS[0]}
set -e
cp "$ENGINE/Engine/Programs/UnrealBuildTool/Log.txt" artifacts/android-build/host-ubt-detailed.log || true
[[ "$RESULT" -eq 0 ]] || exit "$RESULT"
python3 tools/engine_inventory.py
timeout --foreground 10m "$ENGINE/Engine/Binaries/Linux/UnrealEditor-Cmd" \
 /project/PocoSurvival.uproject -run=pythonscript -script=/project/tools/scene/prepare_mobile_scene.py \
 -unattended -nop4 -NullRHI -stdout -FullStdOutLogOutput \
 > artifacts/android-build/mobile-scene-prepare.log 2>&1
set +e
timeout --foreground 65m "$ENGINE/Engine/Binaries/Linux/UnrealEditor-Cmd" \
  /project/PocoSurvival.uproject -run=Cook -TargetPlatform=Android_ASTC \
  -Map=/Game/Worlds/CanalDistrict -unattended -nop4 -NullRHI -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/android-build/mobile-cook.log
RESULT=${PIPESTATUS[0]}
set -e
export COOK_EXIT="$RESULT"
python3 - <<'PYCODE'
import json,os
from pathlib import Path
root=Path('Saved/Cooked');maps=list(root.glob('Android*/PocoSurvival/Content/Worlds/CanalDistrict.umap'));files=[p for p in root.rglob('*') if p.is_file()] if root.exists() else []
r={'phase':'actual-mobile-content-cook','exit_code':int(os.environ['COOK_EXIT']),'cooked_map_files':[str(p) for p in maps],'file_count':len(files),'bytes':sum(p.stat().st_size for p in files),'content_cooked':int(os.environ['COOK_EXIT'])==0 and bool(maps),'apk_produced':False,'physical_device_tested':False}
Path('artifacts/android-build/mobile-cook-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
PYCODE
[[ "$RESULT" -eq 0 ]] || exit "$RESULT"
python3 -c 'import json; assert json.load(open("artifacts/android-build/mobile-cook-result.json"))["content_cooked"]'
# Retain real cooked content and host libraries privately for packaging, not as a game download.
mkdir -p .cache/private-cook
python3 - <<'PYCODE'
from pathlib import Path
import tarfile
engine=Path('/home/ue4/UnrealEngine/Engine');paths=[Path('/project/Saved/Cooked')]
for name in ['AndroidDeviceDetection','AndroidTargetPlatformSettings','AndroidTargetPlatformControls','AndroidTargetPlatform']:
 paths+=list((engine/'Binaries/Linux').rglob('libUnrealEditor-'+name+'.so'))
paths+=list((engine/'Binaries/Linux/Android').glob('*.modules'))
with tarfile.open('.cache/private-cook/cooked-and-host.tar.gz','w:gz',compresslevel=1) as t:
 for p in paths:t.add(p,arcname=str(p).lstrip('/'))
PYCODE
sha256sum .cache/private-cook/cooked-and-host.tar.gz > .cache/private-cook/SHA256SUMS
