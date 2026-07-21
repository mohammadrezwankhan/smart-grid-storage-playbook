from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class EnergyBoundary(str, Enum):
    MINIMUM_SOC = "minimum_soc"
    MAXIMUM_SOC = "maximum_soc"


@dataclass(frozen=True)
class StorageEnergyState:
    """Energy and SOC assumptions for one constant-power dispatch interval."""

    energy_capacity_mwh: float
    initial_soc: float
    minimum_soc: float = 0.10
    maximum_soc: float = 0.90
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95
    auxiliary_load_mw: float = 0.0
    self_discharge_rate_per_hour: float = 0.0

    def validate(self) -> None:
        values = {
            "energy_capacity_mwh": self.energy_capacity_mwh,
            "initial_soc": self.initial_soc,
            "minimum_soc": self.minimum_soc,
            "maximum_soc": self.maximum_soc,
            "charge_efficiency": self.charge_efficiency,
            "discharge_efficiency": self.discharge_efficiency,
            "auxiliary_load_mw": self.auxiliary_load_mw,
            "self_discharge_rate_per_hour": self.self_discharge_rate_per_hour,
        }
        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.energy_capacity_mwh <= 0.0:
            raise ValueError("energy_capacity_mwh must be positive")
        if not (0.0 <= self.minimum_soc < self.maximum_soc <= 1.0):
            raise ValueError(
                "SOC limits must satisfy 0 <= minimum_soc < maximum_soc <= 1"
            )
        if not self.minimum_soc <= self.initial_soc <= self.maximum_soc:
            raise ValueError("initial_soc must be within the configured SOC limits")
        if not 0.0 < self.charge_efficiency <= 1.0:
            raise ValueError("charge_efficiency must be within (0, 1]")
        if not 0.0 < self.discharge_efficiency <= 1.0:
            raise ValueError("discharge_efficiency must be within (0, 1]")
        if self.auxiliary_load_mw < 0.0:
            raise ValueError("auxiliary_load_mw must be nonnegative")
        if self.self_discharge_rate_per_hour < 0.0:
            raise ValueError("self_discharge_rate_per_hour must be nonnegative")


@dataclass(frozen=True)
class EnergyLimitedDispatch:
    requested_active_mw: float
    delivered_active_mw: float
    duration_minutes: float
    initial_soc: float
    ending_soc: float
    dispatch_stored_energy_change_mwh: float
    auxiliary_energy_mwh: float
    self_discharge_energy_mwh: float
    stored_energy_change_mwh: float
    power_shortfall_mw: float
    energy_limited: bool
    limiting_boundary: EnergyBoundary | None


def _retention_terms(
    self_discharge_rate_per_hour: float,
    duration_hours: float,
) -> tuple[float, float]:
    """Return exponential retention and constant-power influence in hours."""

    if self_discharge_rate_per_hour == 0.0:
        return 1.0, duration_hours
    exponent = -self_discharge_rate_per_hour * duration_hours
    retention = math.exp(exponent)
    equivalent_hours = -math.expm1(exponent) / self_discharge_rate_per_hour
    return retention, equivalent_hours


def limit_active_power_by_energy(
    requested_active_mw: float,
    duration_minutes: float,
    state: StorageEnergyState,
) -> EnergyLimitedDispatch:
    """Limit constant AC power so an interval ends inside configured SOC bounds."""

    state.validate()
    if not math.isfinite(requested_active_mw):
        raise ValueError("requested_active_mw must be finite")
    if not math.isfinite(duration_minutes) or duration_minutes <= 0.0:
        raise ValueError("duration_minutes must be finite and positive")

    duration_hours = duration_minutes / 60.0
    initial_energy_mwh = state.initial_soc * state.energy_capacity_mwh
    minimum_energy_mwh = state.minimum_soc * state.energy_capacity_mwh
    maximum_energy_mwh = state.maximum_soc * state.energy_capacity_mwh
    retention, equivalent_hours = _retention_terms(
        state.self_discharge_rate_per_hour,
        duration_hours,
    )
    loss_only_ending_energy_mwh = (
        initial_energy_mwh * retention - state.auxiliary_load_mw * equivalent_hours
    )

    if requested_active_mw > 0.0:
        available_stored_energy_mwh = loss_only_ending_energy_mwh - minimum_energy_mwh
        if available_stored_energy_mwh < -1e-12:
            raise ValueError(
                "auxiliary and self-discharge losses cross minimum_soc before "
                "applying requested discharge"
            )
        maximum_discharge_mw = max(
            0.0,
            available_stored_energy_mwh * state.discharge_efficiency / equivalent_hours,
        )
        delivered_active_mw = min(requested_active_mw, maximum_discharge_mw)
        dispatch_stored_energy_change_mwh = (
            -delivered_active_mw * duration_hours / state.discharge_efficiency
        )
    elif requested_active_mw < 0.0:
        available_storage_room_mwh = maximum_energy_mwh - loss_only_ending_energy_mwh
        maximum_charge_mw = max(
            0.0,
            available_storage_room_mwh / (state.charge_efficiency * equivalent_hours),
        )
        delivered_active_mw = max(requested_active_mw, -maximum_charge_mw)
        dispatch_stored_energy_change_mwh = (
            -delivered_active_mw * duration_hours * state.charge_efficiency
        )
    else:
        delivered_active_mw = 0.0
        dispatch_stored_energy_change_mwh = 0.0

    if delivered_active_mw > 0.0:
        dispatch_stored_power_mw = -delivered_active_mw / state.discharge_efficiency
    else:
        dispatch_stored_power_mw = -delivered_active_mw * state.charge_efficiency
    ending_energy_mwh = (
        loss_only_ending_energy_mwh + dispatch_stored_power_mw * equivalent_hours
    )
    if ending_energy_mwh < minimum_energy_mwh - 1e-10:
        if requested_active_mw == 0.0:
            raise ValueError(
                "auxiliary and self-discharge losses cross minimum_soc without "
                "a charging request"
            )
        raise ValueError(
            "requested charging power is insufficient to cover auxiliary and "
            "self-discharge losses before minimum_soc"
        )
    if ending_energy_mwh > maximum_energy_mwh + 1e-10:
        raise RuntimeError("energy limiter failed to enforce maximum_soc")
    ending_energy_mwh = min(
        maximum_energy_mwh,
        max(minimum_energy_mwh, ending_energy_mwh),
    )

    auxiliary_energy_mwh = state.auxiliary_load_mw * duration_hours
    stored_energy_change_mwh = ending_energy_mwh - initial_energy_mwh
    if state.self_discharge_rate_per_hour == 0.0:
        self_discharge_energy_mwh = 0.0
    else:
        self_discharge_energy_mwh = (
            dispatch_stored_energy_change_mwh
            - auxiliary_energy_mwh
            - stored_energy_change_mwh
        )
        if self_discharge_energy_mwh < -1e-12:
            raise RuntimeError("self-discharge energy must be nonnegative")
        self_discharge_energy_mwh = max(0.0, self_discharge_energy_mwh)
    ending_soc = ending_energy_mwh / state.energy_capacity_mwh
    energy_limited = not math.isclose(
        delivered_active_mw,
        requested_active_mw,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    limiting_boundary = None
    if energy_limited:
        limiting_boundary = (
            EnergyBoundary.MINIMUM_SOC
            if requested_active_mw > 0.0
            else EnergyBoundary.MAXIMUM_SOC
        )
    return EnergyLimitedDispatch(
        requested_active_mw=requested_active_mw,
        delivered_active_mw=delivered_active_mw,
        duration_minutes=duration_minutes,
        initial_soc=state.initial_soc,
        ending_soc=ending_soc,
        dispatch_stored_energy_change_mwh=dispatch_stored_energy_change_mwh,
        auxiliary_energy_mwh=auxiliary_energy_mwh,
        self_discharge_energy_mwh=self_discharge_energy_mwh,
        stored_energy_change_mwh=stored_energy_change_mwh,
        power_shortfall_mw=abs(requested_active_mw - delivered_active_mw),
        energy_limited=energy_limited,
        limiting_boundary=limiting_boundary,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply SOC and interval-energy limits to active power."
    )
    parser.add_argument("--active-mw", type=float, required=True)
    parser.add_argument("--duration-minutes", type=float, required=True)
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
    result = limit_active_power_by_energy(
        args.active_mw,
        args.duration_minutes,
        state,
    )
    boundary = (
        "none" if result.limiting_boundary is None else result.limiting_boundary.value
    )
    print(f"Requested active power: {result.requested_active_mw:.3f} MW")
    print(f"Delivered active power: {result.delivered_active_mw:.3f} MW")
    print(f"Response duration: {result.duration_minutes:.3f} minutes")
    print(f"Energy limited: {str(result.energy_limited).lower()}")
    print(f"Limiting boundary: {boundary}")
    print(f"Initial SOC: {result.initial_soc:.4f}")
    print(f"Ending SOC: {result.ending_soc:.4f}")
    print(
        "Dispatch stored-energy change: "
        f"{result.dispatch_stored_energy_change_mwh:.3f} MWh"
    )
    print(f"Auxiliary energy: {result.auxiliary_energy_mwh:.3f} MWh")
    print(f"Self-discharge energy: {result.self_discharge_energy_mwh:.3f} MWh")
    print(f"Stored energy change: {result.stored_energy_change_mwh:.3f} MWh")
    print(f"Power shortfall: {result.power_shortfall_mw:.3f} MW")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
