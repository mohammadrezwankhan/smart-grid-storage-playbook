# Setup and reproducibility

[Handbook](../INDEX.md) · [Worked labs](WORKED_EXAMPLES_AND_LABS.md)

## Runtime evidence

| Capability | Declared or observed state |
|---|---|
| Native model dependencies | Python standard library; no pip package manifest is required by these modules |
| Reference CI interpreter | Python 3.12 |
| Observed local interpreter | CPython 3.12.14 |
| Observed native checks | 153 tests, eight CI reference commands, four-path guide validator |
| Browser arithmetic | Eight selected lesson checkpoints checked in isolated Node execution |
| Browser interaction/field equipment | Not established by these command results |
| Broad Python/OS support promise | Not inferred from one interpreter or CI declaration |

The existing reference path and workflow specify Python 3.12. [README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/README.md#L57-L71) [.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L37-L44)

## Checkout and isolate

```bash
git clone https://github.com/mohammadrezwankhan/smart-grid-storage-playbook.git
cd smart-grid-storage-playbook
git checkout --detach 8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e
python3.12 -m venv ../smart-grid-env
../smart-grid-env/bin/python -m unittest discover -s tests -v
```

Use the equivalent virtual-environment interpreter path on Windows. The checkout/environment-creation recipe is procedural guidance; recorded verification commands used the isolated interpreter described in the ledger. No dependency installation is needed for the native tests or guide validator. Keep the repository root as the working directory so relative CSV paths resolve.

## First native result

```bash
python models/pq_capability.py --active-mw 80 --reactive-mvar 80 --curve-csv models/data/illustrative_capability_curve.csv --priority active
python models/energy_sequence.py --active-mw-profile 50,50,50,-40 --duration-minutes-profile 15,15,15,30 --energy-capacity-mwh 100 --initial-soc 0.5 --minimum-soc 0.2 --charge-efficiency 0.8 --discharge-efficiency 1
python scripts/portfolio/validate_guide.py
```

Use your selected environment's Python executable. The first command delivers 80 MW and 50 MVAr; the second ends at SOC 0.36 and reports 0.23 throughput-equivalent cycles. These are observed illustrative reference results, not equipment ratings. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L368-L432) [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L50-L183)

## CLI discovery and inputs

Each of the eleven model scripts implements `--help` through argparse. The [interface catalogue](API_CLI_AND_INTERFACES.md) maps option names and source defaults. Profile arguments are comma-separated finite numbers with no empty entries. For a profile beginning with a minus sign, attach the value with `=`, for example `--active-mw-profile=-40,20`, to make its argument boundary explicit.

CSV schemas are exact, ordered and UTF-8-with-optional-BOM compatible:

| File kind | Header |
|---|---|
| Symmetric P–Q | `active_mw,reactive_limit_mvar` |
| Directional P–Q | `quadrant,active_mw,reactive_limit_mvar` |
| Temperature power limits | `temperature_c,max_discharge_mw,max_charge_mw` |

Missing/extra values, invalid numbers and unsupported curve shapes raise errors. Replace illustrative data only under an explicit engineering/provenance review. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L510-L605) [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L185-L222)

## Browser entrypoints

Open `docs/index.html` for the synthetic grid screen, `docs/portfolio/index.html` for the source-linked study guide, and `docs/native-lessons.html` for the preserved catalog. The main teaching page contains its arithmetic engine and configuration; opening it does not execute Python or contact a plant. External source/navigation links still require network access.

Keep native MW/MWh and browser kW/kWh conversions explicit: 100 kW = 0.1 MW, and a constant 100 kW request over 30 minutes is 0.05 MWh at the AC boundary. Storage losses and feasibility require the native model and stated assumptions.

## Reproduction record

Retain source SHA, exact command, Python/runtime versions, CSV hashes and provenance, all defaults overridden or retained, initial/carried state, output, exit status and scope limitations. Preserve raw useful output; human-readable CLI text is not a versioned JSON schema. Do not place confidential site/vendor material in public fixtures.
