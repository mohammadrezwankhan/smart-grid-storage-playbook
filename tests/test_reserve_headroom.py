from __future__ import annotations

import contextlib
import io
import unittest

from models.energy_limits import StorageEnergyState
from models.reserve_headroom import calculate_reserve_headroom, main


class ReserveHeadroomTests(unittest.TestCase):
    def test_soc_headroom_limits_both_reserve_directions(self):
        result = calculate_reserve_headroom(
            baseline_active_mw=10.0,
            duration_minutes=30.0,
            maximum_discharge_mw=100.0,
            maximum_charge_mw=100.0,
            state=StorageEnergyState(
                energy_capacity_mwh=100.0,
                initial_soc=0.50,
                minimum_soc=0.20,
                maximum_soc=0.80,
                charge_efficiency=1.0,
                discharge_efficiency=1.0,
            ),
        )

        self.assertAlmostEqual(result.upward_limit_active_mw, 60.0)
        self.assertAlmostEqual(result.downward_limit_active_mw, -60.0)
        self.assertAlmostEqual(result.upward_reserve_mw, 50.0)
        self.assertAlmostEqual(result.downward_reserve_mw, 70.0)
        self.assertTrue(result.upward_energy_limited)
        self.assertTrue(result.downward_energy_limited)

    def test_efficiency_reduces_sustained_discharge_reserve(self):
        result = calculate_reserve_headroom(
            baseline_active_mw=0.0,
            duration_minutes=15.0,
            maximum_discharge_mw=100.0,
            maximum_charge_mw=100.0,
            state=StorageEnergyState(
                energy_capacity_mwh=100.0,
                initial_soc=0.30,
                minimum_soc=0.20,
                maximum_soc=0.90,
                charge_efficiency=0.90,
                discharge_efficiency=0.80,
            ),
        )

        self.assertAlmostEqual(result.upward_reserve_mw, 32.0)
        self.assertAlmostEqual(result.downward_reserve_mw, 100.0)
        self.assertTrue(result.upward_energy_limited)
        self.assertFalse(result.downward_energy_limited)

    def test_power_limits_bind_when_energy_is_available(self):
        result = calculate_reserve_headroom(
            baseline_active_mw=-5.0,
            duration_minutes=5.0,
            maximum_discharge_mw=20.0,
            maximum_charge_mw=15.0,
            state=StorageEnergyState(
                energy_capacity_mwh=200.0,
                initial_soc=0.50,
            ),
        )

        self.assertEqual(result.upward_limit_active_mw, 20.0)
        self.assertEqual(result.downward_limit_active_mw, -15.0)
        self.assertEqual(result.upward_reserve_mw, 25.0)
        self.assertEqual(result.downward_reserve_mw, 10.0)
        self.assertFalse(result.upward_energy_limited)
        self.assertFalse(result.downward_energy_limited)

    def test_rejects_invalid_limits_and_unsustainable_baseline(self):
        state = StorageEnergyState(
            energy_capacity_mwh=10.0,
            initial_soc=0.30,
            minimum_soc=0.20,
            discharge_efficiency=1.0,
        )
        with self.assertRaisesRegex(ValueError, "maximum_discharge_mw"):
            calculate_reserve_headroom(0.0, 10.0, -1.0, 1.0, state)
        with self.assertRaisesRegex(ValueError, "configured power limits"):
            calculate_reserve_headroom(2.0, 10.0, 1.0, 1.0, state)
        with self.assertRaisesRegex(ValueError, "cannot be sustained"):
            calculate_reserve_headroom(2.0, 60.0, 2.0, 2.0, state)

    def test_operating_sweep_preserves_nonnegative_reserves(self):
        for initial_soc in (0.15, 0.30, 0.50, 0.70, 0.85):
            with self.subTest(initial_soc=initial_soc):
                result = calculate_reserve_headroom(
                    baseline_active_mw=0.0,
                    duration_minutes=20.0,
                    maximum_discharge_mw=50.0,
                    maximum_charge_mw=40.0,
                    state=StorageEnergyState(100.0, initial_soc),
                )
                self.assertGreaterEqual(result.upward_reserve_mw, 0.0)
                self.assertGreaterEqual(result.downward_reserve_mw, 0.0)
                self.assertLessEqual(result.upward_limit_active_mw, 50.0)
                self.assertGreaterEqual(result.downward_limit_active_mw, -40.0)

    def test_cli_reports_directional_reserve_and_binding_limit(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--baseline-active-mw",
                    "10",
                    "--duration-minutes",
                    "30",
                    "--maximum-discharge-mw",
                    "100",
                    "--maximum-charge-mw",
                    "100",
                    "--energy-capacity-mwh",
                    "100",
                    "--initial-soc",
                    "0.5",
                    "--minimum-soc",
                    "0.2",
                    "--maximum-soc",
                    "0.8",
                    "--charge-efficiency",
                    "1",
                    "--discharge-efficiency",
                    "1",
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Upward reserve: 50.000 MW", output)
        self.assertIn("Downward reserve: 70.000 MW", output)
        self.assertIn("Upward energy limited: true", output)
        self.assertIn("Downward energy limited: true", output)


if __name__ == "__main__":
    unittest.main()
