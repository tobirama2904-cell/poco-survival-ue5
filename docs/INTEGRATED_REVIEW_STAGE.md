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
