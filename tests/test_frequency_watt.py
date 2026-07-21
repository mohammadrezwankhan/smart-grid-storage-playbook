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
from models.energy_limits import EnergyBoundary, StorageEnergyState
from models.measurement_filter import FirstOrderFilterConfig
from models.pq_capability import PowerPriority
from models.ramp_limits import RampDirection, RampRateLimits


class FrequencyWattTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
