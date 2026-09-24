# Recover after a chat interruption

This is a developer handoff, not a claim of a finished game or a continuously
running autonomous worker. GitHub holds committed code, completed CI logs and
published art; a chat error is not evidence that these were deleted.

1. Read `docs/STATUS.json`, the latest git commits and Actions status before work.
2. Use `python3 tools/remote_status.py --commit <source-commit>` to check the core
   workflow. Add `--workflow engine` and use `latest_verified_unreal_source_commit`
   to check the actual editor integration. Both modes are read-only and cannot
   accidentally launch a duplicate job.
   Public requests need no credential unless rate-limited; optional authentication
   is through GH_TOKEN or a private --token-file, never a token in command text.
3. Check remote and local commits before any retry. Do not recreate the repository,
   redownload art, reset to the rejected old projects, or create another Codespace
   merely because the chat displayed “Something went wrong”.
4. Local git config and executable file permissions can be missing after workspace
   restoration. Restore repository-local author/remote settings and the private
   credential helper's executable permission before a push. Permission denied on
   the helper is not evidence of a revoked GitHub token.
5. Read the public Release manifests/checksums instead of treating large ZIPs as
   chat attachments. The verified source archive already exceeds 128 MB.
6. Codespaces is optional, allowance-limited and stopped when unused. Do not enable
   paid runners, paid upgrades or automatic unbounded compute. The workshop may
   auto-delete after its short retention period; its definition remains in git.
7. Epic membership and source/registry access are confirmed. The official UE 5.7.4
   editor was installed and compiled this project on an external runner. Check
   the latest engine-probe run before retrying; the remaining engine-platform gap
   is Android support, not Epic authorization. Never publish engine binaries,
   Epic source, tokens or signing keys in this public repo.

## Non-negotiable project scope

UE5; native Android for POCO F4; original infected-city story plus free roaming;
several-hour/full-campaign ambition, not a short test presented as the final game.
Use substantial licensed content, never padding. No silent engine switch. No
physical-device FPS or graphics claims without measurements and inspected builds.
The current small story-state graph is an internal correctness fixture only.

## Android build recovery

Use `--workflow android` with `android_native_build_source_commit` from STATUS to
inspect the active Android run. Do not duplicate it while queued or in progress.
The original slim-image attempt failed at missing GoogleGameSDK source after
successful SDK and binary-dependency installation. The current recipe overlays
matching authorized source. Both real private-cache reuse and native compilation
must be checked from their actual results; a created private repository alone
is not proof that it contains a usable build cache. Public downloads remain art
resources, not a game. The assistant is not an autonomous off-session game author;
the dispatched bounded GitHub build can continue independently of the chat.

## Gameplay scene work (2026-09-24)

- Metadata has moved from lowercase `content/` to **`BuildData/`**. Unreal's
  case-insensitive directory scan crashed when both that folder and the actual
  `Content/` directory existed on Linux. Do not reintroduce that collision.
- Native character, legacy input/touch controller, HUD, movement/vitals, melee,
  a local-steering enemy, short establishing camera and power-restoration lights
  are implemented in source. This is an internal gameplay gate, not final art,
  complete combat, navigation or the requested several-hour campaign.
- `scene-layout-002` is a pinned **scene source**, not an APK. The scene script
  assembles eleven CC0 assets and original geometry. Two Blender layout renders
  were inspected; they are **not Unreal gameplay screenshots**. The yard remains
  too empty/repetitive for final-art acceptance. Manny is temporary licensed art.
- `gameplay-scene.yml` constructs a real map, tests native actors and attempts an
  actual game-mode screenshot using software Vulkan. A headless pass does not
  prove rendering; review PNG and runtime report separately. Physical POCO
  testing remains outstanding.
- Current scene retry: **36024498135**, initial source **e237db0**. It has bounded
  repair windows after failures, with diagnostic artifacts uploaded while the
  runner remains alive. Inspect those artifacts; commit a measured correction
  on main instead of blindly launching another image download. The workflow
  records an effective source if a correction is accepted. No autonomous code
  authoring happens outside the chat.
- First scene attempt **36022292082** downloaded and hash-verified 128 authorized
  character files (54 packs), then failed at the Content/content case collision
  **before UHT/C++ compilation**. Do not call it a successful gameplay build.
- Active Android retry **36021238459**, source **499e2d8**, fixes the observed
  missing Linux-host ISPC binary and Python 3.10 streaming gzip incompatibility.
  The previous source build 36013234761 ended with exit 6 after an 838-action graph
  (last logged index 637); its partial cache was NOT preserved. Wait for actual
  results, not the workflow step label.
