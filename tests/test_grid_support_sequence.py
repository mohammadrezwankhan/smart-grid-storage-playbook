from __future__ import annotations

import contextlib
import io
import math
import unittest
from pathlib import Path

from models.energy_limits import StorageEnergyState
from models.frequency_watt import dispatch_frequency_watt
from models.grid_support_sequence import main, simulate_grid_support_sequence
from models.measurement_filter import FirstOrderFilterConfig
from models.pq_capability import (
    PowerPriority,
    load_capability_curve_csv,
    load_directional_capability_csv,
)
from models.ramp_limits import RampRateLimits
from models.temperature_derating import load_temperature_derating_csv
from models.volt_var import VoltVarCurve


class GridSupportSequenceTests(unittest.TestCase):
    data_directory = Path(__file__).parents[1] / "models" / "data"

    def test_simultaneous_services_carry_delivered_soc(self):
        result = simulate_grid_support_sequence(
            frequency_hz=(50.0, 49.5, 50.5),
            voltage_pu=(1.0, 0.92, 1.08),
            baseline_active_mw=(20.0, 20.0, 20.0),
            duration_minutes=(15.0, 15.0, 15.0),
            energy_state=StorageEnergyState(
                100.0,
                0.50,
                minimum_soc=0.20,
                charge_efficiency=1.0,
                discharge_efficiency=1.0,
            ),
            apparent_power_limit_mva=100.0,
        )

        self.assertAlmostEqual(result.intervals[0].dispatch.capability.active_mw, 20.0)
        self.assertAlmostEqual(result.intervals[0].ending_soc, 0.45)
        self.assertAlmostEqual(
            result.intervals[1].dispatch.unconstrained_active_mw,
            120.0,
        )
        self.assertAlmostEqual(
            result.intervals[1].dispatch.capability.reactive_mvar,
            100.0,
        )
        self.assertAlmostEqual(result.intervals[1].dispatch.capability.active_mw, 0.0)
        self.assertAlmostEqual(result.intervals[1].initial_soc, 0.45)
        self.assertAlmostEqual(result.intervals[1].ending_soc, 0.45)
        self.assertAlmostEqual(result.intervals[2].initial_soc, 0.45)
        self.assertAlmostEqual(result.ending_soc, 0.45)
        self.assertAlmostEqual(result.requested_active_energy_mwh, 15.0)
        self.assertAlmostEqual(result.delivered_active_energy_mwh, 5.0)
        self.assertAlmostEqual(result.active_shortfall_energy_mwh, 50.0)
        self.assertAlmostEqual(result.requested_reactive_service_mvarh, 50.0)
        self.assertAlmostEqual(result.delivered_reactive_service_mvarh, 50.0)
        self.assertAlmostEqual(result.reactive_shortfall_service_mvarh, 0.0)
        self.assertEqual(result.storage_power_limited_interval_count, 1)
        self.assertEqual(result.capability_limited_interval_count, 2)
        self.assertEqual(result.limited_interval_count, 2)

    def test_single_interval_matches_composed_existing_models(self):
        voltage_curve = VoltVarCurve()
        energy_state = StorageEnergyState(100.0, 0.50)
        reactive_request = voltage_curve.reactive_request_pu(0.95) * 100.0
        expected = dispatch_frequency_watt(
            49.725,
            20.0,
            reactive_request,
            100.0,
            priority=PowerPriority.ACTIVE,
            energy_state=energy_state,
            duration_minutes=15.0,
        )
        result = simulate_grid_support_sequence(
            (49.725,),
            (0.95,),
            (20.0,),
            (15.0,),
            energy_state,
            100.0,
            priority=PowerPriority.ACTIVE,
        )

        self.assertEqual(result.intervals[0].dispatch, expected)
        self.assertAlmostEqual(result.intervals[0].requested_reactive_mvar, 50.0)

    def test_directional_sequence_selects_all_four_quadrants(self):
        envelope = load_directional_capability_csv(
            self.data_directory / "illustrative_directional_capability.csv"
        )
        result = simulate_grid_support_sequence(
            (49.5, 49.5, 50.5, 50.5),
            (0.95, 1.05, 0.95, 1.05),
            (0.0, 0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0, 1.0),
            StorageEnergyState(
                1000.0,
                0.50,
                charge_efficiency=1.0,
                discharge_efficiency=1.0,
            ),
            None,
            priority=PowerPriority.REACTIVE,
            capability_envelope=envelope,
        )

        delivered = [
            (
                interval.dispatch.capability.active_mw,
                interval.dispatch.capability.reactive_mvar,
            )
            for interval in result.intervals
        ]
        expected = (
            (81.81818181818181, 50.0),
            (80.0, -45.0),
            (-65.0, 50.0),
            (-60.833333333333336, -45.0),
        )
        for actual, target in zip(delivered, expected, strict=True):
            self.assertAlmostEqual(actual[0], target[0])
            self.assertAlmostEqual(actual[1], target[1])
        for interval, expected_reactive_mvar in zip(
            result.intervals,
            (50.0, -45.0, 50.0, -45.0),
            strict=True,
        ):
            self.assertAlmostEqual(
                interval.requested_reactive_mvar,
                expected_reactive_mvar,
            )
        self.assertAlmostEqual(result.soc_balance_error, 0.0)

    def test_symmetric_sequence_uses_curve_reactive_axis(self):
        curve = load_capability_curve_csv(
            self.data_directory / "illustrative_capability_curve.csv"
        )
        result = simulate_grid_support_sequence(
            (50.0,),
            (0.95,),
            (20.0,),
            (15.0,),
            StorageEnergyState(100.0, 0.50),
            None,
            priority=PowerPriority.ACTIVE,
            capability_envelope=curve,
        )
        interval = result.intervals[0]
        self.assertAlmostEqual(interval.requested_reactive_mvar, 50.0)
        self.assertAlmostEqual(interval.dispatch.capability.active_mw, 20.0)
        self.assertAlmostEqual(interval.dispatch.capability.reactive_mvar, 50.0)

    def test_soc_boundaries_carry_between_opposite_responses(self):
        result = simulate_grid_support_sequence(
            (49.5, 50.5),
            (1.0, 1.0),
            (0.0, 0.0),
            (60.0, 60.0),
            StorageEnergyState(
                100.0,
                0.21,
                minimum_soc=0.20,
                maximum_soc=0.90,
                charge_efficiency=1.0,
                discharge_efficiency=1.0,
            ),
            100.0,
        )

        first, second = result.intervals
        self.assertAlmostEqual(first.dispatch.capability.active_mw, 1.0)
        self.assertAlmostEqual(first.ending_soc, 0.20)
        self.assertAlmostEqual(second.initial_soc, 0.20)
        self.assertAlmostEqual(second.dispatch.capability.active_mw, -70.0)
        self.assertAlmostEqual(second.ending_soc, 0.90)
        self.assertEqual(result.energy_limited_interval_count, 2)
        self.assertAlmostEqual(result.soc_balance_error, 0.0)

    def test_ramp_and_filter_states_are_carried(self):
        result = simulate_grid_support_sequence(
            (49.0, 49.0),
            (1.0, 1.0),
            (0.0, 0.0),
            (0.5, 0.5),
            StorageEnergyState(100.0, 0.50),
            100.0,
            ramp_limits=RampRateLimits(10.0, 20.0),
            initial_active_mw=0.0,
            frequency_filter_config=FirstOrderFilterConfig(60.0),
            initial_filtered_frequency_hz=50.0,
        )

        first, second = result.intervals
        assert first.dispatch.ramp is not None
        assert second.dispatch.ramp is not None
        assert first.dispatch.frequency_filter is not None
        assert second.dispatch.frequency_filter is not None
        self.assertAlmostEqual(first.dispatch.capability.active_mw, 5.0)
        self.assertAlmostEqual(second.dispatch.ramp.previous_active_mw, 5.0)
        self.assertAlmostEqual(second.dispatch.capability.active_mw, 10.0)
        self.assertAlmostEqual(
            second.dispatch.frequency_filter.previous_output_value,
            first.dispatch.control_frequency_hz,
        )
        self.assertEqual(result.ramp_limited_interval_count, 2)

    def test_aggregate_service_and_soc_balances_close(self):
        state = StorageEnergyState(
            120.0,
            0.55,
            minimum_soc=0.15,
            maximum_soc=0.85,
            charge_efficiency=0.92,
            discharge_efficiency=0.88,
        )
        result = simulate_grid_support_sequence(
            (49.8, 50.2, 50.0, 49.5),
            (0.95, 1.05, 1.0, 0.90),
            (10.0, -10.0, 5.0, 0.0),
            (5.0, 10.0, 15.0, 20.0),
            state,
            75.0,
            priority=PowerPriority.PROPORTIONAL,
        )

        expected_stored_change = math.fsum(
            interval.dispatch.delivered_energy.stored_energy_change_mwh
            for interval in result.intervals
            if interval.dispatch.delivered_energy is not None
        )
        self.assertAlmostEqual(result.stored_energy_change_mwh, expected_stored_change)
        self.assertAlmostEqual(
            result.ending_soc,
            state.initial_soc + expected_stored_change / state.energy_capacity_mwh,
        )
        self.assertAlmostEqual(result.soc_balance_error, 0.0)
        self.assertGreaterEqual(result.active_shortfall_energy_mwh, 0.0)
        self.assertGreaterEqual(result.reactive_shortfall_service_mvarh, 0.0)

    def test_storage_losses_carry_through_grid_support_sequence(self):
        result = simulate_grid_support_sequence(
            (50.0, 50.0),
            (1.0, 1.0),
            (0.0, 0.0),
            (60.0, 60.0),
            StorageEnergyState(
                100.0,
                0.80,
                auxiliary_load_mw=2.0,
                self_discharge_rate_per_hour=0.01,
            ),
            100.0,
        )

        self.assertAlmostEqual(result.ending_soc, 0.7445562852589148)
        self.assertEqual(result.dispatch_stored_energy_change_mwh, 0.0)
        self.assertAlmostEqual(result.auxiliary_energy_mwh, 4.0)
        self.assertAlmostEqual(result.self_discharge_energy_mwh, 1.544371474108516)
        self.assertAlmostEqual(
            result.stored_energy_change_mwh,
            -result.auxiliary_energy_mwh - result.self_discharge_energy_mwh,
        )
        self.assertAlmostEqual(result.soc_balance_error, 0.0)

    def test_temperature_profile_applies_and_counts_hard_power_limits(self):
        temperature_curve = load_temperature_derating_csv(
            self.data_directory / "illustrative_temperature_derating.csv"
        )

        result = simulate_grid_support_sequence(
            (49.5, 49.5, 49.5),
            (1.0, 1.0, 1.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            StorageEnergyState(
                1000.0,
                0.50,
                charge_efficiency=1.0,
                discharge_efficiency=1.0,
            ),
            150.0,
            temperature_c=(-20.0, 20.0, 55.0),
            temperature_derating_curve=temperature_curve,
        )

        delivered = tuple(
            interval.dispatch.capability.active_mw for interval in result.intervals
        )
        self.assertEqual(delivered, (30.0, 100.0, 20.0))
        self.assertEqual(
            tuple(interval.temperature_c for interval in result.intervals),
            (-20.0, 20.0, 55.0),
        )
        self.assertEqual(result.temperature_limited_interval_count, 2)
        self.assertEqual(result.limited_interval_count, 2)
        self.assertAlmostEqual(result.ending_soc, 0.4975)

    def test_profile_and_optional_state_inputs_are_validated(self):
        state = StorageEnergyState(100.0, 0.50)
        with self.assertRaisesRegex(ValueError, "at least one interval"):
            simulate_grid_support_sequence((), (), (), (), state, 100.0)
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            simulate_grid_support_sequence(
                (50.0, 50.0),
                (1.0,),
                (0.0, 0.0),
                (1.0, 1.0),
                state,
                100.0,
            )
        with self.assertRaisesRegex(ValueError, r"duration_minutes\[0\]"):
            simulate_grid_support_sequence(
                (50.0,), (1.0,), (0.0,), (0.0,), state, 100.0
            )
        with self.assertRaisesRegex(ValueError, "ramp_limits"):
            simulate_grid_support_sequence(
                (50.0,),
                (1.0,),
                (0.0,),
                (1.0,),
                state,
                100.0,
                ramp_limits=RampRateLimits(1.0, 1.0),
            )
        with self.assertRaisesRegex(ValueError, "frequency_filter_config"):
            simulate_grid_support_sequence(
                (50.0,),
                (1.0,),
                (0.0,),
                (1.0,),
                state,
                100.0,
                initial_filtered_frequency_hz=50.0,
            )
        temperature_curve = load_temperature_derating_csv(
            self.data_directory / "illustrative_temperature_derating.csv"
        )
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            simulate_grid_support_sequence(
                (50.0,),
                (1.0,),
                (0.0,),
                (1.0,),
                state,
                100.0,
                temperature_c=(25.0,),
            )
        with self.assertRaisesRegex(ValueError, "must match"):
            simulate_grid_support_sequence(
                (50.0,),
                (1.0,),
                (0.0,),
                (1.0,),
                state,
                100.0,
                temperature_c=(25.0, 30.0),
                temperature_derating_curve=temperature_curve,
            )
        curve = load_capability_curve_csv(
            self.data_directory / "illustrative_capability_curve.csv"
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            simulate_grid_support_sequence((50.0,), (1.0,), (0.0,), (1.0,), state, None)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            simulate_grid_support_sequence(
                (50.0,),
                (1.0,),
                (0.0,),
                (1.0,),
                state,
                100.0,
                capability_envelope=curve,
            )

    def test_operating_sweep_respects_soc_and_capability_boundaries(self):
        frequencies = (49.0, 49.8, 50.0, 50.2, 51.0)
        voltages = (0.90, 0.95, 1.0, 1.05, 1.10)
        for initial_soc in (0.10, 0.50, 0.90):
            for priority in PowerPriority:
                with self.subTest(initial_soc=initial_soc, priority=priority):
                    result = simulate_grid_support_sequence(
                        frequencies,
                        voltages,
                        (-80.0, -20.0, 0.0, 20.0, 80.0),
                        (1.0, 5.0, 15.0, 30.0, 60.0),
                        StorageEnergyState(100.0, initial_soc),
                        100.0,
                        priority=priority,
                        ramp_limits=RampRateLimits(200.0, 150.0),
                        initial_active_mw=0.0,
                    )
                    for previous, current in zip(
                        result.intervals[:-1],
                        result.intervals[1:],
                        strict=True,
                    ):
                        self.assertAlmostEqual(previous.ending_soc, current.initial_soc)
                        assert current.dispatch.ramp is not None
                        self.assertAlmostEqual(
                            current.dispatch.ramp.previous_active_mw,
                            previous.dispatch.capability.active_mw,
                        )
                    for interval in result.intervals:
                        self.assertGreaterEqual(interval.ending_soc, 0.10 - 1e-12)
                        self.assertLessEqual(interval.ending_soc, 0.90 + 1e-12)
                        self.assertLessEqual(
                            interval.dispatch.capability.apparent_power_mva,
                            100.0 + 1e-12,
                        )
                    self.assertLess(abs(result.soc_balance_error), 1e-12)

    def test_cli_reports_interval_limits_and_aggregate_delivery(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz-profile",
                    "50,49.5,50.5",
                    "--voltage-pu-profile",
                    "1,0.92,1.08",
                    "--baseline-active-mw-profile",
                    "20,20,20",
                    "--duration-minutes-profile",
                    "15,15,15",
                    "--limit-mva",
                    "100",
                    "--energy-capacity-mwh",
                    "100",
                    "--initial-soc",
                    "0.5",
                    "--minimum-soc",
                    "0.2",
                    "--charge-efficiency",
                    "1",
                    "--discharge-efficiency",
                    "1",
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Intervals: 3", output)
        self.assertIn("Limited intervals: 2", output)
        self.assertIn("Ending SOC: 0.4500", output)
        self.assertIn("Delivered active energy: 5.000 MWh", output)
        self.assertIn("Active shortfall energy: 50.000 MWh", output)
        self.assertIn("Delivered reactive service: 50.000 MVArh", output)
        self.assertIn(
            "Interval 2: frequency=49.500 Hz, voltage=0.920 pu",
            output,
        )
        self.assertIn("limits=storage_power,capability", output)

    def test_cli_reports_temperature_profile_limits(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz-profile",
                    "49.5,49.5",
                    "--voltage-pu-profile",
                    "1,1",
                    "--duration-minutes-profile",
                    "1,1",
                    "--limit-mva",
                    "150",
                    "--energy-capacity-mwh",
                    "1000",
                    "--initial-soc",
                    "0.5",
                    "--temperature-c-profile",
                    "20,55",
                    "--temperature-derating-csv",
                    str(self.data_directory / "illustrative_temperature_derating.csv"),
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Temperature derating model: piecewise curve (6 points)", output)
        self.assertIn("Temperature-limited intervals: 1", output)
        self.assertIn("temperature=55.000 C", output)
        self.assertIn("limits=temperature", output)

    def test_cli_rejects_partial_temperature_profile_configuration(self):
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            main(
                [
                    "--frequency-hz-profile",
                    "50",
                    "--voltage-pu-profile",
                    "1",
                    "--duration-minutes-profile",
                    "1",
                    "--limit-mva",
                    "100",
                    "--energy-capacity-mwh",
                    "100",
                    "--initial-soc",
                    "0.5",
                    "--temperature-c-profile",
                    "25",
                ]
            )

    def test_cli_reports_grid_support_storage_losses(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz-profile",
                    "50,50",
                    "--voltage-pu-profile",
                    "1,1",
                    "--duration-minutes-profile",
                    "60,60",
                    "--limit-mva",
                    "100",
                    "--energy-capacity-mwh",
                    "100",
                    "--initial-soc",
                    "0.8",
                    "--auxiliary-load-mw",
                    "2",
                    "--self-discharge-rate-per-hour",
                    "0.01",
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Ending SOC: 0.7446", output)
        self.assertIn("Auxiliary energy: 4.000 MWh", output)
        self.assertIn("Self-discharge energy: 1.544 MWh", output)

    def test_cli_rejects_partial_ramp_and_filter_configuration(self):
        common = [
            "--frequency-hz-profile",
            "50",
            "--voltage-pu-profile",
            "1",
            "--duration-minutes-profile",
            "1",
            "--limit-mva",
            "100",
            "--energy-capacity-mwh",
            "100",
            "--initial-soc",
            "0.5",
        ]
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            main(common + ["--initial-active-mw", "0"])
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            main(common + ["--initial-filtered-frequency-hz", "50"])

    def test_cli_runs_directional_grid_support_sequence(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz-profile",
                    "49.5,49.5,50.5,50.5",
                    "--voltage-pu-profile",
                    "0.95,1.05,0.95,1.05",
                    "--duration-minutes-profile",
                    "1,1,1,1",
                    "--directional-curve-csv",
                    str(
                        self.data_directory / "illustrative_directional_capability.csv"
                    ),
                    "--energy-capacity-mwh",
                    "1000",
                    "--initial-soc",
                    "0.5",
                    "--charge-efficiency",
                    "1",
                    "--discharge-efficiency",
                    "1",
                    "--priority",
                    "reactive",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Capability model: directional envelope", output)
        self.assertIn("requested_q=50.000 MVAr", output)
        self.assertIn("requested_q=-45.000 MVAr", output)
        self.assertIn("delivered_p=-60.833 MW", output)


if __name__ == "__main__":
    unittest.main()
