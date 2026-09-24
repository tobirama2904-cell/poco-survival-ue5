# POCO Survival — Unreal Engine 5

Original Android survival-game development for POCO F4. **This repository is not a finished game and currently has no playable APK.**

## Verified status

- GitHub connection and repository administration: confirmed.
- Separate public repository created; existing private repositories were not made public.
- Source engine access: the authenticated EpicGames/UnrealEngine endpoint returned 404. No pending Epic invitation was found. Access must be granted by linking the owner's Epic and GitHub accounts.
- Engine installation, Unreal import, Android packaging and POCO F4 performance: **not yet verified**.
- A pinned manifest contains 14 genuine CC0 environment assets, about 153 MiB of source data before packaging. These are not placeholder padding.

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
