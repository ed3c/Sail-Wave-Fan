# Sail Wave Fan — AI-driven Origami Manufacturing Cell V0.2

## Goal, measurement and effort horizon

Build a verifiable five-stage workflow:

1. Automatic **crease generation** (Python → manufacturing SVG + sealed JSON pattern)
2. Automatic **scoring** (equipment-specific adapter, machine receipt)
3. **Camera verification** (calibrated measurements and image provenance)
4. **Paper handling** (machine transfer + independent positioning readback)
5. **3D folding** (fold action, mechanical lock and finished-product readback)

**Current software status:** Stage 1 implemented; Stage 2 geometry-envelope planner and no-hardware dry-run implemented; Stages 2–5 have receipt ingestion/transition contracts and deterministic registration math, but **no physical equipment adapters, camera image acquisition, handling mechanism or folding robot**. Any operator-supplied observation is an attestation, not autonomous machine verification.

**Primary measurement:** Number of complete *real, receipted* fans, successful 500-cycle testing, wind-speed comparison with B0, per-stage wall-clock cost, rework, and harm-related failure reports. Until hardware and experimental measurements exist, completed-physical-jobs = **0**.

## State contracts

```text
generate -> validate dimensions & SVG -> plan
    -> score receipt (real observation required)
    -> camera fiducials (calibrated millimetres, real frame ID)
    -> transfer receipt (regrip and readback)
    -> fold receipt (lock observed + finished photograph)
```

The runtime refuses step skipping. A dry-run **never** writes a physical-success receipt. A pattern hash binds the plan to exact geometry. The current code does not cryptographically validate external observation IDs: integration must later attach provider-owned immutable receipt identities. An operator cannot substitute invented CLI decisions for actual machine evidence.

**Source ownership:** Python geometry generator owns SVG; a machine adapter owns scoring receipt; camera calibration/vision owner owns measured fiducials; handling adapter owns relocation receipt; folding/inspection owner owns finish receipt. The AI session may propose variants or review failures, but mechanical code owns state and bounds.

**Critical barrier:** The `cameo5_emboss_unverified` profile is a conservative **285 × 285 mm planning hypothesis**, not a manufacturer's approved working envelope. It rejects a 420 × 297 mm A3 panel but accepts the 150 × 150 mm curve probe. No known open-source Cameo driver has been validated here for Type C embossing force. `a3_xy_plotter_unverified` is likewise a **hypothetical** envelope, not approval to press, move or cut.

## Run the offline prototype

```sh
python -m sailwave_cell generate --variant curve-probe --out build/curve
python -m sailwave_cell plan --design build/curve/pattern.json --machine cameo5_emboss_unverified --out build/curve/job.json
python -m sailwave_cell dry-run --job build/curve/job.json

# Expect BLOCKED because the Emboss Mat profile cannot fit full A3:
python -m sailwave_cell generate --variant b0-a3 --out build/b0
python -m sailwave_cell plan --design build/b0/pattern.json --machine cameo5_emboss_unverified --out build/b0/job.json

python -m unittest discover -s tests -v
```

Output `creases.svg` contains red (mountain) and blue (valley) **scoring-only** paths and machine-ignored guides, but these colors are import hints, not proof that a cutter will use a scoring wheel. The curve probe is **not** a solved manufacturable curved origami structure. Its purpose is to validate coordinate transport and pressure/material experiments. Physical folding instructions still require independent derivation or the author's published reference.

To record a real, externally witnessed stage, create an independent JSON evidence file and call:

```sh
python -m sailwave_cell record --job build/curve/job.json --stage score --evidence /path/to/score_observation.json
```

A score observation has mandatory `mode: "OBSERVED"`, `operator`, `machine_receipt`, `material_loaded: true`, `tool_verified: true`, and `calibration_id`. Other stages have distinct required fields in `sailwave_cell/core.py`. These are contracts for later integrations; the CLI cannot independently prove an observation is authentic. No example file should masquerade as machine-sourced truth.

### Registration readback

The `camera` stage only validates **already measured, calibrated millimetre fiducials**. At least 3 point pairs are required. The validator fits a 2D rigid transform and checks residual ≤1 mm, translation ≤2 mm, absolute rotation ≤1°. These are exploratory internal tolerances, not optical calibration results. It does not currently detect paper scratches, fold cracks, scored depth, deformation, or lock attachment. Those require a future vision acquisition/evaluation module.

OpenPnP's fiducial registration ideas can guide the later optical subsystem; adapting PCB registration does not prove fit for flexible Tyvek.

## Hardware integration and priority

| Stage | Software today | Earliest real integration | Hard gate |
| --- | --- | --- | --- |
| 1. Generator | B0-A3 and curve-probe SVG + hash | ORIPA / Origami Simulator import | Geometry checks, then folding simulation and physical coupon |
| 2. Scoring | Profile gating and receipt contract | Cameo 5 Alpha + official Emboss Tool / A3 XY platform | Actual tool, media, force, full workspace, safe stop |
| 3. Camera | Measured-coordinate gate only | Fixed overhead camera + calibrated reference board | Exposure, scale, fiducial IDs, RMSE, real image record |
| 4. Transfer | Receipt contract only | Manual handoff → vacuum gripper / tray on FluidNC | No simultaneous gripping; independent post-move registration |
| 5. Folding | Receipt contract only | Soft jig/fixture → motorized folds and paper-strip manipulation | Foldability, pinch force, lock proof, photo and 500 cycles |

### Why not two machines initially?

A Cameo feeder only passes sheets in sequence; it does not expand the OEM 12 × 12 inch embossing mat's 305 × 305 mm coverage. A paper-translation robot introduces positioning error and dual-grip risks. Before purchasing a paper mover, verify a short 150 mm Tyvek curved-crease coupon with a known-safe tool and the correct support surface. Build an A3 capable XY scoring platform only if the full width remains required.

### Physical safety

No AI-powered actuator commands are shipped. Future scoring/handling/folding adapters need hardware E-stop, limit switches, positive tool ID, material-presence detection, operator start permission, and bounded force/speed. Unknown write outcome → stop and provider readback before retry. Never auto-switch from rounded embossing tool to knife, raise pressure without a calibrated recipe, or interpret a camera timeout as pass. Do not run unattended until independent physical safety review.

## Verification & falsification

- Unit and CLI tests must pass; B0-A3 must be *rejected* for the Cameo emboss-mat profile.
- A dry-run cannot create a real-scored receipt.
- Camera coordinates outside tolerance, absent camera frame, incorrect stage ordering, and forged digest must be rejected.
- Different sample batches are required for foldability, fatigue, airspeed, wet-state and skin-contact safety.
- Design options advance only when repeated real observation beats B0 controls.
- Paper fan authors and published diagrams retain their rights; no assumption of commercial reuse.

### Primary sources

- OrigamiUSA Sallas/Grand: https://origamiusa.org/thefold/article/diagrams-two-fans-hot-summer
- Curved folding simulator: https://origamisimulator.org/
- Silhouette accessory limitations: https://silhouetteamerica.freshdesk.com/support/solutions/articles/35000307115-silhouette-specialty-tools-overview-and-setup-guide
- Open-source Cameo driver: https://github.com/fablabnbg/inkscape-silhouette
- OpenPnP fiducial design: https://github.com/openpnp/openpnp/wiki/Fiducials
