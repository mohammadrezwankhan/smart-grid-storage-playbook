from __future__ import annotations

import contextlib
import io
import math
import unittest

from models.pq_capability import PowerPriority
from models.volt_var import VoltVarCurve, dispatch_volt_var, main


class VoltVarTests(unittest.TestCase):
    def test_curve_saturates_at_low_and_high_voltage(self):
        curve = VoltVarCurve()
        self.assertEqual(curve.reactive_request_pu(0.80), 1.0)
        self.assertEqual(curve.reactive_request_pu(0.92), 1.0)
        self.assertEqual(curve.reactive_request_pu(1.08), -1.0)
        self.assertEqual(curve.reactive_request_pu(1.20), -1.0)

    def test_curve_interpolates_and_has_a_deadband(self):
        curve = VoltVarCurve()
        self.assertAlmostEqual(curve.reactive_request_pu(0.95), 0.5)
        self.assertEqual(curve.reactive_request_pu(1.0), 0.0)
        self.assertAlmostEqual(curve.reactive_request_pu(1.05), -0.5)

    def test_curve_rejects_invalid_breakpoints_and_voltage(self):
        with self.assertRaisesRegex(ValueError, "voltage breakpoints"):
            VoltVarCurve(low_deadband_pu=0.90).reactive_request_pu(1.0)
        with self.assertRaisesRegex(ValueError, "finite and nonnegative"):
            VoltVarCurve().reactive_request_pu(math.nan)
        with self.assertRaisesRegex(ValueError, "must be positive"):
            VoltVarCurve(max_reactive_power_pu=0.0).reactive_request_pu(1.0)

    def test_feasible_request_passes_through_capability(self):
        result = dispatch_volt_var(0.95, 60.0, 100.0)
        self.assertAlmostEqual(result.requested_reactive_mvar, 50.0)
        self.assertAlmostEqual(result.capability.active_mw, 60.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, 50.0)
        self.assertFalse(result.capability.limited)

    def test_reactive_priority_preserves_voltage_support(self):
        result = dispatch_volt_var(0.95, 90.0, 100.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, 50.0)
        self.assertAlmostEqual(result.capability.active_mw, math.sqrt(7500.0))
        self.assertTrue(result.capability.limited)

    def test_active_priority_preserves_active_power(self):
        result = dispatch_volt_var(
            0.95,
            90.0,
            100.0,
            priority=PowerPriority.ACTIVE,
        )
        self.assertAlmostEqual(result.capability.active_mw, 90.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, math.sqrt(1900.0))

    def test_import_sign_is_preserved_during_reactive_priority(self):
        result = dispatch_volt_var(1.05, -90.0, 100.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, -50.0)
        self.assertAlmostEqual(result.capability.active_mw, -math.sqrt(7500.0))

    def test_cli_reports_request_and_limited_dispatch(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--voltage-pu",
                    "0.95",
                    "--active-mw",
                    "90",
                    "--limit-mva",
                    "100",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Volt-VAR request: 0.500 pu", output)
        self.assertIn("Capability limited: true", output)
        self.assertIn("Delivered active power: 86.603 MW", output)


if __name__ == "__main__":
    unittest.main()
