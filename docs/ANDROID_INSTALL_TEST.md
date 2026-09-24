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
