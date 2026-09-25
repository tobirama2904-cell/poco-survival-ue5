# Content stage: The Uncounted / Те, кого не записали

The user's full specification remains the target. This stage adds playable-source content, not a claim of a completed 12–24 hour campaign or final photoreal art.

## Implemented in source
Six original interconnected rural episodes, using the existing six clearings:
1. The Last Bus — Red Cedar: passenger names and the danger of public disclosure.
2. A Road Without an Address — ranger station: an escape route versus residents' privacy.
3. Someone Else's Watch — lookout: a late relief shift and a risky signal for boats.
4. A Debt in Seeds — orchard: opening a shared reserve versus protecting it for winter.
5. Room Nine — roadhouse: Owen's family, guest records and public shelter.
6. An Open Frequency — relay: Daniel's unedited order and who receives it.

Each has four authored dialogue blocks (read, repair, public outcome, private outcome), six lines each: **144 new Russian + 144 English lines**, 24 blocks. Existing main story retains its 98 lines and 18 scenes; the written Low Water plus county corpus now has 242 lines per language. Legacy secondary-character content remains separate.

Native integration:
- 24 physical interaction objects (new radio, evidence folder and switch meshes), 6 signal lights and 12 persistent local encounters.
- Transactional repair costs: one wood and one scrap. Failed repairs do not consume either resource.
- Public choice enables the site's light and sends a hearing stimulus to nearby infected. Private choice stays dark and grants one bandage, subject to inventory capacity. Those are the actual implemented consequences; the dialogues' future intentions are NOT a claim of simulated caravans, NPC travel or a faction economy.
- Irreversible outcomes, safe replay without duplicate rewards, partial-progress restoration.
- Save format 7; six county states; legacy version 6 migration; malformed latest slot fallback.
- Optional county-dependent epilogue line, localized choices, interruptible radio dialogue rather than a new mission checklist.

The episodes deliberately use one shared interaction structure. More diverse encounter design, NPC performances, animation, final props and film-like staging are still outstanding. No measured gameplay duration is assigned.

## New recorded speech
- 144 individual Russian PCM clips, four previously selected cast voices.
- **545.091208 seconds (9 minutes 5 seconds)** of new recorded material, including alternative branches; not campaign duration.
- Six generated source recordings; ASR word timing and splitting produced 144 clips with zero flagged lexical-alignment issues.
- Immutable public release `county-dialogue-001`, pinned archive and per-clip SHA256, successful independent restore.
- English subtitles only for this addition. In-game playback, delivery and final mixing are not yet verified.
- WAVs fetched into BuildData/countyvoices by the scene worker; they are not duplicated in git/the capped workspace snapshot.

## Tests actually executed
- Seven portable ASan/UBSan suites passed, including all 64 county-choice combinations, invalid inputs, no reward farming, irreversible outcomes and transactional capacity/cost failures.
- 44 Python tests passed (one cached nature-pack check skipped when its excluded cache is absent).
- Three generated GLB props inspected in an explicitly labelled software asset-geometry render. Not an Unreal game frame or final-quality approval.
- New UE integration test code exercises UObject version-7 save/replay/fallback and legacy migration, but execution on the new source must still be recorded.

## Animation sourcing
Verified source downloads for CMU subject 13 trials 17/18 (boxing), plus ASF skeleton. URL/digests and attribution in BuildData/characters/cmu-boxing.lock.json. The publisher permits use inside commercial products, but not direct resale of the motion dataset. These are SOURCE motions, not already retargeted combat animation. Reference: https://mocap.cs.cmu.edu/ . HTTPS on the archive endpoint did not validate its certificate chain; public data files were fetched over the publisher's HTTP endpoint, format checked and pinned by SHA256, never executed.

## Delivery isolation
The existing Android candidate stays on gameplay/low-water, native 36133757073 (2c09ef3). The first material repair/cook 36137142659 correctly failed its new gate because County materials are instances whose shader parents live outside /Game/County. Sky repair and both movement checks passed; the remaining material fallback was not ignored. Branch gameplay/low-water commit 8f6a3a3 follows actual material parents and removes the purple runtime sky tint; repair/cook 36140764253 was dispatched without changing native C++.

New story/gameplay/save changes live on **gameplay/county-stories**, so they do not silently invalidate that candidate's source compatibility or pretend to be in its APK.
