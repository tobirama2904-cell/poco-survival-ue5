# Low Water / Низкая вода — source implementation, not final-game acceptance

## Changed creative direction (user request)
Original story in fictional Bellwether County, Oregon. American leads: Daniel Reed
(41), Mara Ellis (34), Ruth Bennett (58), Owen Hart (49). No copied TLOU plot,
characters, music or art. Story concerns an evacuation decision, unregistered
families, a floodgate and responsibility; not an immune-child escort/cure story.
18 authored scene entries, 98 subtitle lines in Russian and English. This is
**not evidence of 12–28 hours**. Existing 109 Russian clips remain an optional
lower-quarter line; body assets are still licensed, explicitly provisional proxies.
New Russian performances use the previously selected voice actors, not the old clips.

## Implemented in source; new UE/Android verification required
- Bow draw/release with finite arrows, physical projectile sweep/gravity and point
  damage. Original bow/arrow models; no claim of finished drawing/reload animation.
- Player torso/head/arm/leg hit classification; bleeding, limp, impaired shooting,
  consumable bandages and splints. Zone selection falls back to capsule impact
  position when a bone hit is unavailable: **not detailed skeletal hitboxes**.
- Transactional finite loot/craft and 24 persistent containers; three recipes,
  inventory panel, healing, saved doors. No infinite resource generation.
- Ground-floor building shells and furnishings replace inaccessible solid bases;
  up to 24 smoothly opening doors. Four CC0 PBR surfaces, 12 verified 1k maps.
  **Map remains 640 m across, not a completed enormous world.**
- Three infected parameter profiles (walker/runner/listener), 14-second last-known
  search, nearby alerts and runner lateral approach. Local steering, **not validated
  navigation-mesh tactics or new finished infected models**.
- Native film triggers, dialogue timing/audio advancement, collision-aware camera,
  physical gate choice, persistent ending, flooded traversal zone versus sacrificed
  ferry supplies; free roam after story. Basic blocking, **not final cinematography**.
- Four original 32-second synthesized score cues, threat/stealth/dialogue mixing,
  quiet intervals; explicitly spatialized footsteps/gunshot/bow. Not a live score.
- Save version 6 for player trauma, supplies, opened doors and film state. Prior
  format 5 remains supported; malformed newest saves are rejected.

## Tests and acceptance
Portable ASan/UBSan core/vitals/city/combat/climate/field tests passed. 24 Python
integrity/schema/source tests passed before the new voice-alignment gate.
Actual UE run 36120680424 verified the **previous** controls/climate code including
native clock saves, but its PNG was reviewed as too dark. New source adjusts
lighting; this must be rendered again, not assumed fixed.

Final cast art, facial/lip/weapon animation, companion/pet AI, animals, vehicles,
large streaming world, cinematic polish, full UI localization, English voiceover,
co-op, hardware profiling and finished consumer APK are not delivered here.

97 new Russian clips: 345.715 seconds. Six original batches, four direct
short-line replacements after ASR flags; provenance retained. Exact coverage,
PCM format and hashes tested. Original source audio retained in public release
`low-water-voice-source-001` (NOT an APK); no in-game playback claim.
