# Forest rendering budget — source revision

## Measured issue
UE run 36209094563 constructed the woodland map and passed the first walking and six rural-floor checks. Its software-Vulkan render timed out (exit 124) with only one screenshot, before companion/support evidence. The gate correctly failed. The retained log reports the needle texture as **BGRA8, 205×412**. This is concrete evidence of a non-power-of-two, uncompressed texture, not proof that this alone caused the entire stall. No POCO FPS is inferred from the software-render timeout.

Actual courtyard frame was opened. It is not a successful woodland/companion verification. Matching Android native source run **36209095776 succeeded**; native success is not packaging or visual acceptance.

## Asset changes
- Pine LOD0: original 9,728 triangles retained near the player.
- Pine LOD1: 3,556 triangles, retaining complete photographed sprigs rather than collapsing all leaf geometry into the trunk; retained sprays enlarged moderately.
- Pine LOD2: two crossed albedo cutouts, four triangles, 512×512 atlas. Scene lighting is not baked. An explicit 1.65 albedo compensation was applied for overlapping planes. This is a distant representation, not a substitute for the close model.
- Needle texture resized to 256×512, allowing ordinary mips and block compression. Actual runtime codec/mip behavior still requires the new UE render/cook.
- Far LOD does not cast dynamic shadows. Directional dynamic-shadow range reduced from 60 m to 40 m; fern culling from 90 m to 65 m. Scene population and collision terrain are retained.
- Real per-mesh LOD copying and screen thresholds [1, .65, .24] via StaticMeshEditorSubsystem. Medium materials reuse the close mesh's material interfaces. Other nature meshes get conservative automatic LODs; broadleaf uses less aggressive reduction than rocks/ferns.
- Masked materials request dithered LOD transitions. Both imported and retained/cooked scene assets must report the actual LOD counts, vertex counts and screen sizes.

## Checks
The full/medium/far models were rendered together and opened as an explicitly labelled offline asset comparison. This is NOT gameplay. The distant model is deliberately viewed enlarged in that comparison and is not approved as final close-up art.

Initial direct PNG inspection showed RGB dilation beyond cutouts because transparent RGB was visible in the viewer; a proper opaque-background composite was separately generated and inspected. Final alpha is retained. No opaque rectangle is intended as the distant tree.

74 local Python tests: 73 pass, one immutable-base-terrain comparison skipped because that separate cached base archive is absent. Tests cover triangle budgets, actual PNG power-of-two dimensions/alpha, LOD import commands, retained-asset revalidation and preservation of the four-frame/support gate. New Unreal API execution, actual visual transitions and phone performance are not yet verified.

Source art: county-art-004, 18 files, 24,965,739 bytes; archive SHA256 3a03c9e707dad1a0577b5d7331d0f8e3294d1e2a32d394fd0d598f47b4eab6b8. Hash-verified independent restoration completed. No engine assets or padding. Reproduction: tools/scene/rebuild_forest_lods.sh from immutable base 003 using Blender 4.3.2.

The renderer keeps its 35-minute limit and four required screenshots plus walking/collision/companion/support checks. A timeout is not reclassified as success. No C++/Config changes require another ARM64 compilation; successful native 36209095776 can be considered only after source compatibility checks and a successful matching visual/cook gate.

API references used: Epic's LOD scripting and StaticMeshEditorSubsystem documentation. Using lower-detail meshes at distance is an engine-supported technique, not a measured FPS promise. https://dev.epicgames.com/documentation/en-us/unreal-engine/creating-levels-of-detail-in-blueprints-and-python-in-unreal-engine
