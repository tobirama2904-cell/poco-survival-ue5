# Forest distance rendering + integrated melee candidate

## Why this stage changed direction
Woodland run 36209094563 genuinely failed its strict render gate: exit 124 after 35 minutes, one courtyard image, no completed companion/support images. Walking and six county collision probes passed. No material compile failures were reported; the log stalled after the forest transition and recorded PSO creation hitches. That is NOT proof of a particular POCO frame rate or a proven single root cause.

Android native source 36209095776 / bcfe15af succeeded. It does not include the new runtime forest-cell code or subsequently integrated melee code, so it must not be packaged as this new candidate.

A separately published project branch gameplay/forest-lods and county-art-004 was discovered during work. Its UE attempt 36231686378 failed because StaticMeshEditorSubsystem was None in the commandlet. That branch/release was preserved. This variant avoids that unavailable subsystem rather than labelling its construction failure a successful LOD test.

## New forest implementation
- Original high tree retained at 9,728 triangles.
- Authored branch-card middle tree: 2,084 triangles. An initially sparse version was visually rejected and rebuilt with denser baked branches and matching procedural branch directions.
- Far tree: eight triangles / four crossed albedo cutouts. Scene lighting is not baked; this is intentionally a distant representation, not close-up photogrammetry.
- Shared 2048×2048 power-of-two atlas. Original 205×412 needle crop is no longer the standalone runtime cutout texture.
- 2,256 pines grouped into 817 cells, each 64 m wide. Near/middle/far/hidden decisions use cell-centre distances of 90/180/470 m with 6 m hysteresis. This is **cell-level switching**, not smooth per-instance native LOD blending. Visible transitions still require actual review.
- Runtime swaps only the visual mesh. Static trunk collision remains independent. Far cells explicitly stop rendering; only the detailed tier casts dynamic shadows. Invalid/failed swaps fail the render-health gate.
- Compact masked, two-sided Default Lit foliage graph and one shared atlas/material, rather than the general glTF material graph for each leaf tier.
- Directional dynamic-shadow range reduced from 60 to 40 m. Terrain, total population (7,190 instances), placements and story paths are not removed to fake a successful test.

The geometry-only estimate at the ranger test point falls from 3,083,776 potential pine triangles to 1,136,260 before frustum/occlusion. This is not measured FPS. Core range/hysteresis tests cover 120,000 distance steps. New native forest-runtime evidence must show all four tiers in actual play; the timeout remains 35 minutes.

## Motion work integrated, not falsely re-authored
Fetched and merged the existing gameplay/melee-motion branch. It supplies the CMU-derived standing/crouched strike clips, grounded crouch loops, shared impact/animation timing, cancellation and hand-based sweep. Its earlier scene 36211414652 had also failed at the old forest-render stage, not at native compilation.

Re-fetched immutable character-source-003 and reran the actual exported-asset Blender validation locally: five bodies' sampled foot contacts pass, including standing/crouched strikes on Daniel's proxy and the infected proxy. Opened the resulting infected-impact image. This is offline asset evidence, not an Unreal attack result or final character art.

Merged guards preserve **five required game images**, melee timing/impact/recovery proof, forest-tier proof, companion following/aid, physical movement/collision checks and shader failure rejection. No prior test was removed to obtain green status.

## Verification and assets
- 12 portable ASan/UBSan suites passed, including the imported melee suite and new scenery-distance suite.
- 78 Python tests: 76 pass, 2 cached-authoring-input checks skipped.
- New immutable source-art release **forest-cell-art-001**, separate from the existing county-art-004; 18 files, 36,190,716 bytes, SHA256 ee45bd01d656c300dc41f46c33ca10053df9a938fc556667cadfdd7c8c2f3b68. Independent restore passed.
- Rebuild from pinned county-base-003 using bake_pine_lod.py → pack_pine_lod_atlas.py → author_pine_lods.py. No paid services or engine assets are in the public art archive.
- Actual new UE rendering, shader cost, melee impacts, mobile cook/installation and POCO performance remain unverified. Combat art/wardrobe, weapon-specific choreography, ragdolls and full tactical AI are still separate work.
