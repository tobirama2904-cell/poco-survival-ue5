# Android touch routing investigation

The user's full game target is not reduced by this work. Current priority is the unresolved input/save gate on the already signed APK, package 36246392986 / SHA256 b8c1e4730f696cda32abf3a1ae7ac51290ed0e57d5cc381c6eae7d80c1a7ea8e. No game C++/configuration change or new APK is part of this diagnostic stage.

## Measured previous outcomes
- 36247365746: installed/launched, no confirmed backpack opening.
- 36250818749: backpack observed, but no newly written decodable player save established after touch Save.
- 36251361814: same-control close diagnostic true, subsequent reliable opening/save sequence failed. This was NOT counted as a successful interaction gate.
- Actual recordings show very sparse frame presentation on translated ARM64/software rendering. They do not establish physical POCO performance.

## Source inspection, not guesswork
Inspected the exact authorized UE5.7.4 source revision from engine.lock.json in excluded local cache: Android touch queue, Slate viewport/virtual joystick routing and legacy PlayerInput touch dispatch. PlayerInput records Began and Ended event locations separately, so the prior simple explanation that a same-frame press/release is necessarily discarded is not established. No licensed source is copied into this public repository.

## Changes to the probe
- Enable the existing LogAndroid Verbose category through the emulator launch command line. It logs Android-event-thread converted coordinates before Slate/game handling.
- Keep the existing 2-second diagnostic touch duration; do not claim normal short-tap responsiveness.
- Wait for the requested visible menu state after each toggle, rather than blindly toggling again while a prior state change may still be waiting for presentation.
- Preserve raw logs and a parsed native-touch-coordinate report. Observing an Android event does not claim that a game button accepted it or that its coordinate transform is correct.
- Preserve original strict menu, fresh save, displacement and restore-subset requirements. Keyboard remains failure-only diagnosis, never touch-success evidence.

The new run must discriminate mapping/routing/presentation delays before any engine/game input correction is justified. Changes are test tooling only; binary/scene recompilation is intentionally avoided. General test success would still not guarantee POCO driver, thermal or memory behavior.

Source 5c615fdaa6eade0ebfe4769f67e011c620f9bba6. Actual repeated installation/input test **36257316731** dispatched for the same signed APK 36246392986. 109 local Python tests: 103 passed, 6 absent-cache cases skipped. One inherited source-inspection test pointed at the wrong file; it now checks the actual delivery gate rather than weakening its requirements. At the latest observation the job had entered install/launch/input testing; no passing touch/save result is claimed.

## Measured result of 36257316731
The strict job failed, but it established new facts: backpack touch confirmation, fresh save generations 2 → 3 → 5, and an unchanged tested player/inventory/story subset after restart. Player position before and after the 1.5-second joystick gesture was exactly [0, 1700, 98.15000486373901] cm, so movement correctly remained false. This is not full-world save equality or POCO proof.

The native Android log did contain input events, using the non-targeted “motion event from index” form. The parser previously recognized only “targeted ... pointer”; that reporting defect is corrected. Reanalysis found 462 events, including (853.11, 39.93) for the requested (854, 40) menu contact. This establishes event-thread input arrival, not every later routing layer.

Next controlled probe lengthens the actual joystick gesture to eight seconds and captures its mid-contact frame; the slow emulator may not have sampled a nonzero virtual-stick analog value during the old 1.5-second gesture. This is a hypothesis, not an asserted game fix. Pre-restart touch logs are now retained instead of losing them at logcat clear. The same 50–2000 cm actual saved-displacement gate remains mandatory; no teleport, save injection or relaxed threshold is used. Binary inputs remain identical to f53e298.

Sustained-gesture source 5cb10c66ac7cc744f46eb66ece112a068b04b048; actual Android run **36273627140** dispatched against the same signed APK. Local checks: 111 tests total, 105 passed, 6 missing-cache tests skipped. No result for the new run is implied.
