"""Deterministic origami-cell workflow. No motor, blade or press calls are present.

Statuses requiring physical evidence are never inferred from SVGs or dry-runs.
All measurements are millimetres in a calibrated sheet coordinate system.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from xml.sax.saxutils import escape

WORKSPACES = {
    # Usable areas are conservative planning assumptions; must be calibrated.
    "cameo5_emboss_unverified": (285.0, 285.0),
    "a3_xy_plotter_unverified": (430.0, 310.0),
}
ORDER = ["generated", "planned", "scored", "registered", "transferred", "folded"]


class GateError(ValueError):
    pass


def stable_hash(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def create_pattern(kind):
    if kind == "b0-a3":
        width, height = 420.0, 297.0
        creases = [
            {"type": "mountain" if i % 2 else "valley",
             "geometry": "line", "points": [[i * 26.25, 0], [i * 26.25, height]]}
            for i in range(1, 16)
        ]
        # Hem fold direction isn't established from published references;
        # represent hems as references, NOT assigned actuated creases.
        guides = [
            {"geometry": "line", "points": [[0, y], [width, y]]}
            for y in (14.0, 226.0)
        ]
    elif kind == "curve-probe":
        width, height = 150.0, 150.0
        creases = [
            {"type": "valley", "geometry": "cubic",
             "points": [[20, 25], [55, 15], [95, 135], [130, 125]]},
            {"type": "mountain", "geometry": "cubic",
             "points": [[20, 55], [55, 45], [95, 165], [130, 145]]},
        ]
        # Last Bezier control point does not define the actual curve extent;
        # curve geometry is checked by sampling and all controls must fit.
        # Change second curve to remain strictly in 150 x 150.
        creases[1]["points"] = [[20, 50], [55, 30], [95, 115], [130, 105]]
        guides = []
    else:
        raise GateError("Unsupported pattern kind")
    pattern = {
        "schema": "sailwave.pattern.v1",
        "variant": kind,
        "width_mm": width,
        "height_mm": height,
        "creases": creases,
        "guides": guides,
        "foldability": "UNVERIFIED",
        "material": "Tyvek 1056D — application not verified",
    }
    validate_pattern(pattern)
    pattern["design_sha256"] = stable_hash(pattern)
    return pattern


def _bezier(points, t):
    s = 1 - t
    a, b, c, d = points
    return [s**3*a[k] + 3*s*s*t*b[k] + 3*s*t*t*c[k] + t**3*d[k] for k in (0, 1)]


def validate_pattern(pattern):
    w, h = pattern.get("width_mm"), pattern.get("height_mm")
    if not all(isinstance(n, (int, float)) and math.isfinite(n) and n > 0 for n in (w, h)):
        raise GateError("Invalid sheet size")
    if not pattern.get("creases"):
        raise GateError("Missing creases")
    for mark in pattern["creases"] + pattern.get("guides", []):
        geometry, points = mark.get("geometry"), mark.get("points")
        if geometry not in ("line", "cubic") or len(points) != {"line": 2, "cubic": 4}[geometry]:
            raise GateError("Unsupported mark geometry")
        if mark in pattern["creases"] and mark.get("type") not in ("mountain", "valley"):
            raise GateError("Crease needs a mountain/valley assignment")
        for pt in points:
            if len(pt) != 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in pt):
                raise GateError("Invalid coordinates")
            if not (0 <= pt[0] <= w and 0 <= pt[1] <= h):
                raise GateError("Point outside media")
        if geometry == "cubic":
            for i in range(101):
                x, y = _bezier(points, i / 100)
                if not (0 <= x <= w and 0 <= y <= h):
                    raise GateError("Curve exits media")
    return True


def svg_for(pattern):
    # A machining aid, NOT an automatic cutter command. No cuts in this SVG.
    w, h = pattern["width_mm"], pattern["height_mm"]
    colors = {"mountain": "#ff0000", "valley": "#0000ff"}
    result = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">',
        '<g id="SCORE_ONLY_NOT_CUT">',
    ]
    for mark in pattern["creases"]:
        p = mark["points"]
        stroke = colors[mark["type"]]
        if mark["geometry"] == "line":
            elem = f'<line x1="{p[0][0]}" y1="{p[0][1]}" x2="{p[1][0]}" y2="{p[1][1]}"'
        else:
            d = f'M {p[0][0]} {p[0][1]} C {p[1][0]} {p[1][1]} {p[2][0]} {p[2][1]} {p[3][0]} {p[3][1]}'
            elem = f'<path d="{escape(d)}"'
        result.append(elem + f' stroke="{stroke}" stroke-width="0.3" fill="none" data-operation="SCORE" />')
    result += ['</g>', '<g id="GUIDES_NOT_MACHINE_OPERATIONS">']
    for mark in pattern.get("guides", []):
        p = mark["points"]
        result.append(f'<line x1="{p[0][0]}" y1="{p[0][1]}" x2="{p[1][0]}" y2="{p[1][1]}" stroke="#999999" stroke-dasharray="2 2" stroke-width="0.2" />')
    result += ["</g>", "</svg>"]
    return "\n".join(result) + "\n"


def create_job(pattern, machine):
    if machine not in WORKSPACES:
        raise GateError("Machine profile is not supported")
    validate_pattern(pattern)
    expected_sha = pattern.get("design_sha256")
    unsealed = {k: v for k, v in pattern.items() if k != "design_sha256"}
    if expected_sha != stable_hash(unsealed):
        raise GateError("Design digest mismatch")
    maxw, maxh = WORKSPACES[machine]
    if pattern["width_mm"] > maxw or pattern["height_mm"] > maxh:
        raise GateError(f"Sheet {pattern['width_mm']}x{pattern['height_mm']} mm exceeds {machine} assumed safe area {maxw}x{maxh} mm")
    return {
        "schema": "sailwave.job.v1",
        "design_sha256": expected_sha,
        "machine_profile": machine,
        "profile_verified": False,
        "status": "planned",
        "events": [{"step": "planned", "mode": "SOFTWARE_ONLY", "evidence": "geometry envelope check"}],
        "next": "score",
        "limits": {"registration_residual_mm": 1.0, "max_translation_mm": 2.0, "max_rotation_deg": 1.0},
    }


def _transition(job, expected, new, evidence):
    if job["status"] != expected:
        raise GateError(f"Expected stage {expected}; observed {job['status']}")
    if evidence.get("mode") != "OBSERVED":
        raise GateError("A physical transition requires observed evidence, not simulation")
    job["events"].append({"step": new, **evidence})
    job["status"] = new
    job["next"] = {"scored": "camera-registration", "registered": "transfer",
                   "transferred": "fold", "folded": None}[new]
    return job


def record_score(job, evidence):
    required = ("operator", "machine_receipt", "material_loaded", "tool_verified", "calibration_id")
    if not all(evidence.get(k) for k in required) or evidence.get("mode") != "OBSERVED":
        raise GateError("Physical score needs operator, machine receipt, loaded material, tool, calibration")
    return _transition(job, "planned", "scored", evidence)


def registration_result(expected, measured, limits):
    if len(expected) < 3 or len(measured) != len(expected):
        raise GateError("At least three matching fiducials required")
    for points in (expected, measured):
        for xy in points:
            if len(xy) != 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in xy):
                raise GateError("Invalid fiducial coordinates")
        # Three coincident/collinear marks cannot establish a 2-D registration plane.
        ax, ay = points[0]
        if max(abs((points[i][0]-ax)*(points[j][1]-ay)
                   -(points[i][1]-ay)*(points[j][0]-ax))
               for i in range(1, len(points))
               for j in range(i+1, len(points))) < 1e-6:
            raise GateError("Degenerate or collinear fiducials")
    # 2D rigid fit; no scale/shear or pixel-to-mm calibration is inferred.
    ex = sum(p[0] for p in expected) / len(expected)
    ey = sum(p[1] for p in expected) / len(expected)
    mx = sum(p[0] for p in measured) / len(measured)
    my = sum(p[1] for p in measured) / len(measured)
    cosine, sine = 0.0, 0.0
    for (x, y), (u, v) in zip(expected, measured):
        x, y, u, v = x-ex, y-ey, u-mx, v-my
        cosine += x*u + y*v
        sine += x*v - y*u
    if cosine == 0 and sine == 0:
        raise GateError("Degenerate fiducial transform")
    angle = math.atan2(sine, cosine)
    ca, sa = math.cos(angle), math.sin(angle)
    translation = math.hypot(mx - ex, my - ey)
    residuals = [
        math.hypot((mx+ca*(x-ex)-sa*(y-ey))-u, (my+sa*(x-ex)+ca*(y-ey))-v)
        for (x,y),(u,v) in zip(expected, measured)
    ]
    return {
        "translation_mm": round(translation, 4),
        "rotation_deg": round(math.degrees(angle), 4),
        "max_residual_mm": round(max(residuals), 4),
        "passed": (translation <= limits["max_translation_mm"]
                   and abs(math.degrees(angle)) <= limits["max_rotation_deg"]
                   and max(residuals) <= limits["registration_residual_mm"]),
    }


def record_camera(job, evidence):
    required = ("operator", "calibration_id", "camera_frame_id", "expected_mm", "measured_mm")
    if not all(evidence.get(k) for k in required) or evidence.get("mode") != "OBSERVED":
        raise GateError("Real measured camera fiducials required")
    if job["status"] != "scored":
        raise GateError("Score step must be receipted before camera registration")
    result = registration_result(evidence["expected_mm"], evidence["measured_mm"], job["limits"])
    if not result["passed"]:
        raise GateError(f"Registration out of tolerance: {result}")
    evidence = {**evidence, "registration": result, "scope": "coordinates_only_not_surface_defect_detection"}
    return _transition(job, "scored", "registered", evidence)


def record_transfer(job, evidence):
    if job["status"] != "registered":
        raise GateError("Registration must pass before transfer")
    required = ("operator", "handling_receipt", "regrip_confirmed", "position_readback")
    if not all(evidence.get(k) for k in required):
        raise GateError("Missing physical handling evidence")
    return _transition(job, "registered", "transferred", evidence)


def record_fold(job, evidence):
    if job["status"] != "transferred":
        raise GateError("Transfer must be receipted before folding")
    required = ("operator", "folding_receipt", "lock_observed", "finished_photo_id")
    if not all(evidence.get(k) for k in required):
        raise GateError("Missing physical folding/locking evidence")
    return _transition(job, "transferred", "folded", evidence)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sailwave-cell")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="Create parameterized crease SVG & sealed manifest")
    gen.add_argument("--variant", choices=["b0-a3", "curve-probe"], required=True)
    gen.add_argument("--out", required=True)
    plan = sub.add_parser("plan", help="Check assumed work envelope; does not start machine")
    plan.add_argument("--design", required=True)
    plan.add_argument("--machine", choices=list(WORKSPACES), required=True)
    plan.add_argument("--out", required=True)
    dry = sub.add_parser("dry-run", help="Show pending stages; never operate hardware")
    dry.add_argument("--job", required=True)
    record = sub.add_parser("record", help="Advance only on supplied observed evidence")
    record.add_argument("--job", required=True)
    record.add_argument("--stage", choices=["score", "camera", "transfer", "fold"], required=True)
    record.add_argument("--evidence", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            pattern = create_pattern(args.variant)
            out = Path(args.out)
            write_json(out / "pattern.json", pattern)
            (out / "creases.svg").write_text(svg_for(pattern), encoding="utf-8") if out.exists() else None
            print(json.dumps({"status": "GENERATED_UNVERIFIED", "pattern": str(out / "pattern.json"),
                              "svg": str(out / "creases.svg"), "digest": pattern["design_sha256"]}))
        elif args.command == "plan":
            job = create_job(read_json(args.design), args.machine)
            write_json(args.out, job)
            print(json.dumps({"status": job["status"], "next": job["next"], "hardware_called": False}))
        elif args.command == "dry-run":
            job = read_json(args.job)
            print(json.dumps({"current": job["status"], "next": job["next"],
                              "remaining": ORDER[ORDER.index(job["status"])+1:] if job["status"] in ORDER else [],
                              "hardware_called": False, "physical_verification": "NOT_ESTABLISHED"}))
        else:
            job = read_json(args.job)
            evidence = read_json(args.evidence)
            if job.get("schema") != "sailwave.job.v1":
                raise GateError("Unknown job schema")
            {"score": record_score, "camera": record_camera,
             "transfer": record_transfer, "fold": record_fold}[args.stage](job, evidence)
            write_json(args.job, job)
            print(json.dumps({"status": job["status"], "next": job["next"]}))
    except (GateError, OSError, KeyError, ValueError) as exc:
        parser.exit(2, f"BLOCKED: {exc}\n")
