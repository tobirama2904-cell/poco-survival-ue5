# Interior art preparation — separate from the Android candidate

Branch gameplay/interior-art. The ongoing delivery-review candidate is unchanged; these new assets/room changes are not silently included in its APK.

## Actual source/art work
- Nine first-party Poly Haven CC0 assets: medical box/tape, wheelchair, old metal bed frame, worn bookshelf, office desk, school chair/desk and cassette player.
- Publisher MD5 verified on acquisition, then every input pinned by SHA256. All mesh parts retained and joined; metre scale retained; origin moved to floor/XY centre. No global decimation was used to erase thin rails or spokes.
- Nine conditioned GLBs, original PBR textures, full provenance and immutable interior-art-001 archive (15,813,137 bytes). Independent archive restore passed.
- Actual offline Blender material/scale review opened, labelled NOT UNREAL GAMEPLAY. Wheelchair/bed are static props, not implemented ride/sit mechanics.
- Repeatable dressing recipes for existing rooms: medical overflow, classroom and lived-in/storage interiors. Bounding-box tests include rotation, walls and a clear central route, not just prop centre positions.
- Removed overlapping placeholder furnishing cubes from the future generator. Lowered foundation top from 0.6 to 0.3 m; relative to the -0.1 m ground, the step is 0.4 m rather than 0.7 m. This is a source-geometry correction awaiting real traversal, not a claim of tested new interiors.
- Six non-story cache IDs (18–23) are relocated into rooms without adding free resources or resetting their saved loot bits. Bow/clinic/dam-dependent caches and protected main-story items remain unchanged.
- New static props use complex collision when relevant; small tabletop decoration has no collision; 50 m draw-distance limit. Nanite is explicitly disabled. Device performance is unmeasured.

## Limits and verification
The wheelchair has 40,252 triangles and the bed frame 49,990; no claim of final mobile optimization is made. They are locally bounded/cullable set dressing, not global foliage scatter. Texture/material quality, room entry, doors, physics and frame cost still need the actual UE scene and phone checks.

100 Python tests: 94 pass, 6 unavailable-cache cases skipped. New tests cover repeatability, furniture bounds, the foundation source, unchanged loot identity, licensing records and downloaded pack hashes. No new C++/Config/project-descriptor changes were made. No native build was restarted for this art preparation.

The new source branch is intentionally NOT merged into the active Android delivery branch. Run its own scene/room review after the current candidate's installation gates, then decide whether to promote it. A prop count is not a completed campaign, a larger map or final art approval.

The deterministic current city recipe yields 57 rooms and 513 prop placements; these are source-layout counts, not a claim of a completed in-game room review. One foundation slab spans -0.1 to +0.3 m; the old duplicate inner floor was removed to avoid coplanar flicker.
