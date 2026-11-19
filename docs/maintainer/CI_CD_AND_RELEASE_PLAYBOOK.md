# CI, delivery and release playbook

[Handbook](../INDEX.md) · [Evidence ledger](VERIFICATION_EVIDENCE_LEDGER.md) · [Recovery](../owner/BUS_FACTOR_RECOVERY_RUNBOOK.md)

## Tracked GitHub Actions

| Workflow | Events and path scope | Jobs / runtime | Actual responsibility |
|---|---|---|---|
| Model and Markdown validation | Manual; PRs for Markdown/Python/model CSV/own workflow; main pushes for the same paths | `validate`, Ubuntu, 20-minute timeout, Python 3.12 | Native suite, eight references and selected Markdown link globs |
| Flagship dashboard | Manual; main pushes changing `docs/**`, `assets/**` or own workflow | `validate` then guarded main-only `deploy`; Ubuntu, 5/10 minutes | Static lab checks and upload of `docs` to Pages |
| Portfolio guide checks | PR path filters; push path filters with no branch restriction | `validate`, Ubuntu, 5 minutes | Four source-linked learning paths and assets |
| Human authorship policy | PR, merge group, main branch pushes and all tag pushes | `human-authorship-policy`, Ubuntu, 5 minutes | Commit author/committer/co-author metadata |

[.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L1-L43) [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L1-L82) [.github/workflows/portfolio-dashboard-check.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/portfolio-dashboard-check.yml#L1-L22) [.github/workflows/no-codex-attribution.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/no-codex-attribution.yml#L1-L39)

For the portfolio workflow, GitHub does not evaluate path filters on tag pushes. Its push configuration has no tag exclusion, so the path list must not be described as excluding tag events. See [GitHub's trigger rules](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#using-filters-to-target-specific-paths-for-pull-request-or-push-events).

No CircleCI or Buildkite configuration appears in the pinned tracked tree. This is a source-inventory statement; externally configured services and current required checks must still be inspected on the actual PR.

## Limits of the existing validators

The model workflow's link checker targets `README.md CONTRIBUTING.md models/*.md concepts/*.md checklists/*.md glossary/*.md diagrams/*.md`. It does not cover all new handbook/root documents merely because a Markdown change triggers the workflow. The roadmap proposes extending validation without renaming or weakening existing checks. [.github/workflows/markdown-maintenance.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/markdown-maintenance.yml#L115-L119)

The dashboard validator checks expected markers, JSON object shape, symlink absence and external HTTPS script-source absence. It does not execute the teaching engine, verify every declared checkpoint, validate the entire JSON schema or inspect a rendered page. The portfolio validator checks its separate guide data, source paths, SVG and inline-data identity. [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L22-L59) [scripts/portfolio/validate_guide.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/scripts/portfolio/validate_guide.py#L1-L33)

## Documentation PR procedure

1. Capture the source/base SHA and complete tracked tree. Read `AGENTS.md` and the effective branch/ruleset settings.
2. Keep the diff to documentation and deliberate navigation/build changes. Preserve native models, tests, fixture CSVs, browser calculations, existing workflows and historical source pins unless separately authorized.
3. Run the documented local suite and guide validator, validate all authored local links/citations and CFF, compare the full diff, and obtain independent QA of the frozen candidate.
4. Use the repository's legitimate signed-commit mechanism and the human owner's actual attribution. Never impersonate a human reviewer, forge provenance or disable policy.
5. Refresh PR head/base, check runs, review requirements, conflicts and merge policy. A check against another SHA or a skipped path is not a substitute for required evidence.
6. Use an expected-head guard for the audited merge, respect any merge queue, and confirm the actual result. Record merge and publication separately.

The source instructions require full action pins, least privilege, preserved check/event/release coverage, cancellation only of superseded PR runs and evidence for savings. [AGENTS.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/AGENTS.md#L1-L3) Authorship validation examines commit metadata and explicitly allows tool disclosure without tool authorship. [.github/workflows/no-codex-attribution.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/no-codex-attribution.yml#L65-L99)

The 2026-11-19 read-only ruleset observation requires signed commits on **all branches**, with no bypass actors. Classic protection could not be read by the connector. The integration owner must resolve effective policy from supported settings before mutation; an empty status-check field alone does not establish permission to merge.

## Publication route

The existing main-branch deployment uses `actions/upload-pages-artifact` with `path: docs`, then `actions/deploy-pages` in the `github-pages` environment. Workflow permissions grant Pages and OIDC write only to the deploy job. [.github/workflows/deploy-dashboard.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/deploy-dashboard.yml#L61-L82)

The static site's new **Documentation handbook** navigation points to GitHub-rendered `docs/INDEX.md`. Raw Markdown inside the uploaded directory is not claimed to be rendered as an HTML handbook. Preserve the existing site layout and compare script/style bytes so navigation cannot alter calculation behavior.

After merge, inspect the actual deployment revision and live navigation target. A successful old `deploy` check or an accessible stale page is not proof of the new content. Existing metadata lists a custom-site URL, but this source file alone does not establish current DNS, hosting or deployment provenance. [docs/portfolio/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/lesson-config.json#L1-L20)

## Release state and rollback

The read-only 2026-11-19 queries returned no tags or GitHub releases. This handbook adds an **Unreleased** changelog entry, not a numbered software release. The browser configuration's `schema_version: 1.0` is a lesson schema marker, not a project release tag. [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L1-L10)

For a documentation regression, prepare a normal reviewed revert of the affected documentation commit, preserve the numerical source, run applicable checks and let the existing pipeline redeploy. For a stale site, diagnose workflow event, environment approval, artifact path, deployment revision and cache separately. Do not force-push, alter protections or overwrite historical model evidence to make a status appear green.
