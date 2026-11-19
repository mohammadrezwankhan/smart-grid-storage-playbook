# Portfolio integration

[Handbook](../INDEX.md) · [Governance](GOVERNANCE_AND_SCOPE.md) · [Roadmap](../../ROADMAP.md)

## Evidenced relationships

| Relationship | Evidence | What it means |
|---|---|---|
| Native modules → local modules/CSV | [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L1-L53) [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L510-L605) | Local numerical composition and file input; no cross-repository service dependency identified |
| Main browser lab → embedded synthetic engine/config | [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L165-L177) [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L306-L314) | Standalone educational arithmetic with source-provenance labels |
| Learning map → this repository's pinned source | [docs/portfolio/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/lesson-config.json#L15-L44) | Read-only source links at its historical reviewed revision |
| Brand manifest → public profile repository | [docs/visuals/brand-uniformity/manifest.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/visuals/brand-uniformity/manifest.json#L1-L18) | Decorative identity provenance from `mohammadrezwankhan/mohammadrezwankhan`; explicitly no numerical/validation claim |
| Repository → GitHub Pages | [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L61-L82) | Existing publication pipeline, subject to actual environment and deployment state |
| Code metadata → public profile/site links | [codemeta.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/codemeta.json#L15-L23) | Discovery and citation links; not an implemented model/data integration |

No cross-repository numerical import, remote solver or project-data feed is identified in the pinned native source. Similar teaching-engine code elsewhere is not by itself an operational dependency. This handbook does not claim that separate tools exchange runtime data.

## Portfolio-ready evidence

A public portfolio summary can accurately state the repository purpose, native interfaces, unit system, source-bound test observations, teaching limits, maintained entrypoints and actual merge/publication results when those are observed. Keep each evidence class separate:

- **Implementation:** exact source paths and equations.
- **Local verification:** interpreter, inputs, test count, logs and tested identity.
- **Delivery:** actual candidate/merge SHA and provider checks.
- **Publication:** actual deployed revision and observed live target.
- **Engineering validation:** external project data and qualified review, if separately obtained.

The declared unit boundary is especially important in an atlas: native active power is signed MW with MWh/fractional SOC; the selected browser grid uses kW and fixed nonnegative battery contribution. Other generic browser branches have their own units and symbols. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L15-L27) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L199-L205) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L284-L288)

## Proposed future interoperability

Before integrating with another repository, define the exchanged quantities and schemas, unit conversions, sign conventions, initial/boundary conditions, source versions, error semantics and data rights. Use synthetic fixtures and an independently verified acceptance case. SG-R01 and SG-R05 propose local contracts that could support that discussion; no integration implementation is promised.

Shared documentation checks may be maintained as a common process, but every repository still needs its own exact-source, exact-candidate and publication evidence. Historical branding and learning-map pins must remain distinguishable from current model validation.
