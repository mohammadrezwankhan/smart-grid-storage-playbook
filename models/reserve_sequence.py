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
    from models.reserve_headroom import ReserveHeadroom, calculate_reserve_headroom
except ModuleNotFoundError:
    from energy_limits import (
        EnergyLimitedDispatch,
        StorageEnergyState,
        limit_active_power_by_energy,
    )
    from reserve_headroom import ReserveHeadroom, calculate_reserve_headroom


@dataclass(frozen=True)
class ReserveSequenceInterval:
    """Reserve assessment and baseline dispatch for one schedule interval."""

    index: int
    reserve: ReserveHeadroom
    baseline_dispatch: EnergyLimitedDispatch


@dataclass(frozen=True)
class ReserveSequenceAudit:
    """SOC-aware reserve margins carried through a baseline schedule."""

    intervals: tuple[ReserveSequenceInterval, ...]
    response_duration_minutes: float
    initial_soc: float
    ending_soc: float
    total_schedule_duration_minutes: float
    baseline_ac_energy_mwh: float
    stored_energy_change_mwh: float
    auxiliary_energy_mwh: float
    self_discharge_energy_mwh: float
    soc_balance_error: float
    minimum_upward_reserve_mw: float
    minimum_upward_reserve_interval: int
    minimum_downward_reserve_mw: float
    minimum_downward_reserve_interval: int
    upward_energy_limited_interval_count: int
    downward_energy_limited_interval_count: int


def audit_reserve_sequence(
    baseline_active_mw: Sequence[float],
    interval_duration_minutes: Sequence[float],
    response_duration_minutes: float,
    maximum_discharge_mw: float,
    maximum_charge_mw: float,
    state: StorageEnergyState,
) -> ReserveSequenceAudit:
    """Assess sustained reserve before each baseline interval and carry SOC."""

    baselines = tuple(baseline_active_mw)
    durations = tuple(interval_duration_minutes)
    if not baselines:
        raise ValueError("baseline_active_mw must contain at least one interval")
    if len(baselines) != len(durations):
        raise ValueError(
            "baseline_active_mw and interval_duration_minutes must have equal lengths"
        )

    state.validate()
    interval_results: list[ReserveSequenceInterval] = []
    current_state = state
    for index, (baseline_mw, interval_minutes) in enumerate(
        zip(baselines, durations, strict=True),
        start=1,
    ):
        reserve = calculate_reserve_headroom(
            baseline_active_mw=baseline_mw,
            duration_minutes=response_duration_minutes,
            maximum_discharge_mw=maximum_discharge_mw,
            maximum_charge_mw=maximum_charge_mw,
            state=current_state,
        )
        baseline_dispatch = limit_active_power_by_energy(
            baseline_mw,
            interval_minutes,
            current_state,
        )
        if baseline_dispatch.energy_limited:
            raise ValueError(
                f"baseline_active_mw interval {index} cannot be sustained for "
                "its schedule duration"
            )
        interval_results.append(
            ReserveSequenceInterval(
                index=index,
                reserve=reserve,
                baseline_dispatch=baseline_dispatch,
            )
        )
        current_state = replace(
            current_state,
            initial_soc=baseline_dispatch.ending_soc,
        )

    intervals = tuple(interval_results)
    minimum_upward = min(
        intervals,
        key=lambda interval: interval.reserve.upward_reserve_mw,
    )
    minimum_downward = min(
        intervals,
        key=lambda interval: interval.reserve.downward_reserve_mw,
    )
    stored_energy_change_mwh = math.fsum(
        interval.baseline_dispatch.stored_energy_change_mwh
        for interval in intervals
    )
    ending_soc = intervals[-1].baseline_dispatch.ending_soc
    expected_ending_soc = (
        state.initial_soc + stored_energy_change_mwh / state.energy_capacity_mwh
    )

    return ReserveSequenceAudit(
        intervals=intervals,
        response_duration_minutes=response_duration_minutes,
        initial_soc=state.initial_soc,
        ending_soc=ending_soc,
        total_schedule_duration_minutes=math.fsum(durations),
        baseline_ac_energy_mwh=math.fsum(
            baseline_mw * duration_minutes / 60.0
            for baseline_mw, duration_minutes in zip(
                baselines,
                durations,
                strict=True,
            )
        ),
        stored_energy_change_mwh=stored_energy_change_mwh,
        auxiliary_energy_mwh=math.fsum(
            interval.baseline_dispatch.auxiliary_energy_mwh
            for interval in intervals
        ),
        self_discharge_energy_mwh=math.fsum(
            interval.baseline_dispatch.self_discharge_energy_mwh
            for interval in intervals
        ),
        soc_balance_error=ending_soc - expected_ending_soc,
        minimum_upward_reserve_mw=minimum_upward.reserve.upward_reserve_mw,
        minimum_upward_reserve_interval=minimum_upward.index,
        minimum_downward_reserve_mw=minimum_downward.reserve.downward_reserve_mw,
        minimum_downward_reserve_interval=minimum_downward.index,
        upward_energy_limited_interval_count=sum(
            interval.reserve.upward_energy_limited for interval in intervals
        ),
        downward_energy_limited_interval_count=sum(
            interval.reserve.downward_energy_limited for interval in intervals
        ),
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
        description="Audit sustained reserve through a baseline schedule."
    )
    parser.add_argument(
        "--baseline-active-mw-profile",
        type=_parse_number_series,
        required=True,
    )
    parser.add_argument(
        "--interval-duration-minutes-profile",
        type=_parse_number_series,
        required=True,
    )
    parser.add_argument("--response-duration-minutes", type=float, required=True)
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
    result = audit_reserve_sequence(
        baseline_active_mw=args.baseline_active_mw_profile,
        interval_duration_minutes=args.interval_duration_minutes_profile,
        response_duration_minutes=args.response_duration_minutes,
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

    print(f"Intervals: {len(result.intervals)}")
    print(f"Response duration: {result.response_duration_minutes:.3f} minutes")
    print(f"Initial SOC: {result.initial_soc:.4f}")
    print(f"Ending SOC: {result.ending_soc:.4f}")
    print(f"Baseline AC energy: {result.baseline_ac_energy_mwh:.3f} MWh")
    print(
        "Minimum upward reserve: "
        f"{result.minimum_upward_reserve_mw:.3f} MW "
        f"(interval {result.minimum_upward_reserve_interval})"
    )
    print(
        "Minimum downward reserve: "
        f"{result.minimum_downward_reserve_mw:.3f} MW "
        f"(interval {result.minimum_downward_reserve_interval})"
    )
    print(
        "Reserve energy-limited intervals: "
        f"upward={result.upward_energy_limited_interval_count}, "
        f"downward={result.downward_energy_limited_interval_count}"
    )
    print(f"Auxiliary energy: {result.auxiliary_energy_mwh:.3f} MWh")
    print(f"Self-discharge energy: {result.self_discharge_energy_mwh:.3f} MWh")
    print(f"SOC balance error: {result.soc_balance_error:.3e}")
    for interval in result.intervals:
        print(
            f"Interval {interval.index}: "
            f"baseline={interval.reserve.baseline_active_mw:.3f} MW, "
            f"initial_soc={interval.baseline_dispatch.initial_soc:.4f}, "
            f"ending_soc={interval.baseline_dispatch.ending_soc:.4f}, "
            f"upward={interval.reserve.upward_reserve_mw:.3f} MW, "
            f"downward={interval.reserve.downward_reserve_mw:.3f} MW"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
