# Integrated candidate review and actual Android input/save evidence

## Candidate consolidation
The workspace began at woodland-art, whose run 36209094563 timed out at 35 minutes. Its single courtyard image was opened; materials did not report compilation failure, initial/county movement passed, later required images did not arrive. Native ARM64 36209095776 succeeded separately. That is not a valid finished-game/render pass.

A compact alternative canopy was authored and preserved independently in gameplay/foliage-performance / canopy-bough-source-001: 2672 triangles, 588 cards, a baked photograph-derived branch atlas and a minimal masked shader. Its labelled offline render was opened; no UE/FPS result is claimed for it. Existing county-art-004 was discovered and was NOT overwritten.

The newer remote gameplay/forest-lod branch already combines near/mid/far forest cells and the previously authored CMU-derived melee work. This review branch adopts that candidate at f326893 (native/render source 495ba22f), rather than packaging the older alternative without those features. Their runtime verification remains assigned to 36236371819 and 36236372900. No authored-feature credit is claimed here for the inherited LOD or mocap work.

## New verification behavior
- A SHA256-pinned MIT uesave 0.7.1 reader is used only by CI, never included in the APK.
- A native UObject fixture with known nondefault values and a separate save8-default fixture are exported for checking the real GVAS decoder. Synthetic setup is explicit; these fixtures do NOT establish gameplay/touch correctness.
- Android test opens the real backpack through touch and requires OCR of its title before attempting Save. It closes the backpack before moving.
- It searches app-owned internal, external and legacy project save locations, records failures and preserves actual GVAS bytes plus decoded JSON. No arbitrary byte scanning is used to guess positions.
- Before a touchscreen joystick gesture, after it, and after force-stop/relaunch, the probe requires a newly generated save with an increased save generation.
- Movement requires an actual saved XY displacement of 50–2000 cm with limited vertical change. Restore compares player position, field inventory, doors/caches and supported story progression, not every actor/world field.
- Full-world save equality and physical-device performance remain explicitly false. Missing files, unsupported schema, failed menu confirmation, unchanged/stale saves or differing restored state fail the new interaction gate; injected input alone is not success.

83 local Python tests pass (one unavailable authoring-cache test skipped). They include schematic JSON tests, NOT an actual Android or native-binary decoder result. Native fixture, Android UI, real save accessibility/decoding and touch/restore proofs still require their respective jobs. Actual parser results may reveal schema/default differences that must be fixed rather than assumed away.

## New actual five-frame result and measured melee failure
Integrated run 36236371819 finished rendering all five images with exit 0. Opened the rural image and the melee image. Forest tier counts were 7 near / 8 middle / 100 far / 702 hidden; movement, six floor probes, companion following/camera and bandage assistance passed. The grove is visibly present. This is not photoreal-final approval or a physical FPS result.

The overall gate correctly FAILED: the combined human-action-pose flag was false, despite a visible extended-arm pose and passing duplicate-input, single-impact, single-damage and recovery checks. The old compound flag did not identify which condition failed.

Correction now samples loaded clips, actual animation reference and resolved hand at the gameplay impact event, and requests its screenshot there, rather than using a separate 0.38-second timer. Reports retain separate component flags; all remain required. Right-hand resolution additionally handles sanitized/namespaced bone names without accepting left hands or finger bones. The original Unreal API was inspected under authorized access: DoesSocketExist already includes bones, so that was NOT asserted as the root cause.

13 portable sanitizer suites and 86 Python tests passed (one unavailable authoring-input check skipped). New UE pose evidence, decoder-fixture result and current Android touch/save results remain unverified until the jobs complete.

Corrected combined source 024581537dbdf1b64682c2fc34b78b4fd1cc8f22: UE scene 36239195212 and ARM64 native 36239196341 dispatched. Previous native 36236372900 was preserved to finish its compilation/checkpoint, not cancelled. The decoder-fixture probe is 36238611053. No corrected pose/Android interaction result is claimed before completion.

## Measured save-default omission
Native reader probe 36238611053 exported and decoded both real GVAS fixtures, then failed the strict checker: UE omitted default-valued properties, including FormatVersion. The actual nondefault version-7 fixture decoded correctly. Canonical reading now applies only the pinned producer's known optional defaults while still requiring explicit player/map/generation/inventory data. Both original binary fixtures were re-decoded locally with the pinned reader and matched their known values. This is actual native serialization evidence, not Android touch evidence.

This also exposed a production migration hazard: a class default equal to the current save version is omitted by UE. The class now defaults to sentinel 0, normal SaveProgress explicitly writes 8, and an omitted old marker is resolved to a compatible legacy layout from field-inventory shape/save generation. This does not claim to recover the exact old producer version. Malformed shapes and unsupported explicit versions remain rejected. New native migration tests were added; their execution on the corrected source is still required.

Latest source f53e298 includes the save-version correction. Its native UObject/migration/decoder probe is **36239479663**; matching ARM64 native build is **36239480748**. Pending older native 36239196341 was cancelled before compilation. The useful pose-render run **36239195212** is retained at 0245815; it does not itself verify the later save-version change. Any final cook must rebuild/verify the current source before packaging. All fourteen portable sanitizer suites and 87 Python tests pass (one missing authoring-cache case skipped).
