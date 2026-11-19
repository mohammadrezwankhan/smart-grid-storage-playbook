# API, CLI and interfaces

[Handbook](../INDEX.md) · [Architecture](ARCHITECTURE.md) · [Existing model walkthrough](../../models/README.md)

## Calling conventions

The native modules expose annotated functions and frozen dataclasses; validation commonly raises `ValueError`, and consistency failures can raise `RuntimeError`. Successful CLI `main(argv)` returns zero and prints human-readable results. argparse handles parsing/help; there is no registered package console script, web API, JSON-output flag or compatibility/version manifest.

Positive native P means discharge/injection to the AC side; negative P means charging. Positive Q means injection and negative Q absorption. Native SOC is a fraction, not percent. Priority defaults differ: standalone P–Q and frequency-watt use `active`; Volt-VAR and grid-support sequence use `reactive`. Reserve feasibility preserves the supplied Q obligation using reactive priority. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L312-L365) [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L86-L114) [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L159-L179) [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L124-L144) [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L54-L72)

## Complete native declaration catalogue

The following inventory includes 89 source-defined public native declarations: functions, classes, public methods/properties and the capability type alias. Imported names and underscore helpers are not represented as separately implemented APIs. Dataclass fields and enum values are listed under their owning class. Source links include decorators where relevant. There is no declared long-term SDK stability promise.


### models/energy_limits.py

- `class EnergyBoundary(str, Enum)` — enum. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L10-L12)

  Fields/values: `MINIMUM_SOC = 'minimum_soc'`; `MAXIMUM_SOC = 'maximum_soc'`.

- `class StorageEnergyState()` — dataclass. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L15-L57)

  Fields/values: `energy_capacity_mwh: float (required/result field)`; `initial_soc: float (required/result field)`; `minimum_soc: float = 0.1`; `maximum_soc: float = 0.9`; `charge_efficiency: float = 0.95`; `discharge_efficiency: float = 0.95`; `auxiliary_load_mw: float = 0.0`; `self_discharge_rate_per_hour: float = 0.0`.

- `StorageEnergyState.validate`: `def validate(self) -> None` — method. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L28-L57)
- `class EnergyLimitedDispatch()` — dataclass. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L60-L73)

  Fields/values: `requested_active_mw: float (required/result field)`; `delivered_active_mw: float (required/result field)`; `duration_minutes: float (required/result field)`; `initial_soc: float (required/result field)`; `ending_soc: float (required/result field)`; `dispatch_stored_energy_change_mwh: float (required/result field)`; `auxiliary_energy_mwh: float (required/result field)`; `self_discharge_energy_mwh: float (required/result field)`; `stored_energy_change_mwh: float (required/result field)`; `power_shortfall_mw: float (required/result field)`; `energy_limited: bool (required/result field)`; `limiting_boundary: EnergyBoundary | None (required/result field)`.

- `def limit_active_power_by_energy(requested_active_mw: float, duration_minutes: float, state: StorageEnergyState) -> EnergyLimitedDispatch` — function. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L90-L214)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L217-L231)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L234-L269)

### models/energy_sequence.py

- `class EnergyDispatchSequence()` — dataclass. [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L22-L47)

  Fields/values: `intervals: tuple[EnergyLimitedDispatch, ...] (required/result field)`; `initial_soc: float (required/result field)`; `ending_soc: float (required/result field)`; `total_duration_minutes: float (required/result field)`; `requested_ac_energy_mwh: float (required/result field)`; `delivered_ac_energy_mwh: float (required/result field)`; `curtailed_ac_energy_mwh: float (required/result field)`; `delivered_discharge_ac_energy_mwh: float (required/result field)`; `delivered_charge_ac_energy_mwh: float (required/result field)`; `ac_energy_throughput_mwh: float (required/result field)`; `stored_discharge_energy_mwh: float (required/result field)`; `stored_charge_energy_mwh: float (required/result field)`; `stored_energy_throughput_mwh: float (required/result field)`; `conversion_loss_mwh: float (required/result field)`; `throughput_equivalent_full_cycles: float (required/result field)`; `conversion_balance_error_mwh: float (required/result field)`; `dispatch_stored_energy_change_mwh: float (required/result field)`; `auxiliary_energy_mwh: float (required/result field)`; `self_discharge_energy_mwh: float (required/result field)`; `stored_energy_change_mwh: float (required/result field)`; `soc_balance_error: float (required/result field)`; `limited_interval_count: int (required/result field)`.

- `def simulate_energy_dispatch_sequence(requested_active_mw: Sequence[float], duration_minutes: Sequence[float], state: StorageEnergyState) -> EnergyDispatchSequence` — function. [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L50-L183)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L203-L225)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L228-L300)

### models/frequency_watt.py

- `class FrequencyWattCurve()` — dataclass. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L85-L136)

  Fields/values: `nominal_frequency_hz: float = 50.0`; `deadband_hz: float = 0.05`; `full_response_deviation_hz: float = 0.5`; `max_discharge_mw: float = 100.0`; `max_charge_mw: float = 100.0`.

- `FrequencyWattCurve.validate`: `def validate(self) -> None` — method. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L95-L115)
- `FrequencyWattCurve.active_adjustment_mw`: `def active_adjustment_mw(self, frequency_hz: float) -> float` — method. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L117-L136)
- `class FrequencyWattDispatch()` — dataclass. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L139-L156)

  Fields/values: `frequency_hz: float (required/result field)`; `control_frequency_hz: float (required/result field)`; `baseline_active_mw: float (required/result field)`; `droop_adjustment_mw: float (required/result field)`; `unconstrained_active_mw: float (required/result field)`; `power_bounded_active_mw: float (required/result field)`; `ramp_bounded_active_mw: float (required/result field)`; `temperature_bounded_active_mw: float (required/result field)`; `bounded_active_mw: float (required/result field)`; `storage_power_limited: bool (required/result field)`; `frequency_filter: FirstOrderFilterStep | None (required/result field)`; `ramp: RampLimitedDispatch | None (required/result field)`; `temperature_derating: TemperatureLimitedDispatch | None (required/result field)`; `energy: EnergyLimitedDispatch | None (required/result field)`; `delivered_energy: EnergyLimitedDispatch | None (required/result field)`; `capability: CapabilityResult (required/result field)`.

- `def dispatch_frequency_watt(frequency_hz: float, baseline_active_mw: float, reactive_power_mvar: float, apparent_power_limit_mva: float | None, curve: FrequencyWattCurve=FrequencyWattCurve(), priority: PowerPriority | str=PowerPriority.ACTIVE, energy_state: StorageEnergyState | None=None, duration_minutes: float | None=None, ramp_limits: RampRateLimits | None=None, previous_active_mw: float | None=None, ramp_interval_seconds: float | None=None, frequency_filter_config: FirstOrderFilterConfig | None=None, previous_filtered_frequency_hz: float | None=None, measurement_interval_seconds: float | None=None, capability_envelope: PiecewiseCapabilityCurve | DirectionalCapabilityEnvelope | None=None, temperature_c: float | None=None, temperature_derating_curve: TemperaturePowerDeratingCurve | None=None) -> FrequencyWattDispatch` — function. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L159-L320)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L323-L362)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L365-L594)

### models/grid_support_sequence.py

- `class GridSupportInterval()` — dataclass. [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L55-L68)

  Fields/values: `frequency_hz: float (required/result field)`; `voltage_pu: float (required/result field)`; `baseline_active_mw: float (required/result field)`; `duration_minutes: float (required/result field)`; `reactive_request_pu: float (required/result field)`; `requested_reactive_mvar: float (required/result field)`; `temperature_c: float | None (required/result field)`; `initial_soc: float (required/result field)`; `ending_soc: float (required/result field)`; `dispatch: FrequencyWattDispatch (required/result field)`.

- `class GridSupportSequence()` — dataclass. [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L71-L95)

  Fields/values: `intervals: tuple[GridSupportInterval, ...] (required/result field)`; `initial_soc: float (required/result field)`; `ending_soc: float (required/result field)`; `total_duration_minutes: float (required/result field)`; `requested_active_energy_mwh: float (required/result field)`; `delivered_active_energy_mwh: float (required/result field)`; `active_shortfall_energy_mwh: float (required/result field)`; `requested_reactive_service_mvarh: float (required/result field)`; `delivered_reactive_service_mvarh: float (required/result field)`; `reactive_shortfall_service_mvarh: float (required/result field)`; `dispatch_stored_energy_change_mwh: float (required/result field)`; `auxiliary_energy_mwh: float (required/result field)`; `self_discharge_energy_mwh: float (required/result field)`; `stored_energy_change_mwh: float (required/result field)`; `soc_balance_error: float (required/result field)`; `limited_interval_count: int (required/result field)`; `storage_power_limited_interval_count: int (required/result field)`; `temperature_limited_interval_count: int (required/result field)`; `ramp_limited_interval_count: int (required/result field)`; `energy_limited_interval_count: int (required/result field)`; `capability_limited_interval_count: int (required/result field)`.

- `def simulate_grid_support_sequence(frequency_hz: Sequence[float], voltage_pu: Sequence[float], baseline_active_mw: Sequence[float], duration_minutes: Sequence[float], energy_state: StorageEnergyState, apparent_power_limit_mva: float | None, frequency_curve: FrequencyWattCurve=FrequencyWattCurve(), voltage_curve: VoltVarCurve=VoltVarCurve(), reactive_base_mvar: float | None=None, priority: PowerPriority | str=PowerPriority.REACTIVE, ramp_limits: RampRateLimits | None=None, initial_active_mw: float | None=None, frequency_filter_config: FirstOrderFilterConfig | None=None, initial_filtered_frequency_hz: float | None=None, capability_envelope: PiecewiseCapabilityCurve | DirectionalCapabilityEnvelope | None=None, temperature_c: Sequence[float] | None=None, temperature_derating_curve: TemperaturePowerDeratingCurve | None=None) -> GridSupportSequence` — function. [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L124-L386)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L406-L457)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L479-L655)

### models/measurement_filter.py

- `class FirstOrderFilterConfig()` — dataclass. [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L9-L20)

  Fields/values: `time_constant_seconds: float (required/result field)`.

- `FirstOrderFilterConfig.validate`: `def validate(self) -> None` — method. [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L15-L20)
- `class FirstOrderFilterStep()` — dataclass. [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L23-L32)

  Fields/values: `input_value: float (required/result field)`; `previous_output_value: float (required/result field)`; `output_value: float (required/result field)`; `interval_seconds: float (required/result field)`; `time_constant_seconds: float (required/result field)`; `decay_factor: float (required/result field)`; `input_step: float (required/result field)`; `output_change: float (required/result field)`.

- `def filter_first_order_step(input_value: float, previous_output_value: float, interval_seconds: float, config: FirstOrderFilterConfig) -> FirstOrderFilterStep` — function. [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L35-L71)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L74-L82)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L85-L101)

### models/pq_capability.py

- `class PowerPriority(str, Enum)` — enum. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L12-L15)

  Fields/values: `ACTIVE = 'active'`; `REACTIVE = 'reactive'`; `PROPORTIONAL = 'proportional'`.

- `class CapabilityQuadrant(str, Enum)` — enum. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L18-L22)

  Fields/values: `DISCHARGE_INJECTION = 'discharge_injection'`; `DISCHARGE_ABSORPTION = 'discharge_absorption'`; `CHARGE_INJECTION = 'charge_injection'`; `CHARGE_ABSORPTION = 'charge_absorption'`.

- `class CapabilityResult()` — dataclass. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L25-L36)

  Fields/values: `requested_active_mw: float (required/result field)`; `requested_reactive_mvar: float (required/result field)`; `active_mw: float (required/result field)`; `reactive_mvar: float (required/result field)`; `apparent_power_mva: float (required/result field)`; `utilization: float (required/result field)`; `curtailed_active_mw: float (required/result field)`; `curtailed_reactive_mvar: float (required/result field)`; `limited: bool (required/result field)`; `priority: PowerPriority (required/result field)`.

- `class CapabilityCurvePoint()` — dataclass. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L39-L42)

  Fields/values: `active_mw: float (required/result field)`; `reactive_limit_mvar: float (required/result field)`.

- `class PiecewiseCapabilityCurve()` — dataclass. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L45-L181)

  Fields/values: `points: tuple[CapabilityCurvePoint, ...] (required/result field)`.

- `PiecewiseCapabilityCurve.maximum_active_mw`: `def maximum_active_mw(self) -> float` — property. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L94-L96)
- `PiecewiseCapabilityCurve.maximum_reactive_mvar`: `def maximum_reactive_mvar(self) -> float` — property. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L98-L100)
- `PiecewiseCapabilityCurve.reactive_limit_mvar`: `def reactive_limit_mvar(self, active_mw: float) -> float` — method. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L102-L118)
- `PiecewiseCapabilityCurve.active_limit_mw`: `def active_limit_mw(self, reactive_mvar: float) -> float` — method. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L120-L134)
- `PiecewiseCapabilityCurve.contains`: `def contains(self, active_mw: float, reactive_mvar: float) -> bool` — method. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L136-L146)
- `PiecewiseCapabilityCurve.radial_limit_mva`: `def radial_limit_mva(self, active_mw: float, reactive_mvar: float) -> float` — method. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L148-L181)
- `class DirectionalCapabilityEnvelope()` — dataclass. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L184-L260)

  Fields/values: `discharge_injection: PiecewiseCapabilityCurve (required/result field)`; `discharge_absorption: PiecewiseCapabilityCurve (required/result field)`; `charge_injection: PiecewiseCapabilityCurve (required/result field)`; `charge_absorption: PiecewiseCapabilityCurve (required/result field)`.

- `DirectionalCapabilityEnvelope.curves`: `def curves(self) -> dict[CapabilityQuadrant, PiecewiseCapabilityCurve]` — property. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L225-L232)
- `DirectionalCapabilityEnvelope.point_count`: `def point_count(self) -> int` — property. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L234-L236)
- `DirectionalCapabilityEnvelope.quadrant_for`: `def quadrant_for(self, active_mw: float, reactive_mvar: float) -> CapabilityQuadrant` — method. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L238-L253)
- `DirectionalCapabilityEnvelope.curve_for`: `def curve_for(self, active_mw: float, reactive_mvar: float) -> PiecewiseCapabilityCurve` — method. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L255-L260)
- `CapabilityBoundary = float | PiecewiseCapabilityCurve | DirectionalCapabilityEnvelope` — type_alias. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L263-L263)
- `def allocate_power(requested_active_mw: float, requested_reactive_mvar: float, apparent_power_limit_mva: float, priority: PowerPriority | str=PowerPriority.ACTIVE) -> CapabilityResult` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L312-L365)
- `def allocate_power_on_curve(requested_active_mw: float, requested_reactive_mvar: float, curve: PiecewiseCapabilityCurve, priority: PowerPriority | str=PowerPriority.ACTIVE) -> CapabilityResult` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L368-L432)
- `def allocate_power_on_directional_envelope(requested_active_mw: float, requested_reactive_mvar: float, envelope: DirectionalCapabilityEnvelope, priority: PowerPriority | str=PowerPriority.ACTIVE) -> CapabilityResult` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L435-L449)
- `def allocate_power_on_boundary(requested_active_mw: float, requested_reactive_mvar: float, boundary: CapabilityBoundary, priority: PowerPriority | str=PowerPriority.ACTIVE) -> CapabilityResult` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L452-L484)
- `def reactive_axis_limit_mvar(boundary: CapabilityBoundary, reactive_mvar: float) -> float` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L487-L507)
- `def load_capability_curve_csv(path: str | Path) -> PiecewiseCapabilityCurve` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L510-L539)
- `def load_directional_capability_csv(path: str | Path) -> DirectionalCapabilityEnvelope` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L542-L605)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L608-L623)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L626-L673)

### models/ramp_limits.py

- `class RampDirection(str, Enum)` — enum. [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L10-L12)

  Fields/values: `UP = 'ramp_up'`; `DOWN = 'ramp_down'`.

- `class RampRateLimits()` — dataclass. [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L15-L29)

  Fields/values: `ramp_up_mw_per_minute: float (required/result field)`; `ramp_down_mw_per_minute: float (required/result field)`.

- `RampRateLimits.validate`: `def validate(self) -> None` — method. [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L22-L29)
- `class RampLimitedDispatch()` — dataclass. [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L32-L43)

  Fields/values: `previous_active_mw: float (required/result field)`; `requested_active_mw: float (required/result field)`; `delivered_active_mw: float (required/result field)`; `interval_seconds: float (required/result field)`; `minimum_active_mw: float (required/result field)`; `maximum_active_mw: float (required/result field)`; `power_change_mw: float (required/result field)`; `power_shortfall_mw: float (required/result field)`; `ramp_limited: bool (required/result field)`; `limiting_direction: RampDirection | None (required/result field)`.

- `def limit_active_power_by_ramp(requested_active_mw: float, previous_active_mw: float, interval_seconds: float, limits: RampRateLimits) -> RampLimitedDispatch` — function. [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L46-L95)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L98-L107)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L110-L133)

### models/reserve_headroom.py

- `class ReserveHeadroom()` — dataclass. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L37-L51)

  Fields/values: `baseline_active_mw: float (required/result field)`; `reactive_power_mvar: float (required/result field)`; `duration_minutes: float (required/result field)`; `upward_limit_active_mw: float (required/result field)`; `downward_limit_active_mw: float (required/result field)`; `upward_reserve_mw: float (required/result field)`; `downward_reserve_mw: float (required/result field)`; `upward_energy_limited: bool (required/result field)`; `downward_energy_limited: bool (required/result field)`; `upward_capability_limited: bool (required/result field)`; `downward_capability_limited: bool (required/result field)`.

- `def calculate_reserve_headroom(baseline_active_mw: float, duration_minutes: float, maximum_discharge_mw: float, maximum_charge_mw: float, state: StorageEnergyState, *, reactive_power_mvar: float=0.0, capability_boundary: CapabilityBoundary | None=None) -> ReserveHeadroom` — function. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L75-L214)
- `def add_capability_boundary_arguments(parser: argparse.ArgumentParser) -> None` — function. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L217-L222)
- `def capability_boundary_from_args(args: argparse.Namespace) -> CapabilityBoundary | None` — function. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L225-L232)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L235-L252)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L255-L299)

### models/reserve_sequence.py

- `class ReserveSequenceInterval()` — dataclass. [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L36-L42)

  Fields/values: `index: int (required/result field)`; `reserve: ReserveHeadroom (required/result field)`; `baseline_dispatch: EnergyLimitedDispatch (required/result field)`.

- `class ReserveSequenceAudit()` — dataclass. [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L45-L67)

  Fields/values: `intervals: tuple[ReserveSequenceInterval, ...] (required/result field)`; `response_duration_minutes: float (required/result field)`; `reactive_power_mvar_profile: tuple[float, ...] (required/result field)`; `initial_soc: float (required/result field)`; `ending_soc: float (required/result field)`; `total_schedule_duration_minutes: float (required/result field)`; `baseline_ac_energy_mwh: float (required/result field)`; `stored_energy_change_mwh: float (required/result field)`; `auxiliary_energy_mwh: float (required/result field)`; `self_discharge_energy_mwh: float (required/result field)`; `soc_balance_error: float (required/result field)`; `minimum_upward_reserve_mw: float (required/result field)`; `minimum_upward_reserve_interval: int (required/result field)`; `minimum_downward_reserve_mw: float (required/result field)`; `minimum_downward_reserve_interval: int (required/result field)`; `upward_energy_limited_interval_count: int (required/result field)`; `downward_energy_limited_interval_count: int (required/result field)`; `upward_capability_limited_interval_count: int (required/result field)`; `downward_capability_limited_interval_count: int (required/result field)`.

- `def audit_reserve_sequence(baseline_active_mw: Sequence[float], interval_duration_minutes: Sequence[float], response_duration_minutes: float, maximum_discharge_mw: float, maximum_charge_mw: float, state: StorageEnergyState, *, reactive_power_mvar: float=0.0, reactive_power_mvar_profile: Sequence[float] | None=None, capability_boundary: CapabilityBoundary | None=None) -> ReserveSequenceAudit` — function. [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L70-L220)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L240-L267)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L270-L336)

### models/temperature_derating.py

- `class TemperaturePowerPoint()` — dataclass. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L11-L17)

  Fields/values: `temperature_c: float (required/result field)`; `max_discharge_mw: float (required/result field)`; `max_charge_mw: float (required/result field)`.

- `class InterpolatedTemperatureLimits()` — dataclass. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L20-L30)

  Fields/values: `temperature_c: float (required/result field)`; `lower_temperature_c: float (required/result field)`; `upper_temperature_c: float (required/result field)`; `interpolation_fraction: float (required/result field)`; `max_discharge_mw: float (required/result field)`; `max_charge_mw: float (required/result field)`; `endpoint_clamped: bool (required/result field)`.

- `class TemperatureLimitedDispatch()` — dataclass. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L33-L46)

  Fields/values: `requested_active_mw: float (required/result field)`; `nameplate_bounded_active_mw: float (required/result field)`; `delivered_active_mw: float (required/result field)`; `nameplate_max_discharge_mw: float (required/result field)`; `nameplate_max_charge_mw: float (required/result field)`; `effective_max_discharge_mw: float (required/result field)`; `effective_max_charge_mw: float (required/result field)`; `nameplate_limited: bool (required/result field)`; `temperature_limited: bool (required/result field)`; `limits: InterpolatedTemperatureLimits (required/result field)`.

- `class TemperaturePowerDeratingCurve()` — dataclass. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L49-L124)

  Fields/values: `points: tuple[TemperaturePowerPoint, ...] (required/result field)`.

- `TemperaturePowerDeratingCurve.limits_at`: `def limits_at(self, temperature_c: float) -> InterpolatedTemperatureLimits` — method. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L79-L124)
- `def limit_active_power_by_temperature(requested_active_mw: float, temperature_c: float, nameplate_max_discharge_mw: float, nameplate_max_charge_mw: float, curve: TemperaturePowerDeratingCurve) -> TemperatureLimitedDispatch` — function. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L127-L182)
- `def load_temperature_derating_csv(path: str | Path) -> TemperaturePowerDeratingCurve` — function. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L185-L222)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L225-L234)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L237-L256)

### models/volt_var.py

- `class VoltVarCurve()` — dataclass. [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L18-L75)

  Fields/values: `low_saturation_pu: float = 0.92`; `low_deadband_pu: float = 0.98`; `high_deadband_pu: float = 1.02`; `high_saturation_pu: float = 1.08`; `max_reactive_power_pu: float = 1.0`.

- `VoltVarCurve.validate`: `def validate(self) -> None` — method. [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L28-L53)
- `VoltVarCurve.reactive_request_pu`: `def reactive_request_pu(self, voltage_pu: float) -> float` — method. [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L55-L75)
- `class VoltVarDispatch()` — dataclass. [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L78-L83)

  Fields/values: `voltage_pu: float (required/result field)`; `reactive_request_pu: float (required/result field)`; `requested_reactive_mvar: float (required/result field)`; `capability: CapabilityResult (required/result field)`.

- `def dispatch_volt_var(voltage_pu: float, active_power_mw: float, apparent_power_limit_mva: float, reactive_base_mvar: float | None=None, curve: VoltVarCurve=VoltVarCurve(), priority: PowerPriority | str=PowerPriority.REACTIVE) -> VoltVarDispatch` — function. [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L86-L114)
- `def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace` — function. [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L117-L135)
- `def main(argv: Sequence[str] | None=None) -> int` — function. [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L138-L164)

## CLI option catalogue

All eleven scripts expose `--help`. The table records each declared argument in source, including required/default/type/choice expressions; absent optional defaults mean argparse supplies `None` unless the main function supplies a documented construction default. For frequency-watt optional energy inputs, capacity/initial SOC/duration form the required group and constructor defaults are applied only when that feature is enabled. Grid-support baseline profiles default to zeros when omitted. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L381-L425) [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L479-L484)

The shared reserve boundary helper adds `--reactive-mvar` and mutually exclusive `--limit-mva` / `--curve-csv` / `--directional-curve-csv` to both reserve CLIs. A nonzero Q obligation requires a boundary. Other CLI boundary groups are required. Optional filter/ramp/temperature configurations must be supplied in their complete paired/grouped form. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L107-L127) [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L217-L252) [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L240-L267)


### energy_limits options

| Option | Declared contract | Source |
|---|---|---|
| `--active-mw` | `type=float; required=True` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L221-L221) |
| `--duration-minutes` | `type=float; required=True` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L222-L222) |
| `--energy-capacity-mwh` | `type=float; required=True` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L223-L223) |
| `--initial-soc` | `type=float; required=True` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L224-L224) |
| `--minimum-soc` | `type=float; default=0.1` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L225-L225) |
| `--maximum-soc` | `type=float; default=0.9` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L226-L226) |
| `--charge-efficiency` | `type=float; default=0.95` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L227-L227) |
| `--discharge-efficiency` | `type=float; default=0.95` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L228-L228) |
| `--auxiliary-load-mw` | `type=float; default=0.0` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L229-L229) |
| `--self-discharge-rate-per-hour` | `type=float; default=0.0` | [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L230-L230) |

### energy_sequence options

| Option | Declared contract | Source |
|---|---|---|
| `--active-mw-profile` | `type=_parse_number_series; required=True` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L207-L211) |
| `--duration-minutes-profile` | `type=_parse_number_series; required=True` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L212-L216) |
| `--energy-capacity-mwh` | `type=float; required=True` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L217-L217) |
| `--initial-soc` | `type=float; required=True` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L218-L218) |
| `--minimum-soc` | `type=float; default=0.1` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L219-L219) |
| `--maximum-soc` | `type=float; default=0.9` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L220-L220) |
| `--charge-efficiency` | `type=float; default=0.95` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L221-L221) |
| `--discharge-efficiency` | `type=float; default=0.95` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L222-L222) |
| `--auxiliary-load-mw` | `type=float; default=0.0` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L223-L223) |
| `--self-discharge-rate-per-hour` | `type=float; default=0.0` | [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L224-L224) |

### frequency_watt options

| Option | Declared contract | Source |
|---|---|---|
| `--frequency-hz` | `type=float; required=True` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L327-L327) |
| `--baseline-active-mw` | `type=float; default=0.0` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L328-L328) |
| `--reactive-mvar` | `type=float; default=0.0` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L329-L329) |
| `--limit-mva` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L331-L331) |
| `--curve-csv` | `type=Path` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L332-L332) |
| `--directional-curve-csv` | `type=Path` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L333-L333) |
| `--priority` | `choices=[item.value for item in PowerPriority]; default=PowerPriority.ACTIVE.value` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L334-L338) |
| `--nominal-frequency-hz` | `type=float; default=50.0` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L339-L339) |
| `--deadband-hz` | `type=float; default=0.05` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L340-L340) |
| `--full-response-deviation-hz` | `type=float; default=0.5` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L341-L341) |
| `--max-discharge-mw` | `type=float; default=100.0` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L342-L342) |
| `--max-charge-mw` | `type=float; default=100.0` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L343-L343) |
| `--temperature-c` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L344-L344) |
| `--temperature-derating-csv` | `type=Path` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L345-L345) |
| `--previous-filtered-frequency-hz` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L346-L346) |
| `--measurement-interval-seconds` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L347-L347) |
| `--frequency-filter-time-constant-seconds` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L348-L348) |
| `--previous-active-mw` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L349-L349) |
| `--ramp-interval-seconds` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L350-L350) |
| `--ramp-up-mw-per-minute` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L351-L351) |
| `--ramp-down-mw-per-minute` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L352-L352) |
| `--duration-minutes` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L353-L353) |
| `--energy-capacity-mwh` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L354-L354) |
| `--initial-soc` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L355-L355) |
| `--minimum-soc` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L356-L356) |
| `--maximum-soc` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L357-L357) |
| `--charge-efficiency` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L358-L358) |
| `--discharge-efficiency` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L359-L359) |
| `--auxiliary-load-mw` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L360-L360) |
| `--self-discharge-rate-per-hour` | `type=float` | [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L361-L361) |

### grid_support_sequence options

| Option | Declared contract | Source |
|---|---|---|
| `--frequency-hz-profile` | `type=_parse_number_series; required=True` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L412-L414) |
| `--voltage-pu-profile` | `type=_parse_number_series; required=True` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L415-L417) |
| `--baseline-active-mw-profile` | `type=_parse_number_series` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L418-L418) |
| `--duration-minutes-profile` | `type=_parse_number_series; required=True` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L419-L421) |
| `--limit-mva` | `type=float` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L423-L423) |
| `--curve-csv` | `type=Path` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L424-L424) |
| `--directional-curve-csv` | `type=Path` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L425-L425) |
| `--energy-capacity-mwh` | `type=float; required=True` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L426-L426) |
| `--initial-soc` | `type=float; required=True` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L427-L427) |
| `--minimum-soc` | `type=float; default=0.1` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L428-L428) |
| `--maximum-soc` | `type=float; default=0.9` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L429-L429) |
| `--charge-efficiency` | `type=float; default=0.95` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L430-L430) |
| `--discharge-efficiency` | `type=float; default=0.95` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L431-L431) |
| `--auxiliary-load-mw` | `type=float; default=0.0` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L432-L432) |
| `--self-discharge-rate-per-hour` | `type=float; default=0.0` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L433-L433) |
| `--reactive-base-mvar` | `type=float` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L434-L434) |
| `--priority` | `choices=[item.value for item in PowerPriority]; default=PowerPriority.REACTIVE.value` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L435-L439) |
| `--nominal-frequency-hz` | `type=float; default=50.0` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L440-L440) |
| `--frequency-deadband-hz` | `type=float; default=0.05` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L441-L441) |
| `--full-response-deviation-hz` | `type=float; default=0.5` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L442-L442) |
| `--max-discharge-mw` | `type=float; default=100.0` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L443-L443) |
| `--max-charge-mw` | `type=float; default=100.0` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L444-L444) |
| `--temperature-c-profile` | `type=_parse_number_series` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L445-L445) |
| `--temperature-derating-csv` | `type=Path` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L446-L446) |
| `--low-saturation-pu` | `type=float; default=0.92` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L447-L447) |
| `--low-deadband-pu` | `type=float; default=0.98` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L448-L448) |
| `--high-deadband-pu` | `type=float; default=1.02` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L449-L449) |
| `--high-saturation-pu` | `type=float; default=1.08` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L450-L450) |
| `--max-reactive-power-pu` | `type=float; default=1.0` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L451-L451) |
| `--initial-active-mw` | `type=float` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L452-L452) |
| `--ramp-up-mw-per-minute` | `type=float` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L453-L453) |
| `--ramp-down-mw-per-minute` | `type=float` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L454-L454) |
| `--initial-filtered-frequency-hz` | `type=float` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L455-L455) |
| `--frequency-filter-time-constant-seconds` | `type=float` | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L456-L456) |

### measurement_filter options

| Option | Declared contract | Source |
|---|---|---|
| `--input-value` | `type=float; required=True` | [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L78-L78) |
| `--previous-output-value` | `type=float; required=True` | [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L79-L79) |
| `--interval-seconds` | `type=float; required=True` | [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L80-L80) |
| `--time-constant-seconds` | `type=float; required=True` | [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L81-L81) |

### pq_capability options

| Option | Declared contract | Source |
|---|---|---|
| `--active-mw` | `type=float; required=True` | [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L612-L612) |
| `--reactive-mvar` | `type=float; required=True` | [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L613-L613) |
| `--limit-mva` | `type=float` | [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L615-L615) |
| `--curve-csv` | `type=Path` | [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L616-L616) |
| `--directional-curve-csv` | `type=Path` | [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L617-L617) |
| `--priority` | `choices=[item.value for item in PowerPriority]; default=PowerPriority.ACTIVE.value` | [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L618-L622) |

### ramp_limits options

| Option | Declared contract | Source |
|---|---|---|
| `--active-mw` | `type=float; required=True` | [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L102-L102) |
| `--previous-active-mw` | `type=float; required=True` | [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L103-L103) |
| `--interval-seconds` | `type=float; required=True` | [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L104-L104) |
| `--ramp-up-mw-per-minute` | `type=float; required=True` | [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L105-L105) |
| `--ramp-down-mw-per-minute` | `type=float; required=True` | [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L106-L106) |

### reserve_headroom options

| Option | Declared contract | Source |
|---|---|---|
| `--reactive-mvar` | `type=float; default=0.0` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L218-L218) |
| `--limit-mva` | `type=float` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L220-L220) |
| `--curve-csv` | `type=Path` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L221-L221) |
| `--directional-curve-csv` | `type=Path` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L222-L222) |
| `--baseline-active-mw` | `type=float; required=True` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L239-L239) |
| `--duration-minutes` | `type=float; required=True` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L240-L240) |
| `--maximum-discharge-mw` | `type=float; required=True` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L241-L241) |
| `--maximum-charge-mw` | `type=float; required=True` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L242-L242) |
| `--energy-capacity-mwh` | `type=float; required=True` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L243-L243) |
| `--initial-soc` | `type=float; required=True` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L244-L244) |
| `--minimum-soc` | `type=float; default=0.1` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L245-L245) |
| `--maximum-soc` | `type=float; default=0.9` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L246-L246) |
| `--charge-efficiency` | `type=float; default=0.95` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L247-L247) |
| `--discharge-efficiency` | `type=float; default=0.95` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L248-L248) |
| `--auxiliary-load-mw` | `type=float; default=0.0` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L249-L249) |
| `--self-discharge-rate-per-hour` | `type=float; default=0.0` | [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L250-L250) |

### reserve_sequence options

| Option | Declared contract | Source |
|---|---|---|
| `--baseline-active-mw-profile` | `type=_parse_number_series; required=True` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L244-L248) |
| `--interval-duration-minutes-profile` | `type=_parse_number_series; required=True` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L249-L253) |
| `--reactive-mvar-profile` | `type=_parse_number_series` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L254-L254) |
| `--response-duration-minutes` | `type=float; required=True` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L255-L255) |
| `--maximum-discharge-mw` | `type=float; required=True` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L256-L256) |
| `--maximum-charge-mw` | `type=float; required=True` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L257-L257) |
| `--energy-capacity-mwh` | `type=float; required=True` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L258-L258) |
| `--initial-soc` | `type=float; required=True` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L259-L259) |
| `--minimum-soc` | `type=float; default=0.1` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L260-L260) |
| `--maximum-soc` | `type=float; default=0.9` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L261-L261) |
| `--charge-efficiency` | `type=float; default=0.95` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L262-L262) |
| `--discharge-efficiency` | `type=float; default=0.95` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L263-L263) |
| `--auxiliary-load-mw` | `type=float; default=0.0` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L264-L264) |
| `--self-discharge-rate-per-hour` | `type=float; default=0.0` | [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L265-L265) |

### temperature_derating options

| Option | Declared contract | Source |
|---|---|---|
| `--active-mw` | `type=float; required=True` | [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L229-L229) |
| `--temperature-c` | `type=float; required=True` | [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L230-L230) |
| `--max-discharge-mw` | `type=float; required=True` | [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L231-L231) |
| `--max-charge-mw` | `type=float; required=True` | [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L232-L232) |
| `--curve-csv` | `type=Path; required=True` | [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L233-L233) |

### volt_var options

| Option | Declared contract | Source |
|---|---|---|
| `--voltage-pu` | `type=float; required=True` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L121-L121) |
| `--active-mw` | `type=float; required=True` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L122-L122) |
| `--limit-mva` | `type=float; required=True` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L123-L123) |
| `--reactive-base-mvar` | `type=float` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L124-L124) |
| `--priority` | `choices=[item.value for item in PowerPriority]; default=PowerPriority.REACTIVE.value` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L125-L129) |
| `--low-saturation-pu` | `type=float; default=0.92` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L130-L130) |
| `--low-deadband-pu` | `type=float; default=0.98` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L131-L131) |
| `--high-deadband-pu` | `type=float; default=1.02` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L132-L132) |
| `--high-saturation-pu` | `type=float; default=1.08` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L133-L133) |
| `--max-reactive-power-pu` | `type=float; default=1.0` | [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L134-L134) |

## Browser interfaces and controls

The UMD engine exports through `module.exports` in a compatible JavaScript harness or `globalThis.LabSimulation` in the browser. Its five members are:

| Member | Contract |
|---|---|
| `LabSimulation.MODEL_SPECS` | Ten model specifications, including declared ranges/defaults/metrics |
| `LabSimulation.getModelSpec(kind)` | Return a specification; unknown kind throws |
| `LabSimulation.resolveParameters(kind, provided)` | Finite numeric values clamp to min/max; nonnumeric/missing values use engine defaults; no step snapping |
| `LabSimulation.evaluateModel(kind, provided, time)` | Resolve parameters and clamp finite model time to the branch horizon; return metrics |
| `LabSimulation.checkCheckpoint(checkpoint, metrics)` | Return pass/fail/invalid; equality and inclusive inequalities use absolute tolerance, strict inequalities do not |

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L165-L177) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L249-L355)

The three `LabDashboard` members are `LabDashboard.getState()`, `LabDashboard.evaluateModel` and `LabDashboard.getModelSpec`. The snapshot reports kind, copied parameter values, model time, playing state, active metric and active module; the latter two members alias the engine. This makes **eight explicitly exposed JavaScript members** in the catalogue. The review did not exercise a live DOM through that facade. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L488-L488)

The main UI offers parameter sliders, model-time selection, run/pause/reset, module tabs, preset loading, checkpoint checks, 241-sample telemetry CSV export and configuration copy/download. Config export contains the embedded teaching configuration; telemetry contains current parameter values. `docs/portfolio` separately stores study notes/progress locally in the browser. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L419-L488) [docs/portfolio/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/index.html#L270-L296)

## Stable interpretation boundaries

The main page's configured grid defaults and the generic engine defaults are distinct; specifically `batteryKW` is 0 in the lesson configuration and 100 in the engine. Input units are branch-specific; no automatic MW/kW or fraction/percent conversion occurs. The browser engine is not a Python bridge, a plant interface, or a scientific calibration package.
