# Sail Wave Fan — Prototype Manufacturing Specification V0.1

**Status:** Experimental Prototype — not approved for manufacture, commercialization, or use in crowded venues  
**Date:** 2026-10-16  
**Goal:** A single-hand, foldable, asymmetric sail-shaped fan made from water-resistant synthetic paper. No conventional rigid fan ribs.

## Design basis and verification boundary

The Joan Sallas two-sheet accordion fan and Michel Grand paper locking strip, published by OrigamiUSA, establish the baseline **B0** hand-fan construction. This repository provides a separate engineering prototype plan and newly generated dimensional templates. The images of a curved sail-shaped fan are **concept renders**, not a proven crease pattern or fabrication drawing. The S1 wave profile, fold fatigue, fan airflow, and edge safety remain unverified.

**Variant definitions:**

| Variant | Change | Status |
| --- | --- | --- |
| B0-Sallas-A3 | A3 × 2, 16 sections per sheet, paper locking strip | Geometric scale-up to validate |
| S1-SailWave | B0 + asymmetric upper-edge trim, 0–42 mm | Prototype hypothesis |
| S2-SoftGrip | S1 + detachable soft TPU grip | Optional, not validated |
| R2-Corrugated | New radial 3D corrugation crease pattern | Research only; must solve folding geometry separately |

The graphic renders may depict ventilation holes, rivets, and a pivot. **Do not add those to B0 or S1.** Holes introduce tear starters; the original paper-strip approach does not require a metal rivet.

## Dimensional specification

| Parameter | Nominal |
| --- | --- |
| Primary material | Tyvek 1056D (HDPE synthetic paper), approx. 55 g/m², approx. 175 μm |
| Number of body sheets | 2 |
| Body sheet size | A3 landscape, 420 × 297 mm per panel |
| Accordion sections | 16 per sheet; 15 internal fold lines |
| Section pitch | 26.25 mm (420/16) |
| Top reinforcing hem | 14 mm |
| Bottom reinforcing hem | 71 mm |
| Nominal effective face height | 212 mm (297-14-71) |
| Connection overlap | 2 sections = 52.5 mm |
| Unfolded material length after overlap | 787.5 mm |
| Paper locking strip | 52.5 × 226 mm nominal; template uses 226.3 mm |
| Folded object length | At most roughly 297 mm, to measure |
| Open face width | Approx. 400 mm target, **not measured** |
| Face projected envelope area | Approx. 0.05–0.065 m² estimate, **not measured** |
| Two A3 sheets stock mass only | Approx. 13.7 g; excludes lock and finishing |
| Asymmetric upper-edge trim | 0–42 mm depth on outer part of second panel |
| Sharp-corner avoidance | Start with radius 5 mm and re-evaluate interlocks |

**Important distinction:** The A3 dimensions are extrapolations from a previously published A4 paper fan; the original OrigamiUSA article did **not** validate this large Tyvek variant.

### Pattern coordinate system

Each `templates/*.svg` specifies a physical SVG viewport in millimetres. The X axis runs along the 420 mm accordion division, and Y along the 297 mm sheet depth. The blue and purple lines alternate fold *locations*; their color does not certify actual mountain/valley assignment. The two teal lines mark top and bottom reinforcing hems.

Panel A: unmodified rectangular baseline panel.

Panel B: optional **S1-only** orange trimming reference. In global joined-panel coordinates, define `x0=480 mm`, `x1=787.5 mm`, `t=clamp((x-x0)/(x1-x0),0,1)` and `d(x)=42*(3*t²-2*t³) mm`. The local Panel B x coordinate begins at global 367.5 mm, so trim begins at local x=112.5 mm and ends at local x=420 mm.

**Do not cut along the orange contour before constructing B0.** Trimming may eliminate part of the 14 mm hem. Re-bind the cut edge without creating stiff bridges across pleats; then re-evaluate full motion.

The locking-strip template marks reference folds at 28.3, 99.0, 127.3 and 198.0 mm plus a widthwise midline at x=26.25 mm. **Exact locking-strip fold directions and interlock sequence must be checked against the author-provided diagrams**; the template is only a scaled position guide.

## Bill of materials

| ID | Quantity | Material / purpose | Evidence |
| --- | --- | --- | --- |
| M01 | 2 A3 sheets | Tyvek 1056D; face and pleats | Material property from manufacturer; application untested |
| M02 | 1 strip | Same material, 52.5 × 226 mm nominal | Scaled paper-lock hypothesis |
| M03 | As required | Soft edge tape / fold-over edging, starting width 6–8 mm | Compatibility and adhesion untested |
| M04 | Optional 1 | Removable soft TPU finger grip, no exposed fasteners | S2 only |
| M05 | Optional | Quick-release retention loop, risk-assessed | Not part of B0/S1 |

Tyvek is water-resistant, not equivalent to indefinitely waterproof, puncture-proof, nonflammable, or skin-contact safety-certified. Test repeated tight folds for delamination.

## Prototype assembly — B0 before S1

1. Print the full-scale SVGs at **100%**, with no fit-to-page scaling. Verify a 100 mm ruler in the print environment before cutting.
2. Prepare two A3 sheets. Mark every 26.25 mm along X. Make an inexpensive plain-paper trial first.
3. Fold the 14 mm and 71 mm parallel hems; make 16 accordion sections with alternating mountain/valley folds. Do not score by cutting fibers.
4. Overlap two folded sections (52.5 mm) between the sheets. Retuck the reinforcing hems to retain the overlap.
5. Fold the separate paper locking strip and engage its two ends following the OrigamiUSA source diagrams; do not improvise rivets or holes.
6. Repeatedly open and close **B0** slowly. Record the dimensions, folding resistance, opening stability, and any slip in the strip.
7. Only after obtaining B0 measurements, make **S1** with the documented taper on the *second* panel. Treat the exposed trim edge and restore foldability.
8. Compare S1 against B0 under identical conditions. If edge processing obstructs the hinges, the strip slips, or the material splits, revert to B0 and record the causal failure.

## Verification gates

| Gate | Procedure | Provisional acceptance / observation |
| --- | --- | --- |
| G0 geometry | Calipers/ruler for pitch, hem, overlap | Cut ±1 mm; fold lines ±1 mm; overlap ±2 mm |
| G1 cycling | 100, then 500, then 1,000 open-close cycles | No functional failure at 500; continue to 1,000 as observation |
| G2 lock | Axial load of 1, 2, 3 N for 10 s each | No spontaneous release; record elongation or slip |
| G3 fan action | One-hand motion at 1–2 Hz for 60 s | No abrupt buckling, tears, or ejection of lock |
| G4 airflow | 30 cm fixed distance, ≥3 × 20 s; mean and peak | Establish B0 baseline; exploratory S1 threshold ≥85% of B0 |
| G5 wet | Mist, wipe, dry and repeat key tests | No delamination or lock loosening |
| G6 edge | Visual, gloved inspection, silicone-skin surrogate | No accessible sharp edges, curling abrasive tape, rigid points |
| G7 portability | Measure folded size and opening/closing force | Compact without forced bending |

The 85% cutoff and cycling/load numbers are **internal exploratory thresholds**, not product standards or evidence of human safety. Do not market for forceful clacking or use in crowded dance floors before independent dynamic and contact-safety testing.

### Failure modes requiring design rejection

- Notches or sharp edges after trimming; cracks initiating at fold intersections.
- Locking strip slipping, tearing, or disconnecting during motion.
- Tape, binders, or hems bridging pleats and causing folding interference.
- Delamination after wet exposure or cycling.
- Unsafe exposure to flame, sparks, or hot lighting (no flame-resistance claim).
- Excessive asymmetric torque, unstable opening, or unexpected release.

## Source and licensing

- OrigamiUSA, *Diagrams: Two Fans for a Hot Summer* (2026): https://origamiusa.org/thefold/article/diagrams-two-fans-hot-summer
- Joan Sallas / Michel Grand; Jane Rosemarin, original fan and locking-strip diagrams: https://origamiusa.org/system/files/thefold/thefold95_fan_sallas_grand_0.pdf
- DuPont Tyvek 1056D datasheet: https://www.dupont.com/content/dam/dupont/amer/us/en/microsites/tyvek-design/images/documents/2019-C%26I_Tyvek_1056D_Datasheet.pdf
- DuPont Tyvek Design FAQ: https://www.dupont.com/tyvekdesign/design-with-tyvek/dupont-tyvek-faq.html

The original origami diagrams and designs remain subject to their authors' rights. Their public availability does **not** imply commercial manufacturing or diagram reproduction permission. These new SVG engineering aids do not reproduce the author's diagram artwork.

## Release decision

**Prototype only.** B0 requires material and size verification; S1 additionally requires edge/taper verification; R2 requires an independently solved and verified crease pattern before any cutting template or structural claim.
