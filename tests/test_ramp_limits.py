from __future__ import annotations

import contextlib
import io
import math
import unittest

from models.ramp_limits import (
    RampDirection,
    RampRateLimits,
    limit_active_power_by_ramp,
    main,
)


class RampLimitsTests(unittest.TestCase):
    def test_ramp_up_limits_increasing_discharge(self):
        result = limit_active_power_by_ramp(
            80.0,
            20.0,
            30.0,
            RampRateLimits(40.0, 60.0),
        )
        self.assertEqual(result.delivered_active_mw, 40.0)
        self.assertEqual(result.power_change_mw, 20.0)
        self.assertEqual(result.power_shortfall_mw, 40.0)
        self.assertTrue(result.ramp_limited)
        self.assertIs(result.limiting_direction, RampDirection.UP)

    def test_ramp_down_uses_asymmetric_rate(self):
        result = limit_active_power_by_ramp(
            -50.0,
            20.0,
            30.0,
            RampRateLimits(40.0, 60.0),
        )
        self.assertEqual(result.delivered_active_mw, -10.0)
        self.assertEqual(result.minimum_active_mw, -10.0)
        self.assertIs(result.limiting_direction, RampDirection.DOWN)

    def test_feasible_request_passes_through(self):
        result = limit_active_power_by_ramp(
            25.0,
            20.0,
            30.0,
            RampRateLimits(40.0, 60.0),
        )
        self.assertEqual(result.delivered_active_mw, 25.0)
        self.assertFalse(result.ramp_limited)
        self.assertIsNone(result.limiting_direction)

    def test_tiny_interval_overshoot_reports_ramp_limit(self):
        result = limit_active_power_by_ramp(
            20.0 + 1e-13,
            10.0,
            30.0,
            RampRateLimits(20.0, 30.0),
        )
        self.assertEqual(result.delivered_active_mw, 20.0)
        self.assertTrue(result.ramp_limited)
        self.assertIs(result.limiting_direction, RampDirection.UP)

    def test_crossing_zero_preserves_signed_slew_limit(self):
        result = limit_active_power_by_ramp(
            30.0,
            -20.0,
            120.0,
            RampRateLimits(10.0, 30.0),
        )
        self.assertEqual(result.delivered_active_mw, 0.0)
        self.assertEqual(result.power_change_mw, 20.0)
        self.assertIs(result.limiting_direction, RampDirection.UP)

    def test_invalid_rates_and_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "ramp_up_mw_per_minute"):
            limit_active_power_by_ramp(
                10.0,
                0.0,
                30.0,
                RampRateLimits(0.0, 10.0),
            )
        with self.assertRaisesRegex(ValueError, "interval_seconds"):
            limit_active_power_by_ramp(
                10.0,
                0.0,
                0.0,
                RampRateLimits(10.0, 10.0),
            )
        with self.assertRaisesRegex(ValueError, "requested_active_mw"):
            limit_active_power_by_ramp(
                math.nan,
                0.0,
                30.0,
                RampRateLimits(10.0, 10.0),
            )

    def test_operating_sweep_stays_inside_reachable_interval(self):
        limits = RampRateLimits(17.0, 31.0)
        for previous_active_mw in (-100.0, -10.0, 0.0, 30.0, 100.0):
            for requested_active_mw in (-200.0, -20.0, 0.0, 40.0, 200.0):
                for interval_seconds in (0.1, 15.0, 300.0):
                    with self.subTest(
                        previous_active_mw=previous_active_mw,
                        requested_active_mw=requested_active_mw,
                        interval_seconds=interval_seconds,
                    ):
                        result = limit_active_power_by_ramp(
                            requested_active_mw,
                            previous_active_mw,
                            interval_seconds,
                            limits,
                        )
                        self.assertGreaterEqual(
                            result.delivered_active_mw,
                            result.minimum_active_mw - 1e-12,
                        )
                        self.assertLessEqual(
                            result.delivered_active_mw,
                            result.maximum_active_mw + 1e-12,
                        )
                        self.assertLessEqual(
                            abs(result.delivered_active_mw - requested_active_mw),
                            abs(previous_active_mw - requested_active_mw) + 1e-12,
                        )

    def test_cli_reports_limited_ramp_up(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--active-mw",
                    "80",
                    "--previous-active-mw",
                    "20",
                    "--interval-seconds",
                    "30",
                    "--ramp-up-mw-per-minute",
                    "40",
                    "--ramp-down-mw-per-minute",
                    "60",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Delivered active power: 40.000 MW", output)
        self.assertIn("Ramp limited: true", output)
        self.assertIn("Limiting direction: ramp_up", output)


if __name__ == "__main__":
    unittest.main()
