#!/usr/bin/env bash
set -euo pipefail
cd /project
ENGINE=/home/ue4/UnrealEngine/Engine
mkdir -p artifacts/gameplay-scene artifacts/engine-probe artifacts/android-build
rm -f artifacts/gameplay-scene/{scene-construction,city-construction,render-verification}.json
"$ENGINE/Build/BatchFiles/Linux/Build.sh" PocoSurvivalEditor Linux Development \
  -Project=/project/PocoSurvival.uproject -NoHotReloadFromIDE -MaxParallelActions=2 -NoUBA \
  2>&1 | tee artifacts/gameplay-scene/ubt.log
"$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script=/project/tools/ue_integration_smoke.py \
  -unattended -nop4 -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/gameplay-scene/native-save-test.log
"$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script=/project/tools/characters/import_unreal.py \
  -unattended -nop4 -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/gameplay-scene/character-import.log
# Test slots must never leak into the scene capture or become shipped progress.
rm -f Saved/SaveGames/Survival_A.sav Saved/SaveGames/Survival_B.sav
rm -f Content/Worlds/CanalDistrict.umap
"$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script=/project/tools/scene/build_unreal_scene.py \
  -unattended -nop4 -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/gameplay-scene/scene-import.log
test -s artifacts/gameplay-scene/scene-construction.json
"$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script=/project/tools/scene/expand_city.py \
  -unattended -nop4 -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/gameplay-scene/city-import.log
test -s artifacts/gameplay-scene/city-construction.json

export SDL_AUDIODRIVER=dummy
for SCRIPT in /project/tools/scene/import_gameplay_assets.py /project/tools/scene/prepare_mobile_scene.py; do
 "$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script="$SCRIPT" '-ini:Engine:[/Script/Engine.AudioSettings]:DefaultAudioCompressionType=PCM' \
  -unattended -nop4 -NullRHI -AllowCommandletAudio -stdout -FullStdOutLogOutput \
  > "artifacts/gameplay-scene/$(basename "$SCRIPT" .py).log" 2>&1
done
