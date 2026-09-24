# Remaining host-cooking work — research, NOT a verified recipe

The ARM64 native graph completed in run 36021238459, source 499e2d8 (843 actions,
2435.05 s), producing a 999,680,224-byte unstripped .so. The overall run failed
later when Java tried to download Gradle with an empty CA trust store. The
native-only workflow now uses the officially supported `-SkipDeploy` flag and an
explicit read-only CA-store mount plus a real HTTPS preflight. This does not cook
content or turn the native output into the requested game.

The original official Linux image inventory checked only the top-level Linux
binaries directory, but Android Build.cs uses BinariesSubFolder=Android. That
negative probe is therefore insufficient evidence of absence; recursive scanning
is now required. Before attempting an APK with actual content, inspect/build the host
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

Additional measured evidence: run 36028188115 scene-import.log loaded both
TextureFormatASTC (ASTCEnc 5.0.1) and TextureFormatETC2. rendered-game.log loaded
GLSL_ES3_1_ANDROID and SF_VULKAN_ES31_ANDROID shader formats. Do NOT rebuild
those working host formats speculatively. Only Linux target platforms were
registered in that SDK-less scene process; Android registration on a container
with SDK/NDK still needs testing. Exact-source RulesCompiler/RulesAssembly
inspection confirms `-ForceRulesCompile` reaches DynamicCompilation even for
read-only installed rules. If recursive probing confirms missing Android host
modules, per-module `bUsePrecompiled=false` overrides plus forced rules compilation
are a concrete next experiment, while preserving existing Linux editor binaries.

Pixel-format failure was narrowed against the pinned source, not guessed from
Nanite alone: VulkanDevice.cpp MapFormatSupport marks Supported true for a
buffer-only format. MapImageFormatSupport leaves PlatformFormat=0 if no acceptable
image format exists. VelocityRendering.cpp chooses the dummy image format using
Supported alone. The diagnostic fallback checks that exact inconsistent state;
it does not universally disable R64 or run in Android shipping code.

`android-cook.yml` now implements that experiment: recursive inventory, exact
owner-private scene restore/checksum, unchanged installed Linux editor reuse,
selective constructor overrides ONLY for actually absent Android host libraries,
`-ForceRulesCompile`, then a real Android_ASTC map cook. Working ASTC/ETC2 formats
are not rebuilt. The workflow requires an actual cooked CanalDistrict.umap and
retains outputs privately; it does not produce or advertise an APK. Its result
is pending — writing the workflow is not proof that the backend/cook succeeds.
