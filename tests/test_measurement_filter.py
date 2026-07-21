from __future__ import annotations

import contextlib
import io
import math
import unittest

from models.measurement_filter import (
    FirstOrderFilterConfig,
    filter_first_order_step,
    main,
)


class MeasurementFilterTests(unittest.TestCase):
    def test_step_matches_exact_first_order_solution(self):
        result = filter_first_order_step(
            49.0,
            50.0,
            1.0,
            FirstOrderFilterConfig(2.0),
        )
        self.assertAlmostEqual(result.decay_factor, math.exp(-0.5), places=15)
        self.assertAlmostEqual(result.output_value, 49.60653065971263, places=14)
        self.assertEqual(result.input_step, -1.0)
        self.assertAlmostEqual(
            result.output_change,
            result.output_value - 50.0,
            places=15,
        )

    def test_equal_input_and_previous_output_stay_constant(self):
        result = filter_first_order_step(
            50.0,
            50.0,
            10.0,
            FirstOrderFilterConfig(0.25),
        )
        self.assertEqual(result.output_value, 50.0)
        self.assertEqual(result.output_change, 0.0)

    def test_tiny_interval_uses_stable_response_fraction(self):
        result = filter_first_order_step(
            1.0,
            0.0,
            1e-20,
            FirstOrderFilterConfig(1.0),
        )
        self.assertAlmostEqual(result.output_value, 1e-20, places=35)
        self.assertGreater(result.output_change, 0.0)

    def test_split_intervals_match_one_combined_interval(self):
        config = FirstOrderFilterConfig(3.0)
        whole = filter_first_order_step(49.0, 50.0, 2.0, config)
        first = filter_first_order_step(49.0, 50.0, 0.75, config)
        second = filter_first_order_step(49.0, first.output_value, 1.25, config)
        self.assertAlmostEqual(second.output_value, whole.output_value, places=14)

    def test_output_stays_between_previous_output_and_input(self):
        config = FirstOrderFilterConfig(1.7)
        for input_value in (-100.0, -1.0, 0.0, 1.0, 100.0):
            for previous_output in (-50.0, 0.0, 50.0):
                for interval_seconds in (1e-6, 0.1, 10.0, 1e6):
                    with self.subTest(
                        input_value=input_value,
                        previous_output=previous_output,
                        interval_seconds=interval_seconds,
                    ):
                        result = filter_first_order_step(
                            input_value,
                            previous_output,
                            interval_seconds,
                            config,
                        )
                        self.assertGreaterEqual(
                            result.output_value,
                            min(input_value, previous_output),
                        )
                        self.assertLessEqual(
                            result.output_value,
                            max(input_value, previous_output),
                        )

    def test_invalid_config_and_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "time_constant_seconds"):
            filter_first_order_step(
                1.0,
                0.0,
                1.0,
                FirstOrderFilterConfig(0.0),
            )
        with self.assertRaisesRegex(ValueError, "interval_seconds"):
            filter_first_order_step(
                1.0,
                0.0,
                0.0,
                FirstOrderFilterConfig(1.0),
            )
        with self.assertRaisesRegex(ValueError, "input_value"):
            filter_first_order_step(
                math.nan,
                0.0,
                1.0,
                FirstOrderFilterConfig(1.0),
            )

    def test_cli_reports_exact_step(self):
        standard_output = io.StringIO()
        with contextlib.redirect_stdout(standard_output):
            exit_code = main(
                [
                    "--input-value",
                    "49",
                    "--previous-output-value",
                    "50",
                    "--interval-seconds",
                    "1",
                    "--time-constant-seconds",
                    "2",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = standard_output.getvalue()
        self.assertIn("Filtered output value: 49.606531", output)
        self.assertIn("Decay factor: 0.606530660", output)


if __name__ == "__main__":
    unittest.main()
