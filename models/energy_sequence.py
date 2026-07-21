from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, replace
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


@dataclass(frozen=True)
class EnergyDispatchSequence:
    """Reviewable SOC and energy accounting for a requested power trajectory."""

    intervals: tuple[EnergyLimitedDispatch, ...]
    initial_soc: float
    ending_soc: float
    total_duration_minutes: float
    requested_ac_energy_mwh: float
    delivered_ac_energy_mwh: float
    curtailed_ac_energy_mwh: float
    dispatch_stored_energy_change_mwh: float
    auxiliary_energy_mwh: float
    self_discharge_energy_mwh: float
    stored_energy_change_mwh: float
    soc_balance_error: float
    limited_interval_count: int


def simulate_energy_dispatch_sequence(
    requested_active_mw: Sequence[float],
    duration_minutes: Sequence[float],
    state: StorageEnergyState,
) -> EnergyDispatchSequence:
    """Carry SOC through variable-duration requests using the interval limiter."""

    requests = tuple(requested_active_mw)
    durations = tuple(duration_minutes)
    if not requests:
        raise ValueError("requested_active_mw must contain at least one interval")
    if len(requests) != len(durations):
        raise ValueError(
            "requested_active_mw and duration_minutes must have equal lengths"
        )

    state.validate()
    interval_results: list[EnergyLimitedDispatch] = []
    current_state = state
    for requested_power_mw, interval_minutes in zip(
        requests,
        durations,
        strict=True,
    ):
        interval_result = limit_active_power_by_energy(
            requested_power_mw,
            interval_minutes,
            current_state,
        )
        interval_results.append(interval_result)
        current_state = replace(
            current_state,
            initial_soc=interval_result.ending_soc,
        )

    intervals = tuple(interval_results)
    requested_ac_energy_mwh = math.fsum(
        interval.requested_active_mw * interval.duration_minutes / 60.0
        for interval in intervals
    )
    delivered_ac_energy_mwh = math.fsum(
        interval.delivered_active_mw * interval.duration_minutes / 60.0
        for interval in intervals
    )
    curtailed_ac_energy_mwh = math.fsum(
        abs(interval.requested_active_mw - interval.delivered_active_mw)
        * interval.duration_minutes
        / 60.0
        for interval in intervals
    )
    dispatch_stored_energy_change_mwh = math.fsum(
        interval.dispatch_stored_energy_change_mwh for interval in intervals
    )
    auxiliary_energy_mwh = math.fsum(
        interval.auxiliary_energy_mwh for interval in intervals
    )
    self_discharge_energy_mwh = math.fsum(
        interval.self_discharge_energy_mwh for interval in intervals
    )
    stored_energy_change_mwh = math.fsum(
        interval.stored_energy_change_mwh for interval in intervals
    )
    ending_soc = intervals[-1].ending_soc
    expected_ending_soc = (
        state.initial_soc + stored_energy_change_mwh / state.energy_capacity_mwh
    )

    return EnergyDispatchSequence(
        intervals=intervals,
        initial_soc=state.initial_soc,
        ending_soc=ending_soc,
        total_duration_minutes=math.fsum(durations),
        requested_ac_energy_mwh=requested_ac_energy_mwh,
        delivered_ac_energy_mwh=delivered_ac_energy_mwh,
        curtailed_ac_energy_mwh=curtailed_ac_energy_mwh,
        dispatch_stored_energy_change_mwh=dispatch_stored_energy_change_mwh,
        auxiliary_energy_mwh=auxiliary_energy_mwh,
        self_discharge_energy_mwh=self_discharge_energy_mwh,
        stored_energy_change_mwh=stored_energy_change_mwh,
        soc_balance_error=ending_soc - expected_ending_soc,
        limited_interval_count=sum(interval.energy_limited for interval in intervals),
    )


def _parse_number_series(value: str) -> tuple[float, ...]:
    raw_values = value.split(",")
    if not raw_values or any(not raw_value.strip() for raw_value in raw_values):
        raise argparse.ArgumentTypeError(
            "profiles must be comma-separated numbers without empty entries"
        )
    try:
        values = tuple(float(raw_value) for raw_value in raw_values)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "profiles must contain only comma-separated numbers"
        ) from error
    if any(not math.isfinite(number) for number in values):
        raise argparse.ArgumentTypeError("profile values must be finite")
    return values


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carry SOC through a requested multi-interval power trajectory."
    )
    parser.add_argument(
        "--active-mw-profile",
        type=_parse_number_series,
        required=True,
    )
    parser.add_argument(
        "--duration-minutes-profile",
        type=_parse_number_series,
        required=True,
    )
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
    state = StorageEnergyState(
        energy_capacity_mwh=args.energy_capacity_mwh,
        initial_soc=args.initial_soc,
        minimum_soc=args.minimum_soc,
        maximum_soc=args.maximum_soc,
        charge_efficiency=args.charge_efficiency,
        discharge_efficiency=args.discharge_efficiency,
        auxiliary_load_mw=args.auxiliary_load_mw,
        self_discharge_rate_per_hour=args.self_discharge_rate_per_hour,
    )
    result = simulate_energy_dispatch_sequence(
        args.active_mw_profile,
        args.duration_minutes_profile,
        state,
    )

    print(f"Intervals: {len(result.intervals)}")
    print(f"Limited intervals: {result.limited_interval_count}")
    print(f"Total duration: {result.total_duration_minutes:.3f} minutes")
    print(f"Initial SOC: {result.initial_soc:.4f}")
    print(f"Ending SOC: {result.ending_soc:.4f}")
    print(f"Requested AC energy: {result.requested_ac_energy_mwh:.3f} MWh")
    print(f"Delivered AC energy: {result.delivered_ac_energy_mwh:.3f} MWh")
    print(f"Curtailed AC energy: {result.curtailed_ac_energy_mwh:.3f} MWh")
    print(
        "Dispatch stored-energy change: "
        f"{result.dispatch_stored_energy_change_mwh:.3f} MWh"
    )
    print(f"Auxiliary energy: {result.auxiliary_energy_mwh:.3f} MWh")
    print(f"Self-discharge energy: {result.self_discharge_energy_mwh:.3f} MWh")
    print(f"Stored energy change: {result.stored_energy_change_mwh:.3f} MWh")
    print(f"SOC balance error: {result.soc_balance_error:.3e}")
    for interval_index, interval in enumerate(result.intervals, start=1):
        boundary = (
            "none"
            if interval.limiting_boundary is None
            else interval.limiting_boundary.value
        )
        print(
            f"Interval {interval_index}: "
            f"requested={interval.requested_active_mw:.3f} MW, "
            f"delivered={interval.delivered_active_mw:.3f} MW, "
            f"duration={interval.duration_minutes:.3f} min, "
            f"ending_soc={interval.ending_soc:.4f}, "
            f"boundary={boundary}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
