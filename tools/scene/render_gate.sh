#!/usr/bin/env bash
set -uo pipefail
cd /project
# CPU-only diagnostic quality: explicit 640x360/2x512 shadows, NOT a POCO profile.
export XDG_RUNTIME_DIR=/tmp/ue-runtime
mkdir -p "$XDG_RUNTIME_DIR"; chmod 700 "$XDG_RUNTIME_DIR"
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json
rm -f artifacts/gameplay-scene/*.png artifacts/gameplay-scene/runtime-movement.json artifacts/gameplay-scene/county-runtime.json artifacts/gameplay-scene/companion-runtime.json artifacts/gameplay-scene/companion-support.json artifacts/gameplay-scene/render-verification.json artifacts/gameplay-scene/forest-runtime.json
find Saved/Screenshots -type f -name '*.png' -delete 2>/dev/null || true
xvfb-run -a vulkaninfo --summary > artifacts/gameplay-scene/software-vulkan.log 2>&1 || exit $?
timeout --foreground 35m xvfb-run -a -s '-screen 0 640x360x24' \
  /home/ue4/UnrealEngine/Engine/Binaries/Linux/UnrealEditor \
  /project/PocoSurvival.uproject /Game/Worlds/CanalDistrict -game -vulkan -sm5 \
  -windowed -ResX=640 -ResY=360 -unattended -nosound -nop4 -nosplash \
  -SurvivalSmokeScreenshot -SurvivalSoftwareVulkan -AllowSoftwareRendering -stdout -FullStdOutLogOutput \
  -ExecCmds="r.Nanite 0,sg.ShadowQuality 1,sg.PostProcessQuality 1,r.AntiAliasingMethod 1,r.Shadow.MaxResolution 512,r.Shadow.MaxCSMResolution 512,r.Shadow.CSM.MaxCascades 2,r.VolumetricFog 0" \
  > artifacts/gameplay-scene/rendered-game.log 2>&1
RESULT=$?
find Saved/Screenshots -type f -name '*.png' -exec cp {} artifacts/gameplay-scene/ \; 2>/dev/null || true
python3 tools/scene/verify_render.py --exit-code "$RESULT"
