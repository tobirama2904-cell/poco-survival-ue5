# Persistent encounters — implementation under remote verification

Save format 3 retains each authored infected actor's map-scoped ID, location,
orientation, health (including death) and stamina. It also retains the player's
view rotation so loading does not silently turn the camera away from the saved
view. Versions 1/2 remain accepted. Newest saves with malformed/duplicate enemy
snapshots are rejected in favour of the older valid slot.

Enemy threat/alertness restarts on load; it is not simulated while the game is
closed. Combat corpses remain actors and are restorable. Streaming/despawned
actors and enemies destroyed by leaving the world require a later tombstone
registry; this implementation does not claim to solve those cases.

The scene author assigns stable IDs. The editor integration checks actual
serialization, dead/damaged restore and invalid-newest-slot recovery. Its remote
result is pending until the job completes. This branch is intentionally separate
from the APK packaging baseline, which must not silently use an older native
library after public C++ layouts change.
