# Human characters and combat implementation checkpoint

## Source and licensing
Microsoft Rocketbox, pinned commit `0943055db6ec570bcef9f2c8b41c9e5467c808f9`, MIT, copyright Microsoft 2020. License: `BuildData/characters/LICENSE-Rocketbox.txt`. The download manifest pins every source file by SHA-256. These are licensed third-party character foundations, **not original bespoke final character sculpts**.

Five roles (Arsen, Leyla, Nargis, Ilyas, infected municipal worker), 6,740–10,260 triangles each, 80 bones, relinked and reduced 1k textures. Five animation clips per role: idle, walk, run, crouch, talk. Direct animation-curve copying visibly left arms in A-pose; replaced with world-space rotation rebaking in Blender, then inspected the corrected walking render. This is an **asset render, not UE/device verification**. Native UE imports/runtime selection and three placed story NPCs are implemented; their external integration gate is pending. Blended locomotion, attack/death poses, unique final character designs and cinematic facial performance remain unfinished.

## Implemented gameplay
- Pistol pickup, eight-round magazine, timed reload and finite earned ammunition.
- Pipe pickup increases melee damage; firearm selection and touch controls.
- Hitscan checks both camera aim and muzzle obstruction; loud shots alert nearby infected.
- Physically thrown bottles break on collision and attract unalerted infected. Visible targets take priority over distraction.
- Original 3D pistol/pipe/bottle props and original synthesized shot/glass/footstep effects. These are new asset implementations, not a claim of final audiovisual quality.
- Six additional optional pickups bring the authored city definition to 61 actions/sites.
- Save version 4 records ammunition spent, loaded rounds, used bottles and selection. Replay-derived loot grants validate these values. Versions 1–3 remain accepted.
- Sanitized portable tests cover reload cancellation, exhaustion, invalid snapshots, finite resources and 30/60-Hz behavior. Native behavior still requires external UE/Android tests.

## Actual previous gate result
`36083383766`: expanded city's ARM64 native build succeeded.
`36083382140`: failed overall. Native save integration had 55 objectives and a real captured frame proved grounded input-driven walking, but art inspection rejected the heavily overexposed scene. City creation saved 57 buildings/1,852 instances; expected missing-material probes logged errors, and a retry crashed when deleting rooted material expressions. Import scripts now test existence and reuse materials without destructive graph deletion. Matching-header include ordering was also corrected. Stale success reports are removed before rebuilding. The new gate must pass independently.

## Voice scope
Five voices were selected through audition. All 109 currently authored lines now have matching mono 24kHz PCM files (474.623 seconds including repeated-use lines). Seven batch sources were timestamp-aligned with speech recognition; repeated item-use lines share recordings, and two ambiguous lines were re-recorded separately rather than accepting uncertain cuts. Raw source audio, the voice plan, fixed ASR model revision, alignment report and per-file SHA-256s are retained. Audio format, length, non-silence and clipping checks passed. This is coverage of the **current written dialogue**, not proof of a multi-hour campaign or verified Android playback.

External run 36114117078 compiled the native character/combat code, imported all five skinned meshes with five clips each, rebuilt the city, and passed prop/sound import after a measured nested-path repair. The actual human-in-game rendering gate remains pending until its report and frame are inspected. Android native run 36114118993 is separate.

## Important visual rejection after a green process gate
Run `36114117078` finished successfully at the workflow level, including real input-driven walking (387.72 cm), but its actual screenshot **does not show the player mesh**. `human_avatar_loaded=true` was only an object-load check and did not prove visible geometry. Automatic APK chaining was stopped before dispatch. The frame is retained as `docs/verification/2026-09-25-invisible-human-rejected.png`.

The exported skeleton root had a `.01` object scale. The new `character-source-002` derivative bakes location/rotation/scale before animation retargeting; GLB inspection confirms an identity root, and the Blender walking pose remains valid. This is a corrective hypothesis, **not yet proof of a visible in-game avatar**. Added UE import bounds checks and a fixed-view tan-clothing image regression alarm. The image alarm is deliberately narrow and does not replace visual review or hardware testing.
