# Companion support stage — source implementation

Branch gameplay/companion-support, based on the continuous journey branch. The full requested game scope remains unchanged. This stage adds specific support mechanics; it does not claim final animation, tactical combat AI, companion permanent death or a finished game.

## Added
- Backpack companion tab: tell Mara to crouch/wait or resume following; request assisted bandaging. No extra permanent combat-HUD buttons.
- Holding position and map persist in optional save8 fields; corrupt holding positions/maps/early-story states use the existing save-slot fallback. A geometrically unsafe or different-map hold position returns to following rather than placing her inside geometry.
- A held companion does not use the follower's off-screen catch-up teleport. Recall remains available through the companion panel.
- Mara approaches a nearby injured player, crouches near them and requires 2.5 uninterrupted seconds close together, still, with clear line of sight. Total approach budget is 12 seconds.
- Exactly one ordinary player-inventory bandage is consumed only on completion. Bleeding stops, health increases by up to 32; arm/leg injuries are NOT fixed. Ruth's protected quest medical pack is never used.
- Danger, a new hostile hit, death, menus, cinematics, loss of resources, timeout or a loading transition interrupt assistance. Interrupted assistance consumes nothing. Movement/obstruction resets close-contact progress.
- Existing moving dialogue pauses during assistance. Opening the backpack during non-cinematic speech is now permitted, making its existing pause/resume logic reachable.
- Fixed inherited crouched steering probes: a standing-sized capsule at crouched height could intersect the floor and prevent movement. Probe half-height now follows the real capsule; crouched recovery uses its actual half-height.

The treatment is mechanically timed and uses existing locomotion/crouch poses; no new hand-contact/bandaging animation is claimed. Mara and Ruth retain their previously documented narrative damage protection; this is not completed enemy/companion tactics.

## Verification
- Added portable 30/60 Hz medical-state tests: resource use, invalid/dead state, interruption, clear-contact reset, bounded approach, no double-spend, no healing through walls and crouched probe clearance.
- Existing nine portable suites plus the new support suite pass under ASan/UBSan.
- 64 Python tests pass; one missing cached nature-art check is skipped. Old gate assertions were updated for the stricter fourth-frame/support requirement, not weakened.
- Native UObject hold-state roundtrip/corrupt-slot tests added. They remain unexecuted on this new source until the UE run finishes.
- Runtime smoke now requests actual keyboard movement while Mara holds, then actual actor-driven approach and bandaging, a resource/health/bleeding report and a fourth screenshot showing the new panel. Fixture injury/resources/story progress are explicitly diagnostic injection, not a claimed campaign playthrough or touchscreen test.
- The render gate requires companion-support.json passed and four images. Software-render timeout increases to 35 minutes; that is a test timeout, not a device performance claim.

## Remaining checks
New Unreal compilation, actual hold/assist movement and UI image, reload placement, game audio/animation polish, matching Android build and physical POCO performance. Portable tests do not establish these results.
