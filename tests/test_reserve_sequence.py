from __future__ import annotations

import contextlib
import io
import unittest

from models.energy_limits import StorageEnergyState, limit_active_power_by_energy
from models.reserve_headroom import calculate_reserve_headroom
from models.reserve_sequence import audit_reserve_sequence, main


class ReserveSequenceTests(unittest.TestCase):
    def test_discharge_schedule_carries_soc_and_reduces_upward_margin(self):
        result = audit_reserve_sequence(
            baseline_active_mw=[20.0, 20.0, 20.0],
            interval_duration_minutes=[30.0, 30.0, 30.0],
            response_duration_minutes=30.0,
            maximum_discharge_mw=100.0,
            maximum_charge_mw=100.0,
            state=StorageEnergyState(
                100.0,
                0.80,
                minimum_soc=0.20,
                maximum_soc=0.90,
                charge_efficiency=1.0,
                discharge_efficiency=1.0,
            ),
        )

        self.assertEqual(
            [interval.reserve.upward_reserve_mw for interval in result.intervals],
            [80.0, 80.0, 60.0],
        )
        self.assertEqual(
            [interval.reserve.downward_reserve_mw for interval in result.intervals],
            [40.0, 60.0, 80.0],
        )
        self.assertAlmostEqual(result.ending_soc, 0.50)
        self.assertEqual(result.minimum_upward_reserve_interval, 3)
        self.assertEqual(result.minimum_downward_reserve_interval, 1)
        self.assertEqual(result.upward_energy_limited_interval_count, 1)
        self.assertEqual(result.downward_energy_limited_interval_count, 3)

    def test_single_interval_matches_standalone_models(self):
        state = StorageEnergyState(
            100.0,
            0.50,
            minimum_soc=0.20,
            maximum_soc=0.80,
            charge_efficiency=0.90,
            discharge_efficiency=0.80,
        )
        result = audit_reserve_sequence(
            [10.0],
            [15.0],
            30.0,
            100.0,
            100.0,
            state,
        )
        expected_reserve = calculate_reserve_headroom(
            10.0,
            30.0,
            100.0,
            100.0,
            state,
        )
        expected_dispatch = limit_active_power_by_energy(10.0, 15.0, state)

        self.assertEqual(result.intervals[0].reserve, expected_reserve)
        self.assertEqual(result.intervals[0].baseline_dispatch, expected_dispatch)

    def test_charge_schedule_recovers_upward_reserve(self):
        result = audit_reserve_sequence(
            [-20.0, -20.0, -20.0],
            [30.0, 30.0, 30.0],
            30.0,
            100.0,
            100.0,
            StorageEnergyState(
                100.0,
                0.30,
                minimum_soc=0.20,
                maximum_soc=0.90,
                charge_efficiency=1.0,
                discharge_efficiency=1.0,
            ),
        )

        self.assertEqual(
            [interval.reserve.upward_reserve_mw for interval in result.intervals],
            [40.0, 60.0, 80.0],
        )
        self.assertAlmostEqual(result.ending_soc, 0.60)

    def test_standing_losses_are_carried_and_balance_closes(self):
        result = audit_reserve_sequence(
            [0.0, 0.0],
            [60.0, 60.0],
            15.0,
            100.0,
            100.0,
            StorageEnergyState(
                100.0,
                0.80,
                auxiliary_load_mw=1.0,
                self_discharge_rate_per_hour=0.01,
            ),
        )

        self.assertLess(result.ending_soc, 0.78)
        self.assertAlmostEqual(result.auxiliary_energy_mwh, 2.0)
        self.assertGreater(result.self_discharge_energy_mwh, 0.0)
        self.assertAlmostEqual(result.soc_balance_error, 0.0)
        self.assertEqual(
            result.intervals[1].baseline_dispatch.initial_soc,
            result.intervals[0].baseline_dispatch.ending_soc,
        )

    def test_fixed_reactive_obligation_limits_each_sequence_interval(self):
        result = audit_reserve_sequence(
            [10.0, 10.0],
            [15.0, 15.0],
            30.0,
            100.0,
            100.0,
            StorageEnergyState(
                1000.0,
                0.50,
                charge_efficiency=1.0,
                discharge_efficiency=1.0,
            ),
            reactive_power_mvar=80.0,
            capability_boundary=100.0,
        )

        self.assertEqual(
            [interval.reserve.upward_reserve_mw for interval in result.intervals],
            [50.0, 50.0],
        )
        self.assertEqual(
            [interval.reserve.downward_reserve_mw for interval in result.intervals],
            [70.0, 70.0],
        )
        self.assertEqual(result.upward_capability_limited_interval_count, 2)
        self.assertEqual(result.downward_capability_limited_interval_count, 2)
        self.assertEqual(result.upward_energy_limited_interval_count, 0)
        self.assertEqual(result.downward_energy_limited_interval_count, 0)

    def test_reactive_profile_applies_the_correct_limit_each_interval(self):
        result = audit_reserve_sequence(
            [10.0, 10.0],
            [15.0, 15.0],
            30.0,
            100.0,
            100.0,
            StorageEnergyState(1000.0, 0.50),
            reactive_power_mvar_profile=[0.0, 80.0],
            capability_boundary=100.0,
        )

        self.assertEqual(result.reactive_power_mvar_profile, (0.0, 80.0))
        self.assertEqual(
            [interval.reserve.upward_reserve_mw for interval in result.intervals],
            [90.0, 50.0],
        )
        self.assertEqual(result.minimum_upward_reserve_interval, 2)

    def test_reactive_profile_validates_length_and_scalar_conflict(self):
        state = StorageEnergyState(100.0, 0.50)
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            audit_reserve_sequence(
                [0.0], [15.0], 15.0, 10.0, 10.0, state,
                reactive_power_mvar_profile=[0.0, 1.0],
            )
        with self.assertRaisesRegex(ValueError, "must be zero"):
            audit_reserve_sequence(
                [0.0], [15.0], 15.0, 10.0, 10.0, state,
                reactive_power_mvar=1.0,
                reactive_power_mvar_profile=[0.0],
            )

    def test_unsustainable_schedule_interval_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "interval 1 cannot be sustained"):
            audit_reserve_sequence(
                [50.0],
                [60.0],
                5.0,
                100.0,
                100.0,
                StorageEnergyState(
                    100.0,
                    0.50,
                    minimum_soc=0.20,
                    discharge_efficiency=1.0,
                ),
            )

    def test_profile_inputs_are_validated(self):
        state = StorageEnergyState(100.0, 0.50)
        with self.assertRaisesRegex(ValueError, "at least one"):
            audit_reserve_sequence([], [], 15.0, 100.0, 100.0, state)
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            audit_reserve_sequence([0.0], [15.0, 15.0], 15.0, 100.0, 100.0, state)
        with self.assertRaisesRegex(ValueError, "duration_minutes"):
            audit_reserve_sequence([0.0], [15.0], 0.0, 100.0, 100.0, state)

    def test_cli_reports_schedule_minima_and_interval_evidence(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--baseline-active-mw-profile",
                    "20,20,20",
                    "--interval-duration-minutes-profile",
                    "30,30,30",
                    "--response-duration-minutes",
                    "30",
                    "--maximum-discharge-mw",
                    "100",
                    "--maximum-charge-mw",
                    "100",
                    "--energy-capacity-mwh",
                    "100",
                    "--initial-soc",
                    "0.8",
                    "--minimum-soc",
                    "0.2",
                    "--maximum-soc",
                    "0.9",
                    "--charge-efficiency",
                    "1",
                    "--discharge-efficiency",
                    "1",
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Ending SOC: 0.5000", output)
        self.assertIn("Minimum upward reserve: 60.000 MW (interval 3)", output)
        self.assertIn("Minimum downward reserve: 40.000 MW (interval 1)", output)
        self.assertIn("upward=1, downward=3", output)
        self.assertIn("Interval 3: baseline=20.000 MW", output)

    def test_cli_reports_sequence_capability_limit_counts(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--baseline-active-mw-profile",
                    "10,10",
                    "--interval-duration-minutes-profile",
                    "15,15",
                    "--response-duration-minutes",
                    "30",
                    "--maximum-discharge-mw",
                    "100",
                    "--maximum-charge-mw",
                    "100",
                    "--energy-capacity-mwh",
                    "1000",
                    "--initial-soc",
                    "0.5",
                    "--reactive-mvar",
                    "80",
                    "--limit-mva",
                    "100",
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Reactive power profile: 80.000, 80.000 MVAr", output)
        self.assertIn("Minimum upward reserve: 50.000 MW", output)
        self.assertIn("Minimum downward reserve: 70.000 MW", output)
        self.assertIn("capability-limited intervals: upward=2, downward=2", output)

    def test_cli_reports_interval_reactive_profile(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--baseline-active-mw-profile", "10,10",
                    "--interval-duration-minutes-profile", "15,15",
                    "--reactive-mvar-profile", "0,80",
                    "--response-duration-minutes", "30",
                    "--maximum-discharge-mw", "100",
                    "--maximum-charge-mw", "100",
                    "--energy-capacity-mwh", "1000",
                    "--initial-soc", "0.5",
                    "--limit-mva", "100",
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Reactive power profile: 0.000, 80.000 MVAr", output)
        self.assertIn("Interval 2: baseline=10.000 MW, reactive=80.000 MVAr", output)


if __name__ == "__main__":
    unittest.main()
