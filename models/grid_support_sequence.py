from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Sequence

try:
    from models.energy_limits import StorageEnergyState
    from models.frequency_watt import (
        FrequencyWattCurve,
        FrequencyWattDispatch,
        dispatch_frequency_watt,
    )
    from models.measurement_filter import FirstOrderFilterConfig
    from models.pq_capability import (
        DirectionalCapabilityEnvelope,
        PiecewiseCapabilityCurve,
        PowerPriority,
        load_capability_curve_csv,
        load_directional_capability_csv,
        reactive_axis_limit_mvar,
    )
    from models.ramp_limits import RampRateLimits
    from models.volt_var import VoltVarCurve
except ModuleNotFoundError:
    from energy_limits import StorageEnergyState
    from frequency_watt import (
        FrequencyWattCurve,
        FrequencyWattDispatch,
        dispatch_frequency_watt,
    )
    from measurement_filter import FirstOrderFilterConfig
    from pq_capability import (
        DirectionalCapabilityEnvelope,
        PiecewiseCapabilityCurve,
        PowerPriority,
        load_capability_curve_csv,
        load_directional_capability_csv,
        reactive_axis_limit_mvar,
    )
    from ramp_limits import RampRateLimits
    from volt_var import VoltVarCurve


@dataclass(frozen=True)
class GridSupportInterval:
    """One state-linked frequency-watt and Volt-VAR dispatch interval."""

    frequency_hz: float
    voltage_pu: float
    baseline_active_mw: float
    duration_minutes: float
    reactive_request_pu: float
    requested_reactive_mvar: float
    initial_soc: float
    ending_soc: float
    dispatch: FrequencyWattDispatch


@dataclass(frozen=True)
class GridSupportSequence:
    """Aggregated service delivery and state accounting for a profile."""

    intervals: tuple[GridSupportInterval, ...]
    initial_soc: float
    ending_soc: float
    total_duration_minutes: float
    requested_active_energy_mwh: float
    delivered_active_energy_mwh: float
    active_shortfall_energy_mwh: float
    requested_reactive_service_mvarh: float
    delivered_reactive_service_mvarh: float
    reactive_shortfall_service_mvarh: float
    dispatch_stored_energy_change_mwh: float
    auxiliary_energy_mwh: float
    self_discharge_energy_mwh: float
    stored_energy_change_mwh: float
    soc_balance_error: float
    limited_interval_count: int
    storage_power_limited_interval_count: int
    ramp_limited_interval_count: int
    energy_limited_interval_count: int
    capability_limited_interval_count: int


def _validate_profiles(
    frequency_hz: Sequence[float],
    voltage_pu: Sequence[float],
    baseline_active_mw: Sequence[float],
    duration_minutes: Sequence[float],
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    frequencies = tuple(frequency_hz)
    voltages = tuple(voltage_pu)
    baselines = tuple(baseline_active_mw)
    durations = tuple(duration_minutes)
    if not frequencies:
        raise ValueError("profiles must contain at least one interval")
    profile_lengths = {
        len(frequencies),
        len(voltages),
        len(baselines),
        len(durations),
    }
    if len(profile_lengths) != 1:
        raise ValueError("all profiles must have equal lengths")
    for index, duration in enumerate(durations):
        if not math.isfinite(duration) or duration <= 0.0:
            raise ValueError(f"duration_minutes[{index}] must be finite and positive")
    return frequencies, voltages, baselines, durations


def simulate_grid_support_sequence(
    frequency_hz: Sequence[float],
    voltage_pu: Sequence[float],
    baseline_active_mw: Sequence[float],
    duration_minutes: Sequence[float],
    energy_state: StorageEnergyState,
    apparent_power_limit_mva: float | None,
    frequency_curve: FrequencyWattCurve = FrequencyWattCurve(),
    voltage_curve: VoltVarCurve = VoltVarCurve(),
    reactive_base_mvar: float | None = None,
    priority: PowerPriority | str = PowerPriority.REACTIVE,
    ramp_limits: RampRateLimits | None = None,
    initial_active_mw: float | None = None,
    frequency_filter_config: FirstOrderFilterConfig | None = None,
    initial_filtered_frequency_hz: float | None = None,
    capability_envelope: (
        PiecewiseCapabilityCurve | DirectionalCapabilityEnvelope | None
    ) = None,
) -> GridSupportSequence:
    """Compose grid-support controls while carrying plant state between intervals."""

    frequencies, voltages, baselines, durations = _validate_profiles(
        frequency_hz,
        voltage_pu,
        baseline_active_mw,
        duration_minutes,
    )
    energy_state.validate()
    frequency_curve.validate()
    voltage_curve.validate()
    if (apparent_power_limit_mva is None) == (capability_envelope is None):
        raise ValueError(
            "provide exactly one circular MVA limit or sampled capability envelope"
        )
    capability_boundary = (
        capability_envelope
        if capability_envelope is not None
        else apparent_power_limit_mva
    )
    assert capability_boundary is not None
    if reactive_base_mvar is not None and (
        not math.isfinite(reactive_base_mvar) or reactive_base_mvar <= 0.0
    ):
        raise ValueError("reactive_base_mvar must be finite and positive")

    if (ramp_limits is None) != (initial_active_mw is None):
        raise ValueError("ramp_limits and initial_active_mw must be provided together")
    if ramp_limits is not None:
        ramp_limits.validate()
        assert initial_active_mw is not None
        if not math.isfinite(initial_active_mw):
            raise ValueError("initial_active_mw must be finite")
    if (frequency_filter_config is None) != (initial_filtered_frequency_hz is None):
        raise ValueError(
            "frequency_filter_config and initial_filtered_frequency_hz "
            "must be provided together"
        )
    if frequency_filter_config is not None:
        frequency_filter_config.validate()
        assert initial_filtered_frequency_hz is not None
        if (
            not math.isfinite(initial_filtered_frequency_hz)
            or initial_filtered_frequency_hz <= 0.0
        ):
            raise ValueError(
                "initial_filtered_frequency_hz must be finite and positive"
            )

    current_energy_state = energy_state
    previous_active_mw = initial_active_mw
    previous_filtered_frequency_hz = initial_filtered_frequency_hz
    interval_results: list[GridSupportInterval] = []
    for frequency, voltage, baseline, duration in zip(
        frequencies,
        voltages,
        baselines,
        durations,
        strict=True,
    ):
        request_pu = voltage_curve.reactive_request_pu(voltage)
        interval_base_mvar = (
            reactive_axis_limit_mvar(capability_boundary, request_pu)
            if reactive_base_mvar is None
            else reactive_base_mvar
        )
        requested_reactive_mvar = request_pu * interval_base_mvar
        dispatch = dispatch_frequency_watt(
            frequency_hz=frequency,
            baseline_active_mw=baseline,
            reactive_power_mvar=requested_reactive_mvar,
            apparent_power_limit_mva=apparent_power_limit_mva,
            curve=frequency_curve,
            priority=priority,
            energy_state=current_energy_state,
            duration_minutes=duration,
            ramp_limits=ramp_limits,
            previous_active_mw=previous_active_mw,
            ramp_interval_seconds=(None if ramp_limits is None else duration * 60.0),
            frequency_filter_config=frequency_filter_config,
            previous_filtered_frequency_hz=previous_filtered_frequency_hz,
            measurement_interval_seconds=(
                None if frequency_filter_config is None else duration * 60.0
            ),
            capability_envelope=capability_envelope,
        )
        assert dispatch.delivered_energy is not None
        delivered_energy = dispatch.delivered_energy
        interval_results.append(
            GridSupportInterval(
                frequency_hz=frequency,
                voltage_pu=voltage,
                baseline_active_mw=baseline,
                duration_minutes=duration,
                reactive_request_pu=request_pu,
                requested_reactive_mvar=requested_reactive_mvar,
                initial_soc=delivered_energy.initial_soc,
                ending_soc=delivered_energy.ending_soc,
                dispatch=dispatch,
            )
        )
        current_energy_state = replace(
            current_energy_state,
            initial_soc=delivered_energy.ending_soc,
        )
        if ramp_limits is not None:
            previous_active_mw = dispatch.capability.active_mw
        if frequency_filter_config is not None:
            previous_filtered_frequency_hz = dispatch.control_frequency_hz

    intervals = tuple(interval_results)
    requested_active_energy_mwh = math.fsum(
        interval.dispatch.unconstrained_active_mw * interval.duration_minutes / 60.0
        for interval in intervals
    )
    delivered_active_energy_mwh = math.fsum(
        interval.dispatch.capability.active_mw * interval.duration_minutes / 60.0
        for interval in intervals
    )
    active_shortfall_energy_mwh = math.fsum(
        abs(
            interval.dispatch.unconstrained_active_mw
            - interval.dispatch.capability.active_mw
        )
        * interval.duration_minutes
        / 60.0
        for interval in intervals
    )
    requested_reactive_service_mvarh = math.fsum(
        abs(interval.requested_reactive_mvar) * interval.duration_minutes / 60.0
        for interval in intervals
    )
    delivered_reactive_service_mvarh = math.fsum(
        abs(interval.dispatch.capability.reactive_mvar)
        * interval.duration_minutes
        / 60.0
        for interval in intervals
    )
    reactive_shortfall_service_mvarh = math.fsum(
        abs(
            interval.requested_reactive_mvar
            - interval.dispatch.capability.reactive_mvar
        )
        * interval.duration_minutes
        / 60.0
        for interval in intervals
    )
    dispatch_stored_energy_change_mwh = math.fsum(
        interval.dispatch.delivered_energy.dispatch_stored_energy_change_mwh
        for interval in intervals
        if interval.dispatch.delivered_energy is not None
    )
    auxiliary_energy_mwh = math.fsum(
        interval.dispatch.delivered_energy.auxiliary_energy_mwh
        for interval in intervals
        if interval.dispatch.delivered_energy is not None
    )
    self_discharge_energy_mwh = math.fsum(
        interval.dispatch.delivered_energy.self_discharge_energy_mwh
        for interval in intervals
        if interval.dispatch.delivered_energy is not None
    )
    stored_energy_change_mwh = math.fsum(
        interval.dispatch.delivered_energy.stored_energy_change_mwh
        for interval in intervals
        if interval.dispatch.delivered_energy is not None
    )
    ending_soc = intervals[-1].ending_soc
    expected_ending_soc = (
        energy_state.initial_soc
        + stored_energy_change_mwh / energy_state.energy_capacity_mwh
    )

    def interval_is_limited(interval: GridSupportInterval) -> bool:
        dispatch = interval.dispatch
        return (
            dispatch.storage_power_limited
            or (dispatch.ramp is not None and dispatch.ramp.ramp_limited)
            or (dispatch.energy is not None and dispatch.energy.energy_limited)
            or dispatch.capability.limited
        )

    return GridSupportSequence(
        intervals=intervals,
        initial_soc=energy_state.initial_soc,
        ending_soc=ending_soc,
        total_duration_minutes=math.fsum(durations),
        requested_active_energy_mwh=requested_active_energy_mwh,
        delivered_active_energy_mwh=delivered_active_energy_mwh,
        active_shortfall_energy_mwh=active_shortfall_energy_mwh,
        requested_reactive_service_mvarh=requested_reactive_service_mvarh,
        delivered_reactive_service_mvarh=delivered_reactive_service_mvarh,
        reactive_shortfall_service_mvarh=reactive_shortfall_service_mvarh,
        dispatch_stored_energy_change_mwh=dispatch_stored_energy_change_mwh,
        auxiliary_energy_mwh=auxiliary_energy_mwh,
        self_discharge_energy_mwh=self_discharge_energy_mwh,
        stored_energy_change_mwh=stored_energy_change_mwh,
        soc_balance_error=ending_soc - expected_ending_soc,
        limited_interval_count=sum(interval_is_limited(item) for item in intervals),
        storage_power_limited_interval_count=sum(
            item.dispatch.storage_power_limited for item in intervals
        ),
        ramp_limited_interval_count=sum(
            item.dispatch.ramp is not None and item.dispatch.ramp.ramp_limited
            for item in intervals
        ),
        energy_limited_interval_count=sum(
            item.dispatch.energy is not None and item.dispatch.energy.energy_limited
            for item in intervals
        ),
        capability_limited_interval_count=sum(
            item.dispatch.capability.limited for item in intervals
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
        description=(
            "Simulate state-linked frequency-watt and Volt-VAR support intervals."
        )
    )
    parser.add_argument(
        "--frequency-hz-profile", type=_parse_number_series, required=True
    )
    parser.add_argument(
        "--voltage-pu-profile", type=_parse_number_series, required=True
    )
    parser.add_argument("--baseline-active-mw-profile", type=_parse_number_series)
    parser.add_argument(
        "--duration-minutes-profile", type=_parse_number_series, required=True
    )
    boundary = parser.add_mutually_exclusive_group(required=True)
    boundary.add_argument("--limit-mva", type=float)
    boundary.add_argument("--curve-csv", type=Path)
    boundary.add_argument("--directional-curve-csv", type=Path)
    parser.add_argument("--energy-capacity-mwh", type=float, required=True)
    parser.add_argument("--initial-soc", type=float, required=True)
    parser.add_argument("--minimum-soc", type=float, default=0.10)
    parser.add_argument("--maximum-soc", type=float, default=0.90)
    parser.add_argument("--charge-efficiency", type=float, default=0.95)
    parser.add_argument("--discharge-efficiency", type=float, default=0.95)
    parser.add_argument("--auxiliary-load-mw", type=float, default=0.0)
    parser.add_argument("--self-discharge-rate-per-hour", type=float, default=0.0)
    parser.add_argument("--reactive-base-mvar", type=float)
    parser.add_argument(
        "--priority",
        choices=[item.value for item in PowerPriority],
        default=PowerPriority.REACTIVE.value,
    )
    parser.add_argument("--nominal-frequency-hz", type=float, default=50.0)
    parser.add_argument("--frequency-deadband-hz", type=float, default=0.05)
    parser.add_argument("--full-response-deviation-hz", type=float, default=0.50)
    parser.add_argument("--max-discharge-mw", type=float, default=100.0)
    parser.add_argument("--max-charge-mw", type=float, default=100.0)
    parser.add_argument("--low-saturation-pu", type=float, default=0.92)
    parser.add_argument("--low-deadband-pu", type=float, default=0.98)
    parser.add_argument("--high-deadband-pu", type=float, default=1.02)
    parser.add_argument("--high-saturation-pu", type=float, default=1.08)
    parser.add_argument("--max-reactive-power-pu", type=float, default=1.0)
    parser.add_argument("--initial-active-mw", type=float)
    parser.add_argument("--ramp-up-mw-per-minute", type=float)
    parser.add_argument("--ramp-down-mw-per-minute", type=float)
    parser.add_argument("--initial-filtered-frequency-hz", type=float)
    parser.add_argument("--frequency-filter-time-constant-seconds", type=float)
    return parser.parse_args(argv)


def _limit_labels(interval: GridSupportInterval) -> str:
    labels: list[str] = []
    dispatch = interval.dispatch
    if dispatch.storage_power_limited:
        labels.append("storage_power")
    if dispatch.ramp is not None and dispatch.ramp.ramp_limited:
        labels.append("ramp")
    if dispatch.energy is not None and dispatch.energy.energy_limited:
        labels.append("energy")
    if dispatch.capability.limited:
        labels.append("capability")
    return ",".join(labels) if labels else "none"


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    interval_count = len(args.frequency_hz_profile)
    baselines = args.baseline_active_mw_profile
    if baselines is None:
        baselines = (0.0,) * interval_count

    capability_envelope = None
    if args.curve_csv is not None:
        capability_envelope = load_capability_curve_csv(args.curve_csv)
    elif args.directional_curve_csv is not None:
        capability_envelope = load_directional_capability_csv(
            args.directional_curve_csv
        )

    ramp_inputs = (
        args.initial_active_mw,
        args.ramp_up_mw_per_minute,
        args.ramp_down_mw_per_minute,
    )
    if any(value is not None for value in ramp_inputs) and not all(
        value is not None for value in ramp_inputs
    ):
        raise ValueError(
            "initial_active_mw, ramp_up_mw_per_minute, and "
            "ramp_down_mw_per_minute must be provided together"
        )
    ramp_limits = None
    if args.ramp_up_mw_per_minute is not None:
        ramp_limits = RampRateLimits(
            args.ramp_up_mw_per_minute,
            args.ramp_down_mw_per_minute,
        )

    filter_inputs = (
        args.initial_filtered_frequency_hz,
        args.frequency_filter_time_constant_seconds,
    )
    if any(value is not None for value in filter_inputs) and not all(
        value is not None for value in filter_inputs
    ):
        raise ValueError(
            "initial_filtered_frequency_hz and "
            "frequency_filter_time_constant_seconds must be provided together"
        )
    filter_config = None
    if args.frequency_filter_time_constant_seconds is not None:
        filter_config = FirstOrderFilterConfig(
            args.frequency_filter_time_constant_seconds
        )

    result = simulate_grid_support_sequence(
        frequency_hz=args.frequency_hz_profile,
        voltage_pu=args.voltage_pu_profile,
        baseline_active_mw=baselines,
        duration_minutes=args.duration_minutes_profile,
        energy_state=StorageEnergyState(
            energy_capacity_mwh=args.energy_capacity_mwh,
            initial_soc=args.initial_soc,
            minimum_soc=args.minimum_soc,
            maximum_soc=args.maximum_soc,
            charge_efficiency=args.charge_efficiency,
            discharge_efficiency=args.discharge_efficiency,
            auxiliary_load_mw=args.auxiliary_load_mw,
            self_discharge_rate_per_hour=args.self_discharge_rate_per_hour,
        ),
        apparent_power_limit_mva=args.limit_mva,
        frequency_curve=FrequencyWattCurve(
            nominal_frequency_hz=args.nominal_frequency_hz,
            deadband_hz=args.frequency_deadband_hz,
            full_response_deviation_hz=args.full_response_deviation_hz,
            max_discharge_mw=args.max_discharge_mw,
            max_charge_mw=args.max_charge_mw,
        ),
        voltage_curve=VoltVarCurve(
            low_saturation_pu=args.low_saturation_pu,
            low_deadband_pu=args.low_deadband_pu,
            high_deadband_pu=args.high_deadband_pu,
            high_saturation_pu=args.high_saturation_pu,
            max_reactive_power_pu=args.max_reactive_power_pu,
        ),
        reactive_base_mvar=args.reactive_base_mvar,
        priority=args.priority,
        ramp_limits=ramp_limits,
        initial_active_mw=args.initial_active_mw,
        frequency_filter_config=filter_config,
        initial_filtered_frequency_hz=args.initial_filtered_frequency_hz,
        capability_envelope=capability_envelope,
    )

    if isinstance(capability_envelope, DirectionalCapabilityEnvelope):
        print(
            "Capability model: directional envelope "
            f"(4 quadrants, {capability_envelope.point_count} points)"
        )
    elif isinstance(capability_envelope, PiecewiseCapabilityCurve):
        print(
            "Capability model: piecewise curve "
            f"({len(capability_envelope.points)} points)"
        )
    else:
        print(f"Capability model: circular limit ({args.limit_mva:.3f} MVA)")
    print(f"Intervals: {len(result.intervals)}")
    print(f"Limited intervals: {result.limited_interval_count}")
    print(f"Total duration: {result.total_duration_minutes:.3f} minutes")
    print(f"Initial SOC: {result.initial_soc:.4f}")
    print(f"Ending SOC: {result.ending_soc:.4f}")
    print(f"Requested active energy: {result.requested_active_energy_mwh:.3f} MWh")
    print(f"Delivered active energy: {result.delivered_active_energy_mwh:.3f} MWh")
    print(f"Active shortfall energy: {result.active_shortfall_energy_mwh:.3f} MWh")
    print(
        "Requested reactive service: "
        f"{result.requested_reactive_service_mvarh:.3f} MVArh"
    )
    print(
        "Delivered reactive service: "
        f"{result.delivered_reactive_service_mvarh:.3f} MVArh"
    )
    print(
        "Reactive shortfall service: "
        f"{result.reactive_shortfall_service_mvarh:.3f} MVArh"
    )
    print(
        "Dispatch stored-energy change: "
        f"{result.dispatch_stored_energy_change_mwh:.3f} MWh"
    )
    print(f"Auxiliary energy: {result.auxiliary_energy_mwh:.3f} MWh")
    print(f"Self-discharge energy: {result.self_discharge_energy_mwh:.3f} MWh")
    print(f"Stored energy change: {result.stored_energy_change_mwh:.3f} MWh")
    print(f"SOC balance error: {result.soc_balance_error:.3e}")
    for index, interval in enumerate(result.intervals, start=1):
        dispatch = interval.dispatch
        print(
            f"Interval {index}: frequency={interval.frequency_hz:.3f} Hz, "
            f"voltage={interval.voltage_pu:.3f} pu, "
            f"requested_p={dispatch.unconstrained_active_mw:.3f} MW, "
            f"requested_q={interval.requested_reactive_mvar:.3f} MVAr, "
            f"delivered_p={dispatch.capability.active_mw:.3f} MW, "
            f"delivered_q={dispatch.capability.reactive_mvar:.3f} MVAr, "
            f"ending_soc={interval.ending_soc:.4f}, "
            f"limits={_limit_labels(interval)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
