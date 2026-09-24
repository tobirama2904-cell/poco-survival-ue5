#!/usr/bin/env bash
set -euo pipefail
sudo -n apt-get update -qq
sudo -n DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Use-Pty=0 install -y --no-install-recommends python3 python3-numpy python3-pil blender cmake ninja-build git-lfs unzip mesa-vulkan-drivers libvulkan1 vulkan-tools
mkdir -p .cache
python3 -m unittest discover -s tests -v
blender --background --threads 2 --python-exit-code 1 --python tests/blender_smoke.py > .cache/blender-smoke.log 2>&1
python3 tools/dev_environment_report.py
printf '%s\n' 'RESOURCE_WORKSHOP_READY: tests and Blender rendering passed; Unreal Engine is not installed.'
