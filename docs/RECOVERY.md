# Recover after a chat interruption

This is a developer handoff, not a claim of a finished game or a continuously
running autonomous worker. GitHub holds committed code, completed CI logs and
published art; a chat error is not evidence that these were deleted.

1. Read `docs/STATUS.json`, the latest git commits and Actions status before work.
2. Use `python3 tools/remote_status.py --commit <source-commit>` to check the core
   workflow. It is read-only and cannot accidentally launch a duplicate job.
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
7. Epic account/source access and an actual engine installation remain unresolved.
   No engine binaries, Epic source, tokens or signing keys are in this public repo.

## Non-negotiable project scope

UE5; native Android for POCO F4; original infected-city story plus free roaming;
several-hour/full-campaign ambition, not a short test presented as the final game.
Use substantial licensed content, never padding. No silent engine switch. No
physical-device FPS or graphics claims without measurements and inspected builds.
The current small story-state graph is an internal correctness fixture only.
