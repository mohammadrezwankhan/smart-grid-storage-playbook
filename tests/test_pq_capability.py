from __future__ import annotations

import contextlib
import io
import math
import tempfile
import unittest
from pathlib import Path

from models.pq_capability import (
    CapabilityQuadrant,
    CapabilityCurvePoint,
    DirectionalCapabilityEnvelope,
    PiecewiseCapabilityCurve,
    PowerPriority,
    allocate_power,
    allocate_power_on_directional_envelope,
    allocate_power_on_curve,
    load_capability_curve_csv,
    load_directional_capability_csv,
    main,
)


class PqCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.curve = PiecewiseCapabilityCurve(
            (
                CapabilityCurvePoint(0.0, 100.0),
                CapabilityCurvePoint(50.0, 80.0),
                CapabilityCurvePoint(80.0, 50.0),
                CapabilityCurvePoint(100.0, 0.0),
            )
        )
        self.envelope = DirectionalCapabilityEnvelope(
            discharge_injection=PiecewiseCapabilityCurve(
                (
                    CapabilityCurvePoint(0.0, 100.0),
                    CapabilityCurvePoint(50.0, 85.0),
                    CapabilityCurvePoint(80.0, 55.0),
                    CapabilityCurvePoint(100.0, 0.0),
                )
            ),
            discharge_absorption=PiecewiseCapabilityCurve(
                (
                    CapabilityCurvePoint(0.0, 90.0),
                    CapabilityCurvePoint(50.0, 75.0),
                    CapabilityCurvePoint(80.0, 45.0),
                    CapabilityCurvePoint(100.0, 0.0),
                )
            ),
            charge_injection=PiecewiseCapabilityCurve(
                (
                    CapabilityCurvePoint(0.0, 100.0),
                    CapabilityCurvePoint(40.0, 82.0),
                    CapabilityCurvePoint(65.0, 50.0),
                    CapabilityCurvePoint(80.0, 0.0),
                )
            ),
            charge_absorption=PiecewiseCapabilityCurve(
                (
                    CapabilityCurvePoint(0.0, 90.0),
                    CapabilityCurvePoint(40.0, 70.0),
                    CapabilityCurvePoint(65.0, 40.0),
                    CapabilityCurvePoint(80.0, 0.0),
                )
            ),
        )

    def test_feasible_request_passes_through(self):
        result = allocate_power(60.0, 40.0, 100.0)
        self.assertEqual(result.active_mw, 60.0)
        self.assertEqual(result.reactive_mvar, 40.0)
        self.assertFalse(result.limited)
        self.assertLess(result.utilization, 1.0)

    def test_active_priority_preserves_active_command(self):
        result = allocate_power(80.0, 80.0, 100.0, PowerPriority.ACTIVE)
        self.assertAlmostEqual(result.active_mw, 80.0)
        self.assertAlmostEqual(result.reactive_mvar, 60.0)
        self.assertAlmostEqual(result.apparent_power_mva, 100.0)
        self.assertTrue(result.limited)

    def test_reactive_priority_preserves_reactive_command(self):
        result = allocate_power(80.0, 80.0, 100.0, PowerPriority.REACTIVE)
        self.assertAlmostEqual(result.active_mw, 60.0)
        self.assertAlmostEqual(result.reactive_mvar, 80.0)
        self.assertAlmostEqual(result.apparent_power_mva, 100.0)

    def test_proportional_priority_preserves_command_ratio(self):
        result = allocate_power(90.0, 120.0, 100.0, PowerPriority.PROPORTIONAL)
        self.assertAlmostEqual(result.active_mw, 60.0)
        self.assertAlmostEqual(result.reactive_mvar, 80.0)
        self.assertAlmostEqual(result.active_mw / result.reactive_mvar, 0.75)

    def test_single_axis_command_is_clipped(self):
        result = allocate_power(150.0, 20.0, 100.0, PowerPriority.ACTIVE)
        self.assertAlmostEqual(result.active_mw, 100.0)
        self.assertAlmostEqual(result.reactive_mvar, 0.0)
        self.assertAlmostEqual(result.apparent_power_mva, 100.0)

    def test_negative_commands_preserve_quadrant(self):
        result = allocate_power(-80.0, -80.0, 100.0, PowerPriority.ACTIVE)
        self.assertAlmostEqual(result.active_mw, -80.0)
        self.assertAlmostEqual(result.reactive_mvar, -60.0)
        self.assertGreater(result.curtailed_active_mw, -1e-12)
        self.assertLess(result.curtailed_reactive_mvar, 0.0)

    def test_rejects_invalid_inputs(self):
        with self.assertRaisesRegex(ValueError, "must be positive"):
            allocate_power(10.0, 10.0, 0.0)
        with self.assertRaisesRegex(ValueError, "must be finite"):
            allocate_power(math.nan, 10.0, 100.0)
        with self.assertRaisesRegex(ValueError, "priority must be one of"):
            allocate_power(10.0, 10.0, 100.0, "unknown")

    def test_piecewise_rejects_invalid_inputs(self):
        with self.assertRaisesRegex(ValueError, "must be finite"):
            allocate_power_on_curve(math.nan, 10.0, self.curve)
        with self.assertRaisesRegex(ValueError, "priority must be one of"):
            allocate_power_on_curve(10.0, 10.0, self.curve, "unknown")
        with self.assertRaisesRegex(ValueError, "must be finite"):
            self.curve.reactive_limit_mvar(math.inf)

    def test_piecewise_curve_interpolates_both_axes(self):
        self.assertAlmostEqual(self.curve.reactive_limit_mvar(65.0), 65.0)
        self.assertAlmostEqual(self.curve.reactive_limit_mvar(-65.0), 65.0)
        self.assertAlmostEqual(self.curve.active_limit_mw(65.0), 65.0)
        self.assertAlmostEqual(self.curve.active_limit_mw(-65.0), 65.0)
        self.assertAlmostEqual(self.curve.reactive_limit_mvar(120.0), 0.0)
        self.assertAlmostEqual(self.curve.active_limit_mw(120.0), 0.0)

    def test_piecewise_curve_rejects_invalid_shapes(self):
        invalid_curves = (
            (
                (CapabilityCurvePoint(0.0, 100.0),),
                "at least two points",
            ),
            (
                (
                    CapabilityCurvePoint(1.0, 100.0),
                    CapabilityCurvePoint(100.0, 0.0),
                ),
                "reactive axis",
            ),
            (
                (
                    CapabilityCurvePoint(0.0, 100.0),
                    CapabilityCurvePoint(100.0, 1.0),
                ),
                "active axis",
            ),
            (
                (
                    CapabilityCurvePoint(0.0, 100.0),
                    CapabilityCurvePoint(50.0, 60.0),
                    CapabilityCurvePoint(40.0, 0.0),
                ),
                "strictly increasing",
            ),
            (
                (
                    CapabilityCurvePoint(0.0, 100.0),
                    CapabilityCurvePoint(50.0, 20.0),
                    CapabilityCurvePoint(100.0, 0.0),
                ),
                "concave",
            ),
            (
                (
                    CapabilityCurvePoint(0.0, math.inf),
                    CapabilityCurvePoint(100.0, 0.0),
                ),
                "must be finite",
            ),
        )
        for points, message in invalid_curves:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    PiecewiseCapabilityCurve(points)

    def test_piecewise_feasible_request_passes_through(self):
        result = allocate_power_on_curve(40.0, 60.0, self.curve)
        self.assertEqual(result.active_mw, 40.0)
        self.assertEqual(result.reactive_mvar, 60.0)
        self.assertFalse(result.limited)
        self.assertLess(result.utilization, 1.0)

    def test_piecewise_active_priority_preserves_active_command(self):
        result = allocate_power_on_curve(
            80.0,
            80.0,
            self.curve,
            PowerPriority.ACTIVE,
        )
        self.assertAlmostEqual(result.active_mw, 80.0)
        self.assertAlmostEqual(result.reactive_mvar, 50.0)
        self.assertAlmostEqual(result.utilization, 1.0)

    def test_piecewise_reactive_priority_preserves_reactive_command(self):
        result = allocate_power_on_curve(
            80.0,
            80.0,
            self.curve,
            PowerPriority.REACTIVE,
        )
        self.assertAlmostEqual(result.active_mw, 50.0)
        self.assertAlmostEqual(result.reactive_mvar, 80.0)
        self.assertAlmostEqual(result.utilization, 1.0)

    def test_piecewise_proportional_priority_preserves_ratio(self):
        result = allocate_power_on_curve(
            80.0,
            80.0,
            self.curve,
            PowerPriority.PROPORTIONAL,
        )
        self.assertAlmostEqual(result.active_mw, 65.0)
        self.assertAlmostEqual(result.reactive_mvar, 65.0)
        self.assertAlmostEqual(result.active_mw / result.reactive_mvar, 1.0)
        self.assertAlmostEqual(result.utilization, 1.0)

    def test_piecewise_allocation_preserves_negative_quadrant(self):
        result = allocate_power_on_curve(
            -80.0,
            -80.0,
            self.curve,
            PowerPriority.ACTIVE,
        )
        self.assertAlmostEqual(result.active_mw, -80.0)
        self.assertAlmostEqual(result.reactive_mvar, -50.0)
        self.assertLess(result.curtailed_reactive_mvar, 0.0)

    def test_piecewise_single_axis_requests_reach_axis_limits(self):
        active = allocate_power_on_curve(
            120.0,
            10.0,
            self.curve,
            PowerPriority.ACTIVE,
        )
        reactive = allocate_power_on_curve(
            10.0,
            120.0,
            self.curve,
            PowerPriority.REACTIVE,
        )
        self.assertAlmostEqual(active.active_mw, 100.0)
        self.assertAlmostEqual(active.reactive_mvar, 0.0)
        self.assertAlmostEqual(reactive.active_mw, 0.0)
        self.assertAlmostEqual(reactive.reactive_mvar, 100.0)

    def test_directional_envelope_selects_all_four_quadrants(self):
        cases = (
            (10.0, 10.0, CapabilityQuadrant.DISCHARGE_INJECTION),
            (10.0, -10.0, CapabilityQuadrant.DISCHARGE_ABSORPTION),
            (-10.0, 10.0, CapabilityQuadrant.CHARGE_INJECTION),
            (-10.0, -10.0, CapabilityQuadrant.CHARGE_ABSORPTION),
        )
        for active_mw, reactive_mvar, expected in cases:
            with self.subTest(quadrant=expected.value):
                self.assertEqual(
                    self.envelope.quadrant_for(active_mw, reactive_mvar),
                    expected,
                )
        self.assertEqual(self.envelope.point_count, 16)

    def test_directional_active_priority_uses_charge_absorption_curve(self):
        result = allocate_power_on_directional_envelope(
            -65.0,
            -70.0,
            self.envelope,
            PowerPriority.ACTIVE,
        )
        self.assertAlmostEqual(result.active_mw, -65.0)
        self.assertAlmostEqual(result.reactive_mvar, -40.0)
        self.assertAlmostEqual(result.utilization, 1.0)

    def test_directional_reactive_priority_uses_charge_absorption_curve(self):
        result = allocate_power_on_directional_envelope(
            -65.0,
            -70.0,
            self.envelope,
            PowerPriority.REACTIVE,
        )
        self.assertAlmostEqual(result.active_mw, -40.0)
        self.assertAlmostEqual(result.reactive_mvar, -70.0)
        self.assertAlmostEqual(result.utilization, 1.0)

    def test_directional_proportional_priority_preserves_quadrant_and_ratio(self):
        result = allocate_power_on_directional_envelope(
            -80.0,
            80.0,
            self.envelope,
            PowerPriority.PROPORTIONAL,
        )
        selected_curve = self.envelope.charge_injection
        self.assertTrue(selected_curve.contains(result.active_mw, result.reactive_mvar))
        self.assertLess(result.active_mw, 0.0)
        self.assertGreater(result.reactive_mvar, 0.0)
        self.assertAlmostEqual(result.active_mw / result.reactive_mvar, -1.0)
        self.assertAlmostEqual(result.utilization, 1.0)

    def test_directional_envelope_requires_shared_axis_limits(self):
        mismatched_active_axis = PiecewiseCapabilityCurve(
            (
                CapabilityCurvePoint(0.0, 90.0),
                CapabilityCurvePoint(110.0, 0.0),
            )
        )
        with self.assertRaisesRegex(ValueError, "discharge active-axis"):
            DirectionalCapabilityEnvelope(
                discharge_injection=self.envelope.discharge_injection,
                discharge_absorption=mismatched_active_axis,
                charge_injection=self.envelope.charge_injection,
                charge_absorption=self.envelope.charge_absorption,
            )

        mismatched_reactive_axis = PiecewiseCapabilityCurve(
            (
                CapabilityCurvePoint(0.0, 110.0),
                CapabilityCurvePoint(80.0, 0.0),
            )
        )
        with self.assertRaisesRegex(ValueError, "injection reactive-axis"):
            DirectionalCapabilityEnvelope(
                discharge_injection=self.envelope.discharge_injection,
                discharge_absorption=self.envelope.discharge_absorption,
                charge_injection=mismatched_reactive_axis,
                charge_absorption=self.envelope.charge_absorption,
            )

    def test_loads_strict_piecewise_curve_csv(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "curve.csv"
            path.write_text(
                "active_mw,reactive_limit_mvar\n0,100\n50,80\n80,50\n100,0\n",
                encoding="utf-8",
            )
            loaded = load_capability_curve_csv(path)
        self.assertEqual(loaded, self.curve)

    def test_loads_committed_directional_capability_csv(self):
        loaded = load_directional_capability_csv(
            "models/data/illustrative_directional_capability.csv"
        )
        self.assertEqual(loaded, self.envelope)

    def test_directional_csv_rejects_unknown_and_missing_quadrants(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "directional.csv"
            path.write_text(
                "quadrant,active_mw,reactive_limit_mvar\n"
                "unknown,0,100\nunknown,100,0\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "quadrant must be one of"):
                load_directional_capability_csv(path)

            path.write_text(
                "quadrant,active_mw,reactive_limit_mvar\n"
                "discharge_injection,0,100\n"
                "discharge_injection,100,0\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing discharge_absorption"):
                load_directional_capability_csv(path)

    def test_curve_csv_rejects_wrong_header_and_incomplete_rows(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "curve.csv"
            path.write_text("p,q\n0,100\n100,0\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CSV header"):
                load_capability_curve_csv(path)
            path.write_text(
                "active_mw,reactive_limit_mvar\n0,100\n100,\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "must be complete"):
                load_capability_curve_csv(path)

    def test_cli_runs_committed_piecewise_curve(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--active-mw",
                    "80",
                    "--reactive-mvar",
                    "80",
                    "--curve-csv",
                    "models/data/illustrative_capability_curve.csv",
                    "--priority",
                    "active",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Capability model: piecewise curve (4 points)", output)
        self.assertIn("Active power: 80.000 MW", output)
        self.assertIn("Reactive power: 50.000 MVAr", output)
        self.assertIn("Capability utilization: 100.00%", output)

    def test_cli_runs_committed_directional_envelope(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--active-mw",
                    "-65",
                    "--reactive-mvar",
                    "-70",
                    "--directional-curve-csv",
                    "models/data/illustrative_directional_capability.csv",
                    "--priority",
                    "active",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn(
            "Capability model: directional envelope (4 quadrants, 16 points)",
            output,
        )
        self.assertIn("Capability quadrant: charge_absorption", output)
        self.assertIn("Active power: -65.000 MW", output)
        self.assertIn("Reactive power: -40.000 MVAr", output)
        self.assertIn("Capability utilization: 100.00%", output)

    def test_legacy_circular_cli_output_stays_compatible(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--active-mw",
                    "80",
                    "--reactive-mvar",
                    "80",
                    "--limit-mva",
                    "100",
                    "--priority",
                    "active",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertTrue(output.startswith("Priority: active\n"))
        self.assertNotIn("Capability model:", output)
        self.assertIn("Reactive power: 60.000 MVAr", output)


if __name__ == "__main__":
    unittest.main()
