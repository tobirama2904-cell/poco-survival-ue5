#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .cache/core
c++ -std=c++20 -Wall -Wextra -Werror -pedantic -g \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  -I Source/PocoSurvival/Public Source/PocoSurvival/Private/Core/*.cpp \
  tests/core/test_survival.cpp -o .cache/core/test_survival
ASAN_OPTIONS=detect_leaks=1 .cache/core/test_survival

g++ -std=c++20 -Wall -Wextra -Werror -fsanitize=address,undefined -ISource/PocoSurvival/Public tests/core/test_vitals.cpp -o .cache/core/test_vitals
.cache/core/test_vitals

c++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ISource/PocoSurvival/Public Source/PocoSurvival/Private/Core/*.cpp tests/core/test_city.cpp -o .cache/core/test_city
.cache/core/test_city

c++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ISource/PocoSurvival/Public tests/core/test_combat.cpp -o .cache/core/test_combat
.cache/core/test_combat

c++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ISource/PocoSurvival/Public tests/core/test_experience.cpp -o .cache/core/test_experience
.cache/core/test_experience

c++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ISource/PocoSurvival/Public tests/core/test_field.cpp -o .cache/core/test_field
.cache/core/test_field

c++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ISource/PocoSurvival/Public Source/PocoSurvival/Private/Core/CountyStories.cpp tests/core/test_county_stories.cpp -o .cache/core/test_county_stories
.cache/core/test_county_stories

c++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ISource/PocoSurvival/Public Source/PocoSurvival/Private/Core/AmericanStory.cpp tests/core/test_main_campaign.cpp -o .cache/core/test_main_campaign
.cache/core/test_main_campaign

c++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ISource/PocoSurvival/Public Source/PocoSurvival/Private/Core/JourneyDialogue.cpp tests/core/test_journey.cpp -o .cache/core/test_journey
.cache/core/test_journey

c++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ISource/PocoSurvival/Public tests/core/test_companion_support.cpp -o .cache/core/test_companion_support
.cache/core/test_companion_support
