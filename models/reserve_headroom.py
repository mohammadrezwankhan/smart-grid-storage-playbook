from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

try:
    from models.energy_limits import StorageEnergyState, limit_active_power_by_energy
    from models.pq_capability import (
        CapabilityBoundary,
        PowerPriority,
        allocate_power_on_boundary,
        load_capability_curve_csv,
        load_directional_capability_csv,
    )
except ModuleNotFoundError:
    from energy_limits import StorageEnergyState, limit_active_power_by_energy
    from pq_capability import (
        CapabilityBoundary,
        PowerPriority,
        allocate_power_on_boundary,
        load_capability_curve_csv,
        load_directional_capability_csv,
    )


@dataclass(frozen=True)
class ReserveHeadroom:
    """Sustained active-power reserve available around a feasible baseline."""

    baseline_active_mw: float
    reactive_power_mvar: float
    duration_minutes: float
    upward_limit_active_mw: float
    downward_limit_active_mw: float
    upward_reserve_mw: float
    downward_reserve_mw: float
    upward_energy_limited: bool
    downward_energy_limited: bool
    upward_capability_limited: bool
    downward_capability_limited: bool


def _capability_active_limit(
    requested_active_mw: float,
    reactive_power_mvar: float,
    capability_boundary: CapabilityBoundary,
) -> float:
    allocation = allocate_power_on_boundary(
        requested_active_mw,
        reactive_power_mvar,
        capability_boundary,
        PowerPriority.REACTIVE,
    )
    if not math.isclose(
        allocation.reactive_mvar,
        reactive_power_mvar,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("reactive_power_mvar exceeds the capability boundary")
    return allocation.active_mw


def calculate_reserve_headroom(
    baseline_active_mw: float,
    duration_minutes: float,
    maximum_discharge_mw: float,
    maximum_charge_mw: float,
    state: StorageEnergyState,
    *,
    reactive_power_mvar: float = 0.0,
    capability_boundary: CapabilityBoundary | None = None,
) -> ReserveHeadroom:
    """Return sustained upward and downward reserve for one response duration."""

    values = {
        "baseline_active_mw": baseline_active_mw,
        "maximum_discharge_mw": maximum_discharge_mw,
        "maximum_charge_mw": maximum_charge_mw,
        "reactive_power_mvar": reactive_power_mvar,
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if maximum_discharge_mw < 0.0:
        raise ValueError("maximum_discharge_mw must be nonnegative")
    if maximum_charge_mw < 0.0:
        raise ValueError("maximum_charge_mw must be nonnegative")
    if not -maximum_charge_mw <= baseline_active_mw <= maximum_discharge_mw:
        raise ValueError("baseline_active_mw must be within the configured power limits")

    upward_capability_limit_mw = maximum_discharge_mw
    downward_capability_limit_mw = -maximum_charge_mw
    upward_capability_limited = False
    downward_capability_limited = False
    if capability_boundary is None:
        if reactive_power_mvar != 0.0:
            raise ValueError(
                "capability_boundary is required when reactive_power_mvar is nonzero"
            )
    else:
        capability_baseline_mw = _capability_active_limit(
            baseline_active_mw,
            reactive_power_mvar,
            capability_boundary,
        )
        if not math.isclose(
            capability_baseline_mw,
            baseline_active_mw,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError(
                "baseline_active_mw is outside the capability boundary at the "
                "configured reactive power"
            )
        upward_capability_limit_mw = _capability_active_limit(
            maximum_discharge_mw,
            reactive_power_mvar,
            capability_boundary,
        )
        downward_capability_limit_mw = _capability_active_limit(
            -maximum_charge_mw,
            reactive_power_mvar,
            capability_boundary,
        )
        upward_capability_limited = not math.isclose(
            upward_capability_limit_mw,
            maximum_discharge_mw,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        downward_capability_limited = not math.isclose(
            downward_capability_limit_mw,
            -maximum_charge_mw,
            rel_tol=0.0,
            abs_tol=1e-12,
        )

    baseline = limit_active_power_by_energy(
        baseline_active_mw,
        duration_minutes,
        state,
    )
    if baseline.energy_limited:
        raise ValueError(
            "baseline_active_mw cannot be sustained for the response duration"
        )

    upward = limit_active_power_by_energy(
        upward_capability_limit_mw,
        duration_minutes,
        state,
    )
    downward = limit_active_power_by_energy(
        downward_capability_limit_mw,
        duration_minutes,
        state,
    )

    return ReserveHeadroom(
        baseline_active_mw=baseline_active_mw,
        reactive_power_mvar=reactive_power_mvar,
        duration_minutes=duration_minutes,
        upward_limit_active_mw=upward.delivered_active_mw,
        downward_limit_active_mw=downward.delivered_active_mw,
        upward_reserve_mw=max(
            0.0,
            upward.delivered_active_mw - baseline_active_mw,
        ),
        downward_reserve_mw=max(
            0.0,
            baseline_active_mw - downward.delivered_active_mw,
        ),
        upward_energy_limited=upward.energy_limited,
        downward_energy_limited=downward.energy_limited,
        upward_capability_limited=upward_capability_limited,
        downward_capability_limited=downward_capability_limited,
    )


def add_capability_boundary_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--reactive-mvar", type=float, default=0.0)
    boundary = parser.add_mutually_exclusive_group()
    boundary.add_argument("--limit-mva", type=float)
    boundary.add_argument("--curve-csv", type=Path)
    boundary.add_argument("--directional-curve-csv", type=Path)


def capability_boundary_from_args(
    args: argparse.Namespace,
) -> CapabilityBoundary | None:
    if args.curve_csv is not None:
        return load_capability_curve_csv(args.curve_csv)
    if args.directional_curve_csv is not None:
        return load_directional_capability_csv(args.directional_curve_csv)
    return args.limit_mva


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate sustained active-power reserve around a baseline."
    )
    parser.add_argument("--baseline-active-mw", type=float, required=True)
    parser.add_argument("--duration-minutes", type=float, required=True)
    parser.add_argument("--maximum-discharge-mw", type=float, required=True)
    parser.add_argument("--maximum-charge-mw", type=float, required=True)
    parser.add_argument("--energy-capacity-mwh", type=float, required=True)
    parser.add_argument("--initial-soc", type=float, required=True)
    parser.add_argument("--minimum-soc", type=float, default=0.10)
    parser.add_argument("--maximum-soc", type=float, default=0.90)
    parser.add_argument("--charge-efficiency", type=float, default=0.95)
    parser.add_argument("--discharge-efficiency", type=float, default=0.95)
    parser.add_argument("--auxiliary-load-mw", type=float, default=0.0)
    parser.add_argument("--self-discharge-rate-per-hour", type=float, default=0.0)
    add_capability_boundary_arguments(parser)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = calculate_reserve_headroom(
        baseline_active_mw=args.baseline_active_mw,
        duration_minutes=args.duration_minutes,
        maximum_discharge_mw=args.maximum_discharge_mw,
        maximum_charge_mw=args.maximum_charge_mw,
        state=StorageEnergyState(
            energy_capacity_mwh=args.energy_capacity_mwh,
            initial_soc=args.initial_soc,
            minimum_soc=args.minimum_soc,
            maximum_soc=args.maximum_soc,
            charge_efficiency=args.charge_efficiency,
            discharge_efficiency=args.discharge_efficiency,
            auxiliary_load_mw=args.auxiliary_load_mw,
            self_discharge_rate_per_hour=args.self_discharge_rate_per_hour,
        ),
        reactive_power_mvar=args.reactive_mvar,
        capability_boundary=capability_boundary_from_args(args),
    )

    print(f"Response duration: {result.duration_minutes:.3f} minutes")
    print(f"Baseline active power: {result.baseline_active_mw:.3f} MW")
    print(f"Reactive power obligation: {result.reactive_power_mvar:.3f} MVAr")
    print(f"Upward active-power limit: {result.upward_limit_active_mw:.3f} MW")
    print(
        "Downward active-power limit: "
        f"{result.downward_limit_active_mw:.3f} MW"
    )
    print(f"Upward reserve: {result.upward_reserve_mw:.3f} MW")
    print(f"Downward reserve: {result.downward_reserve_mw:.3f} MW")
    print(f"Upward energy limited: {str(result.upward_energy_limited).lower()}")
    print(
        "Downward energy limited: "
        f"{str(result.downward_energy_limited).lower()}"
    )
    print(
        "Upward capability limited: "
        f"{str(result.upward_capability_limited).lower()}"
    )
    print(
        "Downward capability limited: "
        f"{str(result.downward_capability_limited).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
