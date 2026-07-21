from __future__ import annotations

import contextlib
import io
import math
import unittest
from pathlib import Path

from models.frequency_watt import (
    FrequencyWattCurve,
    dispatch_frequency_watt,
    main,
)
from models.energy_limits import EnergyBoundary, StorageEnergyState
from models.measurement_filter import FirstOrderFilterConfig
from models.pq_capability import (
    PowerPriority,
    load_capability_curve_csv,
    load_directional_capability_csv,
)
from models.ramp_limits import RampDirection, RampRateLimits
from models.temperature_derating import load_temperature_derating_csv


class FrequencyWattTests(unittest.TestCase):
    data_directory = Path(__file__).parents[1] / "models" / "data"

    def test_deadband_includes_both_boundaries(self):
        curve = FrequencyWattCurve()
        self.assertEqual(curve.active_adjustment_mw(49.95), 0.0)
        self.assertEqual(curve.active_adjustment_mw(50.00), 0.0)
        self.assertEqual(curve.active_adjustment_mw(50.05), 0.0)

    def test_frequency_filter_applies_before_droop(self):
        unfiltered = dispatch_frequency_watt(49.5, 0.0, 0.0, 100.0)
        filtered = dispatch_frequency_watt(
            49.5,
            0.0,
            0.0,
            100.0,
            frequency_filter_config=FirstOrderFilterConfig(1.0),
            previous_filtered_frequency_hz=50.0,
            measurement_interval_seconds=0.1,
        )

        self.assertEqual(unfiltered.droop_adjustment_mw, 100.0)
        self.assertAlmostEqual(filtered.control_frequency_hz, 49.95241870901798)
        self.assertEqual(filtered.droop_adjustment_mw, 0.0)
        self.assertIsNotNone(filtered.frequency_filter)
        assert filtered.frequency_filter is not None
        self.assertAlmostEqual(
            filtered.frequency_filter.decay_factor,
            math.exp(-0.1),
        )

    def test_frequency_filter_configuration_is_validated(self):
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            dispatch_frequency_watt(
                49.5,
                0.0,
                0.0,
                100.0,
                frequency_filter_config=FirstOrderFilterConfig(1.0),
            )
        with self.assertRaisesRegex(ValueError, "must be positive"):
            dispatch_frequency_watt(
                49.5,
                0.0,
                0.0,
                100.0,
                frequency_filter_config=FirstOrderFilterConfig(1.0),
                previous_filtered_frequency_hz=0.0,
                measurement_interval_seconds=0.1,
            )
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            main(
                [
                    "--frequency-hz",
                    "49.5",
                    "--limit-mva",
                    "100",
                    "--previous-filtered-frequency-hz",
                    "50",
                ]
            )

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

    def test_temperature_curve_hard_limits_discharge_after_power_bound(self):
        temperature_curve = load_temperature_derating_csv(
            self.data_directory / "illustrative_temperature_derating.csv"
        )

        result = dispatch_frequency_watt(
            49.5,
            0.0,
            0.0,
            120.0,
            temperature_c=45.0,
            temperature_derating_curve=temperature_curve,
        )

        self.assertEqual(result.power_bounded_active_mw, 100.0)
        self.assertEqual(result.ramp_bounded_active_mw, 100.0)
        self.assertEqual(result.temperature_bounded_active_mw, 70.0)
        self.assertEqual(result.bounded_active_mw, 70.0)
        self.assertFalse(result.storage_power_limited)
        self.assertIsNotNone(result.temperature_derating)
        assert result.temperature_derating is not None
        self.assertTrue(result.temperature_derating.temperature_limited)
        self.assertEqual(result.capability.active_mw, 70.0)

    def test_temperature_limit_takes_precedence_over_slow_ramp_down(self):
        temperature_curve = load_temperature_derating_csv(
            self.data_directory / "illustrative_temperature_derating.csv"
        )

        result = dispatch_frequency_watt(
            50.0,
            0.0,
            0.0,
            150.0,
            ramp_limits=RampRateLimits(10.0, 10.0),
            previous_active_mw=100.0,
            ramp_interval_seconds=60.0,
            temperature_c=55.0,
            temperature_derating_curve=temperature_curve,
        )

        self.assertEqual(result.power_bounded_active_mw, 0.0)
        self.assertEqual(result.ramp_bounded_active_mw, 90.0)
        self.assertEqual(result.temperature_bounded_active_mw, 20.0)
        assert result.ramp is not None
        assert result.temperature_derating is not None
        self.assertTrue(result.ramp.ramp_limited)
        self.assertTrue(result.temperature_derating.temperature_limited)

    def test_temperature_curve_applies_independent_charge_limit(self):
        temperature_curve = load_temperature_derating_csv(
            self.data_directory / "illustrative_temperature_derating.csv"
        )

        result = dispatch_frequency_watt(
            50.5,
            0.0,
            0.0,
            120.0,
            temperature_c=45.0,
            temperature_derating_curve=temperature_curve,
        )

        self.assertEqual(result.temperature_bounded_active_mw, -50.0)
        assert result.temperature_derating is not None
        self.assertEqual(result.temperature_derating.effective_max_charge_mw, 50.0)
        self.assertTrue(result.temperature_derating.temperature_limited)

    def test_temperature_configuration_is_paired(self):
        temperature_curve = load_temperature_derating_csv(
            self.data_directory / "illustrative_temperature_derating.csv"
        )
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            dispatch_frequency_watt(
                50.0,
                0.0,
                0.0,
                100.0,
                temperature_c=25.0,
            )
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            dispatch_frequency_watt(
                50.0,
                0.0,
                0.0,
                100.0,
                temperature_derating_curve=temperature_curve,
            )

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

    def test_energy_limit_preserves_soc_before_pq_allocation(self):
        energy_state = StorageEnergyState(
            energy_capacity_mwh=100.0,
            initial_soc=0.25,
            minimum_soc=0.20,
            discharge_efficiency=0.90,
        )
        result = dispatch_frequency_watt(
            49.725,
            20.0,
            80.0,
            100.0,
            energy_state=energy_state,
            duration_minutes=15.0,
        )
        self.assertAlmostEqual(result.power_bounded_active_mw, 70.0)
        self.assertAlmostEqual(result.bounded_active_mw, 18.0)
        self.assertIsNotNone(result.energy)
        assert result.energy is not None
        self.assertTrue(result.energy.energy_limited)
        self.assertIs(
            result.energy.limiting_boundary,
            EnergyBoundary.MINIMUM_SOC,
        )
        self.assertAlmostEqual(result.energy.ending_soc, 0.20)
        self.assertIsNotNone(result.delivered_energy)
        assert result.delivered_energy is not None
        self.assertAlmostEqual(result.delivered_energy.ending_soc, 0.20)
        self.assertAlmostEqual(result.capability.active_mw, 18.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, 80.0)
        self.assertFalse(result.capability.limited)

    def test_ramp_limit_applies_before_energy_and_capability(self):
        energy_state = StorageEnergyState(
            energy_capacity_mwh=100.0,
            initial_soc=0.50,
            minimum_soc=0.10,
            discharge_efficiency=1.0,
        )
        result = dispatch_frequency_watt(
            49.725,
            20.0,
            95.0,
            100.0,
            priority=PowerPriority.REACTIVE,
            energy_state=energy_state,
            duration_minutes=15.0,
            ramp_limits=RampRateLimits(40.0, 60.0),
            previous_active_mw=20.0,
            ramp_interval_seconds=30.0,
        )
        self.assertAlmostEqual(result.power_bounded_active_mw, 70.0)
        self.assertAlmostEqual(result.ramp_bounded_active_mw, 40.0)
        self.assertIsNotNone(result.ramp)
        assert result.ramp is not None
        self.assertTrue(result.ramp.ramp_limited)
        self.assertIs(result.ramp.limiting_direction, RampDirection.UP)
        self.assertIsNotNone(result.energy)
        assert result.energy is not None
        self.assertAlmostEqual(result.energy.requested_active_mw, 40.0)
        self.assertAlmostEqual(result.capability.active_mw, 31.22498999199199)
        self.assertAlmostEqual(result.capability.reactive_mvar, 95.0)

    def test_ramp_configuration_and_previous_power_are_validated(self):
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            dispatch_frequency_watt(
                50.0,
                0.0,
                0.0,
                100.0,
                ramp_limits=RampRateLimits(10.0, 10.0),
            )
        with self.assertRaisesRegex(ValueError, "storage power limits"):
            dispatch_frequency_watt(
                50.0,
                0.0,
                0.0,
                100.0,
                ramp_limits=RampRateLimits(10.0, 10.0),
                previous_active_mw=101.0,
                ramp_interval_seconds=30.0,
            )

    def test_delivered_soc_accounts_for_pq_active_power_curtailment(self):
        energy_state = StorageEnergyState(
            energy_capacity_mwh=100.0,
            initial_soc=0.90,
            minimum_soc=0.10,
            discharge_efficiency=1.0,
        )
        result = dispatch_frequency_watt(
            49.725,
            20.0,
            80.0,
            100.0,
            priority=PowerPriority.REACTIVE,
            energy_state=energy_state,
            duration_minutes=60.0,
        )
        self.assertIsNotNone(result.energy)
        self.assertIsNotNone(result.delivered_energy)
        assert result.energy is not None
        assert result.delivered_energy is not None
        self.assertAlmostEqual(result.energy.ending_soc, 0.20)
        self.assertAlmostEqual(result.capability.active_mw, 60.0)
        self.assertAlmostEqual(result.delivered_energy.ending_soc, 0.30)

    def test_delivered_soc_includes_auxiliary_and_self_discharge_losses(self):
        result = dispatch_frequency_watt(
            50.0,
            0.0,
            0.0,
            100.0,
            energy_state=StorageEnergyState(
                100.0,
                0.80,
                auxiliary_load_mw=2.0,
                self_discharge_rate_per_hour=0.01,
            ),
            duration_minutes=120.0,
        )

        assert result.delivered_energy is not None
        self.assertAlmostEqual(result.delivered_energy.ending_soc, 0.7445562852589148)
        self.assertAlmostEqual(result.delivered_energy.auxiliary_energy_mwh, 4.0)
        self.assertAlmostEqual(
            result.delivered_energy.self_discharge_energy_mwh,
            1.544371474108516,
        )

    def test_energy_state_and_duration_must_be_provided_together(self):
        state = StorageEnergyState(100.0, 0.5)
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            dispatch_frequency_watt(
                50.0,
                0.0,
                0.0,
                100.0,
                energy_state=state,
            )
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            dispatch_frequency_watt(
                50.0,
                0.0,
                0.0,
                100.0,
                duration_minutes=15.0,
            )

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

    def test_sampled_curve_limits_composed_frequency_dispatch(self):
        curve = load_capability_curve_csv(
            self.data_directory / "illustrative_capability_curve.csv"
        )
        result = dispatch_frequency_watt(
            49.725,
            20.0,
            80.0,
            None,
            priority=PowerPriority.ACTIVE,
            capability_envelope=curve,
        )

        self.assertAlmostEqual(result.bounded_active_mw, 70.0)
        self.assertAlmostEqual(result.capability.active_mw, 70.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, 60.0)
        self.assertTrue(result.capability.limited)

    def test_directional_envelope_uses_requested_charge_absorption_quadrant(self):
        envelope = load_directional_capability_csv(
            self.data_directory / "illustrative_directional_capability.csv"
        )
        result = dispatch_frequency_watt(
            50.5,
            0.0,
            -70.0,
            None,
            priority=PowerPriority.REACTIVE,
            capability_envelope=envelope,
        )

        self.assertAlmostEqual(result.bounded_active_mw, -100.0)
        self.assertAlmostEqual(result.capability.active_mw, -40.0)
        self.assertAlmostEqual(result.capability.reactive_mvar, -70.0)

    def test_capability_boundary_selection_is_strict(self):
        curve = load_capability_curve_csv(
            self.data_directory / "illustrative_capability_curve.csv"
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            dispatch_frequency_watt(50.0, 0.0, 0.0, None)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            dispatch_frequency_watt(
                50.0,
                0.0,
                0.0,
                100.0,
                capability_envelope=curve,
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

    def test_cli_reports_temperature_derating_stage(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz",
                    "49.5",
                    "--limit-mva",
                    "120",
                    "--temperature-c",
                    "45",
                    "--temperature-derating-csv",
                    str(self.data_directory / "illustrative_temperature_derating.csv"),
                ]
            )

        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Sampled temperature discharge limit: 70.000 MW", output)
        self.assertIn("Temperature-bounded active request: 70.000 MW", output)
        self.assertIn("Temperature power limited: true", output)

    def test_cli_rejects_partial_temperature_configuration(self):
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            main(
                [
                    "--frequency-hz",
                    "49.5",
                    "--limit-mva",
                    "100",
                    "--temperature-c",
                    "45",
                ]
            )

    def test_cli_reports_soc_limited_frequency_response(self):
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
                    "--duration-minutes",
                    "15",
                    "--energy-capacity-mwh",
                    "100",
                    "--initial-soc",
                    "0.25",
                    "--minimum-soc",
                    "0.2",
                    "--discharge-efficiency",
                    "0.9",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Storage-bounded active request: 18.000 MW", output)
        self.assertIn("Energy limited: true", output)
        self.assertIn("Energy limiting boundary: minimum_soc", output)
        self.assertIn("Ending SOC: 0.2000", output)

    def test_cli_reports_delivered_storage_losses(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz",
                    "50",
                    "--limit-mva",
                    "100",
                    "--duration-minutes",
                    "120",
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

    def test_cli_reports_ramp_limited_frequency_response(self):
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
                    "--previous-active-mw",
                    "20",
                    "--ramp-interval-seconds",
                    "30",
                    "--ramp-up-mw-per-minute",
                    "40",
                    "--ramp-down-mw-per-minute",
                    "60",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Ramp-bounded active request: 40.000 MW", output)
        self.assertIn("Ramp limited: true", output)
        self.assertIn("Ramp limiting direction: ramp_up", output)

    def test_cli_reports_filtered_control_frequency(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz",
                    "49.5",
                    "--baseline-active-mw",
                    "0",
                    "--reactive-mvar",
                    "0",
                    "--limit-mva",
                    "100",
                    "--previous-filtered-frequency-hz",
                    "50",
                    "--measurement-interval-seconds",
                    "0.1",
                    "--frequency-filter-time-constant-seconds",
                    "1",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Frequency: 49.500 Hz", output)
        self.assertIn("Control frequency: 49.952 Hz", output)
        self.assertIn("Frequency-filter decay factor: 0.904837", output)
        self.assertIn("Droop adjustment: 0.000 MW", output)

    def test_cli_runs_directional_frequency_dispatch(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--frequency-hz",
                    "50.5",
                    "--reactive-mvar",
                    "-70",
                    "--directional-curve-csv",
                    str(
                        self.data_directory / "illustrative_directional_capability.csv"
                    ),
                    "--priority",
                    "reactive",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Capability model: directional envelope", output)
        self.assertIn("Capability quadrant: charge_absorption", output)
        self.assertIn("Delivered active power: -40.000 MW", output)
        self.assertIn("Delivered reactive power: -70.000 MVAr", output)

    def test_cli_rejects_partial_energy_configuration(self):
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            main(
                [
                    "--frequency-hz",
                    "50",
                    "--limit-mva",
                    "100",
                    "--minimum-soc",
                    "0.2",
                ]
            )
        with self.assertRaisesRegex(ValueError, "must be provided together"):
            main(
                [
                    "--frequency-hz",
                    "50",
                    "--limit-mva",
                    "100",
                    "--auxiliary-load-mw",
                    "1",
                ]
            )


if __name__ == "__main__":
    unittest.main()
