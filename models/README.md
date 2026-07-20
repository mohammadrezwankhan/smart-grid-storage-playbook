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

The model is static. It excludes frequency measurement filtering, control-loop
dynamics, ramp-rate limits, recovery logic, and interactions with plant-level
dispatch. Optional energy arguments enforce SOC reserve, response duration, and
charge/discharge efficiency before P-Q allocation. Replace every frequency,
power, energy, efficiency, baseline, and priority assumption with
project-controlled values before engineering use.

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
derating, uncertain capacity, multi-interval scheduling, or SOC recovery.
