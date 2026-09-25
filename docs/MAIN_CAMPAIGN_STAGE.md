# Main-campaign implementation stage

Branch: gameplay/main-campaign. This is source work awaiting its own UE verification, not a final release.

## Implemented source
- Main story grows from 18 to 30 scenes, 98 to 194 RU/EN lines. The six county stories (144 lines per language) stay optional and independent.
- Original continuous rescue/return journey; four new cinematic-marked scenes and eight moving conversations, not twelve completed final-quality cutscenes.
- Five ordered main-story events and one optional receiver repair-kit pickup. Atomic ordinary-resource repair, protected medical pack, no duplicate quest rewards, extra local kit avoids a consumed-material soft lock.
- Save format 8: main event prefix and repair-kit state; migrated formats 1–7; scene prerequisite validation; retained county choices and earlier flood decision.
- Two protected narrative companions: Mara follows beside/behind the player after part I; Ruth joins more slowly after treatment and stays at the orchard after the new part ends. Stationary staging duplicates are hidden when their moving counterpart is active.
- Physical following, crouching, local obstacle/floor probes, safe initial placement and bounded off-screen recovery. This is NOT full tactical AI/global navigation or permanent companion death. These actors are deliberately damage-protected while those systems remain unimplemented.
- Existing licensed locomotion/talk clips reused; no claim of new final facial/attack animation. Talking stops when banter is paused; no talk gesture while aiming/drawing a bow. Held weapons hidden for cinematic framing and restored afterwards.
- Banter pauses for combat and backpack/control editing; combat music takes priority. Non-narrative loot/doors/main interactions no longer automatically skip speech. Subtitle panels do not cover the backpack.
- Main goals do not depend on the legacy 61-action availability list; goal markers respect terrain height. Bridge story points and latch use the actual bridge at y=40, not the river at y=0.
- Cine camera targets character head height rather than adding 155 cm to an already elevated character capsule.
- Runtime gate extended with a third actual frame plus human companion movement, ground contact, proximity and post-blend cinematic-camera checks. Diagnostic state injection is explicitly recorded, not presented as a campaign playthrough.

## Recorded audio
96 new Russian PCM lines, four existing selected voices, 283.151333 seconds (4 min 43 sec). Two ambiguous one-word phrases failed the initial lexical alignment; dialogue and recordings were revised, then all 96 passed with zero alignment flags. No threshold was lowered. This is recorded-source duration, not gameplay duration or final mixing approval. Immutable release main-dialogue-001, SHA-pinned archive and per-clip integrity; independent archive restore passed. English text is present; no English dub claimed.

## Prior actual evidence
County-story run 36143714242 (cca898f) succeeded, including native UE save7 county-choice/migration tests, import, two real images and rural traversal. Those images were opened in this stage. They show the technical sky/material regressions corrected, but environment and character art are still visibly provisional; no final photoreal acceptance. The present companions/save8/main-story extension is NOT covered by that run.

## Still to verify
New native compilation/UHT and save8 integration, actual companion movement/cinematic frame, five-step in-world rescue sequence, new audio playback, matching Android build, physical-device performance and authored campaign duration. Future chapters in CAMPAIGN_DIRECTION.md are plans, not implemented levels.

## Local verification at commit preparation
Eight portable ASan/UBSan suites passed. 51 Python tests passed with one cached nature-archive test skipped when its excluded cache is absent. Main audio archive independently fetched and SHA-verified. These checks do not compile Unreal actor code. The new native integration checks also exercise a zero-material receiver recovery kit and its actual UObject serialization.

New main-campaign source: `02ed3201631e6e6cc81183cdfd273cd55335a418`; UE verification **36154689044** dispatched on gameplay/main-campaign. No matching Android native run has been dispatched for this source yet.

Separately, the previous gameplay/low-water candidate completed cook 36140764253, package 36147479631 and emulator 36149113269. Actual Android start/backpack-attempt frames were opened: intro then visible human/gameplay, still provisional art. The backpack was not shown in the backpack-attempt frame. Input was injected but touch movement was not proven; save files were not collected by the probe, which does not establish whether the game failed to save or whether the probe could not access them. No POCO performance proof. This older candidate does NOT contain either the 144-line county story extension or the new main continuation. Do not label it as containing the new content.
