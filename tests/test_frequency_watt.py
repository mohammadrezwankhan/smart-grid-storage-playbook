from __future__ import annotations

import contextlib
import io
import math
import unittest

from models.frequency_watt import (
    FrequencyWattCurve,
    dispatch_frequency_watt,
    main,
)
from models.pq_capability import PowerPriority


class FrequencyWattTests(unittest.TestCase):
    def test_deadband_includes_both_boundaries(self):
        curve = FrequencyWattCurve()
        self.assertEqual(curve.active_adjustment_mw(49.95), 0.0)
        self.assertEqual(curve.active_adjustment_mw(50.00), 0.0)
        self.assertEqual(curve.active_adjustment_mw(50.05), 0.0)

    def test_under_frequency_response_interpolates_and_saturates(self):
        curve = FrequencyWattCurve()
        self.assertAlmostEqual(curve.active_adjustment_mw(49.725), 50.0)
        self.assertEqual(curve.active_adjustment_mw(49.50), 100.0)
        self.assertEqual(curve.active_adjustment_mw(48.00), 100.0)

    def test_over_frequency_response_supports_asymmetric_charge_limit(self):
        curve = FrequencyWattCurve(max_charge_mw=60.0)
        self.assertAlmostEqual(curve.active_adjustment_mw(50.275), -30.0)
        self.assertEqual(curve.active_adjustment_mw(50.50), -60.0)

    def test_curve_rejects_invalid_configuration_and_frequency(self):
        with self.assertRaisesRegex(ValueError, "greater than deadband"):
            FrequencyWattCurve(
                deadband_hz=0.5,
                full_response_deviation_hz=0.5,
            ).active_adjustment_mw(50.0)
        with self.assertRaisesRegex(ValueError, "limits must be positive"):
            FrequencyWattCurve(max_charge_mw=0.0).active_adjustment_mw(50.0)
        with self.assertRaisesRegex(ValueError, "finite and positive"):
            FrequencyWattCurve().active_adjustment_mw(math.nan)
        with self.assertRaisesRegex(ValueError, "baseline_active_mw must be finite"):
            dispatch_frequency_watt(50.0, math.inf, 0.0, 100.0)

    def test_storage_power_limit_clips_baseline_plus_response(self):
        result = dispatch_frequency_watt(49.725, 70.0, 0.0, 120.0)
        self.assertAlmostEqual(result.droop_adjustment_mw, 50.0)
        self.assertAlmostEqual(result.unconstrained_active_mw, 120.0)
        self.assertAlmostEqual(result.bounded_active_mw, 100.0)
        self.assertTrue(result.storage_power_limited)
        self.assertFalse(result.capability.limited)

    def test_active_priority_preserves_frequency_support(self):
        result = dispatch_frequency_watt(49.725, 20.0, 80.0, 100.0)
        self.assertAlmostEqual(result.bounded_active_mw, 70.0)
        self.assertAlmostEqual(result.capability.active_mw, 70.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, math.sqrt(5100.0))
        self.assertTrue(result.capability.limited)

    def test_reactive_priority_can_curtail_frequency_support(self):
        result = dispatch_frequency_watt(
            49.725,
            20.0,
            80.0,
            100.0,
            priority=PowerPriority.REACTIVE,
        )
        self.assertAlmostEqual(result.capability.active_mw, 60.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, 80.0)

    def test_operating_sweep_respects_storage_and_capability_limits(self):
        for frequency_hz in (49.0, 49.725, 50.0, 50.275, 51.0):
            for baseline_active_mw in (-120.0, 0.0, 120.0):
                for reactive_power_mvar in (-120.0, 40.0, 120.0):
                    for priority in PowerPriority:
                        with self.subTest(
                            frequency_hz=frequency_hz,
                            baseline_active_mw=baseline_active_mw,
                            reactive_power_mvar=reactive_power_mvar,
                            priority=priority,
                        ):
                            result = dispatch_frequency_watt(
                                frequency_hz,
                                baseline_active_mw,
                                reactive_power_mvar,
                                100.0,
                                priority=priority,
                            )
                            self.assertLessEqual(abs(result.bounded_active_mw), 100.0)
                            self.assertLessEqual(
                                result.capability.apparent_power_mva,
                                100.0 + 1e-12,
                            )

    def test_cli_reports_response_and_capability_limit(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz",
                    "49.725",
                    "--baseline-active-mw",
                    "20",
                    "--reactive-mvar",
                    "80",
                    "--limit-mva",
                    "100",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Droop adjustment: 50.000 MW", output)
        self.assertIn("Capability limited: true", output)
        self.assertIn("Delivered active power: 70.000 MW", output)


if __name__ == "__main__":
    unittest.main()
