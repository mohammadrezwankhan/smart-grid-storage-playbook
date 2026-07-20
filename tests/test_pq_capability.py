from __future__ import annotations

import math
import unittest

from models.pq_capability import PowerPriority, allocate_power


class PqCapabilityTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
