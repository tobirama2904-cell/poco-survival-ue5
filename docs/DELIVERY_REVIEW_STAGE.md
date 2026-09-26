# Consolidated delivery review

The source branch gameplay/delivery-review adopts existing gameplay/integrated-review at f8b9cb4, whose game code is f53e298. Previously authored LOD/mocap/save-reader work is inherited, not claimed as new authorship in this stage.

## What was actually inspected
- Original woodland run 36209094563: exit 124 at 35 minutes, one courtyard PNG; no successful full render gate. No material compiler errors; PSO creation hitches and long frame intervals in the log. Original cutout 205×412 was uncompressed BGRA8. These observations do not prove a single root cause or POCO FPS.
- Integrated scene 36239195212 / 0245815: success with five images. Opened rural and impact images. Actual forest-tier report: 7 near, 8 middle, 100 far, 702 hidden. Actual melee report: action pose, duplicate-input rejection, single impact/damage and locomotion recovery all passed. This is explicitly diagnostic setup, not full campaign or final animation/art approval.
- Native serialization probe 36239479663 / f53e298: actual GVAS fixtures decoded and known fields matched. This verifies the corrected producer/reader and migrations, not Android touchscreen/save behavior.
- Current source/Config/project descriptor compared with f53e298: identical game inputs. ARM64 run 36239480748 is the matching build; the older bcfe15af native is not a substitute.

## Preserved alternate experiment
A separate branch-atlas/minimal-material experiment was authored locally: 2,672-triangle tree, 588 cutout quads, 512×1024 atlas and dedicated small material graphs. Its offline review was opened but no new UE/FPS result was obtained. Publishing as county-art-004 was correctly refused because that immutable release already existed; it was not overwritten. All experiment source was preserved in a named local git stash (hash also in /home/user/woodland-experiment-stash.txt). It is not mixed into this candidate or represented as runtime-verified work.

## Remaining delivery gates
Cook the retained successful scene with current source, rerender its five-frame/forest/companion/melee checks, require a compatible successful ARM64 build, sign an internal APK, then run the stricter actual touch / newly generated save / restart comparison test. Open the actual Android images before treating the candidate as reviewed. Full-world save equality, physical POCO performance, finished art and the requested 12–24 hour game remain unproven.

All five actual images from 36239195212 have now been opened, including courtyard, grove, two-person camera, companion panel and strike. They establish visible development content, not final art acceptance. Local checks: 87 Python tests total, 85 passed and 2 unavailable-cache checks skipped.

Current cook/render job **36241745942** was dispatched on gameplay/delivery-review / 00e6070 with retained scene 36239195212 and required native 36239480748. Successful cooking continues to internal packaging and the stricter emulator test; source matching remains mandatory. The observer uses observe-only mode and does not dispatch a duplicate cook. Current-source game tree is unchanged from the verified save-producer fix f53e298.

## Delivery evidence binding
The install report now records the exact installed APK SHA256 and package-run ID after rechecking the signed/structurally verified file. Signature verification and source-provenance reports also retain that package-run ID. check_delivery.py joins actual reports and reviewed image hashes; it rejects stale files/reports, unconfirmed movement/restore, mismatched source/signing identity and final-game labels. It is an evidence consistency checker, not a substitute for apksigner, actual device execution or human image review. No approval file is fabricated in advance.

These are tooling-only changes; Source, Config and PocoSurvival.uproject still match f53e298 exactly. 94 Python tests: 88 passed and 6 absent-cache checks skipped. The new delivery-binding tests use explicit synthetic records, not a real APK. Current cook/native jobs remain the same, without restarting or changing their game code.

## Save/menu probe review before installation
Found two concrete false-positive risks in the test harness: its title search matched the ordinary HUD phrase containing «рюкзаке», and its save check could accept an already existing initial/restart autosave. The test now requires the full backpack title and a generation newer than the pre-touch snapshot, not merely newer than a previous phase.

Ran the actual OCR command against the real courtyard and backpack images from 36239195212: courtyard rejected, backpack title recognized. These are real UE images, not Android input proof. On restart, the probe now waits for the actual map log and opens the real backpack to pause ordinary dialogue before comparison, rather than waiting an unconditional 90 seconds while story progress can advance. No game-state injection or teleport was added; movement/restore thresholds remain unchanged. Restore mismatch fields and displacement are recorded for diagnosis.

100 Python checks: 94 passed, 6 absent-cache cases skipped. New probe tests are explicitly synthetic; native source/config/project trees remain identical to f53e298, so the active compilation/cook inputs are not invalidated.

ARM64 run 36239480748 completed successfully; its actual native-result.json was retrieved and confirms native compilation and AArch64 ELF verification. Cook 36241745942 is still running. Separate interior preparation c513155 on gameplay/interior-art is NOT included in this candidate. Its nine props/room recipes can be reviewed in a later independent scene without altering this package chain.

## Actual current-source cook and package retry
Cook 36241745942 succeeded: 3,513 cooked files, 491,386,826 bytes, Android ASTC map present. The repeated five-frame renderer passed with no material compilation failures; all five actual images were opened. Functional development-art review only, not final visual acceptance.

Package 36245953384 failed before engine packaging because the new pure probe unit test eagerly imported PIL, absent on the packaging host. Fixed by making the image import local to the actual OCR operation (the emulator job installs Pillow), not by removing tests. A `python -S` test now verifies the pure helper imports without third-party packages. 101 tests total: 95 pass, 6 cache-dependent tests skipped. No game-source/config/descriptor changes. Corrected packaging **36246392986** reuses successful native 36239480748 and cook 36241745942; neither expensive job was restarted.

Future interior work is isolated in gameplay/interior-playtest and is not silently included in this APK candidate.
