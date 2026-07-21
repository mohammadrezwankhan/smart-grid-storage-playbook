from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Sequence

try:
    from models.energy_limits import StorageEnergyState, limit_active_power_by_energy
except ModuleNotFoundError:
    from energy_limits import StorageEnergyState, limit_active_power_by_energy


@dataclass(frozen=True)
class ReserveHeadroom:
    """Sustained active-power reserve available around a feasible baseline."""

    baseline_active_mw: float
    duration_minutes: float
    upward_limit_active_mw: float
    downward_limit_active_mw: float
    upward_reserve_mw: float
    downward_reserve_mw: float
    upward_energy_limited: bool
    downward_energy_limited: bool


def calculate_reserve_headroom(
    baseline_active_mw: float,
    duration_minutes: float,
    maximum_discharge_mw: float,
    maximum_charge_mw: float,
    state: StorageEnergyState,
) -> ReserveHeadroom:
    """Return sustained upward and downward reserve for one response duration."""

    values = {
        "baseline_active_mw": baseline_active_mw,
        "maximum_discharge_mw": maximum_discharge_mw,
        "maximum_charge_mw": maximum_charge_mw,
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
        maximum_discharge_mw,
        duration_minutes,
        state,
    )
    downward = limit_active_power_by_energy(
        -maximum_charge_mw,
        duration_minutes,
        state,
    )

    return ReserveHeadroom(
        baseline_active_mw=baseline_active_mw,
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
    )


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
    )

    print(f"Response duration: {result.duration_minutes:.3f} minutes")
    print(f"Baseline active power: {result.baseline_active_mw:.3f} MW")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
