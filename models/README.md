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
- Dynamic current limits, voltage dependence, temperature derating, SOC, and
  duration limits are excluded.
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
