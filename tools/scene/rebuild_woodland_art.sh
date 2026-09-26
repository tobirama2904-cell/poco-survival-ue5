#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 tools/scene/fetch_county.py --lock BuildData/county-base-002.lock.json
cp .cache/county-pack.zip .cache/county-base-002.zip
python3 tools/scene/fetch_woodland_inputs.py
blender -b -t 2 --python tools/scene/refine_county_art.py
