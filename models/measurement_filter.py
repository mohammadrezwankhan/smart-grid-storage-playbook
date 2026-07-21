from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class FirstOrderFilterConfig:
    """Time constant for an exact first-order low-pass filter step."""

    time_constant_seconds: float

    def validate(self) -> None:
        if (
            not math.isfinite(self.time_constant_seconds)
            or self.time_constant_seconds <= 0.0
        ):
            raise ValueError("time_constant_seconds must be finite and positive")


@dataclass(frozen=True)
class FirstOrderFilterStep:
    input_value: float
    previous_output_value: float
    output_value: float
    interval_seconds: float
    time_constant_seconds: float
    decay_factor: float
    input_step: float
    output_change: float


def filter_first_order_step(
    input_value: float,
    previous_output_value: float,
    interval_seconds: float,
    config: FirstOrderFilterConfig,
) -> FirstOrderFilterStep:
    """Apply the exact zero-order-hold solution for one filter interval."""

    config.validate()
    values = {
        "input_value": input_value,
        "previous_output_value": previous_output_value,
        "interval_seconds": interval_seconds,
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if interval_seconds <= 0.0:
        raise ValueError("interval_seconds must be positive")

    normalized_interval = interval_seconds / config.time_constant_seconds
    response_fraction = -math.expm1(-normalized_interval)
    decay_factor = 1.0 - response_fraction
    output_value = (
        previous_output_value
        + (input_value - previous_output_value) * response_fraction
    )
    return FirstOrderFilterStep(
        input_value=input_value,
        previous_output_value=previous_output_value,
        output_value=output_value,
        interval_seconds=interval_seconds,
        time_constant_seconds=config.time_constant_seconds,
        decay_factor=decay_factor,
        input_step=input_value - previous_output_value,
        output_change=output_value - previous_output_value,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply one exact first-order low-pass filter step."
    )
    parser.add_argument("--input-value", type=float, required=True)
    parser.add_argument("--previous-output-value", type=float, required=True)
    parser.add_argument("--interval-seconds", type=float, required=True)
    parser.add_argument("--time-constant-seconds", type=float, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = filter_first_order_step(
        args.input_value,
        args.previous_output_value,
        args.interval_seconds,
        FirstOrderFilterConfig(args.time_constant_seconds),
    )
    print(f"Input value: {result.input_value:.6f}")
    print(f"Previous output value: {result.previous_output_value:.6f}")
    print(f"Filtered output value: {result.output_value:.6f}")
    print(f"Interval: {result.interval_seconds:.6f} seconds")
    print(f"Time constant: {result.time_constant_seconds:.6f} seconds")
    print(f"Decay factor: {result.decay_factor:.9f}")
    print(f"Input step: {result.input_step:.6f}")
    print(f"Output change: {result.output_change:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
