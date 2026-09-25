# Internal signing continuity

The remote repository was ahead of the restored local workspace. During that
reconciliation, the old unversioned signing-password secret was inadvertently
overwritten before the existing signer was discovered. The original encrypted
keystore remains untouched in private release android-signing-001; its password
is not recoverable from this workspace. This was a tooling mistake, not a planned
rotation or an authentication failure.

Future internal builds use a new explicitly versioned V2 key/password secret pair.
Its certificate is pinned in BuildData/android-signing.public.json. The old
certificate is retained there solely for explicit historical-APK installation
checks. V2 cannot update an installed V1 APK in place; uninstalling V1 would erase
its app data unless backed up. Neither is a finished/public game release. No
claim of signing continuity between those generations is made.

Packaging requires the current certificate; the historical-install workflow
explicitly allows the pinned older internal certificate. Never overwrite a
signing secret from a stale checkout without first inspecting remote state and
the current public certificate pin.
