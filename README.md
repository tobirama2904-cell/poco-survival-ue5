# POCO Survival — Unreal Engine 5

Original Android survival-game development for POCO F4. **This repository is not a finished game and currently has no playable APK.**

## Verified status

- GitHub connection and repository administration: confirmed.
- This repository is public; existing private repositories were not made public.
- Epic invitation accepted; active membership and authenticated engine source / official registry access confirmed (HTTP 200).
- Official UE **5.7.4** installed on an external runner; project UHT/UBT compilation and editor startup verified. Native quest/inventory/choice integration, save/load and recovery from a truncated newest save slot passed inside UE. Art import, Android packaging and POCO F4 performance are **not yet verified**.
- A pinned manifest contains 14 genuine CC0 environment assets, about 153 MiB of source data before packaging. These are not placeholder padding.

## Published and independently downloaded

[Art release artpack-001-3](https://github.com/tobirama2904-cell/poco-survival-ue5/releases/tag/artpack-001-3)
was produced by [successful run 36002462151](https://github.com/tobirama2904-cell/poco-survival-ue5/actions/runs/36002462151).

| Archive | Exact bytes | Verified after downloading from Release |
| --- | ---: | --- |
| Source environment collection | 148,762,599 | SHA-256 and all ZIP CRCs |
| Mobile candidates of the same collection | 82,612,289 | SHA-256 and all ZIP CRCs |

These are two representations of **the same 14-asset collection**, not 231 MB
of unique game content. Four assets were visually inspected in the studio sheet:
textures were visible and there was no obvious missing geometry or pink material.
The other ten received structural checks, not a claimed visual approval.
Candidates still need engine import, final LODs, collision, draw-call and device tests.

![Blender studio renders, not gameplay](docs/verification/2026-09-24-art-preview.jpg)

The actual art runner reported 16,766,414,848 bytes of physical RAM and
91,189,362,688 bytes of free disk at packaging time (about 15.6 and 84.9 GiB).
This demonstrates more capacity than the chat workspace, **not a successful
UE installation** or a guarantee of identical space on every future runner.
Machine-readable reports are under `docs/verification/`.

## Actual first production pipeline

`BuildData/assets.lock.json` pins asset URLs, sizes, author credits and MD5 values supplied by Poly Haven. The pipeline verifies every download, validates glTF dependencies/geometry, creates separate mobile mesh/texture candidates in Blender, produces four clearly labelled studio previews, and packages source art with SHA-256 manifests.

The workflow is **manual only** (`workflow_dispatch`). It performs an actual art build, not a synthetic compute/storage benchmark. Standard Ubuntu runners are selected; no paid runner or external paid service is configured. Releases contain art packages and build reports, **not a game** and **not Unreal Engine binaries/source**.

### Reproduce locally

Requires Python 3, Blender with glTF import/export, and Pillow for the contact sheet.

```sh
python3 -m unittest discover -s tests -v
python3 tools/art_pack.py fetch --work /tmp/poco-art
blender --background --threads 2 --python-exit-code 1 --python tools/condition_assets.py -- /tmp/poco-art
python3 tools/art_pack.py package --work /tmp/poco-art --output artifacts
python3 tools/preview_sheet.py /tmp/poco-art/previews artifacts/art-preview.jpg
```

## Actual Unreal build, not just standalone C++

[Run 36006749716](https://github.com/tobirama2904-cell/poco-survival-ue5/actions/runs/36006749716)
installed the digest-pinned official Epic UE 5.7.4 image, ran UHT, compiled and
linked the game module with UBT, and started UnrealEditor-Cmd. UBT succeeded in
58.21 seconds. The overall run failed afterwards because the integration Python
script used an unavailable API; that call was corrected and
[run 36008146202](https://github.com/tobirama2904-cell/poco-survival-ue5/actions/runs/36008146202)
**completed successfully**: three native classes loaded, eleven objective definitions
were available, native inventory and choices worked, save/load passed, and the
older valid save slot was recovered after truncating the newest slot. This is a
headless integration check, not gameplay footage or a device test.

After runner cleanup, measured free disk was 98.6 GiB; after engine installation
it was still about 50.4 GiB. The official slim image **does not contain Android
target-platform modules or Android runtime binaries**. Installing an SDK alone
will not solve that missing engine-platform component. No APK is claimed.

## Native game source foundation

The repository now includes `PocoSurvival.uproject`, a native runtime module,
portable C++ inventory/quest/world-state logic, and Unreal GameInstance,
interaction and SaveGame adapter source. See [the exact implementation and limits](docs/GAME_FOUNDATION.md).

Run `bash tools/test_core.sh` to compile the portable code with AddressSanitizer
and UndefinedBehaviorSanitizer. A separate, bounded GitHub Actions workflow runs
these tests outside the chat on relevant pushes. **Passing it does not mean the
UE adapter compiles, a level exists, or an Android game has been built.**

## Intended game, not completed features

A third-person infected-city survival game with a story campaign and revisitable districts. Quality goals include grounded movement, stealth, readable combat, environmental interactions and directed cinematics. Twelve hours is a possible full-production target, **not existing content or a promised completion date**. Mobile rendering and real device measurements take precedence over desktop-only feature marketing.

## Rights and privacy

Listed art is CC0; original authors and sources remain in each pack. Redistribution rights for each future character, animation, sound and music asset must be checked independently. Unreal Engine is governed by Epic's EULA and is not republished here. No account tokens, signing keys or personal browser profiles belong in this repository.

## External development environment

`.devcontainer/devcontainer.json` describes a 4-core / 16 GiB resource workshop.
Its bootstrap performs the actual Blender import/export/render integration test.
It does **not** install Unreal Engine or claim to package an Android game.
Codespaces has a finite included allowance and storage accounting; it is not an
unlimited free server. Our provisioned workshop must have a short idle timeout,
be stopped after work, and use a short retention period. No paid upgrade is configured.

Verified on 2026-09-24: authenticated remote SSH, all seven unit tests, and the
Blender CPU-render integration test passed inside the 4-core workshop. It was
stopped after verification. Measured workspace free space was about 27.9 GiB.
The optional workshop has a 5-minute idle timeout and 60-minute stopped retention;
its machine can expire, while the definition, code and published art remain on GitHub.
The website ZIP route requires a separate Epic web login, but the authorized
official GHCR image route now works and has been used for a real editor build.

## Android source build now running externally

[Android native source build 36013234761](https://github.com/tobirama2904-cell/poco-survival-ue5/actions/runs/36013234761)
was launched after an earlier attempt verified the pinned SDK/NDK/JDK and 830
Android dependency files, then stopped on the slim image's missing GoogleGameSDK
module definition. The revised job restores the exact matching authorized source
and additional portable source/header dependencies. Check the live run: the
checkpoint records its observed state, not a promised successful result.

Compiled engine intermediates, if produced, go only into the owner's **private**
engine-cache repository. Public artifacts contain diagnostic JSON/logs only.
The pipeline is bounded to four hours on a standard public runner; no paid
service is configured. The new native-build utility suite has eight locally
passing tests. Real private-cache restore remains unverified until a cache exists.

This job compiles native Android code. **It does not automatically author a game
world or campaign, cook content, sign an APK, or publish a playable game.** Those
parts still have to be implemented and tested; there is no APK download yet.
