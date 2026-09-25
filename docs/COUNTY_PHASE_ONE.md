# First work stage — county art, lighting and controls

This is a work stage, not a promise that three chat messages equal a finished AAA production. The user's complete acceptance list remains in force. No final APK is approved.

## Source work in this stage
- Original 2,400 × 2,400 m region recipe; 16 collision terrain tiles; natural perimeter ridges; river and graded timber crossing.
- Six rural clearings with open furnished shelters, named environmental signs and deterministic runtime test anchors. These are NOT six completed side quests.
- 6,188 nature placements including trees, ferns, scanned mossy rocks, stumps and deadwood. HISM draw-distance budgets and simple trunk blockers; FPS not measured.
- CC0 Poly Haven sources verified by publisher digests and pinned SHA256. Geometry conditioned for mobile; the pine is artistically enlarged from a sapling. Rebuilt 900 photographed-atlas leaves to restore broadleaf coverage lost during simplification.
- Authored meshes pre-compensate the actual measured UE glTF (X,-Y,Z) basis. Import checks that basis, disables Nanite and preserves full mobile geometry. Terrain/shelters use complex static collision.
- Photographic cube-map sky replaces uniform-colour dome; rebalanced sun/ambient/exposure. Actual new UE image is still required.
- Compact circular vector controls; hidden save/load outside backpack; shared visible-control/hit-test rules; nonoverlapping default layout tested over four landscape aspect ratios. Prior custom layouts retained; old default layout migrates.
- Less screen-covering HUD; smaller vitals; film subtitle bars instead of a large portrait panel; virtual stick hidden during cinematic/editor/backpack views. Quality settings applied only on changes, not each modal transition.
- Native diagnostic now requests a second real screenshot at the ranger station, six rural collision rays and a second grounded input-walking test. Final render gate requires both original and county tests.

## Evidence available before this change
- Scene 36128450801: actual Low Water C++/save6/map construction/render and walking passed. Opened frame shows visible hero but dark lighting and intrusive old controls; final art rejected.
- Android install 36129949647: OLD 5d6dde86 source installed, launched and relaunched in a translated Android15 emulator. Not this story, not a POCO benchmark, not an approved finished game.
- New models opened in an offline Blender inspection. This is only asset look-development; it is NOT an in-game screenshot.

## Still unfulfilled acceptance (not silently removed)
- Final photoreal urban art, finished protagonists/rigs, action blends, facial/lip animation, cinematic direction and polished interiors.
- Proven continuous multi-hour original American campaign, rich optional narratives, playable consequences/multiple endings, RU/EN presentation and English voices.
- Fully exercised traversal/climbing/cover, broad weapon set and melee, bow/combat animation, skeletal injury hit zones, complete injury/fear/psyche/realism tuning.
- Advanced demonstrated stealth, coordinated enemy variants/bosses, intelligent companions/dog, orders/rescue/relationships/permanent death.
- Living NPC schedules, animals/hunting/migration, factions/reputation/trade, vehicles/repair, bases/electricity/fire/destruction/seasons/events.
- Final adaptive sound/music/diaries/mix, accessibility and complete localized UI.
- Optional co-op/networking/mod support, final optimization, physical POCO F4 testing and finished signed APK delivery.

Subsequent work should improve actual gameplay and story integration, then verify/package matching assets and native code. A green build, asset count, map dimensions or three stages do not independently satisfy these requirements.

## 2026-09-25 follow-up: actual image rejection and repair

Run 36133754596 compiled and built the county, passed 6/6 rural collision rays and 545.77 cm grounded input movement. Both actual images were opened and rejected: `(Node Saturate) Missing Saturate input` broke the photographic sky; missing `bUsedWithInstancedStaticMeshes` flags caused default-material fallback. This is a measured failure, not final art approval.

Source 3ce5365 uses the unnamed Saturate pin with checked connections, a fresh sky-material asset and saved material-usage flags. `render_health.py` now rejects these actual log failures even if movement/pixel checks pass. Android cook 36137142659 reuses private scene 36133754596, repairs it, renders/tests the exact content again, then cooks it; successful matching native 36133757073 is required by downstream packaging. The native C++ and Config remain 2c09ef3-compatible. A mistaken old-source dispatch 36137090619 was cancelled before cooking, after discovering that excluded git configuration/askpass executable permissions had not persisted. Remote identity and push were restored and verified before the corrected dispatch.

3619210 updates Android tests to open the current backpack before Save and collect actual app-owned GVAS files without claiming save-state equality or verified movement merely from injected touches. 38 Python tests pass, with the cached art-pack test skipped when the excluded cache is absent. Corrected render/cook, APK, mobile image and physical-device verification remain separate gates.
