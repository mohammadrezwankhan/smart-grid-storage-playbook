from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from enum import Enum


class PowerPriority(str, Enum):
    ACTIVE = "active"
    REACTIVE = "reactive"
    PROPORTIONAL = "proportional"


@dataclass(frozen=True)
class CapabilityResult:
    requested_active_mw: float
    requested_reactive_mvar: float
    active_mw: float
    reactive_mvar: float
    apparent_power_mva: float
    utilization: float
    curtailed_active_mw: float
    curtailed_reactive_mvar: float
    limited: bool
    priority: PowerPriority


def _clip(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def allocate_power(
    requested_active_mw: float,
    requested_reactive_mvar: float,
    apparent_power_limit_mva: float,
    priority: PowerPriority | str = PowerPriority.ACTIVE,
) -> CapabilityResult:
    """Apply a circular P-Q capability limit using the selected priority."""

    values = {
        "requested_active_mw": requested_active_mw,
        "requested_reactive_mvar": requested_reactive_mvar,
        "apparent_power_limit_mva": apparent_power_limit_mva,
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if apparent_power_limit_mva <= 0.0:
        raise ValueError("apparent_power_limit_mva must be positive")

    try:
        selected_priority = PowerPriority(priority)
    except ValueError as error:
        choices = ", ".join(item.value for item in PowerPriority)
        raise ValueError(f"priority must be one of: {choices}") from error

    requested_mva = math.hypot(
        requested_active_mw,
        requested_reactive_mvar,
    )
    if requested_mva <= apparent_power_limit_mva:
        active_mw = requested_active_mw
        reactive_mvar = requested_reactive_mvar
    elif selected_priority is PowerPriority.ACTIVE:
        active_mw = _clip(requested_active_mw, apparent_power_limit_mva)
        reactive_limit = math.sqrt(
            max(0.0, apparent_power_limit_mva**2 - active_mw**2)
        )
        reactive_mvar = _clip(requested_reactive_mvar, reactive_limit)
    elif selected_priority is PowerPriority.REACTIVE:
        reactive_mvar = _clip(
            requested_reactive_mvar,
            apparent_power_limit_mva,
        )
        active_limit = math.sqrt(
            max(0.0, apparent_power_limit_mva**2 - reactive_mvar**2)
        )
        active_mw = _clip(requested_active_mw, active_limit)
    else:
        scale = apparent_power_limit_mva / requested_mva
        active_mw = requested_active_mw * scale
        reactive_mvar = requested_reactive_mvar * scale

    apparent_power_mva = math.hypot(active_mw, reactive_mvar)
    active_curtailment = requested_active_mw - active_mw
    reactive_curtailment = requested_reactive_mvar - reactive_mvar
    limited = not (
        math.isclose(active_curtailment, 0.0, rel_tol=0.0, abs_tol=1e-12)
        and math.isclose(reactive_curtailment, 0.0, rel_tol=0.0, abs_tol=1e-12)
    )

    return CapabilityResult(
        requested_active_mw=requested_active_mw,
        requested_reactive_mvar=requested_reactive_mvar,
        active_mw=active_mw,
        reactive_mvar=reactive_mvar,
        apparent_power_mva=apparent_power_mva,
        utilization=apparent_power_mva / apparent_power_limit_mva,
        curtailed_active_mw=active_curtailment,
        curtailed_reactive_mvar=reactive_curtailment,
        limited=limited,
        priority=selected_priority,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply a circular inverter P-Q capability limit."
    )
    parser.add_argument("--active-mw", type=float, required=True)
    parser.add_argument("--reactive-mvar", type=float, required=True)
    parser.add_argument("--limit-mva", type=float, required=True)
    parser.add_argument(
        "--priority",
        choices=[item.value for item in PowerPriority],
        default=PowerPriority.ACTIVE.value,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = allocate_power(
        args.active_mw,
        args.reactive_mvar,
        args.limit_mva,
        args.priority,
    )
    print(f"Priority: {result.priority.value}")
    print(f"Limited: {str(result.limited).lower()}")
    print(f"Active power: {result.active_mw:.3f} MW")
    print(f"Reactive power: {result.reactive_mvar:.3f} MVAr")
    print(f"Apparent power: {result.apparent_power_mva:.3f} MVA")
    print(f"Capability utilization: {100.0 * result.utilization:.2f}%")
    print(f"Active curtailment: {result.curtailed_active_mw:.3f} MW")
    print(
        "Reactive curtailment: "
        f"{result.curtailed_reactive_mvar:.3f} MVAr"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
