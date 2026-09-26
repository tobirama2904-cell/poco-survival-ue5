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
