# Assumptions and limits

[Handbook](../INDEX.md) · [Equations](EQUATIONS_AND_DERIVATIONS.md) · [Verification](../maintainer/VERIFICATION_EVIDENCE_LEDGER.md)

## What the native reference establishes

The models apply explicit static envelopes and exact held-input interval formulas. Deterministic tests exercise those contracts, invalid inputs and operating sweeps. The 2026-11-19 baseline passed 153 methods. This establishes the observed software checks; it does not replace equipment characterization, site studies, protection review or grid-code evidence.

| Area | Implemented assumption | Not established |
|---|---|---|
| P–Q | Circular or concave sampled envelope with strictly increasing P/decreasing Q; equal adjacent slopes allowed; directional shared axes | Voltage/current transients, automatic vendor-curve derivation |
| Frequency / voltage | Held measured input, deadbands and piecewise requests | Network response, feedback stability, fault ride-through or actual grid-forming control |
| Filter | Exact first-order held-input step | Sampling jitter, sensor bias or higher-order dynamics |
| Ramp | Signed reachable setpoint before downstream constraints | Final delivered slew after hard temperature/energy/P–Q curtailment |
| Temperature | External sampled charge/discharge limits, endpoint clamp | Internal cell/coolant/ambient prediction, hysteresis, dwell or fault handling |
| Energy | Fixed capacity/efficiencies/standing-loss coefficient per interval | Nonlinear efficiencies, degradation, uncertain capacity or thermal coupling |
| Reserve | Sustained replacement around feasible baseline at sampled interval starts | Repeated activation, recovery, worst-case within-interval guarantee or market qualification |
| Throughput | AC/stored flow accounting and equivalent-cycle ratio | Cycle aging, rainflow damage, remaining life or warranty |

[models/README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/README.md#L123-L137) [models/README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/README.md#L303-L357) [models/README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/README.md#L449-L457) [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L123-L159) [models/README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/README.md#L730-L751)

## Constraint precedence is part of the contract

Frequency-watt retains the intermediate power, ramp, temperature, energy and capability records. A later hard envelope or reactive-priority decision can move final P beyond the earlier ramp target. SOC is then recomputed from final P. Calling this composition “all constraints satisfied simultaneously” would conceal its ordering semantics. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L242-L320)

Initial SOC and optional previous P/filter state are supplied explicitly. Profiles must have matching lengths; each measurement is held for its interval. Sequence duration is not a numerical integration timestep that can be reduced to establish electromagnetic convergence. Reserve response duration is not automatically the baseline schedule interval.

## Browser limitations

The selected grid screen uses a synthetic daily demand/solar shape, fixed nonnegative battery contribution and constant carbon intensity. It has no storage inventory, P–Q or network state. A lower grid import is not evidence of sustainable reserve. The other nine engine branches are generic teaching proxies with their own local units and assumptions. [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L53-L136) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L177-L337)

All eight configured checkpoint expectations are analytical fixtures at 19 h. Their tolerance is a teaching comparison rule, not a field acceptance margin. A Node arithmetic check does not establish rendered-browser accessibility, interaction correctness or published-page provenance.

## Data and calibration boundary

The three committed CSVs and browser presets are illustrative. No specific PCS, battery, site, operator rule or measured validation dataset is established by them. Preserve public references and original license/author information, but obtain explicit rights and source provenance for any new manufacturer/site data. An absent calibration dataset is a limitation, not a reason to invent one.

## Evidence required for broader use

An engineering study would need project-controlled signs/units, equipment envelopes and operating conditions, initial-state provenance, measurement semantics, applicable standards, validated uncertainties, operating/protection constraints and independent review. Those are future external evidence requirements. This documentation task does not select a grid code, approve settings, operate a plant or certify a design.
