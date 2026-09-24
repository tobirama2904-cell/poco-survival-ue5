#!/usr/bin/env bash
set -euo pipefail
cd /project
ENGINE=/home/ue4/UnrealEngine/Engine
mkdir -p artifacts/gameplay-scene artifacts/engine-probe
"$ENGINE/Build/BatchFiles/Linux/Build.sh" PocoSurvivalEditor Linux Development \
  -Project=/project/PocoSurvival.uproject -NoHotReloadFromIDE -MaxParallelActions=2 -NoUBA \
  2>&1 | tee artifacts/gameplay-scene/ubt.log
"$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script=/project/tools/ue_integration_smoke.py \
  -unattended -nop4 -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/gameplay-scene/native-save-test.log
# Test slots must never leak into the scene capture or become shipped progress.
rm -f Saved/SaveGames/Survival_A.sav Saved/SaveGames/Survival_B.sav
"$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script=/project/tools/scene/build_unreal_scene.py \
  -unattended -nop4 -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/gameplay-scene/scene-import.log
test -s artifacts/gameplay-scene/scene-construction.json
