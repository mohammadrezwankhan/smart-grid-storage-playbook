# Troubleshooting

[Handbook](../INDEX.md) · [Setup](SETUP_AND_REPRODUCIBILITY.md)

| Symptom | Evidence-based explanation | Action |
|---|---|---|
| CSV not found | Relative paths resolve from the current directory | Run from repository root; verify the exact intended fixture |
| Wrong/incomplete CSV header | Loaders require exact column order and complete numeric records | Compare against the three committed illustrative schemas |
| Curve rejected as nonconcave | P–Q sampled boundaries require increasing P, decreasing Q and nonincreasing segment slopes | Check source data/provenance; do not silently reshape equipment data |
| Directional envelope rejects shared axis | Adjacent quadrant intercepts disagree beyond the implemented tolerance | Reconcile the physical meaning and source data before retrying |
| Partial energy/filter/ramp/temperature configuration | Optional features require complete input groups | Use the appropriate script's `--help` and interface catalogue |
| Idle or small charging request raises minimum-SOC error | Standing losses can exceed available inventory | Inspect supplied auxiliary/rate/duration/state assumptions; zero requested AC power does not mean zero stored loss |
| Delivered P differs from ramp-stage P | Later temperature, energy or Q-priority capability limits can reduce the setpoint | Inspect each returned stage and post-capability delivered energy |
| Reserve baseline rejected | The specified baseline or reactive obligation cannot be sustained/delivered | Recheck baseline, response duration, inventory, Q and chosen boundary |
| Different SOC than a hand calculation | MW×minutes needs /60; charge/discharge efficiencies use opposite stored-energy relations | Use signed P and separate AC/stored/standing-loss accounts |
| “Cycles” seems too small or too large | Counter is stored throughput divided by twice capacity | Do not equate it with counted rainflow cycles or degradation |
| Browser and Python disagree | They are different models and units; browser battery power has no SOC bound | Define a native scenario and explicit conversions |
| Browser call differs from initial screen | Generic grid engine uses batteryKW=100; lesson configuration initializes 0 | Supply the intended complete parameters or lesson preset |
| Notes disappear in portfolio guide | Browser storage may be unavailable or cleared | Export a study plan; do not treat local storage as backup |
| Candidate CI is pending | Historical/source results do not apply automatically | Observe the actual run/context/revision and current policy; do not bypass gates |

CSV and boundary contracts: [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L45-L260) [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L510-L605). Energy loss errors: [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L111-L180). Constraint order and feature groups: [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L186-L320). Reserve validation: [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L87-L159). Throughput definition: [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L100-L145). Browser/storage behavior: [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L199-L204) [docs/portfolio/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/index.html#L270-L296).

## Useful reproduction evidence

Report the exact source SHA, interpreter, command, input CSV hash and permission/provenance, expected versus observed values, relevant units/signs and full exception text after removing sensitive project details. Reduce to a small deterministic example while retaining the failing boundary. Existing tests are the first comparison point, not proof that every external dataset is valid.

No documentation workaround changes executable validation. A required engineering assumption that cannot be established remains unresolved.
