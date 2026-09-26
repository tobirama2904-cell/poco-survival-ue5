# Melee motion stage

Branch gameplay/melee-motion, based on woodland-art. Source work and verified exported assets; new Unreal gameplay evidence is still required.

## New art and motion
- Actual public CMU subject 13 trial 17 body motion, source frames 201–297 at 120 Hz. A measured forward right-arm extension selected the source interval, rather than assigning an arbitrary pose to an attack label.
- Own ASF/AMC reader and world-rotation retargeting to the existing Rocketbox bind skeletons. No other retargeting code copied into the project.
- 0.8-second standing/crouched strike clips for Daniel's body proxy and the infected proxy, with a normalized impact at 0.30 seconds. Idle/crouch edge poses are blended into the clips. Wrists stabilized and fingers closed through authored anatomical rotations; the finger motion is NOT claimed as captured CMU finger performance.
- Crouch loops grounded for all five character bodies. Reimported exported files were checked in Blender at multiple sample times; maximum sampled sole-height error was under 0.000002 m in asset space. This is not a live-game foot-contact result.
- Bind matrices and existing Idle/Walk/Run/Crouch/Talk durations compared against immutable source 002 and preserved within test tolerances. Non-skinned Blender bone-display helpers were excluded; an initial infected-foot calculation wrongly selected a helper sphere and was corrected before publication.
- Actual Daniel contact sheet and an exported/reimported infected strike image were opened. These are offline animation renders, not Unreal frames. Character clothing/infected art and general animation quality remain provisional.
- Published immutable character-source-003: five conditioned GLBs and attribution/metadata. Rocketbox character art is MIT; CMU permits inclusion in products but not direct resale of motion data, including converted data. Relevant terms/credits accompany the sources. This release is not an APK.

## Native behavior implemented
- Shared melee clock drives both the one-shot pose and one impact event. No detached hit timer that can fire after a cancelled attack.
- Action overrides locomotion temporarily, refuses duplicate input, plants movement, prevents weapon/reload switching during the strike, and returns to locomotion afterwards.
- Death, incoming damage, falling, stance changes, control editing, backpack use and load cancel the transient action. Enemy attacks also cancel for player cinematics instead of resuming an old delayed hit afterwards.
- Damage sweep uses the actual right-hand bone when available, with a bounded fallback. Hand-bone naming accepts both spaces and underscores. Held weapons are not displayed at a fake root attachment when no valid hand exists.
- Crouched collision half-height adjusted to 60 cm; the previously adaptive companion probes remain compatible. Assistance cannot finish while the patient performs a melee attack.
- New clip import retains vertical skeletal offsets and compensates any imported leading-frame duration. This is not a full animation blueprint/blend-space implementation, ragdoll system, final weapon-specific strikes or precise skeletal hurt boxes. The same short strike is still reused with the existing pipe; bespoke melee-weapon choreography remains to implement.

## Checks
- Eleven portable ASan/UBSan suites pass, including one impact at 15/30/60/120 Hz, rapid duplicate input, cancellation and a bounded large frame delta.
- 74 Python tests passed with local authoring inputs present. Shader/material/previous traversal requirements were retained; required images increased from four to five.
- New native diagnostic spawns a clearly identified temporary target, invokes attack twice, checks one stamina debit and one 25-point hit, requests an actual action-pose screenshot and requires recovery to locomotion. State setup is diagnostic, not a claimed campaign playthrough or touchscreen test.
- New Unreal actor compile/import, this fifth frame, physical interaction and matching Android/POCO behavior are not yet verified.

## Reproduction
`tools/characters/rebuild_melee.sh` fetches immutable character source 002 and hash-pinned CMU data, then authors source GLBs. `verify_melee_assets.py` checks the exported files, not just the pre-export Blender scene. Pinned production source 003 is fetched by the normal scene pipeline.

## Useful verified discovery for future facial work
The conditioned Rocketbox rig retains facial bones including jaw, lips, cheeks, brows and eyelids. Their presence is verified from the actual imported rig; lip sync and facial acting have NOT been implemented in this stage.
