# Compact canopy alternative — isolated experiment

Woodland render 36209094563 timed out at 35 minutes after entering the forest. One courtyard frame was opened; county movement/collision passed, later frames were missing, and the gate failed. No shader compile errors were reported. Long frame gaps and PSO hitches make foliage overdraw/material cost credible optimization targets, not a proven single diagnosis or a POCO benchmark.

This branch experiments with a composite photographic bough atlas, 588 foliage cards instead of 4116, and 2672 Pine triangles instead of 9728. A minimal masked Default Lit material is authored with three expressions. Other geometry and all placements were hash-compared with county-art-003 and retained. The labelled offline image was opened; it is not gameplay/performance evidence. Source release canopy-bough-source-001 is immutable and separate from the already existing county-art-004, which was NOT overwritten.

74 Python tests pass locally. No new UE or Android result is claimed for this experiment.

During work, the newer remote gameplay/forest-lod candidate was discovered. It already integrates melee-motion and a more complete near/mid/far/hidden cell system, shared atlas and compact material. Its five-frame/melee/forest gates must not be replaced with this branch's older four-frame-only path. This alternate canopy is preserved for comparison rather than published as the newest complete game candidate. Continue integration from the newer combined branch.
