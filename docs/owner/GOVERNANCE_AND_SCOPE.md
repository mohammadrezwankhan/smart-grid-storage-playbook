# Governance and scope

[Handbook](../INDEX.md) · [Decision index](ADR/ADR-0000-INDEX.md) · [Security](../../SECURITY.md)

## Recorded identity and purpose

Repository owner: **mohammadrezwankhan**. Existing citation/license metadata identifies **Mohammad Rezwan Khan**, ORCID **0000-0002-1532-0598**, and MIT. This package preserves that attribution and license. It does not invent co-authors, a DOI, a release version, a company authority or a support promise. [CITATION.cff](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/CITATION.cff#L1-L16) [LICENSE](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/LICENSE#L1-L21)

This repository combines storage/grid-service review prompts, explanatory native reference calculations and a separate browser teaching lab. The practical purpose is to make service claims, assumptions, control priorities and evidence gaps reviewable. The native equations do not operate a controller or establish field compliance; checklist status is not a substitute for project evidence. [README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/README.md#L267-L284) [checklists/grid-service-evidence-checklist.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/checklists/grid-service-evidence-checklist.md#L1-L18) [models/README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/README.md#L738-L751)

## Scope and change authority

| Change | Review evidence to request | Suggested responsible role |
|---|---|---|
| Documentation, navigation, source links | Complete diff, local validation and independent source/content review | Documentation maintainer |
| Equations, bounds, defaults, state carry or control order | Intended behavior, dimensional/limit analysis, comparative fixtures and independent engineering review | Numerical/controls maintainer plus domain reviewer |
| Fixture or project data | Origin, rights, operating conditions, signs/units, uncertainty and sanitization | Data steward plus engineering owner |
| CI/publication or dependency pins | Preserved check/event coverage, least privilege, exact runtime evidence and deployment provenance | Repository/integration owner |
| Field qualification or certification claim | Applicable requirement, project-specific evidence and authorized acceptance | External project/operator authority |

These are proposed responsibilities, not an existing staff roster. A named deputy, review quorum, support window and confidential reporting channel have not been established by the inspected source. The repository owner must assign them if needed.

The present documentation change preserves algorithms, models, tests, CSV fixtures, workflow behavior, CFF and license. Roadmap items are proposals requiring their own scoped decisions. Follow the source CI integrity instructions and effective platform rules; the observed all-branch signed-commit rule is not waived by documentation scope. [AGENTS.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/AGENTS.md#L1-L3)

## Data, IP and disclosure

Keep source, synthetic fixtures, explanatory derivations and real project evidence distinct. Existing CSVs are illustrative; they are not manufacturer guarantees. A contributed envelope should identify the permission to share it, equipment/configuration, valid conditions, axis/sign conventions, interpolation assumptions and source revision.

Do not publish customer plant identifiers, access tokens, private connection agreements, proprietary curves or raw operational logs as examples. Use synthetic or approved public data and retain separate access controls for project records. The existing ignore rules exclude local environment files but do not prove that arbitrary new files are safe to publish. [.gitignore](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.gitignore#L1-L14)

Review evidence must identify source/tested/candidate/merged/deployed revisions separately. No successful test report grants authority to energize equipment, accept a site or approve a grid code.

## Decision and issue handling

At the dated 2026-11-19 read-only snapshot, open issue and PR queries returned empty collections. This does not imply an absence of technical debt or future reports. Use [failure modes](../maintainer/FAILURE_MODES_AND_TECH_DEBT.md) and the source-backed roadmap to distinguish maintenance, interpretation risk, engineering improvements and exploratory research.

For a numerical report, request a minimal synthetic input, exact source SHA, units, initial conditions, full stage output and expected derivation. For a confidential issue, establish a private channel through current repository security settings before sharing sensitive material; do not invent an email or response deadline.
