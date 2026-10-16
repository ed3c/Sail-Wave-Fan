#!/usr/bin/env python3
"""Check SVG dimensions and fold marks only; NOT foldability, safety, or airflow."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / "templates"
CASES = (
    ("SailWave_A3_Panel_A_1to1.svg", "420mm", "297mm", 17, 0),
    ("SailWave_A3_Panel_B_Taper_1to1.svg", "420mm", "297mm", 17, 1),
    ("SailWave_LockStrip_A3_1to1.svg", "52.5mm", "226.3mm", 5, 0),
)
NS = "{http://www.w3.org/2000/svg}"
for filename, width, height, num_lines, num_polylines in CASES:
    root = ET.parse(ROOT / filename).getroot()
    assert root.get("width") == width and root.get("height") == height, filename
    assert len(root.findall(NS + "line")) == num_lines, filename
    assert len(root.findall(NS + "polyline")) == num_polylines, filename
    print(f"OK: {filename} ({width} × {height}; fold references)")
print("PASS: structural SVG checks only — no physical product verification")
