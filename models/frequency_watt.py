from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Sequence

try:
    from models.energy_limits import (
        EnergyLimitedDispatch,
        StorageEnergyState,
        limit_active_power_by_energy,
    )
except ModuleNotFoundError:
    from energy_limits import (
        EnergyLimitedDispatch,
        StorageEnergyState,
        limit_active_power_by_energy,
    )

try:
    from models.pq_capability import (
        CapabilityResult,
        PowerPriority,
        allocate_power,
    )
except ModuleNotFoundError:
    from pq_capability import CapabilityResult, PowerPriority, allocate_power

try:
    from models.ramp_limits import (
        RampLimitedDispatch,
        RampRateLimits,
        limit_active_power_by_ramp,
    )
except ModuleNotFoundError:
    from ramp_limits import (
        RampLimitedDispatch,
        RampRateLimits,
        limit_active_power_by_ramp,
    )


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
    power_bounded_active_mw: float
    ramp_bounded_active_mw: float
    bounded_active_mw: float
    storage_power_limited: bool
    ramp: RampLimitedDispatch | None
    energy: EnergyLimitedDispatch | None
    delivered_energy: EnergyLimitedDispatch | None
    capability: CapabilityResult


def dispatch_frequency_watt(
    frequency_hz: float,
    baseline_active_mw: float,
    reactive_power_mvar: float,
    apparent_power_limit_mva: float,
    curve: FrequencyWattCurve = FrequencyWattCurve(),
    priority: PowerPriority | str = PowerPriority.ACTIVE,
    energy_state: StorageEnergyState | None = None,
    duration_minutes: float | None = None,
    ramp_limits: RampRateLimits | None = None,
    previous_active_mw: float | None = None,
    ramp_interval_seconds: float | None = None,
) -> FrequencyWattDispatch:
    """Evaluate frequency response with optional ramp and energy enforcement."""

    if not math.isfinite(baseline_active_mw):
        raise ValueError("baseline_active_mw must be finite")

    adjustment_mw = curve.active_adjustment_mw(frequency_hz)
    unconstrained_active_mw = baseline_active_mw + adjustment_mw
    power_bounded_active_mw = max(
        -curve.max_charge_mw,
        min(curve.max_discharge_mw, unconstrained_active_mw),
    )
    storage_power_limited = not math.isclose(
        unconstrained_active_mw,
        power_bounded_active_mw,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    if (energy_state is None) != (duration_minutes is None):
        raise ValueError("energy_state and duration_minutes must be provided together")
    ramp_inputs = (ramp_limits, previous_active_mw, ramp_interval_seconds)
    if any(value is not None for value in ramp_inputs) and not all(
        value is not None for value in ramp_inputs
    ):
        raise ValueError(
            "ramp_limits, previous_active_mw, and ramp_interval_seconds "
            "must be provided together"
        )
    ramp = None
    ramp_bounded_active_mw = power_bounded_active_mw
    if (
        ramp_limits is not None
        and previous_active_mw is not None
        and ramp_interval_seconds is not None
    ):
        if not (-curve.max_charge_mw <= previous_active_mw <= curve.max_discharge_mw):
            raise ValueError(
                "previous_active_mw must be within configured storage power limits"
            )
        ramp = limit_active_power_by_ramp(
            power_bounded_active_mw,
            previous_active_mw,
            ramp_interval_seconds,
            ramp_limits,
        )
        ramp_bounded_active_mw = ramp.delivered_active_mw
    energy = None
    bounded_active_mw = ramp_bounded_active_mw
    if energy_state is not None and duration_minutes is not None:
        energy = limit_active_power_by_energy(
            ramp_bounded_active_mw,
            duration_minutes,
            energy_state,
        )
        bounded_active_mw = energy.delivered_active_mw
    capability = allocate_power(
        bounded_active_mw,
        reactive_power_mvar,
        apparent_power_limit_mva,
        priority,
    )
    delivered_energy = None
    if energy_state is not None and duration_minutes is not None:
        delivered_energy = limit_active_power_by_energy(
            capability.active_mw,
            duration_minutes,
            energy_state,
        )
    return FrequencyWattDispatch(
        frequency_hz=frequency_hz,
        baseline_active_mw=baseline_active_mw,
        droop_adjustment_mw=adjustment_mw,
        unconstrained_active_mw=unconstrained_active_mw,
        power_bounded_active_mw=power_bounded_active_mw,
        ramp_bounded_active_mw=ramp_bounded_active_mw,
        bounded_active_mw=bounded_active_mw,
        storage_power_limited=storage_power_limited,
        ramp=ramp,
        energy=energy,
        delivered_energy=delivered_energy,
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
    parser.add_argument("--previous-active-mw", type=float)
    parser.add_argument("--ramp-interval-seconds", type=float)
    parser.add_argument("--ramp-up-mw-per-minute", type=float)
    parser.add_argument("--ramp-down-mw-per-minute", type=float)
    parser.add_argument("--duration-minutes", type=float)
    parser.add_argument("--energy-capacity-mwh", type=float)
    parser.add_argument("--initial-soc", type=float)
    parser.add_argument("--minimum-soc", type=float)
    parser.add_argument("--maximum-soc", type=float)
    parser.add_argument("--charge-efficiency", type=float)
    parser.add_argument("--discharge-efficiency", type=float)
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
    energy_inputs = (
        args.duration_minutes,
        args.energy_capacity_mwh,
        args.initial_soc,
        args.minimum_soc,
        args.maximum_soc,
        args.charge_efficiency,
        args.discharge_efficiency,
    )
    required_energy_inputs = (
        args.duration_minutes,
        args.energy_capacity_mwh,
        args.initial_soc,
    )
    if any(value is not None for value in energy_inputs) and not all(
        value is not None for value in required_energy_inputs
    ):
        raise ValueError(
            "duration_minutes, energy_capacity_mwh, and initial_soc "
            "must be provided together"
        )
    energy_state = None
    if args.energy_capacity_mwh is not None and args.initial_soc is not None:
        energy_state = StorageEnergyState(
            energy_capacity_mwh=args.energy_capacity_mwh,
            initial_soc=args.initial_soc,
            minimum_soc=0.10 if args.minimum_soc is None else args.minimum_soc,
            maximum_soc=0.90 if args.maximum_soc is None else args.maximum_soc,
            charge_efficiency=(
                0.95 if args.charge_efficiency is None else args.charge_efficiency
            ),
            discharge_efficiency=(
                0.95 if args.discharge_efficiency is None else args.discharge_efficiency
            ),
        )
    ramp_inputs = (
        args.previous_active_mw,
        args.ramp_interval_seconds,
        args.ramp_up_mw_per_minute,
        args.ramp_down_mw_per_minute,
    )
    if any(value is not None for value in ramp_inputs) and not all(
        value is not None for value in ramp_inputs
    ):
        raise ValueError(
            "previous_active_mw, ramp_interval_seconds, "
            "ramp_up_mw_per_minute, and ramp_down_mw_per_minute "
            "must be provided together"
        )
    ramp_limits = None
    if (
        args.ramp_up_mw_per_minute is not None
        and args.ramp_down_mw_per_minute is not None
    ):
        ramp_limits = RampRateLimits(
            args.ramp_up_mw_per_minute,
            args.ramp_down_mw_per_minute,
        )
    result = dispatch_frequency_watt(
        frequency_hz=args.frequency_hz,
        baseline_active_mw=args.baseline_active_mw,
        reactive_power_mvar=args.reactive_mvar,
        apparent_power_limit_mva=args.limit_mva,
        curve=curve,
        priority=args.priority,
        energy_state=energy_state,
        duration_minutes=args.duration_minutes,
        ramp_limits=ramp_limits,
        previous_active_mw=args.previous_active_mw,
        ramp_interval_seconds=args.ramp_interval_seconds,
    )
    capability = result.capability
    print(f"Frequency: {result.frequency_hz:.3f} Hz")
    print(f"Droop adjustment: {result.droop_adjustment_mw:.3f} MW")
    print(f"Unconstrained active request: {result.unconstrained_active_mw:.3f} MW")
    if result.ramp is not None or result.energy is not None:
        print(f"Power-bounded active request: {result.power_bounded_active_mw:.3f} MW")
    if result.ramp is not None:
        direction = (
            "none"
            if result.ramp.limiting_direction is None
            else result.ramp.limiting_direction.value
        )
        print(f"Previous active power: {result.ramp.previous_active_mw:.3f} MW")
        print(f"Ramp-bounded active request: {result.ramp_bounded_active_mw:.3f} MW")
        print(f"Ramp limited: {str(result.ramp.ramp_limited).lower()}")
        print(f"Ramp limiting direction: {direction}")
    print(f"Storage-bounded active request: {result.bounded_active_mw:.3f} MW")
    print(f"Storage power limited: {str(result.storage_power_limited).lower()}")
    if result.energy is not None:
        boundary = (
            "none"
            if result.energy.limiting_boundary is None
            else result.energy.limiting_boundary.value
        )
        print(f"Energy limited: {str(result.energy.energy_limited).lower()}")
        print(f"Energy limiting boundary: {boundary}")
        assert result.delivered_energy is not None
        print(f"Ending SOC: {result.delivered_energy.ending_soc:.4f}")
    print(f"Capability priority: {capability.priority.value}")
    print(f"Capability limited: {str(capability.limited).lower()}")
    print(f"Delivered active power: {capability.active_mw:.3f} MW")
    print(f"Delivered reactive power: {capability.reactive_mvar:.3f} MVAr")
    print(f"Delivered apparent power: {capability.apparent_power_mva:.3f} MVA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
