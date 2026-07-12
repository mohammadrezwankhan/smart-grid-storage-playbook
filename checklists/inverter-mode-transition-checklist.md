# Inverter Mode Transition Checklist

Use this checklist to review transitions between grid-following, grid-forming, standby, and fault states.

| Transition | Command Owner | Trigger | Allowed Transition | Evidence | Status |
|---|---|---|---|---|---|
| Standby to grid-following | EMS / operator | Grid available and PCS enabled | Standby -> grid-following | Control narrative, SCADA command record | Not started |
| Grid-following to grid-forming | EMS / site controller | Weak-grid, islanding, or resilience mode request | Grid-following -> grid-forming only under approved conditions | Mode logic, simulation, functional test | Not started |
| Grid-forming to grid-following | Site controller / operator | Resynchronization with stable grid | Grid-forming -> synchronized grid-following | Sync record, protection review | Not started |
| Any mode to fault | PCS / protection | Protection trip, internal fault, or unsafe condition | Immediate stop or controlled ramp-down as designed | Trip matrix, event log | Not started |
| Fault to standby | Protection / operator | Fault cleared and reset approved | Fault -> standby only after reset criteria | Reset procedure, alarm log | Not started |

## Review Prompts

- Which system owns the command for each transition?
- Is the transition automatic, operator-confirmed, or blocked by protection logic?
- What evidence proves the transition under project grid conditions?
- Are mode changes visible in SCADA or event logs?
- Does the operator know which transitions are allowed during maintenance, outage, or emergency conditions?
