# Documentation handbook

[Repository overview](../README.md) · [Existing native model guide](../models/README.md) · [Interactive teaching lab](index.html) · [Source-linked learning guide](portfolio/)

This handbook describes source `8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e`. The Python models implement explicit storage constraints; the browser begins with an unconstrained synthetic active-power screen. Read each layer's assumptions before interpreting its outputs.

## Choose a path

| Reader | Start here | Continue with |
|---|---|---|
| Developer | [Setup and reproducibility](developer/SETUP_AND_REPRODUCIBILITY.md) | [Architecture](developer/ARCHITECTURE.md), [API/CLI catalogue](developer/API_CLI_AND_INTERFACES.md), [worked labs](developer/WORKED_EXAMPLES_AND_LABS.md), [troubleshooting](developer/TROUBLESHOOTING.md) |
| Engineering or scientific reviewer | [Equations and derivations](math-and-physics/EQUATIONS_AND_DERIVATIONS.md) | [Parameters and symbols](math-and-physics/PARAMETERS_AND_SYMBOLS.md), [assumptions and limits](math-and-physics/ASSUMPTIONS_AND_LIMITS.md), [existing detailed model reference](../models/README.md) |
| Maintainer | [Verification ledger](maintainer/VERIFICATION_EVIDENCE_LEDGER.md) | [CI and release playbook](maintainer/CI_CD_AND_RELEASE_PLAYBOOK.md), [toolchain matrix](maintainer/TOOLCHAIN_AND_DEPENDENCY_MATRIX.md), [failure modes](maintainer/FAILURE_MODES_AND_TECH_DEBT.md), [docs runbook](maintainer/DOCS_MAINTENANCE_RUNBOOK.md) |
| Owner or deputy | [Governance and scope](owner/GOVERNANCE_AND_SCOPE.md) | [Decision index](owner/ADR/ADR-0000-INDEX.md), [recovery runbook](owner/BUS_FACTOR_RECOVERY_RUNBOOK.md), [portfolio relationships](owner/PORTFOLIO_INTEGRATION.md) |

## Canonical material retained

The [native model guide](../models/README.md) remains the detailed command/example reference. Existing [concept notes](../concepts/storage-dispatch-basics.md), [review checklists](../checklists/weak-grid-storage-review-checklist.md), [glossary](../glossary/storage-glossary.md) and [control-flow explanation](../diagrams/bess-control-flow.md) provide engineering discussion and evidence prompts. They do not operate equipment or establish compliance.

The [native catalog](native-lessons.html), [portfolio guide](portfolio/) and [animation archive](animations/) have their own recorded historical source identities. Their preserved provenance is distinct from this handbook's source and any future deployment.

## Project records

[Contributing](../CONTRIBUTING.md) · [Changelog](../CHANGELOG.md) · [Citation metadata](../CITATION.cff) · [Security and sensitive data](../SECURITY.md) · [Roadmap](../ROADMAP.md) · [MIT license](../LICENSE)

The 2026-11-19 native baseline passed 153 tests. The [ledger](maintainer/VERIFICATION_EVIDENCE_LEDGER.md) states exact local scope and separates historical/source checks, candidate checks, merge and publication.
