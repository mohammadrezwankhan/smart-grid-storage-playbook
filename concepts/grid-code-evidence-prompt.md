# Grid-Code Evidence Prompt

Use this prompt to structure early BESS grid-code review discussions. It is jurisdiction-neutral and should be adapted to the applicable connection agreement, utility requirement, or grid-code document.

## Evidence Prompt

| Topic | Review Prompt | Evidence Owner | Example Evidence |
|---|---|---|---|
| Voltage operating range | What voltage range must the BESS tolerate, support, or disconnect from? | Grid studies / protection lead | Connection agreement, voltage ride-through curve, protection settings. |
| Frequency operating range | What frequency deviations require continued operation, response, or trip? | Controls lead | Frequency ride-through requirement, EMS/BESS controller settings, test report. |
| Reactive power capability | What reactive power or power-factor envelope is required at the point of interconnection? | Electrical design lead | Capability curve, inverter datasheet, commissioning test record. |
| Ride-through behavior | What voltage or frequency events must the system ride through without disconnecting? | Protection and controls leads | Ride-through settings, simulation case, secondary injection or functional test evidence. |
| Ramp-rate limits | What real-power ramp limits apply during normal dispatch or recovery? | EMS / operations lead | Dispatch logic, ramp-rate setting, event log, operator procedure. |
| Active power control | Who can curtail, limit, or command active power? | Operations lead | Control narrative, SCADA point list, command hierarchy. |
| Evidence ownership | Who owns each final evidence artifact before handover? | Project controls | Evidence matrix, document index, acceptance tracker. |

## Discussion Questions

- Does the grid-code requirement apply at inverter terminals, plant controller output, transformer high side, or the point of interconnection?
- Are reactive power obligations still valid while the battery is at high or low SOC?
- What happens if a market dispatch command conflicts with voltage support or ride-through requirements?
- Are grid-code tests repeated after firmware, protection, or transformer changes?
- Which evidence artifacts will be accepted by the grid owner, EPC, owner, and operator?

## Closeout Notes

- Keep each requirement tied to a responsible owner and a specific evidence artifact.
- Do not mix design intent, simulation output, and commissioning evidence in the same status field.
- Record assumptions for unavailable grid-code clauses instead of leaving review cells blank.
- Use the commissioning evidence matrix to map this prompt into final handover records.
