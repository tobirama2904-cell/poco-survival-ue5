# Continuous-journey dialogue and story direction

Base adopted from existing remote gameplay/main-campaign 864251e, not rewritten or credited as newly authored here. Its 30 main scenes, moving companions, 194 RU/EN story lines and 96 new main-campaign voice clips are retained. The six county arcs remain optional. Full requested acceptance and the 12–24 hour main-campaign target are unchanged; no new measured duration is claimed.

## New content in this stage
- Twelve situational conversations / 72 original lines per language. Shoes, school lunches, coffee, paint, night, injury, a recipe, the orchard table and shared silence give the central pair warmth and ordinary life, not just accusations and explanations.
- 72 new Russian PCM files, **217.187958 seconds (3 minutes 37 seconds)**, existing selected Mara/Daniel voices. One phrase had uncertain lexical alignment; its text and batch were revised. Final alignment: zero flags. No threshold was lowered. In-game delivery/mixing remains to verify.
- A full original 12-chapter narrative treatment in CAMPAIGN_TREATMENT.md clarifies beginning, development and ending. Chapters 3–12 in that document are story development, NOT ten already implemented levels. It does not reproduce TLOU's characters, immunity, cure, hospital climax or dialogue.

## Native source behavior added
- Eligibility by main-story stage, actual walking/resting, rain/night, injury and river proximity.
- Requires visible, nearby moving Mara; blocks starting during danger, aim, menus, airborne movement, another scene or close to the next main-story trigger.
- Suppresses casual conversation while carrying Ruth's emergency medical pack. An advanced main-story interaction interrupts optional speech without falsely marking it finished. Ordinary loot still does not skip it.
- Injury conversation has priority over jokes. The water remark requires both rest and actual proximity to the authored river.
- Only completion marks a conversation resolved. Interrupted conversations can recur when eligible; no dialogue unlocks a mandatory quest or awards supplies.
- Optional tagged JourneyHeard property extends save8 with default zero; old saves remain readable; invalid masks use existing slot fallback.
- At least 75 seconds of quiet after another conversation. These optional conversations do not automatically trigger emotional/exploration music; combat/stealth cues retain priority.

## Verification
- Nine portable ASan/UBSan suites pass; journey tests cover all 4096 valid history masks, context filters, injury priority, river condition, invalid inputs and repeat completion.
- Native UObject history serialization/fallback test added, not yet executed for this new branch.
- The base main-campaign UE run 36154689044 failed to compile two lines in companion camera proof: auto pointer deduction from TObjectPtr and shadowed PC. Both were fixed in 0450c41 and fast-forwarded separately to gameplay/main-campaign without publishing this stage's unfinished changes there. A corrected base run was dispatched.
- County-story run 36143714242 is verified separately (save7/import/two frames/rural movement); it does not prove these new conversations.
- Existing older low-water Android candidate passed internal install/restart testing, not final art, touch movement/save equality, POCO performance or the newly added story content.

## Reference study
Read the full substantive GameSpot developer interview, including relationship-driven level planning, contrast, companion autonomy and development tradeoffs. Applied general design principles through original material. This is not a claim of personally replaying the entire reference game. Source: https://www.gamespot.com/articles/bonds-forged-in-difficult-times-the-making-of-the-last-of-us/1100-6412499/ .

Final local source checks: 58 Python tests passed, with one absent cached nature-archive check skipped. New audio archive was independently restored and verified against its per-file hashes. Recorded duration is not gameplay duration.

New journey source: d9cc508d0bc98384ebdd0d15d725bb14dbebd245. UE verification run 36160687330 on gameplay/journey-dialogue. Corrected base-main verification run 36160065706 on gameplay/main-campaign / 0450c41. Both dispatched; no new Android build or physical-device result is implied.
