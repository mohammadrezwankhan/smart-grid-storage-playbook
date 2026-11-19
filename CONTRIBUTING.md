# Contributing

Contributions should make smart-grid and storage concepts easier to inspect,
teach, or reuse.

## Good Contributions

- Improve explanations.
- Add diagrams.
- Add glossary entries.
- Link to public technical references.

## Pull Request Checklist

- [ ] The explanation is technically accurate.
- [ ] Acronyms are defined.
- [ ] Diagrams include alt text or descriptions.
- [ ] Sources are public.
- [ ] `python -m unittest discover -s tests -v` passes for model changes.
- [ ] Control breakpoints and sign conventions are documented.


## Reproducible changes

Use the [setup guide](docs/developer/SETUP_AND_REPRODUCIBILITY.md) and [verification ledger](docs/maintainer/VERIFICATION_EVIDENCE_LEDGER.md). Record the exact source/candidate revision, command, interpreter, exit status and retained output. Run `python -m unittest discover -s tests -v` for native changes and `python scripts/portfolio/validate_guide.py` when the source-linked guide changes.

Preserve the distinction between native MW/MWh constraints and browser kW teaching scenarios. State signs, units, measurement intervals, defaults and the layer that enforces each limit. Update the relevant [model reference](models/README.md), handbook page and tests together when an independently authorized implementation change alters a contract.

Use illustrative or approved public fixtures. Do not publish vendor-confidential capability curves, site identifiers, control settings, credentials or operating traces. Dataset provenance, permission and calibration require explicit evidence.

## Documentation and review

Keep [docs/INDEX.md](docs/INDEX.md) as the audience map and [models/README.md](models/README.md) as the existing native walkthrough. Link to the canonical explanation rather than creating an unsynchronized copy. Cite implementation facts with a commit permalink and lines. Treat architecture observations and roadmap proposals as such; do not fabricate historical decisions or releases.

Validate local navigation and CITATION.cff, preserve the original license/author identity, and describe any unexecuted checks explicitly. A passing diagnostic or illustrative model is not an engineering acceptance certificate.

Respect the existing CI instructions in [AGENTS.md](AGENTS.md): retain required contexts, branch/tag coverage, matrices and publication guards. Do not change workflows or protection rules merely to make a documentation PR pass. Current signed-commit and merge requirements must be verified by the authorized integration owner.
