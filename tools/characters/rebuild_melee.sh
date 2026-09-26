#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 tools/characters/fetch_conditioned.py --lock BuildData/characters/base-002.lock.json
python3 tools/characters/fetch_melee_sources.py
blender -b -t 2 --python tools/characters/author_melee_motion.py -- Arsen Infected Leyla Nargis Ilyas
