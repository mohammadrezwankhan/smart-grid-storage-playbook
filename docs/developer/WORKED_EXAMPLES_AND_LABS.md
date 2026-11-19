# Worked examples and labs

[Handbook](../INDEX.md) · [Setup](SETUP_AND_REPRODUCIBILITY.md) · [Detailed native guide](../../models/README.md)

Run from the repository root using the selected Python environment. These examples use committed illustrative inputs and print to stdout. The 2026-11-19 baseline observed the following commands in the existing CI reference set; final candidate records retain exact command/output evidence.

## 1. Distinguish circular and sampled capability

```bash
python models/pq_capability.py --active-mw 80 --reactive-mvar 80 --curve-csv models/data/illustrative_capability_curve.csv --priority active
python models/pq_capability.py --active-mw -65 --reactive-mvar -70 --directional-curve-csv models/data/illustrative_directional_capability.csv --priority active
```

The symmetric example delivers **80 MW, 50 MVAr**. The charge/absorption example delivers **-65 MW, -40 MVAr**. A reported negative reactive curtailment is the signed requested-minus-delivered difference, not a negative magnitude error. Sampled utilization is measured relative to the boundary along the output ray, not an assumed constant 100 MVA circle. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L278-L309) [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L368-L449)

## 2. Carry SOC and separate throughput from net energy

```bash
python models/energy_sequence.py --active-mw-profile 50,50,50,-40 --duration-minutes-profile 15,15,15,30 --energy-capacity-mwh 100 --initial-soc 0.5 --minimum-soc 0.2 --charge-efficiency 0.8 --discharge-efficiency 1
```

Delivered powers are **50, 50, 20, -40 MW**. Ending SOC is **0.36**; net delivered AC energy is **10 MWh**, AC throughput **50 MWh**, stored-energy throughput **46 MWh**, conversion loss **4 MWh**, and throughput-equivalent cycles **0.23**. Net energy and throughput answer different questions; the cycle counter is not a degradation or warranty model. [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L74-L183)

## 3. Make standing losses explicit

```bash
python models/energy_limits.py --active-mw 0 --duration-minutes 120 --energy-capacity-mwh 100 --initial-soc 0.8 --auxiliary-load-mw 2 --self-discharge-rate-per-hour 0.01
```

The CLI prints ending SOC **0.7446**, auxiliary energy **4.000 MWh**, self-discharge **1.544 MWh**, and stored change **-5.544 MWh**. Display rounding is not an uncertainty estimate. The model assumes the storage medium supplies the auxiliaries; a separate feeder needs separate accounting. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L103-L180) [models/README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/README.md#L392-L457)

## 4. Preserve Q while auditing reserve

```bash
python models/reserve_headroom.py --baseline-active-mw 10 --duration-minutes 30 --maximum-discharge-mw 100 --maximum-charge-mw 100 --energy-capacity-mwh 100 --initial-soc 0.5 --minimum-soc 0.2 --maximum-soc 0.8 --charge-efficiency 1 --discharge-efficiency 1 --reactive-mvar 80 --limit-mva 100
```

Holding 80 MVAr on a 100 MVA circle leaves endpoints ±60 MW. Relative to a 10 MW baseline, upward reserve is **50 MW** and downward reserve **70 MW**. This is sustained replacement-setpoint headroom for the stated response duration, not evidence of repeated reserve activation. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L103-L214)

## 5. Inspect an external temperature envelope

```bash
python models/temperature_derating.py --active-mw -90 --temperature-c 40 --max-discharge-mw 80 --max-charge-mw 100 --curve-csv models/data/illustrative_temperature_derating.csv
```

At 40 °C the illustrative curve gives 85 MW discharge and 65 MW charge limits. Nameplate reduces discharge to 80 MW; delivered charging is **-65 MW**. The temperature is supplied, not predicted. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L79-L182)

## 6. Trace all four P-Q quadrants in a sequence

```bash
python models/grid_support_sequence.py --frequency-hz-profile 49.5,49.5,50.5,50.5 --voltage-pu-profile 0.95,1.05,0.95,1.05 --duration-minutes-profile 1,1,1,1 --directional-curve-csv models/data/illustrative_directional_capability.csv --energy-capacity-mwh 1000 --initial-soc 0.5 --charge-efficiency 1 --discharge-efficiency 1 --priority reactive
```

The four rounded delivered P/Q pairs are **(81.818, 50)**, **(80, -45)**, **(-65, 50)** and **(-60.833, -45)** in MW/MVAr. The result reports 0.600 MWh net active delivery and 3.167 MVArh absolute reactive service; ending SOC prints 0.4994. State advances from delivered active power, after capability allocation. [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L221-L335)

## 7. Connect browser screening to a native question

Load Module 2 in the teaching lab: 500 kW demand baseline, 600 kW solar peak, 100 kW fixed battery contribution, and 400 g/kWh carbon factor. At model time 19 h the declared checks expect **450 kW import** and **180 kg/h** grid emissions, with absolute tolerance 0.02. The eight selected checkpoints were evaluated arithmetically; this is not a recorded browser-interaction test. [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L181-L219)

A 100 kW contribution requested for 30 minutes corresponds to 0.1 MW and 0.05 MWh AC. A native study must separately specify capacity, initial SOC, allowed SOC interval, efficiencies, standing losses, P–Q boundary, response duration and any ramp/temperature limits. Exporting browser CSV does not supply those missing assumptions.

## Reproduce the existing test suite

```bash
python -m unittest discover -s tests -v
python scripts/portfolio/validate_guide.py
```

Retain observed results and exact revisions in the [verification ledger](../maintainer/VERIFICATION_EVIDENCE_LEDGER.md). An invalid-input test passing means the rejection was expected; it does not authorize the rejected engineering condition.
