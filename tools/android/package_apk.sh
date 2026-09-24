#!/usr/bin/env bash
set -euo pipefail
cd /project
ENGINE=/home/ue4/UnrealEngine
mkdir -p artifacts/android-build artifacts/apk
"$JAVA_HOME/bin/java" tools/android/TrustStoreProbe.java | tee artifacts/android-build/java-trust-store.log
if [[ ! -f .cache/package-inputs-ready ]]; then
cat .cache/native-restore/android-cache.tar.gz.part??? | python3 tools/android/restore_package_inputs.py native
python3 tools/android/restore_package_inputs.py cooked
rm -rf .cache/native-restore .cache/private-cook
# Runtime Java/templates/UPL files and Android third-party binaries are required
# by deployment even though native compilation and cooking are deliberately skipped.
python3 tools/android/overlay_source.py
python3 tools/android/engine_deps.py --manifest .cache/engine-dependencies.xml --engine-root "$ENGINE" --report artifacts/android-build/package-dependencies.json
  touch .cache/package-inputs-ready
fi
set +e
timeout --foreground 50m "$ENGINE/Engine/Build/BatchFiles/RunUAT.sh" \
  -NoCompile BuildCookRun -project=/project/PocoSurvival.uproject \
  -nop4 -unattended -utf8output -nocompileeditor -skipbuild -skipcook \
  -platform=Android -cookflavor=ASTC -clientconfig=Development \
  -stage -pak -package -archive -archivedirectory=/project/.cache/packaged \
  2>&1 | tee artifacts/android-build/apk-package.log
RESULT=${PIPESTATUS[0]}
set -e
cat /sys/fs/cgroup/memory.events > artifacts/android-build/package-memory.log || true
export PACKAGE_EXIT="$RESULT"
python3 - <<'PYCODE'
from pathlib import Path
import json,os,shutil
candidates=list(Path('.cache/packaged').rglob('*.apk'))
if not candidates:candidates=list(Path('Binaries/Android').glob('*.apk'))
candidates=[p for p in candidates if 'AFS' not in p.name]
r={'phase':'Android packaging','uat_exit_code':int(os.environ['PACKAGE_EXIT']),'candidate_apks':[{'path':str(p),'bytes':p.stat().st_size} for p in candidates],'apk_produced':int(os.environ['PACKAGE_EXIT'])==0 and bool(candidates),'signed_and_verified':False,'physical_device_tested':False,'finished_game':False}
Path('artifacts/android-build/apk-package-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
if r['apk_produced']:
 if len(candidates)!=1:raise RuntimeError('Expected one unambiguous ARM64/ASTC APK')
 shutil.copy2(candidates[0],'artifacts/apk/unsigned-internal.apk')
PYCODE
[[ "$RESULT" -eq 0 ]] || exit "$RESULT"
test -s artifacts/apk/unsigned-internal.apk
