# Remaining host-cooking work — research, NOT a verified recipe

The ARM64 native graph completed in run 36021238459, source 499e2d8 (843 actions,
2435.05 s), producing a 999,680,224-byte unstripped .so. The overall run failed
later when Java tried to download Gradle with an empty CA trust store. The
native-only workflow now uses the officially supported `-SkipDeploy` flag and an
explicit read-only CA-store mount plus a real HTTPS preflight. This does not cook
content or turn the native output into the requested game.

The original official Linux image inventory reported no Android target-platform
module. Before attempting an APK with actual content, inspect/build the host
cooking backend and confirm supported cook platforms. Do not fake an installed
platform declaration or treat successful native linking as a successful cook.

## Facts inspected in the authorized exact-version source

Source commit: `260bb2e1c5610b31c63a36206eedd289409c5f11`.

Developer/Android modules include `AndroidDeviceDetection`,
`AndroidTargetPlatform`, `AndroidTargetPlatformControls`,
`AndroidTargetPlatformSettings`, `AndroidPlatformEditor`, `AndroidZenServerPlugin`.
Texture formats include `TextureFormatASTC` (depends on
`TextureFormatIntelISPCTexComp` and `astcenc`) and `TextureFormatETC2` (depends on
`etc2comp`). Their required **host Linux** binaries/dependencies are not established
by the Android dependency filter.

RulesAssembly initializes `bUsePrecompiled` from its read-only/installed state
before invoking a module-rules constructor. A targeted override for missing host
modules may permit reusing existing Linux editor libraries, rather than rebuilding
all of Linux Unreal. This remains a hypothesis: rules-assembly recompilation,
module output manifests/ABI identity and the dependency closure must be measured.
No host augmentation has yet been dispatched or proven.

ClangToolChain in this source disables PCH timestamps and enables validation of
PCH input contents. Immutable verified dependency files now receive stable mtimes.
This supports a sensible cache-reuse attempt, but the real restored build must
still report its results; synthetic tar tests alone do not establish reuse.

## Delivery boundary

Private cache `android-5.7.4-dev-36021238459`: 6,756,451,747 uncompressed bytes,
2,627,992,938 compressed bytes, two parts. Publication exists and matches listed
part sizes. Restoration/hash verification/use on a subsequent runner is pending.

The native-only job must not publish a no-content APK. The required next steps
are actual game content and host platform modules, mobile cooking, packaging,
signing, installation/launch, visual verification and device profiling. The
current courtyard/temporary character is an internal gate, not the several-hour
finished campaign the user requested.

## First measured software-render failure

Scene run 36028188115 compiled the updated gameplay and saved/preserved the map
in private release `scene-36028188115` (Content archive 227,348,411 bytes). Its
optional render step crashed before the first frame: PF_R64_UINT (84) had no
Vulkan image mapping. Overall green workflow did NOT constitute visual proof.
Exact-source inspection found Vulkan MapFormatSupport marks a format supported
for buffer-only usage, while the velocity dummy-UAV path chooses R64 using that
broad flag. A Linux-editor-only diagnostic flag now excludes buffer-only R64
when its PlatformFormat is VK_FORMAT_UNDEFINED, allowing the existing R32G32
image fallback. This is not an Android/hardware test or an engine binary patch.
The next render gate explicitly requires PNG + actual input/grounded evidence.

The same render log exposed automatic Nanite import and a 256-triangle yard
fallback. Mesh import now explicitly disables Nanite, preserving authored
geometry for the mobile path. This asset-side fix still requires remote checking.
