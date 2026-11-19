# Parameters and symbols

[Handbook](../INDEX.md) · [Equations](EQUATIONS_AND_DERIVATIONS.md) · [Full API fields](../developer/API_CLI_AND_INTERFACES.md)

## Native units and signs

| Quantity | Units / convention | Interpretation |
|---|---|---|
| Active P and baseline | MW; positive discharge, negative charging | Signed AC setpoint or delivery |
| Reactive Q | MVAr; positive injection, negative absorption | Preserve interval direction |
| Circular S | Positive MVA | Static P–Q radius |
| Capacity and stored/AC energy | MWh | Distinguish AC conversion from stored inventory |
| SOC | Fraction 0–1 | Initial value must lie inside configured bounds |
| Charge/discharge efficiency | Fraction in (0,1] | Charge multiplies; discharge divides stored-energy exchange |
| Auxiliary load | Nonnegative MW, stored side | Separate feeder use is outside this account |
| Self-discharge rate | Nonnegative per hour | Continuous decay coefficient, not a percent input |
| Frequency | Positive Hz | Raw and filtered control values are distinct |
| Voltage | Nonnegative per unit | Native curve is normalized around 1 pu |
| Ramp rates | Positive MW/min | Signed power movement through zero |
| Filter/ramp interval | Seconds | Distinct from energy-response minutes |
| Temperature | °C | External curve coordinate; no thermal-state estimator |
| Reactive service | MVArh of absolute Q | Does not cancel injection against absorption |
| Throughput-equivalent cycles | Stored throughput/(2 × capacity) | Dimensionless throughput ratio; no aging law |

[models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L15-L57) [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L103-L180) [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L15-L95) [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L275-L335)

## Declared native configuration defaults

The following values come from dataclass definitions. “Required” means no field default. CLI-specific construction and required option groups remain in the [API catalogue](../developer/API_CLI_AND_INTERFACES.md); declaring a Python default is not evidence of a suitable project value.


### StorageEnergyState

| Field | Annotation | Default |
|---|---|---|
| `energy_capacity_mwh` | `float` | Required |
| `initial_soc` | `float` | Required |
| `minimum_soc` | `float` | `0.1` |
| `maximum_soc` | `float` | `0.9` |
| `charge_efficiency` | `float` | `0.95` |
| `discharge_efficiency` | `float` | `0.95` |
| `auxiliary_load_mw` | `float` | `0.0` |
| `self_discharge_rate_per_hour` | `float` | `0.0` |

[models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L15-L57)

### FrequencyWattCurve

| Field | Annotation | Default |
|---|---|---|
| `nominal_frequency_hz` | `float` | `50.0` |
| `deadband_hz` | `float` | `0.05` |
| `full_response_deviation_hz` | `float` | `0.5` |
| `max_discharge_mw` | `float` | `100.0` |
| `max_charge_mw` | `float` | `100.0` |

[models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L85-L136)

### FirstOrderFilterConfig

| Field | Annotation | Default |
|---|---|---|
| `time_constant_seconds` | `float` | Required |

[models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L9-L20)

### CapabilityCurvePoint

| Field | Annotation | Default |
|---|---|---|
| `active_mw` | `float` | Required |
| `reactive_limit_mvar` | `float` | Required |

[models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L39-L42)

### PiecewiseCapabilityCurve

| Field | Annotation | Default |
|---|---|---|
| `points` | `tuple[CapabilityCurvePoint, ...]` | Required |

[models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L45-L181)

### DirectionalCapabilityEnvelope

| Field | Annotation | Default |
|---|---|---|
| `discharge_injection` | `PiecewiseCapabilityCurve` | Required |
| `discharge_absorption` | `PiecewiseCapabilityCurve` | Required |
| `charge_injection` | `PiecewiseCapabilityCurve` | Required |
| `charge_absorption` | `PiecewiseCapabilityCurve` | Required |

[models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L184-L260)

### RampRateLimits

| Field | Annotation | Default |
|---|---|---|
| `ramp_up_mw_per_minute` | `float` | Required |
| `ramp_down_mw_per_minute` | `float` | Required |

[models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L15-L29)

### TemperaturePowerPoint

| Field | Annotation | Default |
|---|---|---|
| `temperature_c` | `float` | Required |
| `max_discharge_mw` | `float` | Required |
| `max_charge_mw` | `float` | Required |

[models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L11-L17)

### TemperaturePowerDeratingCurve

| Field | Annotation | Default |
|---|---|---|
| `points` | `tuple[TemperaturePowerPoint, ...]` | Required |

[models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L49-L124)

### VoltVarCurve

| Field | Annotation | Default |
|---|---|---|
| `low_saturation_pu` | `float` | `0.92` |
| `low_deadband_pu` | `float` | `0.98` |
| `high_deadband_pu` | `float` | `1.02` |
| `high_saturation_pu` | `float` | `1.08` |
| `max_reactive_power_pu` | `float` | `1.0` |

[models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L18-L75)

## CSV parameter provenance

| Fixture | Shape and purpose | Provenance limit |
|---|---|---|
| `illustrative_capability_curve.csv` | Four symmetric positive-quadrant samples | Illustrative, not a PCS rating |
| `illustrative_directional_capability.csv` | Four curves, sixteen total points | Distinct charge/discharge and injection/absorption limits; shared axes |
| `illustrative_temperature_derating.csv` | Six temperature samples with two power limits | External illustrative envelope; no temperature estimator |

[models/data/illustrative_capability_curve.csv](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/data/illustrative_capability_curve.csv#L1-L5) [models/data/illustrative_directional_capability.csv](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/data/illustrative_directional_capability.csv#L1-L17) [models/data/illustrative_temperature_derating.csv](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/data/illustrative_temperature_derating.csv#L1-L7)

Record project data origin, permission, applicable operating conditions, coordinate/sign conventions and validation separately before replacing these samples.

## Browser parameter inventory

The selected lesson is `grid`. All ten exported branches are inventoried below because callers can select them. “Engine default” is what a missing/non-numeric direct API input receives; selected lesson defaults override the displayed grid inputs. Slider steps describe the UI, not API quantization. Constants are synthetic teaching choices, not measured calibration.


### Browser battery (generic branch)

Model time: **h**; horizon: **6**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `capacityAh` | Ah | 20–200 / 5 | 100 | N/A |
| `currentA` | A | 0–30 / 1 | 12 | N/A |
| `resistanceOhm` | Ω | 0.005–0.1 / 0.005 | 0.035 | N/A |
| `ambientC` | °C | 0–45 / 1 | 25 | N/A |
| `initialSoc` | % | 30–100 / 5 | 90 | N/A |

Metrics: `socPct` (%, 1 display decimals); `voltageV` (V, 1 display decimals); `temperatureC` (°C, 1 display decimals); `powerKW` (kW, 2 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L178-L184)

### Browser thermal (generic branch)

Model time: **min**; horizon: **60**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `heatW` | W | 100–3000 / 100 | 1200 | N/A |
| `coolingWK` | W/K | 10–120 / 5 | 40 | N/A |
| `capacityJPerK` | J/K | 3000–60000 / 1000 | 18000 | N/A |
| `ambientC` | °C | 0–45 / 1 | 25 | N/A |

Metrics: `temperatureC` (°C, 1 display decimals); `heatRemovedW` (W, 0 display decimals); `storedEnergyKJ` (kJ, 1 display decimals); `residualW` (W, 0 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L185-L191)

### Browser degradation (generic branch)

Model time: **cycles**; horizon: **1000**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `fadePer1000Pct` | % / 1k cycles | 2–40 / 1 | 18 | N/A |
| `temperatureC` | °C | 10–50 / 1 | 25 | N/A |
| `cRate` | C | 0.2–3 / 0.1 | 1 | N/A |
| `initialCapacityAh` | Ah | 10–200 / 5 | 100 | N/A |

Metrics: `retentionPct` (%, 1 display decimals); `capacityAh` (Ah, 1 display decimals); `resistanceGrowthPct` (%, 1 display decimals); `throughputKWh` (kWh, 1 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L192-L198)

### Browser grid (selected)

Model time: **h**; horizon: **24**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `demandKW` | kW | 100–1200 / 25 | 500 | 500 |
| `solarKW` | kW | 0–1400 / 25 | 600 | 600 |
| `batteryKW` | kW | 0–300 / 10 | 100 | 0 |
| `carbonGPerKWh` | g/kWh | 0–800 / 25 | 400 | 400 |

Metrics: `gridImportKW` (kW, 1 display decimals); `solarOutputKW` (kW, 1 display decimals); `renewablePct` (%, 1 display decimals); `emissionsKgPerH` (kg/h, 1 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L199-L205)

### Browser cooling (generic branch)

Model time: **min**; horizon: **60**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `serverCount` | servers | 10–500 / 10 | 100 | N/A |
| `utilizationPct` | % | 10–90 / 5 | 65 | N/A |
| `ambientC` | °C | 5–45 / 1 | 30 | N/A |
| `coolingEfficiency` | ratio | 1.5–6 / 0.1 | 3.5 | N/A |

Metrics: `itKW` (kW, 1 display decimals); `coolingKW` (kW, 1 display decimals); `pue` (×, 2 display decimals); `inletC` (°C, 1 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L206-L212)

### Browser agents (generic branch)

Model time: **min**; horizon: **30**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `arrivalRate` | tasks/min | 2–40 / 1 | 12 | N/A |
| `agentCount` | agents | 1–12 / 1 | 4 | N/A |
| `serviceRate` | tasks/min | 1–10 / 0.5 | 4 | N/A |
| `coordinationPct` | % | 0–70 / 5 | 20 | N/A |

Metrics: `backlog` (tasks, 1 display decimals); `throughput` (tasks/min, 1 display decimals); `utilizationPct` (%, 1 display decimals); `waitMinutes` (min, 1 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L213-L219)

### Browser markets (generic branch)

Model time: **h**; horizon: **24**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `baseSpreadBps` | bps | 0–100 / 1 | 35 | N/A |
| `feeBps` | bps | 0–50 / 1 | 15 | N/A |
| `slippageBps` | bps | 0–30 / 1 | 8 | N/A |
| `notionalUSD` | USD | 1000–100000 / 1000 | 10000 | N/A |

Metrics: `spreadBps` (bps, 1 display decimals); `netEdgeBps` (bps, 1 display decimals); `netPnlUSD` (USD, 2 display decimals); `costUSD` (USD, 2 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L220-L226)

### Browser control (generic branch)

Model time: **s**; horizon: **20**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `setpoint` | units | 10–100 / 5 | 60 | N/A |
| `damping` | ζ | 0.1–2 / 0.05 | 0.5 | N/A |
| `naturalFrequency` | rad/s | 0.2–3 / 0.1 | 1 | N/A |
| `gain` | × | 0.5–1.5 / 0.05 | 1 | N/A |

Metrics: `output` (units, 2 display decimals); `error` (units, 2 display decimals); `velocity` (units/s, 2 display decimals); `overshootPct` (%, 1 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L227-L233)

### Browser security (generic branch)

Model time: **min**; horizon: **60**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `alertRate` | alerts/min | 2–60 / 1 | 20 | N/A |
| `analystCount` | people | 1–12 / 1 | 4 | N/A |
| `reviewRate` | alerts/min/person | 1–10 / 0.5 | 4 | N/A |
| `automationPct` | % | 0–90 / 5 | 35 | N/A |

Metrics: `backlog` (alerts, 1 display decimals); `coveragePct` (%, 1 display decimals); `reviewedAlerts` (alerts, 0 display decimals); `workloadPct` (%, 1 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L234-L240)

### Browser charging (generic branch)

Model time: **min**; horizon: **120**.

| Key | Unit | Range / UI step | Engine default | Selected lesson default |
|---|---|---|---|---|
| `capacityKWh` | kWh | 20–120 / 5 | 60 | N/A |
| `chargerKW` | kW | 5–180 / 5 | 60 | N/A |
| `initialSoc` | % | 5–70 / 5 | 20 | N/A |
| `efficiencyPct` | % | 75–99 / 1 | 92 | N/A |

Metrics: `socPct` (%, 1 display decimals); `chargingKW` (kW, 1 display decimals); `energyAddedKWh` (kWh, 2 display decimals); `lossKW` (kW, 2 display decimals).

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L241-L247)

## Precision and symbol conflicts

Native changed-power flags commonly use absolute `1e-12` comparisons. Shared directional axes use relative and absolute `1e-12`; the energy limiter additionally permits endpoint residual guards of `1e-10` MWh before clamping. These are local floating-point guards, not a universal accuracy or uncertainty specification. Browser checkpoints use their own declared metric tolerance; CLI display decimals are formatting. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L220-L223) [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L286-L296) [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L151-L193) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L338-L353)

- Native SOC is fractional; browser `initialSoc` in battery/charging branches is percent.
- Native capacity is MWh; browser branches use Ah or kWh according to their declared model.
- Native storage P is signed MW; selected browser `batteryKW` is a nonnegative fixed contribution.
- Native temperature derating consumes °C but does not use the shared browser thermal branch.
- A symbol such as $Q$, $C$, $\lambda$ or $t$ must be read with its local model, quantity and unit. No portfolio-wide meaning is silently imposed.

Native dataclass result fields and annotations are fully listed in the API catalogue. The operational symbols inventory preserves all 206 class fields/enum values and all 41 browser parameters/40 metrics without inventing numerical defaults for result records.
