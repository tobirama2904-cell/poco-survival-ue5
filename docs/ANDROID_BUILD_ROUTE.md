# Remaining Android build gate

## Measured, not guessed

The authorized official UE 5.7.4 Linux slim image successfully compiled this game
module with UHT/UBT and ran its native integration and save recovery tests.
The image contains actual Core private C++ source, Android platform source and
Android UBT source. The inspected Android target-platform binary, Android game
binary directory and installed-Android platform declaration were absent.
A local Android SDK was not mounted into that tested container.

The image left about 50 GiB free on the external runner. There is no need to
repeat Epic account linking: source and registry authorization are both working.

`content/engine.lock.json` pins the authorized official image digest and exact
matching GitHub source commit. `content/android-toolchain.lock.json` pins Google
package metadata for API 35, build-tools 35.0.1 and NDK r27c; Java 21 is required.
These Google packages were verified in the official repository metadata, not yet
installed or tested in an Android UE build.

## Next implementation sequence — not claimed completed

1. Inventory all relevant Android module names and third-party ARM64 libraries,
   and inspect the existing runner SDK/JDK before duplicating installations.
2. Supply the pinned SDK/NDK/JDK to the engine build environment.
3. Build the missing Android runtime and host Android cook/platform modules from
   authorized, matching source. Source paths alone are not compiled modules;
   adding a platform name to a config does not prove working Android support.
4. Verify native Android compilation and actual content cooking, package a signed
   installable APK, then test launch, touch input, saves and scene rendering.
5. Only after that gate, scale authored districts, animation, gameplay and story.

Any reusable engine/source/cache artifacts must stay private to licensed users.
Public releases may contain the appropriately packaged game and licensed game
content, not an extracted Unreal Editor or raw Epic engine tree. No paid runner
or paid service is enabled. A successful headless Linux editor check is not a
substitute for Android execution, visual review or physical POCO F4 measurements.

## Executed Android bootstrap update

The pinned SDK/NDK/JDK setup now passed on a real runner. The downloader verified
830 Android dependency files (178 already present; 652 installed, from 219 packs).
The first native attempt stopped at the missing GoogleGameSDK module definition.
The next job adds authorized matching source and portable dependency headers.
This is active implementation, but native compilation and APK production are not
yet verified. See `docs/STATUS.json` and the live run before restarting anything.

A new private repository holds licensed intermediates when available. Capture is
attempted after compiler failure as well as success; checksummed restore code has
synthetic tests, but no real checkpoint roundtrip is claimed yet. Never expose
these engine archives as public game downloads.
