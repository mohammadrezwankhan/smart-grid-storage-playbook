from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class RampDirection(str, Enum):
    UP = "ramp_up"
    DOWN = "ramp_down"


@dataclass(frozen=True)
class RampRateLimits:
    """Asymmetric signed active-power slew limits."""

    ramp_up_mw_per_minute: float
    ramp_down_mw_per_minute: float

    def validate(self) -> None:
        values = {
            "ramp_up_mw_per_minute": self.ramp_up_mw_per_minute,
            "ramp_down_mw_per_minute": self.ramp_down_mw_per_minute,
        }
        for name, value in values.items():
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class RampLimitedDispatch:
    previous_active_mw: float
    requested_active_mw: float
    delivered_active_mw: float
    interval_seconds: float
    minimum_active_mw: float
    maximum_active_mw: float
    power_change_mw: float
    power_shortfall_mw: float
    ramp_limited: bool
    limiting_direction: RampDirection | None


def limit_active_power_by_ramp(
    requested_active_mw: float,
    previous_active_mw: float,
    interval_seconds: float,
    limits: RampRateLimits,
) -> RampLimitedDispatch:
    """Limit a signed active-power request to the reachable ramp interval."""

    limits.validate()
    values = {
        "requested_active_mw": requested_active_mw,
        "previous_active_mw": previous_active_mw,
        "interval_seconds": interval_seconds,
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if interval_seconds <= 0.0:
        raise ValueError("interval_seconds must be positive")

    interval_minutes = interval_seconds / 60.0
    minimum_active_mw = (
        previous_active_mw - limits.ramp_down_mw_per_minute * interval_minutes
    )
    maximum_active_mw = (
        previous_active_mw + limits.ramp_up_mw_per_minute * interval_minutes
    )
    delivered_active_mw = max(
        minimum_active_mw,
        min(maximum_active_mw, requested_active_mw),
    )
    limiting_direction = None
    if requested_active_mw > maximum_active_mw:
        limiting_direction = RampDirection.UP
    elif requested_active_mw < minimum_active_mw:
        limiting_direction = RampDirection.DOWN
    ramp_limited = limiting_direction is not None

    return RampLimitedDispatch(
        previous_active_mw=previous_active_mw,
        requested_active_mw=requested_active_mw,
        delivered_active_mw=delivered_active_mw,
        interval_seconds=interval_seconds,
        minimum_active_mw=minimum_active_mw,
        maximum_active_mw=maximum_active_mw,
        power_change_mw=delivered_active_mw - previous_active_mw,
        power_shortfall_mw=abs(requested_active_mw - delivered_active_mw),
        ramp_limited=ramp_limited,
        limiting_direction=limiting_direction,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply asymmetric ramp limits to signed active power."
    )
    parser.add_argument("--active-mw", type=float, required=True)
    parser.add_argument("--previous-active-mw", type=float, required=True)
    parser.add_argument("--interval-seconds", type=float, required=True)
    parser.add_argument("--ramp-up-mw-per-minute", type=float, required=True)
    parser.add_argument("--ramp-down-mw-per-minute", type=float, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = limit_active_power_by_ramp(
        args.active_mw,
        args.previous_active_mw,
        args.interval_seconds,
        RampRateLimits(
            args.ramp_up_mw_per_minute,
            args.ramp_down_mw_per_minute,
        ),
    )
    direction = (
        "none" if result.limiting_direction is None else result.limiting_direction.value
    )
    print(f"Previous active power: {result.previous_active_mw:.3f} MW")
    print(f"Requested active power: {result.requested_active_mw:.3f} MW")
    print(f"Delivered active power: {result.delivered_active_mw:.3f} MW")
    print(f"Ramp interval: {result.interval_seconds:.3f} seconds")
    print(f"Reachable minimum: {result.minimum_active_mw:.3f} MW")
    print(f"Reachable maximum: {result.maximum_active_mw:.3f} MW")
    print(f"Ramp limited: {str(result.ramp_limited).lower()}")
    print(f"Limiting direction: {direction}")
    print(f"Power shortfall: {result.power_shortfall_mw:.3f} MW")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
