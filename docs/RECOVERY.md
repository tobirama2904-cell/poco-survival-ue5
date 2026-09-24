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
