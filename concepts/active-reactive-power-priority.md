# Active Reactive Power Priority

Use this page for explaining how active and reactive power commands should be
prioritized during constrained operation. It keeps smart-grid storage discussions
tied to service intent, control behavior, evidence, and operating limits.

<!-- markdownlint-disable MD013 -->

| Review Area | Prompt | Evidence To Request |
| --- | --- | --- |
| Service intent | Which grid service, operating mode, or reliability outcome is being claimed? | State the service and use-case boundary. |
| Control behavior | What setpoint, priority, threshold, or mode change drives the behavior? | Request settings, control notes, or event records. |
| Limits | Which SOC, power, reactive capability, warranty, or grid-code limit applies? | Link limits and responsible owner. |
| Test evidence | What proves the behavior was tested rather than only configured? | Capture test case, pass criteria, and result. |
| Operations | What should operators monitor or escalate? | List alarms, dashboards, and handover notes. |

<!-- markdownlint-enable MD013 -->

## Review Prompts

- Does the claim require grid-forming behavior, grid-following behavior, or either
  mode?
- Which service takes priority during constrained operation?
- What evidence would satisfy the system operator or interconnection reviewer?
- Which assumption should be revisited after the first operating event?

## Executable Reference

The [active/reactive capability model](../models/README.md) provides a small,
testable example of active-priority, reactive-priority, and proportional
curtailment under a circular MVA limit. It is an educational allocator, not a
replacement for the project's manufacturer capability curve or control model.
