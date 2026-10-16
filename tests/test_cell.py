import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sailwave_cell.core import (
    GateError, create_job, create_pattern, record_camera, record_fold,
    record_score, record_transfer, registration_result, svg_for, validate_pattern,
)

class CellTests(unittest.TestCase):
    def setUp(self):
        self.pattern = create_pattern("curve-probe")
        self.job = create_job(self.pattern, "cameo5_emboss_unverified")

    def test_generate_curve_svg(self):
        svg = svg_for(self.pattern)
        self.assertIn('C 55 15 95 135', svg)
        self.assertIn('SCORE_ONLY_NOT_CUT', svg)
        self.assertIn('#ff0000', svg)
        self.assertIn('#0000ff', svg)
        self.assertEqual(self.pattern["foldability"], "UNVERIFIED")

    def test_b0_16_divisions(self):
        b0 = create_pattern("b0-a3")
        self.assertEqual(len(b0["creases"]), 15)
        self.assertEqual(len(b0["guides"]), 2)
        self.assertEqual(b0["creases"][0]["points"][0], [26.25, 0])
        self.assertEqual(b0["width_mm"], 420)

    def test_curve_outside_media_rejected(self):
        p = copy.deepcopy(self.pattern)
        p["creases"][0]["points"][1] = [170, 15]
        with self.assertRaises(GateError):
            validate_pattern(p)

    def test_b0_blocked_on_emboss_mat(self):
        with self.assertRaisesRegex(GateError, "exceeds"):
            create_job(create_pattern("b0-a3"), "cameo5_emboss_unverified")
        self.assertEqual(self.job["status"], "planned")
        self.assertFalse(self.job["profile_verified"])

    def test_digest_tamper_rejected(self):
        p = copy.deepcopy(self.pattern)
        p["width_mm"] = 151
        with self.assertRaisesRegex(GateError, "digest"):
            create_job(p, "cameo5_emboss_unverified")

    def test_score_cannot_be_inferred_from_dry_run(self):
        with self.assertRaises(GateError):
            record_score(self.job, {"mode": "SIMULATED", "operator": "tester"})
        self.assertEqual(self.job["status"], "planned")
        with self.assertRaises(GateError):
            record_transfer(self.job, {"mode": "OBSERVED"})

    def test_registered_measurements(self):
        expected = [[10, 10], [130, 10], [10, 130]]
        measured = [[10.5, 10.2], [130.5, 10.2], [10.5, 130.2]]
        result = registration_result(expected, measured, self.job["limits"])
        self.assertTrue(result["passed"])
        measured_bad = [[15, 10], [135, 10], [15, 130]]
        self.assertFalse(registration_result(expected, measured_bad, self.job["limits"])["passed"])

    def test_complete_observed_evidence_chain(self):
        score = {"mode": "OBSERVED", "operator": "test-op",
                 "machine_receipt": "external-record-123", "material_loaded": True,
                 "tool_verified": True, "calibration_id": "external-calibration-123"}
        record_score(self.job, score)
        with self.assertRaises(GateError):
            record_camera(self.job, {"mode": "SIMULATED"})
        cam = {"mode": "OBSERVED", "operator": "test-op",
               "calibration_id": "camera-calibration-123", "camera_frame_id": "frame-123",
               "expected_mm": [[10,10],[130,10],[10,130]],
               "measured_mm": [[10.5,10.2],[130.5,10.2],[10.5,130.2]]}
        record_camera(self.job, cam)
        self.assertEqual(self.job["status"], "registered")
        with self.assertRaises(GateError):
            record_fold(self.job, {"mode": "OBSERVED"})
        record_transfer(self.job, {"mode": "OBSERVED", "operator": "test-op",
                                 "handling_receipt": "external-handling-123",
                                 "regrip_confirmed": True,
                                 "position_readback": "regrip-camera-123"})
        record_fold(self.job, {"mode": "OBSERVED", "operator": "test-op",
                              "folding_receipt": "external-fold-123",
                              "lock_observed": True, "finished_photo_id": "photo-123"})
        self.assertEqual(self.job["status"], "folded")
        self.assertEqual(len(self.job["events"]), 5)
        with self.assertRaises(GateError):
            record_fold(self.job, {"mode": "OBSERVED"})

    def test_cli_smoke_offline(self):
        with tempfile.TemporaryDirectory() as temp:
            generated = Path(temp) / "design"
            cmd = [sys.executable, "-m", "sailwave_cell", "generate",
                   "--variant", "curve-probe", "--out", str(generated)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((generated / "creases.svg").is_file())
            job = Path(temp) / "job.json"
            cmd = [sys.executable, "-m", "sailwave_cell", "plan",
                   "--design", str(generated / "pattern.json"),
                   "--machine", "cameo5_emboss_unverified", "--out", str(job)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            dry = subprocess.run([sys.executable, "-m", "sailwave_cell",
                                  "dry-run", "--job", str(job)], capture_output=True, text=True)
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertFalse(json.loads(dry.stdout)["hardware_called"])


if __name__ == "__main__":
    unittest.main()
