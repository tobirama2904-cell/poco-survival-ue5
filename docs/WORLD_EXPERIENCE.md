# World experience — implementation checkpoint, not completion

2026-09-25. Target: original UE5 Android game for POCO F4.

## Corrected character review
Run **36117717433**, source **551375c**, passed native/import/render gates.
Actual PNG opened and reviewed: player now visibly rendered; movement **523.72 cm**,
grounded, camera -10 degrees. Arsen imported bounds **189.82 cm**. This resolves
the measured invisible-body regression of run 36114117078. Scene is still dark,
sparse and below final quality. Software Vulkan does not establish phone performance.

## New source, requires separate UE/Android verification
- Fourteen shared normalized controls; renderer and input use identical aspect-aware
  hitboxes. F10/settings opens a drag editor; sensitivity, scale, opacity, mirror,
  invert-Y, two candidate quality levels, reset and config persistence. Left stick
  relocates on apply/viewport change. Player damage, movement and AI attacks blocked
  while editing. No claim of comfortable physical touch testing yet.
- Persistent time (17:00 arrival, 1 real hour/day) and seeded continuous weather;
  movable sunlight/skylight, parameterized sky, fog, local capped rain, shelter check,
  original procedural rain sound, city-material wetness and non-shadowing flashlight.
  Maximum 64/128 local rain instances; nominal 30fps cap, **not measured 30fps**.
- Save format 5 validates time/seed, recovers older valid slot from corrupt newest,
  and migrates version 4 to arrival time. Native smoke assertions added, not yet run.
- Radio at depot and brother's radio can trigger on proximity without movement lock;
  doctor/guard face-to-face scenes require grounded stationary player, line of sight,
  no nearby living infected, and validated narrative prerequisites. Voice-end advances
  all scenes; manual advance removes old delegate before stopping audio.
- A chapter/intention overlay supplements existing notes. **This is NOT a finished
  continuous campaign**: existing event graph and most interactions remain; renaming
  notes is not treated as narrative completion.

## Verified locally
ASan/UBSan strict C++ core, vitals, city, combat and experience tests pass. Experience
covers malformed settings math, aspect ratios, hitboxes, 30/60Hz climate equivalence,
pause/restore, 90 days of seeded weather and transition continuity. 21 Python tests
pass; Python compilation and generated story synchronization pass.

## Still missing
Huge dense world, finished region/interior art, authored multi-hour pacing/events,
full animation blending/combat cinematics, bow, measured native control feel,
render review of new environment, current APK and physical POCO performance.
Neither this checkpoint nor old private engineering APK is the requested final game.
