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
