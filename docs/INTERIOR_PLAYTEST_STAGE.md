# Interior integration / traversal verification stage

Branch gameplay/interior-playtest is separate from the active gameplay/delivery-review Android candidate. It inherits the nine verified CC0 props and city-room dressing from gameplay/interior-art / c513155; that existing asset work is not presented as newly authored here.

## Work in this stage
- Integrated the prepared room-dressing/foundation changes with the current source and delivery tooling without changing the active Android branch.
- Re-fetched the immutable interior-art-001 archive and verified all nine model checksums.
- Rendered and opened a fresh offline material/scale review: desk, medical kit/tape, cassette player, wheelchair, bed frame, bookcase, school desks and chairs. The image is explicitly NOT an Unreal game frame. Wheelchair/bed remain static props, not ride/sit mechanics.
- Six actual level probe anchors record the first six room centres/bounds. The upcoming runtime test traces their unobstructed central floors at the authored 30 cm height.
- A new runtime sequence starts the hero OUTSIDE the first room, invokes the real door interaction with its reach/occlusion checks, verifies the door's 90-degree rotation, sends ordinary W input and requires the hero to finish inside the room, grounded, after 250–1200 cm of movement. No teleport into the room or jump input is used.
- A sixth real screenshot is required. All previous forest, melee, companion support and movement gates remain mandatory. The 35-minute software-render limit is unchanged.
- Six existing non-story cache IDs move indoors without new rewards or cleared loot bits; main-story/Bow/clinic/dam supplies stay unchanged.

## Scope and evidence
The generator currently describes 57 rooms / 513 prop placements. The new test is one physical entry and six floor probes, NOT a claim that all 57 rooms have been walked through. Desktop movement, new UI/image quality, prop collision and performance must still be executed in Unreal. Portable/source tests are not that result. The current game's overall graphics, animation, duration and physical POCO acceptance remain separate work.

The prepared foundation change is 40 cm above the street rather than the old 70 cm ledge. Its ability to be walked over is specifically tested rather than assumed. The cot/desk props are scanned assets; no final art approval is implied.

Local checks: all fourteen portable ASan/UBSan suites passed. 110 Python checks: 104 passed and 6 absent-cache checks skipped. These do not compile the new Unreal game-mode probe.

UE room-entry/six-frame run **36246314267** dispatched at source 559df2f. The packaging-tool lazy-Pillow-import correction was cherry-picked independently; it does not change the room geometry or C++ probe in that run. No room traversal result is claimed before its native execution.
