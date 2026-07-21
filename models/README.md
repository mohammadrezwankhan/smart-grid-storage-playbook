# Active/Reactive Capability Reference

This dependency-free Python example makes constrained active/reactive power
priority explicit. It applies either a circular inverter capability limit or a
sampled piecewise envelope and reports the delivered command, curtailed
command, apparent power, and utilization.

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

The symmetric CSV envelope samples the positive-quadrant boundary as strictly
increasing active power and strictly decreasing reactive limit. The loader
requires reactive-axis and active-axis endpoints plus a concave piecewise-linear
shape. Allocation mirrors that boundary into all four quadrants. A directional
CSV may instead provide separate discharge/injection, discharge/absorption,
charge/injection, and charge/absorption curves.

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

Run the committed noncircular example with the same priority policies:

```powershell
python models/pq_capability.py `
  --active-mw 80 `
  --reactive-mvar 80 `
  --curve-csv models/data/illustrative_capability_curve.csv `
  --priority active
```

The sampled boundary limits the 80 MW request to 50 MVAr:

```text
Capability model: piecewise curve (4 points)
Active power: 80.000 MW
Reactive power: 50.000 MVAr
Capability utilization: 100.00%
```

## Directional Four-Quadrant Envelope

Use `--directional-curve-csv` when charge and discharge capability or reactive
injection and absorption capability differ. The strict CSV groups four curves
by these exact quadrant identifiers:

- `discharge_injection`
- `discharge_absorption`
- `charge_injection`
- `charge_absorption`

Each group uses nonnegative magnitudes and follows the same increasing-active,
decreasing-reactive, concave shape contract as the symmetric curve. Curves on
either side of an axis must share that axis intercept: both discharge curves
must have the same active limit, both charge curves must have the same active
limit, and the corresponding charge/discharge curves must agree on injection
or absorption limits at zero active power. This makes commands on an axis
independent of an arbitrary quadrant choice.

Run the committed charge-and-absorption example:

```powershell
python models/pq_capability.py `
  --active-mw -65 `
  --reactive-mvar -70 `
  --directional-curve-csv `
    models/data/illustrative_directional_capability.csv `
  --priority active
```

Expected key values:

```text
Capability model: directional envelope (4 quadrants, 16 points)
Capability quadrant: charge_absorption
Active power: -65.000 MW
Reactive power: -40.000 MVAr
Capability utilization: 100.00%
```

The example deliberately limits charging to 80 MW, discharge to 100 MW,
reactive injection to 100 MVAr, and absorption to 90 MVAr, with different
interior boundaries in every quadrant. These are illustrative values, not a
claim about a particular PCS. The Python API exposes
`DirectionalCapabilityEnvelope`, `load_directional_capability_csv`, and
`allocate_power_on_directional_envelope` for the same operation.

Run the regression checks with:

```powershell
python -m unittest discover -s tests -v
```

## Explicit Limitations

- Every sampled quadrant curve is concave and linearly interpolated. The
  symmetric input mirrors one curve; the directional input requires four
  curves and consistent shared-axis intercepts.
- Dynamic current limits and voltage dependence are not calculated internally.
  Temperature-dependent active-power limits can be composed through
  `temperature_derating.py`, but only after an external study supplies the
  applicable sampled envelope. SOC and interval-duration limits can be
  composed through `energy_limits.py`; neither layer is inherent to the P-Q
  allocator.
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

| Region                 | Default Behavior                        |
| ---------------------- | --------------------------------------- |
| `V <= 0.92 pu`         | Saturate at `+1.0 pu` reactive request. |
| `0.92 < V < 0.98 pu`   | Ramp linearly from injection to zero.   |
| `0.98 <= V <= 1.02 pu` | Hold a zero-reactive-power deadband.    |
| `1.02 < V < 1.08 pu`   | Ramp linearly from zero to absorption.  |
| `V >= 1.08 pu`         | Saturate at `-1.0 pu` reactive request. |

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
and circular or sampled P-Q capability enforcement. Positive active power means
discharge and injection into the grid; negative active power means charging.
Below the lower deadband boundary, the controller increases injection. Above
the upper deadband boundary, it reduces injection and can request charging.

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

Replace `--limit-mva` with `--curve-csv` or
`--directional-curve-csv` to apply a sampled boundary after the same frequency,
storage-power, ramp, and energy stages. For example, reactive-priority charging
and absorption selects the directional charge/absorption quadrant:

```powershell
python models/frequency_watt.py `
  --frequency-hz 50.5 --reactive-mvar -70 `
  --directional-curve-csv `
    models/data/illustrative_directional_capability.csv `
  --priority reactive
```

The model is static. It excludes sensor errors, higher-order measurement
dynamics, control-loop dynamics, recovery logic, and interactions with
plant-level dispatch. Optional filter arguments apply a first-order frequency
measurement filter before deadband and droop evaluation. Optional ramp
arguments enforce asymmetric signed active-power slew limits. An optional
externally supplied temperature curve then applies a hard active-power envelope
before SOC and P-Q allocation. Optional energy arguments enforce SOC reserve,
response duration, and charge/discharge efficiency. Replace every frequency,
filter, power, ramp, temperature, energy, efficiency, baseline, and priority
assumption with project-controlled values before engineering use.

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
optional hard temperature envelope, interval energy bound, and the selected
circular or sampled P-Q allocation. The returned `ramp`,
`temperature_derating`, `energy`, and `capability` records preserve each stage
for review. The ramp interval is the time available to move from the previous
command; it is distinct from the energy response duration. A newly reduced
temperature limit takes precedence over the ramp stage so a carried setpoint
cannot remain outside the current operating envelope.

## External Temperature Power Derating

[`temperature_derating.py`](temperature_derating.py) consumes an externally
supplied table of temperature, maximum discharge power, and maximum charge
power. Temperatures must be strictly increasing; every power limit must be
finite and nonnegative. The model linearly interpolates between samples and
clamps outside temperatures to the nearest endpoint instead of extrapolating.
It reports the bracketing temperatures, interpolation fraction, endpoint-clamp
status, sampled limits, nameplate-constrained effective limits, and delivered
active power.

Run the committed illustrative 40 C charging case:

```powershell
python models/temperature_derating.py `
  --active-mw -90 --temperature-c 40 `
  --max-discharge-mw 80 --max-charge-mw 100 `
  --curve-csv models/data/illustrative_temperature_derating.csv
```

Expected key values:

```text
Sampled discharge limit: 85.000 MW
Sampled charge limit: 65.000 MW
Effective discharge limit: 80.000 MW
Effective charge limit: 65.000 MW
Delivered active power: -65.000 MW
Temperature limited: true
```

The committed values deliberately show different cold and hot charge/discharge
limits. They are test data, not ratings for a battery, inverter, or thermal
management system. The temperature input is also external: this model does not
estimate cell, module, coolant, enclosure, or ambient temperature. Project use
must define the measured temperature, sensor policy, hysteresis, dwell time,
fault handling, and the study or vendor data behind every sample.

Add `--temperature-c` and `--temperature-derating-csv` to
`frequency_watt.py`, or a comma-separated `--temperature-c-profile` plus the
same CSV to `grid_support_sequence.py`. Both inputs are required as a pair.
The effective limit is the smaller of the sampled limit and the configured
frequency-watt nameplate limit in each direction.

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

## Auxiliary Demand And Self-Discharge

Optional `--auxiliary-load-mw` and `--self-discharge-rate-per-hour` inputs add
standing losses to the same energy boundary calculation. The stored-energy
state follows this constant-coefficient interval equation:

```text
dE/dt = P_stored - P_auxiliary - lambda E
```

`P_stored` is negative AC discharge divided by discharge efficiency, or
positive AC charge multiplied by charge efficiency. `lambda` is a continuous
decay coefficient per hour, not a percentage value. For nonzero `lambda`, the
model applies the exact zero-order-hold update:

```text
E_next = E_initial exp(-lambda dt)
         + (P_stored - P_auxiliary) (1 - exp(-lambda dt)) / lambda
```

The zero-rate branch uses the exact linear limit, avoiding division by zero.
`expm1` preserves accuracy for small rates and short intervals. Discharge and
charge headroom are solved from the same update, so standing losses reduce
available discharge and create additional charge room. The model rejects an
interval when auxiliary and self-discharge losses would cross minimum SOC and
the requested dispatch cannot supply enough charging energy to prevent it.

Run an idle two-hour example with a 2 MW auxiliary demand and a continuous
`0.01/h` self-discharge rate:

```powershell
python models/energy_limits.py `
  --active-mw 0 --duration-minutes 120 `
  --energy-capacity-mwh 100 --initial-soc 0.80 `
  --auxiliary-load-mw 2 --self-discharge-rate-per-hour 0.01
```

Expected loss and state values:

```text
Ending SOC: 0.7446
Auxiliary energy: 4.000 MWh
Self-discharge energy: 1.544 MWh
Stored energy change: -5.544 MWh
```

Every interval reports dispatch stored-energy change, auxiliary energy,
self-discharge energy, and total stored-energy change. Their independent audit
identity is:

```text
stored change = dispatch stored change - auxiliary energy - self-discharge
```

The terminology follows Sandia's distinction between
[standby energy loss and self-discharge](https://www.osti.gov/servlets/purl/1368468).
An NREL field study also shows why auxiliary demand must be treated as a stated
project assumption: measured pump consumption changed with active power and
SOC in its [utility-scale flow-battery demonstration](https://www.osti.gov/biblio/1464729).

This reference deliberately uses one constant auxiliary load and one constant
self-discharge rate. It assumes the storage medium supplies the auxiliary
demand. Set auxiliary load to zero when a separate feeder supplies it, and
account for that feeder outside this SOC model. Operating-state-dependent
auxiliaries, nonlinear conversion efficiency, degradation, thermal derating,
and uncertain capacity remain excluded.

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
AC energy throughput: 50.000 MWh
Stored energy throughput: 46.000 MWh
Conversion loss: 4.000 MWh
Throughput-equivalent full cycles: 0.230000
Stored energy change: -14.000 MWh
```

Positive AC energy is net discharge to the grid; negative AC energy is net
charging. Curtailed energy is the absolute requested-versus-delivered gap, so
it remains nonnegative in either direction. `soc_balance_error` independently
reconstructs final SOC from cumulative stored-energy change.

The sequence also separates positive discharge and charge magnitudes on the AC
and stored-energy sides. AC throughput is their AC-side sum. Stored-energy
throughput is the sum of battery-side dispatch discharge and charge after the
configured conversion efficiencies. Conversion loss closes the independent
identity:

```text
net delivered AC energy + dispatch stored-energy change + conversion loss = 0
```

`throughput_equivalent_full_cycles` divides stored-energy throughput by twice
the nominal energy capacity. One full discharge plus one full recharge is
therefore one throughput-equivalent cycle. Auxiliary demand and self-discharge
remain separately reported standing losses and do not increase this dispatch
throughput metric.

This is a forward audit of a supplied power trajectory, not a scheduler or
optimizer. It does not choose prices, services, or interval requests, and it
does not compose frequency, ramp, or P-Q constraints across time. The constant
loss assumptions and nonlinear-efficiency, degradation, thermal, and capacity
limitations of the single-interval model still apply. The equivalent-cycle
value is an accounting normalization, not a rainflow cycle count, degradation
estimate, warranty interpretation, or remaining-life prediction.

## Sustained Reserve Headroom

[`reserve_headroom.py`](reserve_headroom.py) converts nameplate charge and
discharge limits into sustained upward and downward active-power reserve around
a feasible baseline. It evaluates the configured response duration through the
same SOC and standing-loss limiter, so a result distinguishes a power-limited
reserve from one constrained by stored-energy headroom. An optional circular,
symmetric sampled, or directional P-Q boundary also preserves a fixed reactive
power obligation and distinguishes capability-limited reserve.

Run a 30-minute assessment around a 10 MW discharge baseline:

```powershell
python models/reserve_headroom.py `
  --baseline-active-mw 10 --duration-minutes 30 `
  --maximum-discharge-mw 100 --maximum-charge-mw 100 `
  --energy-capacity-mwh 100 --initial-soc 0.50 `
  --minimum-soc 0.20 --maximum-soc 0.80 `
  --charge-efficiency 1 --discharge-efficiency 1
```

Expected directional headroom:

```text
Upward active-power limit: 60.000 MW
Downward active-power limit: -60.000 MW
Upward reserve: 50.000 MW
Downward reserve: 70.000 MW
Upward energy limited: true
Downward energy limited: true
```

Positive power is discharge and negative power is charge. Upward reserve is
the sustained discharge limit minus the baseline. Downward reserve is the
baseline minus the sustained charge limit, so a discharging baseline can have
more downward headroom than the charge limit magnitude alone.

For example, holding 80 MVAr on a 100 MVA circular boundary leaves 60 MW in
either active-power direction. With ample stored energy, the same 10 MW
baseline therefore has 50 MW upward and 70 MW downward reserve:

```powershell
python models/reserve_headroom.py `
  --baseline-active-mw 10 --duration-minutes 30 `
  --maximum-discharge-mw 100 --maximum-charge-mw 100 `
  --energy-capacity-mwh 1000 --initial-soc 0.50 `
  --reactive-mvar 80 --limit-mva 100
```

```text
Reactive power obligation: 80.000 MVAr
Upward active-power limit: 60.000 MW
Downward active-power limit: -60.000 MW
Upward capability limited: true
Downward capability limited: true
```

Use `--curve-csv` for the symmetric sampled boundary or
`--directional-curve-csv` for the four-quadrant envelope. Reactive power is held
with reactive priority; the audit rejects a reactive obligation or baseline
that the selected boundary cannot deliver. Capability is applied before the
energy limiter, so curtailment by each stage remains independently visible.

The baseline must itself remain feasible for the full response duration. This
reference evaluates replacement setpoints from the initial state; it does not
model activation delay, ramping, time-varying reactive dispatch, thermal
derating, reserve recovery, simultaneous services, or probabilistic
availability. Compose those constraints separately before making a market or
grid-code claim.

## Reserve Sequence Audit

[`reserve_sequence.py`](reserve_sequence.py) applies the sustained reserve
calculation before every interval in a baseline schedule, then advances SOC
through the interval with the same exact standing-loss and conversion model.
This makes reserve erosion or recovery from earlier dispatch visible instead
of treating every commitment as if it started from the original SOC.

Run three 30-minute discharge intervals with a 30-minute reserve requirement:

```powershell
python models/reserve_sequence.py `
  --baseline-active-mw-profile 20,20,20 `
  --interval-duration-minutes-profile 30,30,30 `
  --response-duration-minutes 30 `
  --maximum-discharge-mw 100 --maximum-charge-mw 100 `
  --energy-capacity-mwh 100 --initial-soc 0.80 `
  --minimum-soc 0.20 --maximum-soc 0.90 `
  --charge-efficiency 1 --discharge-efficiency 1
```

Expected schedule minima:

```text
Ending SOC: 0.5000
Minimum upward reserve: 60.000 MW (interval 3)
Minimum downward reserve: 40.000 MW (interval 1)
Reserve energy-limited intervals: upward=1, downward=3
```

The baseline schedule is a firm input: an interval is rejected if its baseline
cannot be delivered for the full schedule duration. Reserve limits are assessed
from interval-start SOC and represent replacement setpoints held for the stated
response duration; they do not simulate activation energy in addition to the
baseline trajectory. Ramping, time-varying reactive dispatch, temperature
derating, recovery requirements, and overlapping reserve activations remain
separate constraints. The same `--reactive-mvar` and mutually exclusive P-Q
boundary arguments carry a fixed reactive obligation through every interval;
the summary reports how many upward and downward intervals are capability
limited independently of their energy-limit counts.

## Multi-Service Grid-Support Sequence

[`grid_support_sequence.py`](grid_support_sequence.py) composes the existing
frequency-watt, Volt-VAR, measurement-filter, active-power-ramp, SOC, and
optional temperature-derating and circular or sampled P-Q models over a
variable-duration profile. Each interval starts from the prior interval's
delivered ending SOC. When ramp limits or frequency filtering are enabled, it
also starts from the prior delivered active power or filtered frequency, so
curtailment at one control layer changes the next interval's reachable state.

Run three simultaneous frequency and voltage events with reactive-power
priority:

```powershell
python models/grid_support_sequence.py `
  --frequency-hz-profile 50,49.5,50.5 `
  --voltage-pu-profile 1,0.92,1.08 `
  --baseline-active-mw-profile 20,20,20 `
  --duration-minutes-profile 15,15,15 `
  --limit-mva 100 --energy-capacity-mwh 100 `
  --initial-soc 0.50 --minimum-soc 0.20 `
  --charge-efficiency 1 --discharge-efficiency 1
```

Expected summary:

```text
Intervals: 3
Limited intervals: 2
Ending SOC: 0.4500
Requested active energy: 15.000 MWh
Delivered active energy: 5.000 MWh
Active shortfall energy: 50.000 MWh
Delivered reactive service: 50.000 MVArh
```

At low voltage and under-frequency, both active and reactive support request
the full 100-unit capability. The default reactive priority preserves the
100 MVAr voltage request and curtails active power to zero; delivered-energy
accounting therefore keeps SOC at 0.45 instead of applying the pre-capability
active request. `active`, `reactive`, and `proportional` priorities remain
available for explicit service-conflict studies.

Use `--curve-csv` or `--directional-curve-csv` instead of `--limit-mva` to
apply the same strict sampled boundaries as the standalone allocator. With a
directional envelope and no explicit `--reactive-base-mvar`, positive Volt-VAR
requests use the injection-axis limit and negative requests use the
absorption-axis limit. This keeps asymmetric MVAr capability visible rather
than scaling both directions from one circular rating.

Run a four-interval case that traverses discharge/injection,
discharge/absorption, charge/injection, and charge/absorption:

```powershell
python models/grid_support_sequence.py `
  --frequency-hz-profile 49.5,49.5,50.5,50.5 `
  --voltage-pu-profile 0.95,1.05,0.95,1.05 `
  --duration-minutes-profile 1,1,1,1 `
  --directional-curve-csv `
    models/data/illustrative_directional_capability.csv `
  --energy-capacity-mwh 1000 --initial-soc 0.50 `
  --charge-efficiency 1 --discharge-efficiency 1 `
  --priority reactive
```

Expected directional results:

```text
Intervals: 4
Limited intervals: 4
Ending SOC: 0.4994
Delivered active energy: 0.600 MWh
Requested reactive service: 3.167 MVArh
Delivered reactive service: 3.167 MVArh
SOC balance error: 0.000e+00
```

The four delivered P/Q pairs are `(81.818, 50.000)`, `(80.000, -45.000)`,
`(-65.000, 50.000)`, and `(-60.833, -45.000)` in MW/MVAr. Capability
allocation remains after storage power, ramp, temperature, and energy bounds.
Final SOC is recomputed from active power after capability curtailment, so the
sequence does not debit energy for a pre-envelope request that the PCS cannot
deliver.

Active-energy totals preserve sign, so charging offsets discharge. Reactive
service totals sum absolute MVArh because injection and absorption are both
delivered voltage-support work; each interval row retains the Q direction.

The profile is an auditable control composition, not a dynamic network or
electromagnetic-transient simulation. Each measurement is held constant for
its interval. When ramp limits are enabled, they constrain the active setpoint
before temperature, energy, and P-Q limits; a higher-priority reactive request
may then curtail delivered active power beyond that setpoint. Sampled P-Q and
temperature envelopes remain static external inputs. They do not derive SOC,
voltage, temperature, or grid-condition derating internally. Voltage feedback
from reactive injection, frequency dynamics, controller latency, temperature
estimation, degradation, operating-state-dependent auxiliary demand, and
uncertainty remain excluded.
