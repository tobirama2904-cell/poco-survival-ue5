# POCO Survival — Unreal Engine 5

Original Android survival-game development for POCO F4. **This repository is not a finished game and currently has no playable APK.**

## Verified status

- GitHub connection and repository administration: confirmed.
- This repository is public; existing private repositories were not made public.
- Source engine access: the authenticated EpicGames/UnrealEngine endpoint returned 404. No pending Epic invitation was found. Access must be granted by linking the owner's Epic and GitHub accounts.
- Engine installation, Unreal import, Android packaging and POCO F4 performance: **not yet verified**.
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

`content/assets.lock.json` pins asset URLs, sizes, author credits and MD5 values supplied by Poly Haven. The pipeline verifies every download, validates glTF dependencies/geometry, creates separate mobile mesh/texture candidates in Blender, produces four clearly labelled studio previews, and packages source art with SHA-256 manifests.

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
The official precompiled Linux UE page was also checked and redirects to
“Epic Account Required”; no Epic login or UE installation is claimed.
