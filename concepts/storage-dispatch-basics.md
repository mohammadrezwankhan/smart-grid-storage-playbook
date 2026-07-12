# Storage Dispatch Basics

Storage dispatch is the decision process for when a battery energy storage system charges, discharges, holds reserve, or stays idle.

## Core Idea

A BESS is constrained by both power and energy:

- **Power** defines how fast the system can charge or discharge at a moment in time.
- **Energy** defines how long it can sustain that charge or discharge.
- **State of charge (SOC)** defines the usable energy position between operating limits.

## Dispatch Inputs

| Input | Why It Matters |
|---|---|
| Power setpoint | Defines immediate charge or discharge command. |
| SOC limits | Prevents operation outside approved battery operating window. |
| Availability | Accounts for maintenance, faults, derating, or auxiliary limits. |
| Market or grid signal | Defines the reason for dispatch, such as peak shaving or frequency support. |
| Temperature or thermal limit | Can reduce available charge/discharge power. |
| Grid constraint | May limit export, import, ramp rate, or reactive power behavior. |

## Example Dispatch Modes

| Mode | Typical Goal | Review Question |
|---|---|---|
| Peak shaving | Reduce site or grid peak demand | What measurement point defines the peak? |
| Energy shifting | Charge during low-price/low-demand periods and discharge later | What SOC reserve must remain after dispatch? |
| Frequency response | Respond quickly to grid frequency deviations | What response time and accuracy are required? |
| Renewable smoothing | Reduce variability from PV or wind output | What ramp-rate limit is being enforced? |
| Backup or resilience | Hold energy for contingency operation | Who owns the decision to release reserve energy? |

## Project Review Questions

- What system sends the dispatch command: EMS, SCADA, market platform, grid operator, or local controller?
- Are SOC limits contractual, warranty-based, grid-code-driven, or project-specific?
- What happens when dispatch conflicts with battery thermal limits?
- How are unavailable capacity and derating communicated to operators?
- Are dispatch records included in the evidence package for performance review?
