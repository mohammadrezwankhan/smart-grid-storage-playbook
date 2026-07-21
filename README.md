# Smart Grid Storage Playbook

[![Model and Markdown validation](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/actions/workflows/markdown-maintenance.yml/badge.svg)](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/actions/workflows/markdown-maintenance.yml)

Explainable smart-grid and grid-forming BESS concepts for engineers, students,
and project teams.

## What This Covers

- Grid-following vs grid-forming storage.
- Storage dispatch concepts.
- Resilience and reliability framing.
- Renewable integration scenarios.
- Technical diagrams and plain-English explainers.

## Starter Pages

- [Executable active/reactive capability reference](models/README.md)
- [Executable Volt-VAR dispatch reference](models/README.md#volt-var-dispatch-reference)
- [Executable frequency-watt dispatch reference](models/README.md#frequency-watt-dispatch-reference)
- [Executable active-power ramp limits](models/README.md#active-power-ramp-limits)
- [Executable SOC and response-duration limits](models/README.md#soc-and-response-duration-limits)

- [Grid-forming vs grid-following storage](concepts/grid-forming-vs-grid-following.md)
- [Grid-code evidence prompt](concepts/grid-code-evidence-prompt.md)
- [Storage dispatch basics](concepts/storage-dispatch-basics.md)
- [Weak-grid storage review checklist](checklists/weak-grid-storage-review-checklist.md)
- [Inverter mode transition checklist](checklists/inverter-mode-transition-checklist.md)
- [Storage glossary](glossary/storage-glossary.md)
- [BESS control flow](diagrams/bess-control-flow.md)
- [Grid support service comparison](concepts/grid-support-service-comparison.md)
- [Grid service evidence checklist](checklists/grid-service-evidence-checklist.md)

- [Storage Dispatch Priority Matrix](concepts/storage-dispatch-priority-matrix.md)

- [Interconnection Review Questions](concepts/interconnection-review-questions.md)

- [Grid Forming Test Scenario Log](concepts/grid-forming-test-scenario-log.md)

- [Resilience Use Case Template](concepts/resilience-use-case-template.md)

- [Renewable Smoothing Case Note](concepts/renewable-smoothing-case-note.md)

- [Active Reactive Power Priority](concepts/active-reactive-power-priority.md)

- [Protection Coordination Review](checklists/protection-coordination-review.md)

- [Black Start Readiness Prompts](concepts/black-start-readiness-prompts.md)

- [Microgrid Mode Transition Log](concepts/microgrid-mode-transition-log.md)

- [Grid Code Traceability Matrix](concepts/grid-code-traceability-matrix.md)

- [Operator Control Room Handover](concepts/operator-control-room-handover.md)

- [Event Log Review Guide](concepts/event-log-review-guide.md)

- [Congestion Relief Dispatch Note](concepts/congestion-relief-dispatch-note.md)

- [Market Service Assumption Register](concepts/market-service-assumption-register.md)

- [Islanding Risk Review Checklist](checklists/islanding-risk-review-checklist.md)

- [Harmonic Performance Evidence](concepts/harmonic-performance-evidence.md)

- [Availability Performance Template](concepts/availability-performance-template.md)

- [Service Stacking Conflict Log](concepts/service-stacking-conflict-log.md)

- [System Operator Query Log](concepts/system-operator-query-log.md)

- [Playbook Next Research Questions](concepts/playbook-next-research-questions.md)

## Repository Topics

```text
smart-grid grid-forming energy-storage renewable-integration
power-systems bess technical-writing
```

## Planned Sections

```text
concepts/
checklists/
diagrams/
case-notes/
glossary/
README.md
CONTRIBUTING.md
LICENSE
```

## Run The Executable Reference

The dependency-free allocator demonstrates active-priority, reactive-priority,
and proportional handling of commands outside a circular MVA limit:

```powershell
python models/pq_capability.py `
  --active-mw 80 --reactive-mvar 80 --limit-mva 100 --priority active
python models/volt_var.py `
  --voltage-pu 0.95 --active-mw 90 --limit-mva 100
python models/frequency_watt.py `
  --frequency-hz 49.725 --baseline-active-mw 20 `
  --reactive-mvar 80 --limit-mva 100
python models/ramp_limits.py `
  --active-mw 80 --previous-active-mw 20 --interval-seconds 30 `
  --ramp-up-mw-per-minute 40 --ramp-down-mw-per-minute 60
python models/energy_limits.py `
  --active-mw 100 --duration-minutes 60 `
  --energy-capacity-mwh 50 --initial-soc 0.50 `
  --minimum-soc 0.20 --discharge-efficiency 0.90
python -m unittest discover -s tests -v
```

Review the [model assumptions and limitations](models/README.md) before mapping
the result to a plant controller, PCS capability curve, or grid-code study.

## Contribution Entry Points

- Add a storage dispatch concept page.
- Improve weak-grid review prompts with project examples.
- Add project-specific examples to the grid-code evidence prompt.
- Improve the BESS control-flow diagram notes.
- Add project-specific inverter mode transition examples.
- Add project-specific grid support service examples.
- Add project-specific examples to the grid service evidence checklist.
- Add project-specific examples to the storage dispatch priority matrix.
- Add project-specific examples to the interconnection review questions.
- Add project-specific examples to the grid forming test scenario log.
- Add project-specific examples to the resilience use case template.
- Add project-specific examples to the renewable smoothing case note.
- Add project-specific examples to the active reactive power priority.
- Add project-specific examples to the protection coordination review.
- Add project-specific examples to the black start readiness prompts.
- Add project-specific examples to the microgrid mode transition log.
- Add project-specific examples to the grid code traceability matrix.
- Add project-specific examples to the operator control room handover.
- Add project-specific examples to the event log review guide.
- Add project-specific examples to the congestion relief dispatch note.
- Add project-specific examples to the market service assumption register.
- Add project-specific examples to the islanding risk review checklist.
- Add project-specific examples to the harmonic performance evidence.
- Add project-specific examples to the availability performance template.
- Add project-specific examples to the service stacking conflict log.
- Add project-specific examples to the system operator query log.
- Add project-specific examples to the playbook next research questions.
