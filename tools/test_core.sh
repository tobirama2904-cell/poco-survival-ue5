#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .cache/core
c++ -std=c++20 -Wall -Wextra -Werror -pedantic -g \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  -I Source/PocoSurvival/Public Source/PocoSurvival/Private/Core/*.cpp \
  tests/core/test_survival.cpp -o .cache/core/test_survival
ASAN_OPTIONS=detect_leaks=1 .cache/core/test_survival

g++ -std=c++20 -Wall -Wextra -Werror -fsanitize=address,undefined -ISource/PocoSurvival/Public tests/core/test_vitals.cpp -o .cache/tests/vitals
.cache/tests/vitals
