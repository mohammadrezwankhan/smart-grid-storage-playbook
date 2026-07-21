from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence


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


@dataclass(frozen=True)
class CapabilityCurvePoint:
    active_mw: float
    reactive_limit_mvar: float


@dataclass(frozen=True)
class PiecewiseCapabilityCurve:
    """Symmetric positive-quadrant P-Q boundary with linear interpolation."""

    points: tuple[CapabilityCurvePoint, ...]

    def __post_init__(self) -> None:
        points = tuple(self.points)
        object.__setattr__(self, "points", points)
        if len(points) < 2:
            raise ValueError("capability curve must contain at least two points")

        for index, point in enumerate(points):
            values = {
                f"points[{index}].active_mw": point.active_mw,
                f"points[{index}].reactive_limit_mvar": (point.reactive_limit_mvar),
            }
            for name, value in values.items():
                if not math.isfinite(value):
                    raise ValueError(f"{name} must be finite")
                if value < 0.0:
                    raise ValueError(f"{name} must be nonnegative")

        if points[0].active_mw != 0.0:
            raise ValueError("capability curve must start on the reactive axis")
        if points[0].reactive_limit_mvar <= 0.0:
            raise ValueError("reactive-axis capability must be positive")
        if points[-1].reactive_limit_mvar != 0.0:
            raise ValueError("capability curve must end on the active axis")
        if points[-1].active_mw <= 0.0:
            raise ValueError("active-axis capability must be positive")

        previous_slope = math.inf
        for left, right in zip(points[:-1], points[1:], strict=True):
            active_step = right.active_mw - left.active_mw
            reactive_step = right.reactive_limit_mvar - left.reactive_limit_mvar
            if active_step <= 0.0:
                raise ValueError(
                    "capability curve active power must be strictly increasing"
                )
            if reactive_step >= 0.0:
                raise ValueError(
                    "capability curve reactive limit must be strictly decreasing"
                )
            slope = reactive_step / active_step
            if slope > previous_slope + 1e-12:
                raise ValueError("capability curve must be concave")
            previous_slope = slope

    @property
    def maximum_active_mw(self) -> float:
        return self.points[-1].active_mw

    @property
    def maximum_reactive_mvar(self) -> float:
        return self.points[0].reactive_limit_mvar

    def reactive_limit_mvar(self, active_mw: float) -> float:
        """Interpolate the symmetric reactive limit at signed active power."""

        if not math.isfinite(active_mw):
            raise ValueError("active_mw must be finite")
        active_magnitude = abs(active_mw)
        if active_magnitude >= self.maximum_active_mw:
            return 0.0
        for left, right in zip(self.points[:-1], self.points[1:], strict=True):
            if active_magnitude <= right.active_mw:
                fraction = (active_magnitude - left.active_mw) / (
                    right.active_mw - left.active_mw
                )
                return left.reactive_limit_mvar + fraction * (
                    right.reactive_limit_mvar - left.reactive_limit_mvar
                )
        raise RuntimeError("validated capability curve did not cover active power")

    def active_limit_mw(self, reactive_mvar: float) -> float:
        """Interpolate the symmetric active limit at signed reactive power."""

        if not math.isfinite(reactive_mvar):
            raise ValueError("reactive_mvar must be finite")
        reactive_magnitude = abs(reactive_mvar)
        if reactive_magnitude >= self.maximum_reactive_mvar:
            return 0.0
        for left, right in zip(self.points[:-1], self.points[1:], strict=True):
            if reactive_magnitude >= right.reactive_limit_mvar:
                fraction = (left.reactive_limit_mvar - reactive_magnitude) / (
                    left.reactive_limit_mvar - right.reactive_limit_mvar
                )
                return left.active_mw + fraction * (right.active_mw - left.active_mw)
        raise RuntimeError("validated capability curve did not cover reactive power")

    def contains(self, active_mw: float, reactive_mvar: float) -> bool:
        values = {
            "active_mw": active_mw,
            "reactive_mvar": reactive_mvar,
        }
        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        return abs(active_mw) <= self.maximum_active_mw and abs(
            reactive_mvar
        ) <= self.reactive_limit_mvar(active_mw)

    def radial_limit_mva(self, active_mw: float, reactive_mvar: float) -> float:
        """Return the boundary magnitude along the command's P-Q direction."""

        values = {
            "active_mw": active_mw,
            "reactive_mvar": reactive_mvar,
        }
        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        active_magnitude = abs(active_mw)
        reactive_magnitude = abs(reactive_mvar)
        if active_magnitude == 0.0:
            return self.maximum_reactive_mvar

        ray_slope = reactive_magnitude / active_magnitude
        tolerance = 1e-12 * max(1.0, self.maximum_active_mw)
        for left, right in zip(self.points[:-1], self.points[1:], strict=True):
            boundary_slope = (right.reactive_limit_mvar - left.reactive_limit_mvar) / (
                right.active_mw - left.active_mw
            )
            intercept = left.reactive_limit_mvar - boundary_slope * left.active_mw
            boundary_active_mw = intercept / (ray_slope - boundary_slope)
            if (
                left.active_mw - tolerance
                <= boundary_active_mw
                <= right.active_mw + tolerance
            ):
                boundary_reactive_mvar = ray_slope * boundary_active_mw
                return math.hypot(
                    boundary_active_mw,
                    boundary_reactive_mvar,
                )
        raise RuntimeError("validated capability curve did not intersect command ray")


def _clip(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def _select_priority(priority: PowerPriority | str) -> PowerPriority:
    try:
        return PowerPriority(priority)
    except ValueError as error:
        choices = ", ".join(item.value for item in PowerPriority)
        raise ValueError(f"priority must be one of: {choices}") from error


def _build_result(
    requested_active_mw: float,
    requested_reactive_mvar: float,
    active_mw: float,
    reactive_mvar: float,
    utilization: float,
    priority: PowerPriority,
) -> CapabilityResult:
    apparent_power_mva = math.hypot(active_mw, reactive_mvar)
    active_curtailment = requested_active_mw - active_mw
    reactive_curtailment = requested_reactive_mvar - reactive_mvar
    limited = not (
        math.isclose(active_curtailment, 0.0, rel_tol=0.0, abs_tol=1e-12)
        and math.isclose(
            reactive_curtailment,
            0.0,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
    )
    return CapabilityResult(
        requested_active_mw=requested_active_mw,
        requested_reactive_mvar=requested_reactive_mvar,
        active_mw=active_mw,
        reactive_mvar=reactive_mvar,
        apparent_power_mva=apparent_power_mva,
        utilization=utilization,
        curtailed_active_mw=active_curtailment,
        curtailed_reactive_mvar=reactive_curtailment,
        limited=limited,
        priority=priority,
    )


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

    selected_priority = _select_priority(priority)

    requested_mva = math.hypot(
        requested_active_mw,
        requested_reactive_mvar,
    )
    if requested_mva <= apparent_power_limit_mva:
        active_mw = requested_active_mw
        reactive_mvar = requested_reactive_mvar
    elif selected_priority is PowerPriority.ACTIVE:
        active_mw = _clip(requested_active_mw, apparent_power_limit_mva)
        reactive_limit = math.sqrt(max(0.0, apparent_power_limit_mva**2 - active_mw**2))
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

    return _build_result(
        requested_active_mw,
        requested_reactive_mvar,
        active_mw,
        reactive_mvar,
        math.hypot(active_mw, reactive_mvar) / apparent_power_limit_mva,
        selected_priority,
    )


def allocate_power_on_curve(
    requested_active_mw: float,
    requested_reactive_mvar: float,
    curve: PiecewiseCapabilityCurve,
    priority: PowerPriority | str = PowerPriority.ACTIVE,
) -> CapabilityResult:
    """Apply a sampled symmetric P-Q envelope using the selected priority."""

    values = {
        "requested_active_mw": requested_active_mw,
        "requested_reactive_mvar": requested_reactive_mvar,
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    selected_priority = _select_priority(priority)

    if curve.contains(requested_active_mw, requested_reactive_mvar):
        active_mw = requested_active_mw
        reactive_mvar = requested_reactive_mvar
    elif selected_priority is PowerPriority.ACTIVE:
        active_mw = _clip(requested_active_mw, curve.maximum_active_mw)
        reactive_mvar = _clip(
            requested_reactive_mvar,
            curve.reactive_limit_mvar(active_mw),
        )
    elif selected_priority is PowerPriority.REACTIVE:
        reactive_mvar = _clip(
            requested_reactive_mvar,
            curve.maximum_reactive_mvar,
        )
        active_mw = _clip(
            requested_active_mw,
            curve.active_limit_mw(reactive_mvar),
        )
    else:
        requested_mva = math.hypot(
            requested_active_mw,
            requested_reactive_mvar,
        )
        scale = (
            curve.radial_limit_mva(
                requested_active_mw,
                requested_reactive_mvar,
            )
            / requested_mva
        )
        active_mw = requested_active_mw * scale
        reactive_mvar = requested_reactive_mvar * scale

    apparent_power_mva = math.hypot(active_mw, reactive_mvar)
    utilization = 0.0
    if apparent_power_mva > 0.0:
        utilization = min(
            1.0,
            apparent_power_mva / curve.radial_limit_mva(active_mw, reactive_mvar),
        )
    return _build_result(
        requested_active_mw,
        requested_reactive_mvar,
        active_mw,
        reactive_mvar,
        utilization,
        selected_priority,
    )


def load_capability_curve_csv(path: str | Path) -> PiecewiseCapabilityCurve:
    """Load a strict active/reactive-limit capability curve from CSV."""

    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_columns = ("active_mw", "reactive_limit_mvar")
        if tuple(reader.fieldnames or ()) != expected_columns:
            raise ValueError(
                "capability curve CSV header must be active_mw,reactive_limit_mvar"
            )
        points: list[CapabilityCurvePoint] = []
        for line_number, row in enumerate(reader, start=2):
            if None in row or any(
                value is None or not value.strip() for value in row.values()
            ):
                raise ValueError(
                    f"capability curve CSV line {line_number} must be complete"
                )
            try:
                point = CapabilityCurvePoint(
                    active_mw=float(row["active_mw"]),
                    reactive_limit_mvar=float(row["reactive_limit_mvar"]),
                )
            except ValueError as error:
                raise ValueError(
                    f"capability curve CSV line {line_number} must be numeric"
                ) from error
            points.append(point)
    return PiecewiseCapabilityCurve(tuple(points))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply a circular or sampled inverter P-Q capability limit."
    )
    parser.add_argument("--active-mw", type=float, required=True)
    parser.add_argument("--reactive-mvar", type=float, required=True)
    boundary = parser.add_mutually_exclusive_group(required=True)
    boundary.add_argument("--limit-mva", type=float)
    boundary.add_argument("--curve-csv", type=Path)
    parser.add_argument(
        "--priority",
        choices=[item.value for item in PowerPriority],
        default=PowerPriority.ACTIVE.value,
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.curve_csv is None:
        result = allocate_power(
            args.active_mw,
            args.reactive_mvar,
            args.limit_mva,
            args.priority,
        )
        capability_model = None
    else:
        curve = load_capability_curve_csv(args.curve_csv)
        result = allocate_power_on_curve(
            args.active_mw,
            args.reactive_mvar,
            curve,
            args.priority,
        )
        capability_model = f"piecewise curve ({len(curve.points)} points)"
    if capability_model is not None:
        print(f"Capability model: {capability_model}")
    print(f"Priority: {result.priority.value}")
    print(f"Limited: {str(result.limited).lower()}")
    print(f"Active power: {result.active_mw:.3f} MW")
    print(f"Reactive power: {result.reactive_mvar:.3f} MVAr")
    print(f"Apparent power: {result.apparent_power_mva:.3f} MVA")
    print(f"Capability utilization: {100.0 * result.utilization:.2f}%")
    print(f"Active curtailment: {result.curtailed_active_mw:.3f} MW")
    print(f"Reactive curtailment: {result.curtailed_reactive_mvar:.3f} MVAr")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
