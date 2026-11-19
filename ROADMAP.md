# Development roadmap

[Handbook](docs/INDEX.md) · [Findings](docs/maintainer/FAILURE_MODES_AND_TECH_DEBT.md) · [Owner scope](docs/owner/GOVERNANCE_AND_SCOPE.md)

**Planning window: 2026-11-19 through 2027-11-18**, twelve calendar months with the final day immediately before the anniversary. Dates, staffing and effort below are **proposals**, not delivery commitments. This documentation change implements none of the proposed numerical, control, API or pipeline changes.

| Horizon | Calendar interval | Focus |
|---|---|---|
| Now | 2026-11-19–2026-12-31, partial Q4 2026 | Unit/feasibility teaching contract and complete docs validation |
| Next | 2027-01-01–2027-03-31, Q1 2027 | Constraint precedence and data validity |
| Later | 2027-04-01–2027-09-30, Q2–Q3 2027 | Interchange, numerical evidence and bounded reserve research |
| Horizon | 2027-10-01–2027-11-18, partial Q4 2027 | Reproducible publication and owner recovery |

Priorities reflect the inspected source and documented evidence gaps. The dated read-only issue/PR queries returned no open items; no issue numbers or release promises are invented. Findings are interpretation risks, missing contracts or proposed maintenance unless a specific reproducible defect is established.

## Now

### SG-R01 — Make the native/browser comparison contract executable

**P1 · Documentation · 2026-11-19 to 2026-12-15**

**Evidence:** SG-F01. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L284-L288) [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L90-L214)

**Outcome:** Readers can translate one selected kW teaching scenario into an explicitly timed, signed-MW/MWh native example without assuming unlimited storage.

**Proposed change:** Add a source-reviewed comparison fixture/lesson specification that states 100 kW = 0.1 MW and names capacity, duration, SOC and efficiency before calculating feasibility.

**Suggested owner:** Documentation and numerical maintainer. **Effort:** 2–4 focused days. **Confidence:** high. **Dependencies:** none; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- One synthetic comparison records every unit, initial condition and limit; native feasibility and browser import results are independently reproduced.
- The example explicitly identifies omitted charging/energy/carbon assumptions and does not promise equal semantics.

**Verification:** Independent dimensional review plus exact-source native and browser arithmetic fixtures.

**Risks:** A visually similar result can conceal different time/energy assumptions.

**Unresolved assumptions:** Owner agrees which teaching question the comparison should answer.

### SG-R02 — Cover the complete handbook and selected browser contract in validation

**P1 · Maintenance · 2026-12-01 to 2026-12-31**

**Evidence:** SG-F02, SG-F08. [.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L115-L119) [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L22-L59) [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L53-L136) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L199-L205)

**Outcome:** A green documentation check has an explicit coverage statement for all handbook paths and the selected lesson defaults/checkpoints.

**Proposed change:** Propose reproducible CFF/local-link/lesson-schema/arithmetic checks and include current handbook paths while preserving workflow names, required checks, event coverage, permissions and publication guards.

**Suggested owner:** CI and documentation maintainer. **Effort:** 3–6 focused days. **Confidence:** high. **Dependencies:** SG-R01; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- All 24 entrypoints and local targets are validated; deliberately broken-link/config fixtures fail the relevant documentation check.
- All eight configured checkpoints and engine-versus-lesson default differences are checked; static, arithmetic and rendered UI results stay separate.
- Existing native 153-test baseline and reference commands remain intact at the unchanged source.

**Verification:** Reviewed pipeline diff, offline failure fixtures, exact-candidate CI and no application changes.

**Risks:** Broadening checks may expose historical warnings; triage them rather than suppressing a required gate.

**Unresolved assumptions:** Effective required checks and approved execution environment must be observed before the pipeline proposal.

## Next

### SG-R03 — Record approved constraint precedence and stage diagnostics

**P1 · Engineering Improvement · 2027-01-01 to 2027-02-15**

**Evidence:** SG-F03. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L242-L320) [tests/test_frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_frequency_watt.py#L143-L166)

**Outcome:** Maintainers and downstream users can explain when a hard bound overrides an earlier ramp target and which final state is authoritative.

**Proposed change:** Prepare a proposed ADR and stage-evidence matrix for temperature, energy and reactive-priority interactions; any behavioral alternative needs a separately approved engineering change.

**Suggested owner:** Controls/numerical maintainer and independent domain reviewer. **Effort:** 4–8 focused days. **Confidence:** medium. **Dependencies:** SG-R01; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- Accepted or explicitly deferred ADR names final-P, stage-P, SOC recomputation and residual semantics.
- Fixtures cover each priority and hard-bound interaction, including required charging for losses; contradictory claims are removed.

**Verification:** Independent controls review, comparative existing fixtures and intended-behavior sign-off.

**Risks:** A simultaneous-feasibility expectation may require a different controller design, not a documentation adjustment.

**Unresolved assumptions:** The repository remains an educational reference; no site priority contract is presumed.

### SG-R04 — Define sampled-envelope data provenance and validity contracts

**P1 · Engineering Improvement · 2027-02-01 to 2027-03-31**

**Evidence:** SG-F05. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L45-L93) [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L510-L605) [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L79-L124)

**Outcome:** Users know which curve shapes and operating ranges the loaders accept, and what endpoint clamping means.

**Proposed change:** Specify optional provenance/validity metadata for externally supplied curves, rights, conditions, units, strictly increasing P/decreasing Q, concavity (equal adjacent slopes allowed; a slope greater than the previous slope plus 1e-12 is rejected), shared axes and an explicit temperature out-of-range policy; start with synthetic examples.

**Suggested owner:** Data steward and numerical maintainer. **Effort:** 4–7 focused days. **Confidence:** high. **Dependencies:** SG-R03; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- Each illustrative fixture has a documented source/rights/units/validity disposition without fabricated manufacturer calibration.
- Synthetic valid/invalid examples demonstrate ordered headers, shape restrictions and exact/outside endpoint behavior.
- Any policy change is separately reviewed and preserves reproducible historical behavior until approved.

**Verification:** Schema/loader fixture review, source-bound outputs and data-rights review for any non-synthetic contribution.

**Risks:** Real vendor envelopes may violate the current restricted shape family.

**Unresolved assumptions:** No manufacturer data license or field dataset is assumed available.

## Later

### SG-R05 — Evaluate a stable result interchange contract

**P2 · Engineering Improvement · 2027-04-01 to 2027-05-31**

**Evidence:** SG-F07. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L626-L673) [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L55-L95)

**Outcome:** An integration can distinguish signed delivery, absolute service totals, units, errors and source provenance without scraping display text.

**Proposed change:** Gather a concrete consumer need, then propose a versioned schema/serialization design for existing result records; retain current CLI text compatibility unless separately authorized.

**Suggested owner:** API maintainer and prospective consumer. **Effort:** 5–10 focused days. **Confidence:** medium. **Dependencies:** SG-R03, SG-R04; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- A reviewed schema assigns units/signs and required provenance to all selected result fields and names unsupported/nonfinite cases.
- Round-trip synthetic fixtures and compatibility expectations are documented; no runtime cross-repository integration is claimed without implementation.

**Verification:** Consumer review, schema/round-trip fixtures and exact expected-output compatibility checks.

**Risks:** Freezing all internal fields prematurely may constrain useful future design.

**Unresolved assumptions:** A concrete consumer and stable subset must be selected before implementation.

### SG-R07 — Establish scale-aware numerical evidence and uncertainty boundaries

**P2 · Engineering Improvement · 2027-04-01 to 2027-06-30**

**Evidence:** SG-F06. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L151-L193) [tests/test_measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_measurement_filter.py#L16-L57) [tests/test_grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/tests/test_grid_support_sequence.py#L381-L416)

**Outcome:** Numerical guards, printed precision and physical/data uncertainty are explicitly separated across expected scales.

**Proposed change:** Propose dimensionally justified operating ranges and invariant/property fixtures for energy balance, curve axes, tiny/large intervals and loss-sensitive boundaries; do not silently standardize every tolerance.

**Suggested owner:** Numerical analyst and independent reviewer. **Effort:** 5–9 focused days. **Confidence:** medium. **Dependencies:** SG-R03, SG-R04; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- An evidence table identifies each reviewed tolerance, units, reason and tested scale.
- Property/limit fixtures report conservation and boundary residuals over declared synthetic ranges.
- Missing physical uncertainty remains labeled unknown rather than inferred from floating-point precision.

**Verification:** Independent derivation, property fixtures and comparison with exact held-input solutions.

**Risks:** Extreme inputs may reveal underflow/overflow or model invalidity requiring separate source work.

**Unresolved assumptions:** Practical supported ranges require an owner decision and evidence.

### SG-R06 — Explore reserve activation and recovery beyond sampled headroom

**P2 · Exploratory Research · 2027-07-01 to 2027-09-30**

**Evidence:** SG-F04. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L87-L214) [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L123-L220)

**Outcome:** A study can distinguish start-of-interval margin from actual activation energy and recovery requirements.

**Proposed change:** Write a bounded research protocol with synthetic activation schedules, response duration, standing losses and recovery objectives; compare against the current baseline-only audit before proposing new behavior.

**Suggested owner:** Storage/controls researcher. **Effort:** 8–15 focused days. **Confidence:** low. **Dependencies:** SG-R03, SG-R04, SG-R07; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- Protocol states activation timing, response/recovery assumptions and criteria before experiments.
- At least one synthetic counterexample explains why sampled headroom is not a continuous guarantee.
- Report identifies whether a new model is warranted; no market qualification or field guarantee is asserted.

**Verification:** Independent research review, reproducible synthetic studies and comparison with current headroom/energy equations.

**Risks:** Broad market/controller requirements can expand beyond this repository's purpose.

**Unresolved assumptions:** No actual grid-code, market product or repeated-event requirement has been selected.

## Horizon

### SG-R08 — Make catalogue refresh and publication provenance reproducible

**P2 · Maintenance · 2027-10-01 to 2027-10-31**

**Evidence:** SG-F09. [docs/native-lessons.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/native-lessons.json#L8-L22) [docs/portfolio/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/lesson-config.json#L15-L20) [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L61-L82)

**Outcome:** Readers can distinguish source, generated catalogue, tested candidate and deployed revision on a repeatable update.

**Proposed change:** Define deterministic catalogue generation/update records and a publication receipt; preserve previous pins as history and keep canonical Markdown linked or reproducibly rendered.

**Suggested owner:** Documentation/publication maintainer. **Effort:** 4–7 focused days. **Confidence:** high. **Dependencies:** SG-R02, SG-R05; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- Two clean generation runs from the same declared inputs produce identical outputs or documented intentional nondeterminism.
- Historical source links remain labeled and resolvable by their original purpose.
- One publication exercise binds merged revision, deployment identity and observed new live navigation/content.

**Verification:** Clean reproduction, diff review and actual deployment/live observation.

**Risks:** A new handbook rendering toolchain could duplicate content unless canonical generation is explicit.

**Unresolved assumptions:** Owner decides whether GitHub-rendered Markdown remains sufficient.

### SG-R09 — Rehearse owner recovery and assign evidence responsibilities

**P2 · Governance · 2027-11-01 to 2027-11-18**

**Evidence:** SG-F10. [AGENTS.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/AGENTS.md#L1-L3) [CITATION.cff](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/CITATION.cff#L1-L16) [checklists/grid-service-evidence-checklist.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/checklists/grid-service-evidence-checklist.md#L1-L18)

**Outcome:** A second authorized person can reproduce checks, explain model limits and restore documentation delivery through current policy.

**Proposed change:** Assign a deputy, decide the confidential reporting route and rehearse the recovery runbook using synthetic/public inputs; retain access decisions privately.

**Suggested owner:** Repository owner and authorized deputy. **Effort:** 2–4 focused days. **Confidence:** medium. **Dependencies:** SG-R08; these are proposal dependencies, not deployed integrations.

**Acceptance criteria:**

- Named authorized roles, access gaps and escalation/reporting route are recorded without publishing secrets.
- A fresh reproduction records interpreter, source/candidate identity, tests, guide checks and a publication trace.
- The exercise separates implemented software evidence from external engineering acceptance authority.

**Verification:** Observed clean-environment handover and owner-reviewed recovery receipt.

**Risks:** Signing, environment or account recovery may depend on unavailable owner access.

**Unresolved assumptions:** No deputy, response-time promise or additional account access is currently established.


## Sequencing and boundaries

Resolve the native/browser unit contract before expanding teaching checks. Agree constraint precedence and envelope provenance before a stable data interchange or broader reserve study. Establish numerical ranges before activation/recovery research. Reproducible catalogue/publication evidence then supports a meaningful recovery rehearsal.

No runtime dependency on another repository is introduced. The existing public-profile brand reference is decorative provenance only. Potential interoperability must first name a real consumer and agree units, signs, schemas, rights and revision identity. See [Portfolio integration](docs/owner/PORTFOLIO_INTEGRATION.md).

Review this plan when evidence changes. Track accepted, deferred and superseded decisions separately; preserve original observed failures and passed baselines. Any broader engineering or field claim requires its own project evidence and authorized review.
