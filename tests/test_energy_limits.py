from __future__ import annotations

import contextlib
import io
import math
import unittest

from models.energy_limits import (
    EnergyBoundary,
    StorageEnergyState,
    limit_active_power_by_energy,
    main,
)


class EnergyLimitsTests(unittest.TestCase):
    def test_feasible_discharge_preserves_request_and_applies_losses(self):
        state = StorageEnergyState(
            energy_capacity_mwh=100.0,
            initial_soc=0.50,
            minimum_soc=0.20,
            discharge_efficiency=0.90,
        )
        result = limit_active_power_by_energy(40.0, 30.0, state)
        self.assertEqual(result.delivered_active_mw, 40.0)
        self.assertAlmostEqual(result.stored_energy_change_mwh, -20.0 / 0.90)
        self.assertAlmostEqual(result.ending_soc, 0.50 - 20.0 / 90.0)
        self.assertFalse(result.energy_limited)
        self.assertIsNone(result.limiting_boundary)

    def test_discharge_is_limited_at_minimum_soc(self):
        state = StorageEnergyState(
            energy_capacity_mwh=50.0,
            initial_soc=0.50,
            minimum_soc=0.20,
            discharge_efficiency=0.90,
        )
        result = limit_active_power_by_energy(100.0, 60.0, state)
        self.assertAlmostEqual(result.delivered_active_mw, 13.5)
        self.assertAlmostEqual(result.ending_soc, 0.20)
        self.assertAlmostEqual(result.power_shortfall_mw, 86.5)
        self.assertTrue(result.energy_limited)
        self.assertIs(result.limiting_boundary, EnergyBoundary.MINIMUM_SOC)

    def test_charge_is_limited_at_maximum_soc(self):
        state = StorageEnergyState(
            energy_capacity_mwh=50.0,
            initial_soc=0.80,
            maximum_soc=0.90,
            charge_efficiency=0.80,
        )
        result = limit_active_power_by_energy(-100.0, 60.0, state)
        self.assertAlmostEqual(result.delivered_active_mw, -6.25)
        self.assertAlmostEqual(result.stored_energy_change_mwh, 5.0)
        self.assertAlmostEqual(result.ending_soc, 0.90)
        self.assertAlmostEqual(result.power_shortfall_mw, 93.75)
        self.assertTrue(result.energy_limited)
        self.assertIs(result.limiting_boundary, EnergyBoundary.MAXIMUM_SOC)

    def test_zero_power_keeps_soc_unchanged(self):
        state = StorageEnergyState(100.0, 0.50)
        result = limit_active_power_by_energy(0.0, 15.0, state)
        self.assertEqual(result.delivered_active_mw, 0.0)
        self.assertEqual(result.stored_energy_change_mwh, 0.0)
        self.assertEqual(result.ending_soc, 0.50)
        self.assertFalse(result.energy_limited)

    def test_boundary_states_block_only_the_outward_direction(self):
        lower = StorageEnergyState(100.0, 0.20, minimum_soc=0.20)
        upper = StorageEnergyState(100.0, 0.90, maximum_soc=0.90)
        self.assertEqual(
            limit_active_power_by_energy(10.0, 15.0, lower).delivered_active_mw,
            0.0,
        )
        self.assertLess(
            limit_active_power_by_energy(-10.0, 15.0, lower).delivered_active_mw,
            0.0,
        )
        self.assertEqual(
            limit_active_power_by_energy(-10.0, 15.0, upper).delivered_active_mw,
            0.0,
        )
        self.assertGreater(
            limit_active_power_by_energy(10.0, 15.0, upper).delivered_active_mw,
            0.0,
        )

    def test_invalid_configuration_and_dispatch_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "energy_capacity_mwh"):
            limit_active_power_by_energy(10.0, 15.0, StorageEnergyState(0.0, 0.5))
        with self.assertRaisesRegex(ValueError, "SOC limits"):
            limit_active_power_by_energy(
                10.0,
                15.0,
                StorageEnergyState(100.0, 0.5, minimum_soc=0.9),
            )
        with self.assertRaisesRegex(ValueError, "initial_soc"):
            limit_active_power_by_energy(10.0, 15.0, StorageEnergyState(100.0, 0.0))
        with self.assertRaisesRegex(ValueError, "charge_efficiency"):
            limit_active_power_by_energy(
                10.0,
                15.0,
                StorageEnergyState(100.0, 0.5, charge_efficiency=1.1),
            )
        with self.assertRaisesRegex(ValueError, "requested_active_mw"):
            limit_active_power_by_energy(math.nan, 15.0, StorageEnergyState(100.0, 0.5))
        with self.assertRaisesRegex(ValueError, "duration_minutes"):
            limit_active_power_by_energy(10.0, 0.0, StorageEnergyState(100.0, 0.5))

    def test_operating_sweep_never_crosses_soc_boundaries(self):
        for initial_soc in (0.20, 0.35, 0.75, 0.90):
            for requested_active_mw in (-200.0, -20.0, 0.0, 20.0, 200.0):
                for duration_minutes in (1.0, 15.0, 120.0):
                    with self.subTest(
                        initial_soc=initial_soc,
                        requested_active_mw=requested_active_mw,
                        duration_minutes=duration_minutes,
                    ):
                        state = StorageEnergyState(100.0, initial_soc)
                        result = limit_active_power_by_energy(
                            requested_active_mw,
                            duration_minutes,
                            state,
                        )
                        self.assertGreaterEqual(result.ending_soc, 0.10)
                        self.assertLessEqual(result.ending_soc, 0.90)
                        self.assertLessEqual(
                            abs(result.delivered_active_mw),
                            abs(requested_active_mw) + 1e-12,
                        )

    def test_cli_reports_limited_discharge_and_ending_soc(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--active-mw",
                    "100",
                    "--duration-minutes",
                    "60",
                    "--energy-capacity-mwh",
                    "50",
                    "--initial-soc",
                    "0.5",
                    "--minimum-soc",
                    "0.2",
                    "--discharge-efficiency",
                    "0.9",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Delivered active power: 13.500 MW", output)
        self.assertIn("Energy limited: true", output)
        self.assertIn("Limiting boundary: minimum_soc", output)
        self.assertIn("Ending SOC: 0.2000", output)


if __name__ == "__main__":
    unittest.main()
