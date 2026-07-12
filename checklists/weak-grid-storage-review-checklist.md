# Weak-Grid Storage Review Checklist

Use this checklist when a BESS dispatch plan must operate in a weak-grid, constrained-grid, islanded, or low-short-circuit-strength context.

## Project Context

| Review Item | Question | Evidence To Request | Status |
|---|---|---|---|
| Grid condition | What operating cases define "weak" for this site? | Grid study, short-circuit estimate, connection agreement, operating envelope. | Not started |
| Operating mode | Is the BESS grid-following, grid-forming, or switching between modes? | Controls description, mode-transition logic, protection notes. | Not started |
| Dispatch objective | Is dispatch driven by energy shifting, voltage support, frequency support, backup, or constraint relief? | EMS logic, control narrative, market or operator requirement. | Not started |

## Dispatch Constraints

| Constraint | Review Question | Why It Matters |
|---|---|---|
| Voltage support | Does dispatch reserve reactive-power capability for voltage control? | Real-power export can reduce remaining converter capability for voltage support. |
| Ramp limits | Are charge/discharge ramps coordinated with grid strength and feeder constraints? | Aggressive ramps can stress voltage, frequency, or protection settings. |
| Reserve margin | Is energy or power held back for contingency response? | Full economic dispatch may leave too little margin for grid events. |
| SOC window | Are minimum and maximum SOC limits stated for normal and contingency operation? | Weak-grid operation can need a different reserve policy than market-only dispatch. |
| Outage operation | Who authorizes islanding, black-start support, or backup discharge? | Operational authority must be clear before an event occurs. |
| Derating | How are thermal, auxiliary, or equipment derates communicated to the dispatch controller? | Dispatch targets should follow available capability, not nameplate assumptions. |
| Protection interaction | Are protection settings reviewed against grid-forming or high-ramp operation? | Control behavior and protection assumptions can conflict if reviewed separately. |

## Operator Review Prompts

- What is the fallback dispatch mode if communications with EMS or SCADA are lost?
- Are voltage, frequency, SOC, and converter-limit alarms visible to the operator?
- Does the operator know which limits are warranty-based, grid-code-based, or project-specific?
- Are dispatch logs retained with enough detail to reconstruct a grid event?
- Is there a clear handoff between normal operation, contingency operation, and recovery?

## Closeout Evidence

- Approved operating envelope.
- Controls narrative with dispatch modes and mode transitions.
- SOC reserve policy for normal and contingency operation.
- Protection and grid-study references.
- Commissioning records for voltage, frequency, ramp-rate, and command-following behavior.
