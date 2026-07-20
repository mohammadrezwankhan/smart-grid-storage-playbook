from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Sequence

try:
    from models.pq_capability import (
        CapabilityResult,
        PowerPriority,
        allocate_power,
    )
except ModuleNotFoundError:
    from pq_capability import CapabilityResult, PowerPriority, allocate_power


@dataclass(frozen=True)
class FrequencyWattCurve:
    """Illustrative deadband and linear frequency-watt response."""

    nominal_frequency_hz: float = 50.0
    deadband_hz: float = 0.05
    full_response_deviation_hz: float = 0.50
    max_discharge_mw: float = 100.0
    max_charge_mw: float = 100.0

    def validate(self) -> None:
        values = {
            "nominal_frequency_hz": self.nominal_frequency_hz,
            "deadband_hz": self.deadband_hz,
            "full_response_deviation_hz": self.full_response_deviation_hz,
            "max_discharge_mw": self.max_discharge_mw,
            "max_charge_mw": self.max_charge_mw,
        }
        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.nominal_frequency_hz <= 0.0:
            raise ValueError("nominal_frequency_hz must be positive")
        if self.deadband_hz < 0.0:
            raise ValueError("deadband_hz must be nonnegative")
        if self.full_response_deviation_hz <= self.deadband_hz:
            raise ValueError(
                "full_response_deviation_hz must be greater than deadband_hz"
            )
        if self.max_discharge_mw <= 0.0 or self.max_charge_mw <= 0.0:
            raise ValueError("charge and discharge limits must be positive")

    def active_adjustment_mw(self, frequency_hz: float) -> float:
        """Return positive response below nominal and negative response above."""

        self.validate()
        if not math.isfinite(frequency_hz) or frequency_hz <= 0.0:
            raise ValueError("frequency_hz must be finite and positive")

        deviation_hz = self.nominal_frequency_hz - frequency_hz
        magnitude_hz = abs(deviation_hz)
        if magnitude_hz <= self.deadband_hz:
            return 0.0

        response_fraction = min(
            1.0,
            (magnitude_hz - self.deadband_hz)
            / (self.full_response_deviation_hz - self.deadband_hz),
        )
        if deviation_hz > 0.0:
            return response_fraction * self.max_discharge_mw
        return -response_fraction * self.max_charge_mw


@dataclass(frozen=True)
class FrequencyWattDispatch:
    frequency_hz: float
    baseline_active_mw: float
    droop_adjustment_mw: float
    unconstrained_active_mw: float
    bounded_active_mw: float
    storage_power_limited: bool
    capability: CapabilityResult


def dispatch_frequency_watt(
    frequency_hz: float,
    baseline_active_mw: float,
    reactive_power_mvar: float,
    apparent_power_limit_mva: float,
    curve: FrequencyWattCurve = FrequencyWattCurve(),
    priority: PowerPriority | str = PowerPriority.ACTIVE,
) -> FrequencyWattDispatch:
    """Evaluate frequency-watt response and enforce power and P-Q limits."""

    if not math.isfinite(baseline_active_mw):
        raise ValueError("baseline_active_mw must be finite")

    adjustment_mw = curve.active_adjustment_mw(frequency_hz)
    unconstrained_active_mw = baseline_active_mw + adjustment_mw
    bounded_active_mw = max(
        -curve.max_charge_mw,
        min(curve.max_discharge_mw, unconstrained_active_mw),
    )
    storage_power_limited = not math.isclose(
        unconstrained_active_mw,
        bounded_active_mw,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    capability = allocate_power(
        bounded_active_mw,
        reactive_power_mvar,
        apparent_power_limit_mva,
        priority,
    )
    return FrequencyWattDispatch(
        frequency_hz=frequency_hz,
        baseline_active_mw=baseline_active_mw,
        droop_adjustment_mw=adjustment_mw,
        unconstrained_active_mw=unconstrained_active_mw,
        bounded_active_mw=bounded_active_mw,
        storage_power_limited=storage_power_limited,
        capability=capability,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate illustrative frequency-watt and P-Q dispatch."
    )
    parser.add_argument("--frequency-hz", type=float, required=True)
    parser.add_argument("--baseline-active-mw", type=float, default=0.0)
    parser.add_argument("--reactive-mvar", type=float, default=0.0)
    parser.add_argument("--limit-mva", type=float, required=True)
    parser.add_argument(
        "--priority",
        choices=[item.value for item in PowerPriority],
        default=PowerPriority.ACTIVE.value,
    )
    parser.add_argument("--nominal-frequency-hz", type=float, default=50.0)
    parser.add_argument("--deadband-hz", type=float, default=0.05)
    parser.add_argument("--full-response-deviation-hz", type=float, default=0.50)
    parser.add_argument("--max-discharge-mw", type=float, default=100.0)
    parser.add_argument("--max-charge-mw", type=float, default=100.0)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    curve = FrequencyWattCurve(
        nominal_frequency_hz=args.nominal_frequency_hz,
        deadband_hz=args.deadband_hz,
        full_response_deviation_hz=args.full_response_deviation_hz,
        max_discharge_mw=args.max_discharge_mw,
        max_charge_mw=args.max_charge_mw,
    )
    result = dispatch_frequency_watt(
        frequency_hz=args.frequency_hz,
        baseline_active_mw=args.baseline_active_mw,
        reactive_power_mvar=args.reactive_mvar,
        apparent_power_limit_mva=args.limit_mva,
        curve=curve,
        priority=args.priority,
    )
    capability = result.capability
    print(f"Frequency: {result.frequency_hz:.3f} Hz")
    print(f"Droop adjustment: {result.droop_adjustment_mw:.3f} MW")
    print(f"Unconstrained active request: {result.unconstrained_active_mw:.3f} MW")
    print(f"Storage-bounded active request: {result.bounded_active_mw:.3f} MW")
    print(f"Storage power limited: {str(result.storage_power_limited).lower()}")
    print(f"Capability priority: {capability.priority.value}")
    print(f"Capability limited: {str(capability.limited).lower()}")
    print(f"Delivered active power: {capability.active_mw:.3f} MW")
    print(f"Delivered reactive power: {capability.reactive_mvar:.3f} MVAr")
    print(f"Delivered apparent power: {capability.apparent_power_mva:.3f} MVA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
