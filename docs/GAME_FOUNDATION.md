# Game foundation — source only

## Precisely what exists

`PocoSurvival.uproject` declares the native module. The same portable domain C++
is consumed by the Unreal GameInstance and compiled independently by the core CI.
The UE engine is not installed: **UHT, UBT, GameInstance, interaction actor and
SaveGame adapters have NOT been engine-compiled or executed**. There is no map,
character, controller, combat, touch UI, animation, audio, cutscene or APK yet.
The art Release is still a separate, unimported resource collection.

Implemented and native-tested domain logic:
- Author-defined inventory quantities, gram-based carry capacity and stack limits.
- Atomic quest transactions: a failure changes neither items nor world facts.
- One-time rewards; prerequisites; mutually exclusive persistent choices.
- Four free-order discoveries across five **logical district IDs**, not built maps.
- Eleven authored actions and two independent decisions with four terminal variants.
- An ordered event journal; validated replay rejects duplicate or out-of-order actions,
  unknown items, inconsistent flags, modified counters and unsupported save versions.
- Exhaustive traversal of 40 reachable fact states; no non-ending dead-end in this
  limited graph. This does not prove a future physical level is navigable or fun.
- 16,000 deterministic randomized action attempts with rollback/replay checks.

Unreal integration source, awaiting real engine verification:
- Blueprint-accessible objectives, inventory and world flags.
- A quest-prop actor with range and line-of-sight checks; no per-frame tick.
- Two alternating save slots. Loading selects the newest replay-valid slot.
  Actual disk interruption, Android storage and recovery tests are pending.

## Original dramatic premise (working outline, not a finished script)

Working title: **«Нулевая отметка»**. A fictional reservoir city has lost power
and safe transport after an infection outbreak. The protagonist is a municipal
water-network technician, not an immune saviour. Repairs reconnect districts but
also change where survivors and infected can move.

The opening dilemma is operational, not a dialogue-only switch: route the single
working generator to the clinic or to the pumping station. Clinic power requires
recovering a manual valve handle to restore water; pump power restores water
sooner but leaves the clinic without this supply. After water returns, the relay
can connect the neighbourhoods or transmit an evacuation beacon. Both decisions
are recorded in persistent facts and survive journal replay.

This describes intended consequences, not populated survivor scenes. No deaths,
NPC schedules, changed navigation, sound performances or cinematic shots are
claimed to exist yet. The current graph is an internal correctness fixture, not
an offered replacement for the requested several-hour campaign.

## Quality and performance gates

Before growing the campaign: install an authorized UE distribution; select and
pin the engine minor version and matching Android toolchain; import the actual
art; author representative interior/exterior spaces; integrate a properly rigged
character and locomotion; build touch controls, combat, stealth and a directed
scene; then package and measure on POCO F4. Every visual build needs inspected
captures, and every device performance claim needs recorded measurements.

The initial config deliberately avoids desktop Lumen, Nanite, virtual shadow maps
and motion blur. This is a candidate mobile-forward configuration, **not** an
optimal device profile. Texture memory, streaming, CPU/GPU frame times, thermal
behaviour and sustained FPS have not been measured. No ideal optimization claim.
