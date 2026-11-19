# Verification evidence ledger

[Handbook](../INDEX.md) · [Reproduction](../developer/SETUP_AND_REPRODUCIBILITY.md) · [CI and delivery](CI_CD_AND_RELEASE_PLAYBOOK.md)

## Revision and evidence boundary

This is a dated **2026-11-19** observation of source `8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e`. Local model checks used an isolated **CPython 3.12.14** environment with no third-party runtime packages installed. The immutable source snapshot, original logs and later candidate fingerprints are retained in the external review records. A successful source check does not certify a later commit.

The documentation candidate has no commit identity at authorship. Final candidate checks, independent QA, PR checks, merged SHA and deployed revision must be recorded externally against their actual identities. Do not insert the not-yet-created commit's own hash into this page.

## Observed local baseline

| Check | Exact scope | Observed result | Limit |
|---|---|---|---|
| `python -m unittest discover -s tests -v` | 11 native test modules | **153 tests passed** | Deterministic software assertions; no field measurements or code-coverage percentage |
| Eight reference commands from the model workflow | Standing losses, throughput, reserve headroom/sequence, symmetric/directional P–Q, temperature, grid sequence | All exited 0; outputs retained | Illustrative configured cases |
| `python scripts/portfolio/validate_guide.py` | Four learning paths, local paths/SVG, embedded data and source links | Passed | Static guide integrity, not native-model or rendered-browser execution |
| Isolated JavaScript arithmetic review | Embedded engine, all eight grid checkpoints, 24 grid balance samples, input/default/comparison contracts | Passed | Node VM without browser DOM, network or external services |
| Generic engine endpoint review | Finite metrics at the default start/end of all ten branches | Passed | Small contract check, not all possible inputs or domain validation |

The reference command definitions are [.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L42-L113). The guide validator is [scripts/portfolio/validate_guide.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/scripts/portfolio/validate_guide.py#L1-L33). Browser checkpoints and arithmetic are [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L138-L305) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L249-L353). The local results above are observed review executions, not claims inferred merely from those files.

## Native claim-to-test map

The test count is a count of executed `unittest` methods, not assertions, parameter combinations, line coverage or engineering cases. The source suite comprises:

| Module | Methods | Principal contracts |
|---|---:|---|
| [tests/test_energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_energy_limits.py#L17-L286) | 13 | Feasible/outward SOC bounds, exact standing losses, rejection and CLI |
| [tests/test_energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_energy_sequence.py#L13-L295) | 11 | Carry/roundoff, variable durations, losses, throughput, conversion/SOC residuals |
| [tests/test_frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_frequency_watt.py#L28-L668) | 32 | Deadbands, filter/ramp/temperature ordering, energy/P–Q composition, paired inputs and CLI |
| [tests/test_grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_grid_support_sequence.py#L26-L594) | 17 | All quadrants, carried SOC/P/filter state, aggregates, profiles and CLI |
| [tests/test_measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_measurement_filter.py#L16-L125) | 7 | Exact exponential, tiny interval, composition, bounds and CLI |
| [tests/test_pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_pq_capability.py#L70-L448) | 28 | Three priorities, curve shapes, quadrants/shared axes, CSV schemas and legacy CLI |
| [tests/test_ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_ramp_limits.py#L17-L147) | 8 | Asymmetric signed ramps, zero crossing, tiny overshoot, bounds and CLI |
| [tests/test_reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_reserve_headroom.py#L15-L289) | 11 | Loss-covering charging endpoint, sustainable reserve, P–Q obligation and CLI |
| [tests/test_reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_reserve_sequence.py#L13-L305) | 12 | Baseline carry, response duration, losses, fixed/profile Q and rejection |
| [tests/test_temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_temperature_derating.py#L27-L123) | 6 | Interpolation, outside-range clamping, effective directional limits and strict CSV |
| [tests/test_volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_volt_var.py#L13-L79) | 8 | Breakpoints, deadband, Q request, priorities and sign preservation |


Selected acceptance details matter more than the total:

- The first-order filter tests compare exponential behavior at 14–15 decimal places, and a tiny response at 35 places, while explicitly requiring a positive change. [tests/test_measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_measurement_filter.py#L16-L57)
- Energy-sequence sweeps require bounded SOC and absolute SOC residual below `1e-12`. Grid-sequence sweeps check carried SOC and capability with their declared local tolerances. [tests/test_energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_energy_sequence.py#L204-L229) [tests/test_grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_grid_support_sequence.py#L381-L416)
- Temperature is deliberately allowed to override a slow earlier ramp-down request. A passing ramp-stage check is not a guarantee of final delivered slew. [tests/test_frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_frequency_watt.py#L143-L166)
- Delivered SOC is recomputed after P–Q curtailment; standing losses remain in that account. [tests/test_frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_frequency_watt.py#L309-L354)
- Reserve tests include a negative highest sustainable charging endpoint and strict rejection of unsustainable baselines. [tests/test_reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_reserve_headroom.py#L15-L49) [tests/test_reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_reserve_headroom.py#L166-L207)

Many other assertions use `assertAlmostEqual` without an explicit places argument. Do not interpret that convenience assertion, a printed three-decimal output or a flag tolerance as a universal engineering accuracy specification. The numerical guards and units are described in [Parameters and symbols](../math-and-physics/PARAMETERS_AND_SYMBOLS.md).

## Browser acceptance and selected defaults

All four modules check at 19 hours with absolute tolerance 0.02 in the selected metric's units. Module 2 expects 450 kW import and 180 kg/h emissions; those are analytical fixtures. The direct engine's missing-parameter battery default is 100 kW, while the selected lesson's displayed default is 0 kW. Both contexts were checked. This distinction is not silently normalized. [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L53-L136) [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L181-L219) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L199-L205)

The local arithmetic review also checked strict versus inclusive comparisons, unknown metrics/model kinds, finite input clamping, nonnumeric defaults, no step quantization and time bounds. It did not click controls, inspect accessibility, run every generic branch over its full domain or verify a hosted deployment. No network endpoint or plant was contacted.

## Source remote baseline and policy

At the 2026-11-19 observation, the exact source SHA had three completed GitHub checks: `deploy`, `validate` and `human-authorship-policy`, all successful. Their run URLs and full provider records are retained externally. The repeated job name `validate` is insufficient by itself to identify which workflow ran; do not attribute the local 153-test result to remote CI without its specific run.

The active [repository ruleset](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/rules/20091521) required signed commits on all branches, with no bypass actors and no current-user bypass. Reading classic branch protection returned an integration-permission error. That is an unresolved visibility gap, not evidence that there are no additional rules. Refresh effective policy and actual PR checks at delivery time.

## Evidence still required at delivery

1. Freeze the complete candidate file manifest; repeat local commands and documentation validation against that fingerprint.
2. Obtain independent source/content/scientific QA and repair/recheck findings without dropping prior receipts.
3. Bind the signed candidate commit to that exact tree; observe all applicable current CI and review requirements.
4. Guard merge against the audited head and record the actual merge SHA.
5. Observe the existing deployment and its source identity, then inspect the live handbook navigation and target content.

No candidate CI, merged revision or live publication success is asserted by this dated source ledger. Hardware, certification, field calibration, billing savings and guaranteed support remain outside the evidence collected here.
