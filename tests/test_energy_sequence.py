from __future__ import annotations

import contextlib
import io
import math
import unittest

from models.energy_limits import StorageEnergyState, limit_active_power_by_energy
from models.energy_sequence import main, simulate_energy_dispatch_sequence


class EnergySequenceTests(unittest.TestCase):
    def test_variable_intervals_carry_soc_to_a_boundary_and_recover(self):
        state = StorageEnergyState(
            energy_capacity_mwh=100.0,
            initial_soc=0.50,
            minimum_soc=0.20,
            maximum_soc=0.90,
            charge_efficiency=0.80,
            discharge_efficiency=1.0,
        )
        result = simulate_energy_dispatch_sequence(
            (50.0, 50.0, 50.0, -40.0),
            (15.0, 15.0, 15.0, 30.0),
            state,
        )

        for delivered_active_mw, expected_active_mw in zip(
            (interval.delivered_active_mw for interval in result.intervals),
            (50.0, 50.0, 20.0, -40.0),
            strict=True,
        ):
            self.assertAlmostEqual(delivered_active_mw, expected_active_mw)
        self.assertEqual(result.limited_interval_count, 1)
        self.assertAlmostEqual(result.total_duration_minutes, 75.0)
        self.assertAlmostEqual(result.requested_ac_energy_mwh, 17.5)
        self.assertAlmostEqual(result.delivered_ac_energy_mwh, 10.0)
        self.assertAlmostEqual(result.curtailed_ac_energy_mwh, 7.5)
        self.assertAlmostEqual(result.stored_energy_change_mwh, -14.0)
        self.assertAlmostEqual(result.ending_soc, 0.36)
        self.assertAlmostEqual(result.soc_balance_error, 0.0)

    def test_single_interval_matches_the_existing_limiter(self):
        state = StorageEnergyState(
            energy_capacity_mwh=80.0,
            initial_soc=0.30,
            minimum_soc=0.20,
            discharge_efficiency=0.90,
        )
        expected = limit_active_power_by_energy(100.0, 30.0, state)
        result = simulate_energy_dispatch_sequence((100.0,), (30.0,), state)

        self.assertEqual(result.intervals, (expected,))
        self.assertEqual(result.initial_soc, state.initial_soc)
        self.assertEqual(result.ending_soc, expected.ending_soc)

    def test_mixed_profile_closes_stored_energy_and_soc_balance(self):
        state = StorageEnergyState(
            energy_capacity_mwh=120.0,
            initial_soc=0.55,
            minimum_soc=0.15,
            maximum_soc=0.85,
            charge_efficiency=0.92,
            discharge_efficiency=0.88,
        )
        result = simulate_energy_dispatch_sequence(
            (35.0, -20.0, 0.0, 75.0, -60.0),
            (10.0, 35.0, 5.0, 20.0, 15.0),
            state,
        )

        expected_stored_change = math.fsum(
            interval.stored_energy_change_mwh for interval in result.intervals
        )
        expected_ending_soc = state.initial_soc + (
            expected_stored_change / state.energy_capacity_mwh
        )
        self.assertAlmostEqual(
            result.stored_energy_change_mwh,
            expected_stored_change,
        )
        self.assertAlmostEqual(result.ending_soc, expected_ending_soc)
        self.assertAlmostEqual(result.soc_balance_error, 0.0)
        for previous, current in zip(
            result.intervals[:-1],
            result.intervals[1:],
            strict=True,
        ):
            self.assertEqual(previous.ending_soc, current.initial_soc)

    def test_profile_inputs_are_validated(self):
        state = StorageEnergyState(100.0, 0.50)
        with self.assertRaisesRegex(ValueError, "at least one interval"):
            simulate_energy_dispatch_sequence((), (), state)
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            simulate_energy_dispatch_sequence((10.0, 20.0), (15.0,), state)
        with self.assertRaisesRegex(ValueError, "requested_active_mw"):
            simulate_energy_dispatch_sequence((math.nan,), (15.0,), state)
        with self.assertRaisesRegex(ValueError, "duration_minutes"):
            simulate_energy_dispatch_sequence((10.0,), (0.0,), state)

    def test_operating_sweep_stays_inside_soc_limits(self):
        for initial_soc in (0.10, 0.25, 0.50, 0.75, 0.90):
            for request_scale in (1.0, 10.0, 100.0):
                requests = (
                    2.0 * request_scale,
                    -request_scale,
                    0.0,
                    -3.0 * request_scale,
                    4.0 * request_scale,
                )
                with self.subTest(
                    initial_soc=initial_soc,
                    request_scale=request_scale,
                ):
                    result = simulate_energy_dispatch_sequence(
                        requests,
                        (1.0, 5.0, 15.0, 30.0, 120.0),
                        StorageEnergyState(100.0, initial_soc),
                    )
                    self.assertTrue(
                        all(
                            0.10 <= interval.ending_soc <= 0.90
                            for interval in result.intervals
                        )
                    )
                    self.assertLess(abs(result.soc_balance_error), 1e-12)

    def test_cli_reports_sequence_summary_and_limited_interval(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--active-mw-profile",
                    "50,50,50,-40",
                    "--duration-minutes-profile",
                    "15,15,15,30",
                    "--energy-capacity-mwh",
                    "100",
                    "--initial-soc",
                    "0.5",
                    "--minimum-soc",
                    "0.2",
                    "--charge-efficiency",
                    "0.8",
                    "--discharge-efficiency",
                    "1",
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Intervals: 4", output)
        self.assertIn("Limited intervals: 1", output)
        self.assertIn("Ending SOC: 0.3600", output)
        self.assertIn("Delivered AC energy: 10.000 MWh", output)
        self.assertIn("Curtailed AC energy: 7.500 MWh", output)
        self.assertIn(
            "Interval 3: requested=50.000 MW, delivered=20.000 MW",
            output,
        )
        self.assertIn("boundary=minimum_soc", output)


if __name__ == "__main__":
    unittest.main()
