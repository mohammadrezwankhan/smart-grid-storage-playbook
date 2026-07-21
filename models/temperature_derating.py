from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class TemperaturePowerPoint:
    """One externally supplied temperature and active-power limit sample."""

    temperature_c: float
    max_discharge_mw: float
    max_charge_mw: float


@dataclass(frozen=True)
class InterpolatedTemperatureLimits:
    """Auditable piecewise-linear limits at one operating temperature."""

    temperature_c: float
    lower_temperature_c: float
    upper_temperature_c: float
    interpolation_fraction: float
    max_discharge_mw: float
    max_charge_mw: float
    endpoint_clamped: bool


@dataclass(frozen=True)
class TemperatureLimitedDispatch:
    """Active-power request after nameplate and temperature limits."""

    requested_active_mw: float
    nameplate_bounded_active_mw: float
    delivered_active_mw: float
    nameplate_max_discharge_mw: float
    nameplate_max_charge_mw: float
    effective_max_discharge_mw: float
    effective_max_charge_mw: float
    nameplate_limited: bool
    temperature_limited: bool
    limits: InterpolatedTemperatureLimits


@dataclass(frozen=True)
class TemperaturePowerDeratingCurve:
    """Strict sampled charge/discharge limits with linear interpolation."""

    points: tuple[TemperaturePowerPoint, ...]

    def __post_init__(self) -> None:
        points = tuple(self.points)
        object.__setattr__(self, "points", points)
        if len(points) < 2:
            raise ValueError(
                "temperature derating curve must contain at least two points"
            )

        for index, point in enumerate(points):
            values = {
                f"points[{index}].temperature_c": point.temperature_c,
                f"points[{index}].max_discharge_mw": point.max_discharge_mw,
                f"points[{index}].max_charge_mw": point.max_charge_mw,
            }
            for name, value in values.items():
                if not math.isfinite(value):
                    raise ValueError(f"{name} must be finite")
            if point.max_discharge_mw < 0.0 or point.max_charge_mw < 0.0:
                raise ValueError("temperature power limits must be nonnegative")

        for left, right in zip(points[:-1], points[1:], strict=True):
            if right.temperature_c <= left.temperature_c:
                raise ValueError("curve temperatures must be strictly increasing")

    def limits_at(self, temperature_c: float) -> InterpolatedTemperatureLimits:
        """Interpolate limits, clamping temperatures outside sampled endpoints."""

        if not math.isfinite(temperature_c):
            raise ValueError("temperature_c must be finite")

        first = self.points[0]
        last = self.points[-1]
        if temperature_c <= first.temperature_c:
            return InterpolatedTemperatureLimits(
                temperature_c=temperature_c,
                lower_temperature_c=first.temperature_c,
                upper_temperature_c=first.temperature_c,
                interpolation_fraction=0.0,
                max_discharge_mw=first.max_discharge_mw,
                max_charge_mw=first.max_charge_mw,
                endpoint_clamped=temperature_c < first.temperature_c,
            )
        if temperature_c >= last.temperature_c:
            return InterpolatedTemperatureLimits(
                temperature_c=temperature_c,
                lower_temperature_c=last.temperature_c,
                upper_temperature_c=last.temperature_c,
                interpolation_fraction=0.0,
                max_discharge_mw=last.max_discharge_mw,
                max_charge_mw=last.max_charge_mw,
                endpoint_clamped=temperature_c > last.temperature_c,
            )

        for left, right in zip(self.points[:-1], self.points[1:], strict=True):
            if temperature_c <= right.temperature_c:
                fraction = (temperature_c - left.temperature_c) / (
                    right.temperature_c - left.temperature_c
                )
                return InterpolatedTemperatureLimits(
                    temperature_c=temperature_c,
                    lower_temperature_c=left.temperature_c,
                    upper_temperature_c=right.temperature_c,
                    interpolation_fraction=fraction,
                    max_discharge_mw=left.max_discharge_mw
                    + fraction * (right.max_discharge_mw - left.max_discharge_mw),
                    max_charge_mw=left.max_charge_mw
                    + fraction * (right.max_charge_mw - left.max_charge_mw),
                    endpoint_clamped=False,
                )
        raise RuntimeError("validated temperature curve did not cover temperature")


def limit_active_power_by_temperature(
    requested_active_mw: float,
    temperature_c: float,
    nameplate_max_discharge_mw: float,
    nameplate_max_charge_mw: float,
    curve: TemperaturePowerDeratingCurve,
) -> TemperatureLimitedDispatch:
    """Apply asymmetric nameplate and sampled temperature power limits."""

    values = {
        "requested_active_mw": requested_active_mw,
        "nameplate_max_discharge_mw": nameplate_max_discharge_mw,
        "nameplate_max_charge_mw": nameplate_max_charge_mw,
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if nameplate_max_discharge_mw <= 0.0 or nameplate_max_charge_mw <= 0.0:
        raise ValueError("nameplate charge and discharge limits must be positive")

    limits = curve.limits_at(temperature_c)
    nameplate_bounded_active_mw = max(
        -nameplate_max_charge_mw,
        min(nameplate_max_discharge_mw, requested_active_mw),
    )
    effective_max_discharge_mw = min(
        nameplate_max_discharge_mw,
        limits.max_discharge_mw,
    )
    effective_max_charge_mw = min(
        nameplate_max_charge_mw,
        limits.max_charge_mw,
    )
    delivered_active_mw = max(
        -effective_max_charge_mw,
        min(effective_max_discharge_mw, nameplate_bounded_active_mw),
    )

    def differs(left: float, right: float) -> bool:
        return not math.isclose(left, right, rel_tol=0.0, abs_tol=1e-12)

    return TemperatureLimitedDispatch(
        requested_active_mw=requested_active_mw,
        nameplate_bounded_active_mw=nameplate_bounded_active_mw,
        delivered_active_mw=delivered_active_mw,
        nameplate_max_discharge_mw=nameplate_max_discharge_mw,
        nameplate_max_charge_mw=nameplate_max_charge_mw,
        effective_max_discharge_mw=effective_max_discharge_mw,
        effective_max_charge_mw=effective_max_charge_mw,
        nameplate_limited=differs(requested_active_mw, nameplate_bounded_active_mw),
        temperature_limited=differs(
            nameplate_bounded_active_mw,
            delivered_active_mw,
        ),
        limits=limits,
    )


def load_temperature_derating_csv(
    path: str | Path,
) -> TemperaturePowerDeratingCurve:
    """Load a strict temperature-to-charge/discharge-limit CSV."""

    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_columns = (
            "temperature_c",
            "max_discharge_mw",
            "max_charge_mw",
        )
        if tuple(reader.fieldnames or ()) != expected_columns:
            raise ValueError(
                "temperature derating CSV header must be "
                "temperature_c,max_discharge_mw,max_charge_mw"
            )
        points: list[TemperaturePowerPoint] = []
        for line_number, row in enumerate(reader, start=2):
            if None in row or any(
                value is None or not value.strip() for value in row.values()
            ):
                raise ValueError(
                    f"temperature derating CSV line {line_number} must be complete"
                )
            try:
                point = TemperaturePowerPoint(
                    temperature_c=float(row["temperature_c"]),
                    max_discharge_mw=float(row["max_discharge_mw"]),
                    max_charge_mw=float(row["max_charge_mw"]),
                )
            except ValueError as error:
                raise ValueError(
                    f"temperature derating CSV line {line_number} must be numeric"
                ) from error
            points.append(point)
    return TemperaturePowerDeratingCurve(tuple(points))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply an external sampled temperature power envelope."
    )
    parser.add_argument("--active-mw", type=float, required=True)
    parser.add_argument("--temperature-c", type=float, required=True)
    parser.add_argument("--max-discharge-mw", type=float, required=True)
    parser.add_argument("--max-charge-mw", type=float, required=True)
    parser.add_argument("--curve-csv", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    curve = load_temperature_derating_csv(args.curve_csv)
    result = limit_active_power_by_temperature(
        args.active_mw,
        args.temperature_c,
        args.max_discharge_mw,
        args.max_charge_mw,
        curve,
    )
    limits = result.limits
    print(f"Temperature: {limits.temperature_c:.3f} C")
    print(f"Sampled discharge limit: {limits.max_discharge_mw:.3f} MW")
    print(f"Sampled charge limit: {limits.max_charge_mw:.3f} MW")
    print(f"Effective discharge limit: {result.effective_max_discharge_mw:.3f} MW")
    print(f"Effective charge limit: {result.effective_max_charge_mw:.3f} MW")
    print(f"Endpoint clamped: {str(limits.endpoint_clamped).lower()}")
    print(f"Delivered active power: {result.delivered_active_mw:.3f} MW")
    print(f"Temperature limited: {str(result.temperature_limited).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
