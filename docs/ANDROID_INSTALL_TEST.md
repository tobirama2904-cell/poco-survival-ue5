# Installation gate — not yet run or verified

`android-install-test.yml` only accepts an actual signed private APK release.
It verifies the SHA256 and signing identity, boots an official Google APIs API 30
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
