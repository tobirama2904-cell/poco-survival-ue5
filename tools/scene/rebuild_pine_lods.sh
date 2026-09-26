#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 tools/scene/fetch_county.py --lock BuildData/county-base-003.lock.json
blender -b -t 2 --python tools/scene/bake_pine_lod.py
python3 tools/scene/pack_pine_lod_atlas.py
blender -b -t 2 --python tools/scene/author_pine_lods.py
