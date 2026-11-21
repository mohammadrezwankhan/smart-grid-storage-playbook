# Storage Dispatch Priority Matrix

Use this page for ordering control objectives when storage services compete for the same power or energy headroom. It keeps smart-grid storage discussions tied to service intent, control behavior, evidence, and operating limits.

| Review Area | Prompt | Evidence To Request |
|---|---|---|
| Service intent | Which grid service, operating mode, or reliability outcome is being claimed? | State the service and use-case boundary. |
| Control behavior | What setpoint, priority, threshold, or mode change drives the behavior? | Request settings, control notes, or event records. |
| Limits | Which SOC, power, reactive capability, warranty, or grid-code limit applies? | Link limits and responsible owner. |
| Test evidence | What proves the behavior was tested rather than only configured? | Capture test case, pass criteria, and result. |
| Operations | What should operators monitor or escalate? | List alarms, dashboards, and handover notes. |

## Review Prompts

- Does the claim require grid-forming behavior, grid-following behavior, or either mode?
- Which service takes priority during constrained operation?
- What evidence would satisfy the system operator or interconnection reviewer?
- Which assumption should be revisited after the first operating event?

## Joint activation feasibility

Record one row per permitted activation scenario against the same baseline.
Identify when activations can overlap and use the longest required hold time
or the actual sequence of activation and recovery intervals.

| Scenario | Requested setpoints | Evidence to retain |
|---|---|---|
| Baseline | Scheduled active and reactive power at the point of common coupling (PCC), starting state of charge (SOC) | Schedule, measurement boundary, charging/discharging efficiencies, auxiliary loads and applicable capability limits |
| Concurrent upward | Baseline plus all upward activations permitted to overlap, with reactive commitments | Delivered MW and MVAr, ramp feasibility, minimum SOC during the hold, binding limit and curtailed service |
| Concurrent downward | Baseline minus all overlapping downward activations, with reactive commitments | Delivered MW and MVAr, ramp feasibility, maximum SOC during the hold, binding limit and curtailed service |
| Mixed or repeated | Time-ordered upward/downward activations, simultaneous reactive requirements and recovery setpoints | SOC at every transition, feasible recovery time and remaining headroom before the next activation |

Record which services are mutually exclusive and cite the rule that enforces
that exclusion. Compare each joint setpoint against the shared inverter limit
and carry SOC forward from interval to interval. Separate single-product
headroom results do not establish that capacity can be committed more than once.
Use the [reserve model guide](../models/README.md) for model inputs and scope.
