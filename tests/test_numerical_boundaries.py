import math
import random
import sys
import unittest

from models.energy_limits import StorageEnergyState, limit_active_power_by_energy
from models.pq_capability import PowerPriority, allocate_power


class NumericalBoundaryTests(unittest.TestCase):
    def test_active_priority_at_large_finite_rating(self):
        result = allocate_power(-9e199, 9e199, 1e200, PowerPriority.ACTIVE)
        self.assertEqual(result.active_mw, -9e199)
        self.assertAlmostEqual(result.reactive_mvar / 1e200, math.sqrt(0.19))

    def test_reactive_priority_at_large_finite_rating(self):
        result = allocate_power(9e199, -9e199, 1e200, PowerPriority.REACTIVE)
        self.assertEqual(result.reactive_mvar, -9e199)
        self.assertAlmostEqual(result.active_mw / 1e200, math.sqrt(0.19))

    def test_proportional_priority_with_overflowing_request_norm(self):
        result = allocate_power(1.4e308, -1.4e308, 1e308, PowerPriority.PROPORTIONAL)
        self.assertAlmostEqual(result.active_mw / 1e308, 1 / math.sqrt(2))
        self.assertEqual(result.reactive_mvar, -result.active_mw)

    def test_largest_finite_rating_keeps_result_norm_finite(self):
        rating = sys.float_info.max
        result = allocate_power(
            -1.2294889085007471e308, -1.513839114874491e308,
            rating, PowerPriority.PROPORTIONAL,
        )
        self.assertLessEqual(result.apparent_power_mva, rating)
        self.assertAlmostEqual(result.utilization, 1.0)

    def test_seeded_circular_allocations_respect_rating_and_priority(self):
        source = random.Random(219)
        for _ in range(500):
            rating = 10.0 ** source.uniform(-300, 300)
            active, reactive = (source.uniform(-2, 2) for _ in range(2))
            for priority in PowerPriority:
                result = allocate_power(active * rating, reactive * rating, rating, priority)
                delivered_active = result.active_mw / rating
                delivered_reactive = result.reactive_mvar / rating
                self.assertLessEqual(math.hypot(delivered_active, delivered_reactive), 1 + 1e-14)
                if priority is PowerPriority.ACTIVE:
                    self.assertAlmostEqual(delivered_active, max(-1, min(1, active)))
                elif priority is PowerPriority.REACTIVE:
                    self.assertAlmostEqual(delivered_reactive, max(-1, min(1, reactive)))
                else:
                    self.assertAlmostEqual(delivered_active * reactive, delivered_reactive * active)

    def test_positive_duration_that_rounds_to_zero_hours_is_rejected(self):
        state = StorageEnergyState(100, 0.5)
        with self.assertRaisesRegex(ValueError, "duration_minutes"):
            limit_active_power_by_energy(1, math.ulp(0.0), state)

    def test_underflowing_retention_exponent_uses_zero_loss_limit(self):
        lossless = StorageEnergyState(100, 0.5)
        negligible_loss = StorageEnergyState(100, 0.5, self_discharge_rate_per_hour=1e-300)
        for request in (-1, 1):
            expected = limit_active_power_by_energy(request, 1e-298, lossless)
            actual = limit_active_power_by_energy(request, 1e-298, negligible_loss)
            self.assertEqual(actual.delivered_active_mw, request)
            self.assertEqual(actual.ending_soc, expected.ending_soc)

    def test_charge_when_efficiency_times_hours_rounds_to_zero(self):
        state = StorageEnergyState(100, 0.5, charge_efficiency=0.1)
        result = limit_active_power_by_energy(-1, 60 * math.ulp(0.0), state)
        self.assertEqual(result.delivered_active_mw, -1)
