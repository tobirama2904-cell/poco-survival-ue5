# City campaign implementation — development branch

This is an implementation checkpoint, not the requested finished APK and not a claim of 12–28 hours.

- Authored source: `BuildData/story/city.json`; generated native definition: `Private/Core/CityContent.cpp`.
- 55 one-time actions: 11 historical foundation actions and 44 added story/resource actions.
- 6 districts, 55 action sites, 103 Russian dialogue lines, two extra narrative decision pairs.
- Native game instance and load replay use the same expanded definition. Foundation saves remain accepted; new saves identify `city-1`.
- Story interactions start a manually advanced subtitle/camera sequence. These are not performance-captured cinematic scenes.
- Native healing consumes a medkit only below full health and restores up to 55 health. Supplies and crafting are finite, not repeatable resource exploits.
- Journal/navigation/touch controls and portrait-backed subtitles are implemented in C++; UE compilation and rendering are separate gates.
- `expand_city.py` authors connected ground, instanced architectural blockout, all added sites, and ten additional persistent patrol encounters into the actual map. Architecture/interaction props and the mannequin remain temporary art. No final NPC models are included.
- `portraits.jpg` contains original AI-generated fictional character concept portraits (Leyla / Nargis / Timur), generated for this project. It is not a photo of real people or proof of shipped character quality.

Local verification: sanitizer-enabled legacy core and city tests passed, including eight branch combinations, post-ending actions, atomic invalid actions, historical journal migration, and randomized save replay. Sixteen Android pipeline unit tests passed. Python files compile. These tests do **not** validate native UE adapters, reachability, rendering, Android installation, playtime, or POCO frame rate.

Previous baseline cook `36082332279` subsequently failed **before cooking**: the pinned editor's Python module does not expose `unreal.AudioSettings`. Log evidence confirms dummy audio device/submix initialization succeeded; this is not the previous missing-decoder error. The city branch now supplies the PCM default through the Engine ini command-line override, retaining explicit PCM on the imported wave. The repair still needs its actual cook gate.
