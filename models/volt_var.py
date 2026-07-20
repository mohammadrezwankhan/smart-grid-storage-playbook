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
class VoltVarCurve:
    """Illustrative four-breakpoint voltage-to-reactive-power curve."""

    low_saturation_pu: float = 0.92
    low_deadband_pu: float = 0.98
    high_deadband_pu: float = 1.02
    high_saturation_pu: float = 1.08
    max_reactive_power_pu: float = 1.0

    def validate(self) -> None:
        values = {
            "low_saturation_pu": self.low_saturation_pu,
            "low_deadband_pu": self.low_deadband_pu,
            "high_deadband_pu": self.high_deadband_pu,
            "high_saturation_pu": self.high_saturation_pu,
            "max_reactive_power_pu": self.max_reactive_power_pu,
        }
        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if not (
            0.0
            < self.low_saturation_pu
            < self.low_deadband_pu
            <= 1.0
            <= self.high_deadband_pu
            < self.high_saturation_pu
        ):
            raise ValueError(
                "voltage breakpoints must satisfy "
                "0 < low saturation < low deadband <= 1 <= high deadband "
                "< high saturation"
            )
        if self.max_reactive_power_pu <= 0.0:
            raise ValueError("max_reactive_power_pu must be positive")

    def reactive_request_pu(self, voltage_pu: float) -> float:
        """Return positive Q injection at low voltage and absorption at high."""

        self.validate()
        if not math.isfinite(voltage_pu) or voltage_pu < 0.0:
            raise ValueError("voltage_pu must be finite and nonnegative")
        if voltage_pu <= self.low_saturation_pu:
            return self.max_reactive_power_pu
        if voltage_pu < self.low_deadband_pu:
            fraction = (self.low_deadband_pu - voltage_pu) / (
                self.low_deadband_pu - self.low_saturation_pu
            )
            return self.max_reactive_power_pu * fraction
        if voltage_pu <= self.high_deadband_pu:
            return 0.0
        if voltage_pu < self.high_saturation_pu:
            fraction = (voltage_pu - self.high_deadband_pu) / (
                self.high_saturation_pu - self.high_deadband_pu
            )
            return -self.max_reactive_power_pu * fraction
        return -self.max_reactive_power_pu


@dataclass(frozen=True)
class VoltVarDispatch:
    voltage_pu: float
    reactive_request_pu: float
    requested_reactive_mvar: float
    capability: CapabilityResult


def dispatch_volt_var(
    voltage_pu: float,
    active_power_mw: float,
    apparent_power_limit_mva: float,
    reactive_base_mvar: float | None = None,
    curve: VoltVarCurve = VoltVarCurve(),
    priority: PowerPriority | str = PowerPriority.REACTIVE,
) -> VoltVarDispatch:
    """Evaluate a Volt-VAR request and enforce circular inverter capability."""

    base_mvar = (
        apparent_power_limit_mva if reactive_base_mvar is None else reactive_base_mvar
    )
    if not math.isfinite(base_mvar) or base_mvar <= 0.0:
        raise ValueError("reactive_base_mvar must be finite and positive")
    request_pu = curve.reactive_request_pu(voltage_pu)
    requested_reactive_mvar = request_pu * base_mvar
    capability = allocate_power(
        active_power_mw,
        requested_reactive_mvar,
        apparent_power_limit_mva,
        priority,
    )
    return VoltVarDispatch(
        voltage_pu=voltage_pu,
        reactive_request_pu=request_pu,
        requested_reactive_mvar=requested_reactive_mvar,
        capability=capability,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate an illustrative Volt-VAR command and P-Q limit."
    )
    parser.add_argument("--voltage-pu", type=float, required=True)
    parser.add_argument("--active-mw", type=float, required=True)
    parser.add_argument("--limit-mva", type=float, required=True)
    parser.add_argument("--reactive-base-mvar", type=float)
    parser.add_argument(
        "--priority",
        choices=[item.value for item in PowerPriority],
        default=PowerPriority.REACTIVE.value,
    )
    parser.add_argument("--low-saturation-pu", type=float, default=0.92)
    parser.add_argument("--low-deadband-pu", type=float, default=0.98)
    parser.add_argument("--high-deadband-pu", type=float, default=1.02)
    parser.add_argument("--high-saturation-pu", type=float, default=1.08)
    parser.add_argument("--max-reactive-power-pu", type=float, default=1.0)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    curve = VoltVarCurve(
        low_saturation_pu=args.low_saturation_pu,
        low_deadband_pu=args.low_deadband_pu,
        high_deadband_pu=args.high_deadband_pu,
        high_saturation_pu=args.high_saturation_pu,
        max_reactive_power_pu=args.max_reactive_power_pu,
    )
    result = dispatch_volt_var(
        voltage_pu=args.voltage_pu,
        active_power_mw=args.active_mw,
        apparent_power_limit_mva=args.limit_mva,
        reactive_base_mvar=args.reactive_base_mvar,
        curve=curve,
        priority=args.priority,
    )
    capability = result.capability
    print(f"Voltage: {result.voltage_pu:.3f} pu")
    print(f"Volt-VAR request: {result.reactive_request_pu:.3f} pu")
    print(f"Requested reactive power: {result.requested_reactive_mvar:.3f} MVAr")
    print(f"Capability priority: {capability.priority.value}")
    print(f"Capability limited: {str(capability.limited).lower()}")
    print(f"Delivered active power: {capability.active_mw:.3f} MW")
    print(f"Delivered reactive power: {capability.reactive_mvar:.3f} MVAr")
    print(f"Delivered apparent power: {capability.apparent_power_mva:.3f} MVA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
