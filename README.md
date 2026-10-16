# Sail Wave Fan

An experimental **ribless origami rave fan** made from water-resistant synthetic paper. Inspired by the *structural principles* of Joan Sallas' hand fan and Michel Grand's paper locking strip, with a proposed asymmetric sail/wave silhouette.

> **Engineering status: V0.1 prototype.** The original source demonstrates an origami paper fan; the A3 Tyvek scale-up and Sail Wave asymmetric trim have **not** been validated as real products. Concept art is not fabrication evidence.

## Manufacturing Cell V0.2 (software prototype)

**[Architecture, CLI and verification gates](docs/Manufacturing_Cell_V0.2.md)**. Five-stage state machine: generate → score → camera readback → transfer → fold. Today the Python CLI generates B0-A3 and curved probe SVGs, enforces a machine-envelope gate, and accepts strictly ordered *external observation* receipts; it does **not** actuate machinery, read a camera, move paper, or fold a fan.

```sh
python -m sailwave_cell generate --variant curve-probe --out build/curve
python -m sailwave_cell plan --design build/curve/pattern.json --machine cameo5_emboss_unverified --out build/curve/job.json
python -m sailwave_cell dry-run --job build/curve/job.json
python -m unittest discover -s tests -v
```

`cameo5_emboss_unverified` is a conservative uncalibrated capability profile. The full 420 × 297 mm sheet is rejected for this profile, as it should be. Physical stages remain blocked without observations.

## Repository contents

- [Prototype manufacturing specification V0.1](docs/Prototype_Spec_V0.1.md) — dimensions, bill of materials, assembly, safety notes, verification gates.
- [Panel A — 1:1 A3 baseline SVG](templates/SailWave_A3_Panel_A_1to1.svg)
- [Panel B — 1:1 A3 optional tapered SVG](templates/SailWave_A3_Panel_B_Taper_1to1.svg)
- [Locking strip — 1:1 SVG](templates/SailWave_LockStrip_A3_1to1.svg)
- [Template geometry checker](scripts/verify_templates.py) — validates only dimensions and fold-line count, not physical foldability.

## Start here

Make **B0** from two full-height A3 panels and one paper strip; validate the original mechanical interlock before trying the **S1** non-symmetric edge trim. Work from the original [OrigamiUSA diagrams](https://origamiusa.org/system/files/thefold/thefold95_fan_sallas_grand_0.pdf) for the locking *sequence*, and from these SVGs for scaled dimensional *placement*.

Print SVGs at **actual size / 100%**, never 'fit to page'. The panel size is 420 × 297 mm. A cutter or printer must be calibrated before manufacturing.

## Remaining tests

Physical foldability, single-hand airflow, strip fatigue, wet-state behavior, edge injury risk and any industrial safety claims remain unverified. Do not use a prototype for aggressive clacking or in dense festival crowds.

## Attribution

Structural inspiration: Joan Sallas and Michel Grand (OrigamiUSA, 2026). The source diagrams are copyrighted; public access is not a commercial use license. This repository stores independent engineering templates, not copies of those PDFs.
