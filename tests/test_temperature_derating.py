from __future__ import annotations

import contextlib
import io
import math
import tempfile
import unittest
from pathlib import Path

from models.temperature_derating import (
    TemperaturePowerDeratingCurve,
    TemperaturePowerPoint,
    limit_active_power_by_temperature,
    load_temperature_derating_csv,
    main,
)


class TemperatureDeratingTests(unittest.TestCase):
    data_file = (
        Path(__file__).parents[1]
        / "models"
        / "data"
        / "illustrative_temperature_derating.csv"
    )

    def test_curve_interpolates_charge_and_discharge_limits(self):
        curve = load_temperature_derating_csv(self.data_file)

        limits = curve.limits_at(40.0)

        self.assertEqual(limits.lower_temperature_c, 35.0)
        self.assertEqual(limits.upper_temperature_c, 45.0)
        self.assertEqual(limits.interpolation_fraction, 0.5)
        self.assertEqual(limits.max_discharge_mw, 85.0)
        self.assertEqual(limits.max_charge_mw, 65.0)
        self.assertFalse(limits.endpoint_clamped)

    def test_curve_clamps_outside_sampled_temperature_range(self):
        curve = load_temperature_derating_csv(self.data_file)

        cold = curve.limits_at(-30.0)
        hot = curve.limits_at(70.0)

        self.assertEqual((cold.max_discharge_mw, cold.max_charge_mw), (30.0, 0.0))
        self.assertEqual((hot.max_discharge_mw, hot.max_charge_mw), (20.0, 10.0))
        self.assertTrue(cold.endpoint_clamped)
        self.assertTrue(hot.endpoint_clamped)

    def test_dispatch_applies_asymmetric_temperature_and_nameplate_limits(self):
        curve = load_temperature_derating_csv(self.data_file)

        discharge = limit_active_power_by_temperature(90.0, 40.0, 80.0, 100.0, curve)
        charge = limit_active_power_by_temperature(-90.0, 40.0, 80.0, 100.0, curve)

        self.assertEqual(discharge.delivered_active_mw, 80.0)
        self.assertTrue(discharge.nameplate_limited)
        self.assertFalse(discharge.temperature_limited)
        self.assertEqual(discharge.effective_max_discharge_mw, 80.0)
        self.assertEqual(charge.delivered_active_mw, -65.0)
        self.assertFalse(charge.nameplate_limited)
        self.assertTrue(charge.temperature_limited)
        self.assertEqual(charge.effective_max_charge_mw, 65.0)

    def test_curve_rejects_invalid_points_and_temperature(self):
        point = TemperaturePowerPoint(20.0, 100.0, 80.0)
        with self.assertRaisesRegex(ValueError, "at least two"):
            TemperaturePowerDeratingCurve((point,))
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            TemperaturePowerDeratingCurve((point, point))
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            TemperaturePowerDeratingCurve(
                (point, TemperaturePowerPoint(30.0, -1.0, 50.0))
            )
        curve = TemperaturePowerDeratingCurve(
            (point, TemperaturePowerPoint(30.0, 90.0, 70.0))
        )
        with self.assertRaisesRegex(ValueError, "temperature_c must be finite"):
            curve.limits_at(math.nan)

    def test_csv_loader_requires_exact_complete_numeric_schema(self):
        cases = (
            ("temperature_c,max_discharge_mw\n20,100\n", "header must be"),
            (
                "temperature_c,max_discharge_mw,max_charge_mw\n20,100,\n",
                "must be complete",
            ),
            (
                "temperature_c,max_discharge_mw,max_charge_mw\n20,high,80\n",
                "must be numeric",
            ),
        )
        for content, message in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "curve.csv"
                path.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    load_temperature_derating_csv(path)

    def test_cli_reports_interpolated_and_effective_limits(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(
                [
                    "--active-mw",
                    "-90",
                    "--temperature-c",
                    "40",
                    "--max-discharge-mw",
                    "80",
                    "--max-charge-mw",
                    "100",
                    "--curve-csv",
                    str(self.data_file),
                ]
            )

        self.assertEqual(exit_code, 0)
        report = output.getvalue()
        self.assertIn("Sampled discharge limit: 85.000 MW", report)
        self.assertIn("Effective discharge limit: 80.000 MW", report)
        self.assertIn("Delivered active power: -65.000 MW", report)
        self.assertIn("Temperature limited: true", report)


if __name__ == "__main__":
    unittest.main()
