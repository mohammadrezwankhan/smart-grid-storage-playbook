# Security and sensitive reporting

## Project boundary

The native models read explicit local inputs/CSV files and perform reference calculations. The browser lesson is a static teaching surface. This repository does not establish a supported production-control deployment or a security-response service. Do not use its examples as operational credentials, plant settings or authorization to control equipment. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L510-L605) [docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L306-L314)

## Report safely

For an ordinary reproducible defect that contains no sensitive information, use the repository's current issue interface with the source SHA, a minimal synthetic input, expected/actual behavior and relevant logs. For a vulnerability or private data exposure, open [GitHub Security Advisories](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/security/advisories) and select **Report a vulnerability**. If the option is unavailable, arrange a private channel with the owner. Do not publish exploit details, tokens or proprietary data to a public issue while trying to establish that channel.

There is no published security email, guaranteed response time, or supported-version range.

## Information to exclude

Remove customer/site identifiers, proprietary equipment curves, access tokens, connection credentials, network locations and sensitive raw event records. Use fictional or approved public examples. Ignore patterns for environment files are an aid, not a guarantee against accidental disclosure. [.gitignore](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.gitignore#L1-L14)

If a credential has been exposed, the authorized account owner should revoke/rotate it through the relevant service and assess access/history. Deleting text alone does not revoke access. Preserve incident evidence privately and avoid changing unrelated model behavior.

## Supply and publication changes

Review full action pins, least-privilege permissions, actual tested revisions and deployment provenance. Preserve signing/review protections and all existing checks. The source's human-authorship workflow validates commit attribution; it is not a vulnerability scanner or scientific review. [AGENTS.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/AGENTS.md#L1-L3) [.github/workflows/no-codex-attribution.yml](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/.github/workflows/no-codex-attribution.yml#L65-L99)

Keep confidential project evidence outside the public documentation. New data or dependency contributions require their own rights, provenance and review.
