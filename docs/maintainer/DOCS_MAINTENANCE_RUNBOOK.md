# Documentation maintenance runbook

[Handbook](../INDEX.md) · [API catalogue](../developer/API_CLI_AND_INTERFACES.md) · [Evidence ledger](VERIFICATION_EVIDENCE_LEDGER.md)

## Canonical map

| Subject | Canonical source / document | Update rule |
|---|---|---|
| Native implementation | `models/*.py` and `models/data/*.csv` | Source changes require authorized engineering review; derive docs from the reviewed revision |
| Existing detailed examples | `models/README.md` | Preserve useful detail and link from the handbook |
| Public Python/CLI contracts | Developer API catalogue | Reconcile declarations, dataclass fields, parser flags and helper-added options |
| Equation/unit/validity narrative | Three math-and-physics chapters | Keep literal implementation, derivations and external requirements distinct |
| Selected browser lesson | `docs/lesson-config.json` and matching embedded config | Reconcile configured defaults, presets/checkpoints and exported engine defaults |
| Browser engine | Inline `LabSimulation` implementation | Verify behavior separately from lesson metadata and HTML appearance |
| Learning map | `docs/portfolio/lesson-config.json`, inline data and guide validator | Preserve the reviewed source pin or explicitly regenerate with provenance |
| Historical native/animation catalogues | Their existing JSON manifests and HTML/SVG | Preserve historical identities; do not imply current execution |
| Authorship/license | `CITATION.cff`, `LICENSE`, `codemeta.json` | Change only on evidenced owner instruction |

[docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L165-L177) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L338-L355) [scripts/portfolio/validate_guide.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/scripts/portfolio/validate_guide.py#L1-L33) [docs/native-lessons.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/native-lessons.json#L8-L22) [CITATION.cff](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/CITATION.cff#L1-L16)

## Change-to-document checklist

1. Record the immutable source/base SHA and complete recursive tree, including hidden files and directory identities. Give every tracked entry an analyzed, indexed-only, excluded or unavailable disposition with a reason.
2. Re-extract public declarations and CLI registrations. Count shared helper registrations once and document where they are reused. Compare removals/renames/defaults, not merely file counts.
3. Trace affected math with its units, signs, validation, state carry, tolerances and tests. Reconcile examples and fields against source, not older prose.
4. Preserve useful existing documents. Update the canonical entrypoint and links; avoid divergent copied manuals or unreproducible generated HTML.
5. Keep all 24 handbook/root entrypoints substantive and navigable. Validate relative files/fragments, source SHA/path/line ranges, tables, code fences, Mermaid and CFF.
6. Execute documented reproducibility commands appropriate to the change, retaining exact revision, environment, exit status, outputs and limits. Separate arithmetic, static document, rendered UI and field evidence.
7. Freeze the complete candidate, obtain independent QA and bind later commit/merge/deployment receipts to the actual tree.

## Source citations and histories

Link implementation facts to `blob/<immutable-commit>/<path>#Lx-Ly`. Include decorators when claiming frozen dataclasses and include all relevant composed stages when describing a workflow. A correct line range is necessary but does not prove that the linked code supports the prose.

Historical package/source pins are intentional records. The current source is `8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e`; the preserved guide/browser-package pin is `24de0b792ecb4357b42be5bbe20183c1112b5702`; the native catalogue pin is `92a0b4ea1d5c4c30bbc7869f7914751c1e96a0ac`. Label their purpose rather than replacing one with another. [docs/portfolio/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/portfolio/lesson-config.json#L15-L20) [docs/native-lessons.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/native-lessons.json#L8-L22)

## Small navigation changes

Use the established button/link styles and preserve layout, motion preferences and script/style behavior. The added handbook link uses GitHub-rendered Markdown; it does not promise that Pages will transform uploaded raw Markdown. Check the target and keyboard link semantics locally, then verify the actual live site and deployment revision after merge.

## Recurring maintenance proposal

- With each numerical/API change: repeat affected source, equation, CLI, test and unit comparisons.
- With each dependency/action update: inspect exact pin changes and run applicable existing checks.
- Before release or publication: inspect current rules, candidate SHA, CI/review state, complete diff, merged identity and live content.
- Quarterly, if the owner adopts this cadence: review unresolved roadmap items, contributor/recovery access, provenance manifests and public-data permissions.

This cadence is proposed. There is no documented response-time or staffing commitment. Cost claims require actual runtime/billing evidence, consistent with [AGENTS.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/AGENTS.md#L1-L3).
