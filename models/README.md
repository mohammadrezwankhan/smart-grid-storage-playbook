# Active/Reactive Capability Reference

This dependency-free Python example makes constrained active/reactive power
priority explicit. It applies a circular inverter capability limit and reports
the delivered command, curtailed command, apparent power, and utilization.

## Capability Rule

The requested command is feasible when:

```text
sqrt(P^2 + Q^2) <= S_limit
```

When the request is outside that circle, the selected policy behaves as
follows:

- `active`: preserve active power first and use remaining MVA headroom for
  reactive power;
- `reactive`: preserve reactive power first and use remaining headroom for
  active power; or
- `proportional`: scale active and reactive power by the same factor.

## Run A Constrained Example

```powershell
python models/pq_capability.py `
  --active-mw 80 `
  --reactive-mvar 80 `
  --limit-mva 100 `
  --priority active
```

Expected delivered command:

```text
Active power: 80.000 MW
Reactive power: 60.000 MVAr
Apparent power: 100.000 MVA
Capability utilization: 100.00%
```

Run the regression checks with:

```powershell
python -m unittest discover -s tests -v
```

## Explicit Limitations

- The capability boundary is a fixed circle rather than a manufacturer curve.
- Dynamic current limits, voltage dependence, and temperature derating are
  excluded. SOC and interval-duration limits can be composed through
  `energy_limits.py`, but are not inherent to the P-Q allocator.
- The allocator is static and does not model control-loop response.
- Grid-code, protection, and plant-controller constraints remain project
  inputs.
- Sign conventions must be aligned with the target EMS, PCS, and study model.

## Volt-VAR Dispatch Reference

[`volt_var.py`](volt_var.py) adds an illustrative four-breakpoint voltage
support curve and sends its reactive-power request through the circular P-Q
allocator. Positive reactive power means injection at low voltage; negative
reactive power means absorption at high voltage.

The default breakpoints are configurable educational values, not a claim about
any grid code, inverter setting, or interconnection agreement:

| Region | Default Behavior |
| --- | --- |
| `V <= 0.92 pu` | Saturate at `+1.0 pu` reactive request. |
| `0.92 < V < 0.98 pu` | Ramp linearly from injection to zero. |
| `0.98 <= V <= 1.02 pu` | Hold a zero-reactive-power deadband. |
| `1.02 < V < 1.08 pu` | Ramp linearly from zero to absorption. |
| `V >= 1.08 pu` | Saturate at `-1.0 pu` reactive request. |

Run a low-voltage case where reactive-priority dispatch reduces active power to
stay inside a 100 MVA limit:

```powershell
python models/volt_var.py `
  --voltage-pu 0.95 `
  --active-mw 90 `
  --limit-mva 100
```

Expected key values:

```text
Volt-VAR request: 0.500 pu
Requested reactive power: 50.000 MVAr
Capability limited: true
Delivered active power: 86.603 MW
Delivered reactive power: 50.000 MVAr
```

Use `--priority active` to study the competing policy that preserves active
power and curtails the reactive request instead. Replace all breakpoints,
reactive base, priority, and capability assumptions with project-controlled
settings before engineering use.

## Frequency-Watt Dispatch Reference

[`frequency_watt.py`](frequency_watt.py) adds an illustrative frequency
deadband, linear droop region, charge/discharge saturation, baseline schedule,
and circular P-Q capability enforcement. Positive active power means discharge
and injection into the grid; negative active power means charging. Below the
lower deadband boundary, the controller increases injection. Above the upper
deadband boundary, it reduces injection and can request charging.

The defaults assume a 50 Hz system, a `+/-0.05 Hz` deadband, and full response
at a `+/-0.50 Hz` deviation. These values are educational examples, not
grid-code or plant settings.

Run an under-frequency case with a 20 MW baseline export and an 80 MVAr request:

```powershell
python models/frequency_watt.py `
  --frequency-hz 49.725 `
  --baseline-active-mw 20 `
  --reactive-mvar 80 `
  --limit-mva 100
```

Expected key values with the default active-power priority:

```text
Droop adjustment: 50.000 MW
Storage-bounded active request: 70.000 MW
Capability limited: true
Delivered active power: 70.000 MW
Delivered reactive power: 71.414 MVAr
```

The model is static. It excludes sensor errors, higher-order measurement
dynamics, control-loop dynamics, recovery logic, and interactions with
plant-level dispatch. Optional filter arguments apply a first-order frequency
measurement filter before deadband and droop evaluation. Optional ramp
arguments enforce asymmetric signed active-power slew limits before SOC and P-Q
allocation. Optional energy arguments then enforce SOC reserve, response
duration, and charge/discharge efficiency. Replace every frequency, filter,
power, ramp, energy, efficiency, baseline, and priority assumption with
project-controlled values before engineering use.

## Frequency Measurement Filter

[`measurement_filter.py`](measurement_filter.py) applies the exact
zero-order-hold solution of a first-order low-pass filter over one interval:

```text
y_next = input + (y_previous - input) exp(-interval / time_constant)
```

This makes the raw frequency measurement and the filtered control frequency
separate, reviewable values. For example, a sudden raw measurement of 49.5 Hz
does not immediately leave the default deadband when the previous filtered
value is 50 Hz, the sample interval is 0.1 seconds, and the filter time constant
is 1 second:

```powershell
python models/frequency_watt.py `
  --frequency-hz 49.5 --baseline-active-mw 0 `
  --reactive-mvar 0 --limit-mva 100 `
  --previous-filtered-frequency-hz 50 `
  --measurement-interval-seconds 0.1 `
  --frequency-filter-time-constant-seconds 1
```

Expected filter and droop values:

```text
Frequency: 49.500 Hz
Control frequency: 49.952 Hz
Frequency-filter decay factor: 0.904837
Droop adjustment: 0.000 MW
```

The previous filtered value must be carried from the prior control interval.
The model assumes one constant input during each interval; it does not represent
sampling jitter, sensor bias, rate-of-change-of-frequency logic, or a
higher-order plant controller.

## Active-Power Ramp Limits

[`ramp_limits.py`](ramp_limits.py) converts separate ramp-up and ramp-down rates
in MW/minute into the active-power interval reachable from the previous plant
command. Increasing signed power is ramp-up, including movement from charging
toward discharge; decreasing signed power is ramp-down. Crossing zero therefore
uses one continuous signed slew limit rather than two disconnected magnitudes.

Run a frequency event that requests 70 MW from a previous 20 MW operating point
with only 30 seconds to respond:

```powershell
python models/frequency_watt.py `
  --frequency-hz 49.725 --baseline-active-mw 20 `
  --reactive-mvar 80 --limit-mva 100 `
  --previous-active-mw 20 --ramp-interval-seconds 30 `
  --ramp-up-mw-per-minute 40 --ramp-down-mw-per-minute 60
```

Expected ramp values:

```text
Power-bounded active request: 70.000 MW
Ramp-bounded active request: 40.000 MW
Ramp limited: true
Ramp limiting direction: ramp_up
```

The integrated sequence is raw measurement, optional frequency filter,
frequency-watt request, storage charge/discharge power bound, ramp bound,
interval energy bound, and circular P-Q allocation.
The returned `ramp`, `energy`, and `capability` records preserve each stage for
review. The ramp interval is the time available to move from the previous
command; it is distinct from the energy response duration.

## SOC And Response-Duration Limits

[`energy_limits.py`](energy_limits.py) converts SOC headroom into the maximum
constant AC charge or discharge power that can be sustained for one interval.
Positive active power discharges the battery; negative active power charges it.
Discharge efficiency increases the stored energy consumed per delivered MWh,
while charge efficiency reduces the stored energy gained per imported MWh.

Run a 60-minute discharge request that reaches a 20% minimum SOC boundary:

```powershell
python models/energy_limits.py `
  --active-mw 100 --duration-minutes 60 `
  --energy-capacity-mwh 50 --initial-soc 0.50 `
  --minimum-soc 0.20 --discharge-efficiency 0.90
```

Expected key values:

```text
Delivered active power: 13.500 MW
Energy limited: true
Limiting boundary: minimum_soc
Ending SOC: 0.2000
```

The same inputs can be added to `frequency_watt.py`; energy limiting is applied
after the frequency response and instantaneous storage power bound, but before
the P-Q capability allocator. This sequencing makes both energy curtailment and
inverter curtailment visible. The returned `energy` result describes the
energy-bounded request, while `delivered_energy` recomputes ending SOC from the
active power that remains after P-Q allocation.

This is a single-interval energy accounting reference. It does not model
self-discharge, auxiliary load, nonlinear efficiency, degradation, thermal
derating, or uncertain capacity.

## Multi-Interval Energy Trajectory

[`energy_sequence.py`](energy_sequence.py) carries ending SOC into the next
requested interval while delegating every power decision to the same
single-interval limiter. It supports variable durations and preserves the full
interval result so reviewers can see exactly where a request reached an SOC
boundary.

Run a four-interval profile that discharges to the minimum SOC boundary and
then recovers through charging:

```powershell
python models/energy_sequence.py `
  --active-mw-profile 50,50,50,-40 `
  --duration-minutes-profile 15,15,15,30 `
  --energy-capacity-mwh 100 --initial-soc 0.50 `
  --minimum-soc 0.20 --charge-efficiency 0.80 `
  --discharge-efficiency 1.00
```

Expected summary:

```text
Intervals: 4
Limited intervals: 1
Ending SOC: 0.3600
Requested AC energy: 17.500 MWh
Delivered AC energy: 10.000 MWh
Curtailed AC energy: 7.500 MWh
Stored energy change: -14.000 MWh
```

Positive AC energy is net discharge to the grid; negative AC energy is net
charging. Curtailed energy is the absolute requested-versus-delivered gap, so
it remains nonnegative in either direction. `soc_balance_error` independently
reconstructs final SOC from cumulative stored-energy change.

This is a forward audit of a supplied power trajectory, not a scheduler or
optimizer. It does not choose prices, services, or interval requests, and it
does not compose frequency, ramp, or P-Q constraints across time. The standing
loss, auxiliary-load, nonlinear-efficiency, degradation, thermal, and capacity
limitations of the single-interval model still apply.
