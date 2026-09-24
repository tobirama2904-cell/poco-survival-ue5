#!/usr/bin/env bash
set -euo pipefail
cd /project
ENGINE=/home/ue4/UnrealEngine
mkdir -p artifacts/android-build
python3 tools/engine_inventory.py
python3 tools/android/overlay_source.py
python3 tools/android/engine_deps.py --manifest .cache/engine-dependencies.xml --engine-root "$ENGINE" --report artifacts/android-build/dependency-report.json
# The official installed image lacks Android prebuilts but includes source.
# Use real source compilation, not a fake installed-platform declaration.
if [[ -f "$ENGINE/Engine/Build/InstalledBuild.txt" ]]; then
  mv "$ENGINE/Engine/Build/InstalledBuild.txt" "$ENGINE/Engine/Build/InstalledBuild.disabled-for-android"
fi
if [[ -s .cache/native-restore/android-cache-manifest.json ]]; then
  cat .cache/native-restore/android-cache.tar.gz.part??? | python3 tools/android/restore_cache.py --manifest .cache/native-restore/android-cache-manifest.json
  rm -rf .cache/native-restore
fi
set +e
timeout --foreground 180m "$ENGINE/Engine/Build/BatchFiles/Linux/Build.sh" \
  PocoSurvival Android Development -Project=/project/PocoSurvival.uproject \
  -architectures=arm64 -MaxParallelActions=2 -NoUBA -NoHotReloadFromIDE \
  2>&1 | tee artifacts/android-build/native-build.log
RESULT=${PIPESTATUS[0]}
set -e
export NATIVE_BUILD_EXIT="$RESULT"
python3 - <<'PY'
import json,os
from pathlib import Path
binaries=[{'name':p.name,'bytes':p.stat().st_size} for p in Path('/project/Binaries/Android').glob('*.so')]
result={'phase':'android-native-source-build','exit_code':int(os.environ['NATIVE_BUILD_EXIT']),'native_binaries':binaries,'native_compilation_succeeded':int(os.environ['NATIVE_BUILD_EXIT'])==0 and bool(binaries),'content_cooked':False,'apk_produced':False,'physical_device_tested':False}
Path('artifacts/android-build/native-result.json').write_text(json.dumps(result,indent=2)+'\n');print('ANDROID_NATIVE_RESULT',json.dumps(result),flush=True)
PY
# Save useful partial work even when compilation fails. This folder must ONLY
# be uploaded to the owner's private engine-cache repository, never this repo.
timeout --foreground 20m python3 tools/android/cache_intermediates.py || echo 'PRIVATE_CACHE_CAPTURE_FAILED'
if [[ "$RESULT" -eq 0 ]]; then
  python3 -c 'import json; assert json.load(open("artifacts/android-build/native-result.json"))["native_compilation_succeeded"], "No Android shared library produced"'
fi
exit "$RESULT"
