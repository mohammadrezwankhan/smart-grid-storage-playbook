# BESS Control Flow

```mermaid
flowchart LR
    Grid["Grid / Point of Interconnection"]
    EMS["Energy Management System"]
    PCS["Power Conversion System"]
    BMS["Battery Management System"]
    Battery["Battery Racks"]
    SCADA["SCADA / Operator Interface"]

    SCADA --> EMS
    EMS --> PCS
    EMS --> BMS
    BMS --> Battery
    PCS <--> Grid
    PCS <--> Battery
    BMS --> EMS
    PCS --> EMS
```

## Review Notes

- Define which system owns active/reactive power commands.
- Define which system owns battery protection limits.
- Define how alarms and trips propagate.
- Confirm whether remote commands are advisory, supervisory, or directly controlling.
