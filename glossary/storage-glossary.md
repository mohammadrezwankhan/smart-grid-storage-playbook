# Storage Glossary

| Term | Plain-English Meaning | Engineering Note |
|---|---|---|
| BESS | Battery energy storage system | Includes battery racks, PCS, BMS, EMS, auxiliaries, and integration scope. |
| BMS | Battery management system | Protects and monitors cells/modules/racks. |
| PCS | Power conversion system | Converts DC battery power to AC grid power and back. |
| EMS | Energy management system | Coordinates dispatch, limits, operating modes, and external commands. |
| FAT | Factory acceptance test | Confirms equipment behavior before shipment. |
| SAT | Site acceptance test | Confirms installed system behavior on site. |
| Grid-forming | Control behavior that can establish/support voltage and frequency reference | Requires careful evidence, not just a marketing label. |
| Grid-following | Control behavior that follows an existing grid reference | Common for grid-connected inverter systems. |
| SOC | State of charge | Estimated battery energy level, often expressed as a percentage. |
| SOH | State of health | Estimate of degradation or remaining useful condition. |
| Active power command | Instruction for how much real power the BESS should charge or discharge | Usually expressed in kW or MW with sign convention stated. |
| Reactive power command | Instruction for voltage-support power exchange with the grid | Usually expressed in kvar or Mvar; may be limited by inverter capability. |
| Ramp-rate limit | Maximum allowed rate of change for charge or discharge power | Helps avoid abrupt grid, equipment, or market-control impacts. |
| Reserve margin | Power or energy intentionally held back for reliability or contingency response | Prevents economic dispatch from consuming all operating flexibility. |
| Curtailment | Intentional reduction of active power output or charging demand | Can be required by grid constraints, market instructions, or equipment limits. |
| Ride-through | Ability to remain connected during defined voltage or frequency disturbances | Requires settings and test evidence, not just controller intent. |
| Droop control | Control method that changes power response based on voltage or frequency deviation | Often discussed for grid-support and grid-forming behavior. |
| Protection trip | Automatic disconnection or stop triggered by a protection function | Should be mapped to cause, owner, reset logic, and event record. |
| Point of interconnection | Electrical point where plant obligations are usually measured | Important for grid-code evidence and performance guarantees. |
| Dispatch schedule | Planned sequence of charge, discharge, idle, or reserve behavior | Should respect SOC, availability, grid limits, and operating priorities. |
