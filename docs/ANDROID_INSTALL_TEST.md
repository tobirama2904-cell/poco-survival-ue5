# Installation gate — APK installed; startup not yet verified

`android-install-test.yml` only accepts an actual signed private APK release.
It verifies the SHA256 and signing identity, boots an official Google APIs API 35
x86_64 development image, records its actual ABI/native-bridge properties, and
refuses to claim ARM64 coverage unless the image advertises arm64-v8a. It then
installs, launches, captures screenshots, sends touch input and tests relaunch.
Screenshots still require visual inspection; input injection alone does not prove
correct controls, and finding save files alone does not prove state equality.

The Android team documents ARM translation in its Android 11 Google APIs emulator
images [1](https://android-developers.googleblog.com/2020/03/run-arm-apps-on-android-emulator.html).
These images are used only for app development/debug, never redistributed or
provided as a hosted commercial translation service. No physical POCO F4 test,
Adreno performance, stable FPS, final art or complete campaign is implied.

Run 36041635033 booted Android 11, advertised arm64-v8a, and installed the
signed APK successfully. Startup failed before world load: libndk_translation
0.2.2 reported undefined instruction 0x5ea1b8a7 and raised SIGILL from its
DecodeSimdScalarTwoRegMisc interpreter. The next test uses the official API 35
image to test a newer translator. This is not a claim that the APK will or will
not launch on physical ARM hardware; that remains unverified.

Run 36042443571 installed the same unchanged APK on Android 15. Native startup
passed the previous SIGILL point and initialized Unreal 5.7.4/ARM64, but Vulkan
rejected the single software CPU device. The actual screenshot shows startup
and an OS immersive-mode hint, not gameplay. Exact authorized engine source
confirms Vulkan skips CPU devices unless `-AllowSoftwareRendering` is specified;
the next emulator-only launch supplies this supported debug command-line extra
without modifying/re-signing the APK. Test resolution is 960×540, not POCO native
resolution. No software-engine feature checks are bypassed.

## Visual review of completed run 36043369641

The API35 emulator installed and loaded the real map and survived restart. Its
first two screenshots were black; the restart screenshot showed the actual
courtyard/HUD but severe magenta glare and the mobile SkyAtmosphere missing-mesh
warning. The earlier green process/map gate is NOT visual acceptance. New tests
wait for actual nonblack frames and reject this large-magenta regression. They
still do not claim touch displacement, equal restored state, final graphics,
physical POCO compatibility or FPS.

A mobile-content patch replaces the unsupported sky-atmosphere setup with a real
unlit two-sided sky sphere, restrains bloom/lens flare, and adds an original
looping wind SoundWave/AmbientSound. It requires a new cook/package and visual
check. The prior latest save-format-3 cook timed out at 40 minutes with 7,218
shaders complete and a remaining shader queue, not missing native code. The
bounded cook limit is now 65 minutes; only successful exit plus actual map counts.
