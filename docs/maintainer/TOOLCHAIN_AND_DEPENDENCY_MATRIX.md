# Toolchain and dependency matrix

[Handbook](../INDEX.md) · [Setup](../developer/SETUP_AND_REPRODUCIBILITY.md) · [CI](CI_CD_AND_RELEASE_PLAYBOOK.md)

## Native runtime and data

| Capability | Declared / inferred from source | Tested in this review | Boundary |
|---|---|---|---|
| Python | CI explicitly selects 3.12; type syntax requires a compatible modern interpreter | CPython 3.12.14, isolated standard-library environment | No claim of a full support matrix or older-version compatibility |
| Native models | Standard-library `argparse`, `csv`, `dataclasses`, `enum`, `math`, `pathlib`, typing and local modules | 153 tests and eight reference commands | No NumPy/SciPy/toolbox, solver service or package install needed by these paths |
| Tests | Standard-library `unittest`, temporary files and subprocess CLI tests | Existing suite executed | No coverage tool or field data used |
| Curve inputs | Three committed CSVs with strict ordered headers | Loader tests and reference commands | Illustrative samples, not equipment calibration |
| Native model guide | Existing `models/README.md` | Preserved and cross-linked | Retains canonical worked reference detail |

[.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L37-L43) [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L1-L8) [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L1-L9) [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L1-L53) [tests/test_pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_pq_capability.py#L1-L67)

There is no tracked Python dependency lock, package installer manifest, MATLAB code, Simulink model or toolbox requirement. “No third-party runtime dependency” describes the inspected native paths; it is not a promise about arbitrary future plugins or external engineering software.

## Browser and guide

| Surface | Runtime / persistence | Local review | Not established |
|---|---|---|---|
| Main lesson lab | Embedded JavaScript/CSS/config; Canvas, native browser controls and Blob downloads | Engine arithmetic in isolated Node VM; embedded config identity | Real browser support matrix, accessibility, visual layout and hosted behavior |
| Portfolio guide | Standalone HTML/JSON/SVG, local browser notes/progress and exported study plan | Static source-linked guide validator | Local storage as a durable backup; native model execution |
| Native lesson catalogue | Static metadata/links with its original source pins | Indexed and provenance reviewed | Execution of every historical command or historical source revision |
| Preserved animation assets | Historical SVG/HTML and manifest provenance | Hashed and structurally indexed | Revalidated historical science or a new animation build |

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L419-L488) [docs/portfolio/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/index.html#L270-L296) [docs/portfolio/README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/README.md#L5-L24) [docs/native-lessons.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/native-lessons.json#L1-L46)

Node is an operational arithmetic-review tool here; the native model CLI does not require it. CFF/JSON/Markdown validation packages used by reviewers are external review dependencies, not new application dependencies or a newly committed build system.

## CI action pins

| Action | Pinned revision in source | Use |
|---|---|---|
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L28-L28), [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L70-L70), [.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L33-L33), [.github/workflows/no-codex-attribution.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/no-codex-attribution.yml#L24-L24), [.github/workflows/portfolio-dashboard-check.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/portfolio-dashboard-check.yml#L18-L18) |
| `actions/configure-pages` | `45bfe0192ca1faeb007ade9deae92b16b8254a0d` | [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L75-L75) |
| `actions/upload-pages-artifact` | `fc324d3547104276b827a68afc52ff2a11cc49c9` | [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L77-L77) |
| `actions/deploy-pages` | `368f82528645a54fb793d4d04e342629a3f51346` | [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L82-L82) |
| `actions/setup-python` | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` | [.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L38-L38) |
| `lycheeverse/lychee-action` | `e7477775783ea5526144ba13e8db5eec57747ce8` | [.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L116-L116) |


Action comments can label a release, but the immutable hash is the effective source pin. Dependabot is configured for weekly GitHub Actions updates with at most five open update PRs. An update is a review input, not proof of compatibility or license/security approval. [.github/dependabot.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/dependabot.yml#L1-L7)

## License and data/IP register

The repository retains its MIT license and the existing CFF attribution to Mohammad Rezwan Khan with the recorded ORCID. This package does not change those statements or invent a release version/DOI. [LICENSE](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/LICENSE#L1-L21) [CITATION.cff](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/CITATION.cff#L1-L16)

The tracked illustrative CSVs have no separate per-fixture provenance manifest or equipment-license declaration. Treat their repository context and illustrative status explicitly; do not present them as manufacturer data. External equipment curves, event logs, site coordinates, settings or connection agreements require their own rights/access review before contribution. CI action dependencies retain their own upstream terms; their complete license transitive inventory was not audited here.

## Credentials, cost and reproducibility

No application secret names or external model service endpoints are required by the native calculations. Deployment uses the configured GitHub Pages/OIDC permissions; the source does not establish a separate deploy credential or external hosting secret. [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L61-L82)

Retain source identity, interpreter version, exact command, fixture hashes, output/error logs and test result when reproducing a claim. Record browser/Node versions separately if changing the static engine. Billing savings remain **unknown**: no current price model, billable usage or measured before/after cost was collected.
