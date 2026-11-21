# Harmonic Performance Evidence

![Section 04 · Verification / output](../docs/visuals/sections/section-04-verification.svg)

Use this page for framing the evidence needed for harmonic performance and power quality review. It keeps smart-grid storage discussions tied to service intent, control behavior, evidence, and operating limits.

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

## Measurement and evaluation record

Record the following for each measurement campaign or study operating point.

| Field | Evidence to retain |
|---|---|
| Measurement point | Point of common coupling (PCC), one-line diagram reference, nominal voltage, transformer/filter arrangement and network configuration |
| Operating point | Active and reactive power, charge/discharge direction, state of charge, inverter count, control mode and switching/filter configuration |
| Background | Pre-connection or plant-off spectra, upstream distortion and short-circuit level or impedance assumptions |
| Acquisition | Instrument model, calibration status, transducer ratios and bandwidth, sampling and aggregation settings, timestamps and operating duration |
| Individual orders | Per-phase voltage and current spectra with units and normalization, harmonic orders and any recorded interharmonics |
| Summary quantities | Voltage/current total harmonic distortion (THD) with the fundamental denominator and current total demand distortion (TDD) with the documented demand-current reference |
| Assessment | Applicable rule revision and clause, PCC-specific limits, aggregation method, exceptions, source data, reviewer and disposition |

Keep the raw evidence and calculation inputs with the record. A model trace or
illustrative spectrum can support planning a measurement campaign. A
compliance determination requires the applicable limits and qualifying
measurement or study evidence for the actual PCC and operating conditions.
