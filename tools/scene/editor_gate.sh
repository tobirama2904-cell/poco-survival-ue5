#!/usr/bin/env bash
set -euo pipefail
cd /project
ENGINE=/home/ue4/UnrealEngine/Engine
mkdir -p artifacts/gameplay-scene artifacts/engine-probe artifacts/android-build
rm -f artifacts/gameplay-scene/{scene-construction,city-construction,field-content,county-content,county-runtime,companion-runtime,companion-support,melee-runtime,melee-pose-detail,forest-runtime,scene-ready,render-verification}.json
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
  -run=pythonscript -script=/project/tools/scene/import_surfaces.py \
  -unattended -nop4 -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/gameplay-scene/surface-import.log
"$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script=/project/tools/scene/expand_city.py \
  -unattended -nop4 -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput \
  2>&1 | tee artifacts/gameplay-scene/city-import.log
test -s artifacts/gameplay-scene/city-construction.json

export SDL_AUDIODRIVER=dummy
for SCRIPT in /project/tools/scene/import_gameplay_assets.py /project/tools/scene/populate_field.py /project/tools/scene/populate_county.py /project/tools/scene/populate_county_stories.py /project/tools/scene/populate_main_continuation.py /project/tools/scene/prepare_mobile_scene.py /project/tools/scene/repair_materials.py; do
 "$ENGINE/Binaries/Linux/UnrealEditor-Cmd" /project/PocoSurvival.uproject \
  -run=pythonscript -script="$SCRIPT" '-ini:Engine:[/Script/Engine.AudioSettings]:DefaultAudioCompressionType=PCM' \
  -unattended -nop4 -NullRHI -AllowCommandletAudio -stdout -FullStdOutLogOutput \
  > "artifacts/gameplay-scene/$(basename "$SCRIPT" .py).log" 2>&1
done

python3 - <<'READY'
import json,subprocess
from pathlib import Path
root=Path('artifacts/gameplay-scene');field=json.loads((root/'field-content.json').read_text());assert field['loot_caches']==24 and field['openable_doors']==24
county=json.loads((root/'county-content.json').read_text());assert county['terrain_tiles']==16 and county['rural_shelters']==6
(root/'scene-ready.json').write_text(json.dumps({'source':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'all_construction_steps_succeeded':True,'field':field,'county':county},indent=2)+'\n')
READY
