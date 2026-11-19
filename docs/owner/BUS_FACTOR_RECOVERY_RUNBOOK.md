# Bus-factor and recovery runbook

[Handbook](../INDEX.md) · [Governance](GOVERNANCE_AND_SCOPE.md) · [Setup](../developer/SETUP_AND_REPRODUCIBILITY.md)

## Recovery objective

Enable an authorized successor to reproduce the source calculations and restore documented publication without relying on one person's unrecorded environment. This is a proposed runbook, not evidence that a deputy has access or a recovery exercise has passed.

## Assets and authority to preserve

| Asset | Required record | Recovery constraint |
|---|---|---|
| Repository and signed history | Owner-approved access, immutable commits/tags, complete source tree | Preserve signatures and effective rules; no force push or policy bypass |
| Native calculations and CSVs | Exact hashes, interpreter, commands, outputs and test logs | Illustrative inputs remain distinct from project data |
| Documentation/API/equations | Canonical handbook and preserved native guide | Reconcile source facts before changing a historical statement |
| Browser/guide/catalogues | HTML, canonical/embedded JSON, source pins, SVG assets | Historical provenance is not a current execution receipt |
| Pages environment | Existing workflow, approved environment access and actual deployment identity | Source declares Pages/OIDC permissions; external DNS/settings must be observed |
| Local learning notes | User-exported study plans where desired | Browser local storage is personal state, not a repository backup |

[.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L61-L82) [docs/portfolio/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/index.html#L270-L296) [docs/native-lessons.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/native-lessons.json#L8-L22)

## Technical reproduction

1. Obtain the repository through an authorized read-only route and verify the intended immutable commit/tree. For the dated source baseline, use `8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e`.
2. Inspect instructions and code before execution. Use a clean Python 3.12 environment; the observed baseline interpreter was 3.12.14. No third-party runtime install is needed for the inspected native tests.
3. Run the following from the repository root and retain version, complete command, stdout/stderr and exit status:

```bash
python --version
python -m unittest discover -s tests -v
python scripts/portfolio/validate_guide.py
```

4. Run the eight reference commands in the source workflow and compare units, limits and expected values with the [worked labs](../developer/WORKED_EXAMPLES_AND_LABS.md). A new revision can legitimately have a different test count; investigate the diff rather than forcing the old number.
5. Verify the browser lesson separately: embedded config identity, source/default context, eight declared checkpoints, then actual browser interaction and accessibility if this surface is in scope. Native tests do not execute that UI.
6. Reconcile authorship/license and all required documentation entrypoints. Keep operational logs and credentials outside the public content.

The dated baseline observed 153 tests and four validated guide paths. The final recovery record must state what the successor actually ran, not repeat those numbers without evidence. [.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L42-L113) [scripts/portfolio/validate_guide.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/scripts/portfolio/validate_guide.py#L1-L33)

## Restore delivery safely

Inspect current branch/ruleset protections, signing access, required CI/reviews and environment approvals. Prepare a normal scoped PR, bind independent QA to its exact tree, merge only through the current guarded route, and observe the actual Pages deployment revision and new live content.

No application secret is declared for local calculations. Do not create or transfer unnecessary tokens. Any owner recovery, credential rotation or external DNS action requires the real account authority and recorded settings; this guide supplies no credentials or bypass.

If the site is broken, first separate artifact/build failure, environment approval, source revision, URL mapping and stale cache. Reverting documentation through a normal reviewed commit preserves evidence. Do not rewrite a historical catalogue's source pin to mask a missing deployment.

## Proposed handover exercise

Have a second authorized maintainer reproduce the native suite and guide from a clean source copy, explain the MW/kW and SOC boundaries, find a source claim through its immutable link, and trace a deployment from merge to live handbook navigation. Record elapsed steps, missing access and corrections. The owner should then assign a deputy and a repeat cadence; neither is assumed to exist today.
