# Grid Support Service Comparison

Battery storage can support the grid through several services. Use this comparison to align the service name, control question, and evidence request before making performance claims.

| Service | Typical Goal | Key Dispatch / Control Question | Evidence To Request |
|---|---|---|---|
| Frequency response | Arrest or correct frequency deviations | How fast must active power change after a frequency event? | Droop settings, response-time test, event logs |
| Voltage support | Hold voltage within a target range | What reactive-power range is available at the interconnection point? | Capability curve, voltage-control mode notes, grid-code reference |
| Ramp smoothing | Reduce renewable output variability | Which ramp-rate limit triggers charge or discharge? | Dispatch rule, renewable profile, SOC limits |
| Backup / resilience | Serve critical load during outages | Which loads are prioritized and for how long? | Load list, islanding sequence, minimum SOC rule |
| Peak shaving | Reduce demand peaks or network congestion | Which forecast or threshold starts discharge? | Baseline load data, dispatch threshold, settlement logic |

## Review Prompts

- Does the service require grid-forming behavior, grid-following behavior, or either mode?
- Which service has priority when two controls request different power setpoints?
- What evidence proves the service was tested rather than only configured?
- Which operating limits, SOC windows, or warranty constraints restrict the service?
