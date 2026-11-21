# Market Service Assumption Register

![Section 02 · Equations / provenance](../docs/visuals/sections/section-02-equations.svg)

Use this page for separating market-service assumptions from technical grid-service evidence. It keeps smart-grid storage discussions tied to service intent, control behavior, evidence, and operating limits.

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

## Product and settlement record

Keep one record per market product and effective rule revision. Mark each
unconfirmed input as an assumption and identify who can verify it.

| Field | Evidence to retain |
|---|---|
| Product identity | Jurisdiction, market operator, product identifier, rule section, revision, effective date and source link |
| Eligibility and delivery | Qualification, metering boundary, response deadline, ramp, minimum hold, repetition and recovery requirements |
| Activation terms | Upward/downward direction, dispatch reference and baseline, allowed overlap or exclusion with other products |
| Settlement | Capacity and utilization payment bases, currency, price and quantity units, settlement interval, adjustment and non-delivery rules |
| Feasibility evidence | MW, MVAr and usable MWh reserved by interval, test scenario, delivered quantity and reason for any shortfall |
| Record ownership | Owner, verification date, unresolved assumptions and rule changes requiring reassessment |

Link the product record to the applicable
[joint activation scenario](storage-dispatch-priority-matrix.md) before adding
its capacity or utilization payment to a stacked-services estimate.
