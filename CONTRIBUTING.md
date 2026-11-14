# Contributing

This repository contains governance documentation plus disposable sandbox artifacts that comply with the [exploration boundary](docs/delivery-plan.md#exploration-boundary). Other implementation contributions are not authorized. Follow the authority and status rules in the [documentation guide](docs/README.md), and do not present proposed or sandbox behavior as implemented product capability.

Sandbox contributions must use demonstrably synthetic data, remain inside the documented isolation boundary, and carry **`EXPERIMENTAL`**, **`SYNTHETIC_ONLY`**, and **`NOT VALIDATION OR PRODUCTION AUTHORIZATION`**. If a format cannot embed the markings, include the adjacent path-and-digest manifest required by the delivery plan; human-visible renderings must still display them. A sandbox contribution is not a supported prototype, external-validation or promotion evidence, an MVP component, or pilot/production work.

Executable synthetic research belongs in the lightweight [experimental research workspace](experiments/README.md). Use its short experiment record and template rather than creating new milestone or governance paperwork for each disposable technical spike.

## Contribution attribution and provenance

Effective only after this policy change is merged into main. Contributions made before that point remain subject to the DCO 1.1 requirement in force when they were made. This change does not retroactively certify or waive any unsigned contribution.

For contributions made by the repository's solo maintainer after this policy becomes effective, a per-commit Signed-off-by trailer is not required.

The maintainer remains responsible for confirming the right to submit each contribution under the applicable project license, including AI-assisted contributions. Material third-party sources, their licenses, relevant modifications, and restrictions must remain traceable in the corresponding pull request.

Authenticated GitHub attribution provides traceability but is not, by itself, a legal certification of contribution rights.

External contributors must provide a truthful rights-to-submit declaration acceptable to the maintainer before integration. Until a separately accepted contribution policy establishes another mechanism, external contributions continue to require DCO 1.1 sign-off on each commit.

No agent may fabricate, impersonate, backfill, or attribute a personal DCO certification without the contributor's actual authorization and certification.

All contributions must respect the project's effective licensing, intellectual-property, privacy, experimental-safety, and technical authorization requirements.

## Licensing and provenance

Contributions are provided under the license effective for the destination file or path. See [`LICENSING.md`](LICENSING.md); currently the root MIT `LICENSE` remains effective and the layered model is only Proposed. The project requires no contributor copyright assignment and has no CLA requirement. A CLA could be introduced only by a separately reviewed future decision.

Identify third-party material, its source, version, license, notices, and modifications in the pull request. Contributors are responsible for having permission to submit it. Do not assume project terms override upstream obligations.

Never commit secrets, credentials, private keys, proof witnesses, private telemetry, customer or participant data, production identifiers, re-identifying combinations, or other confidential, personal, export-controlled, or restricted material. Fixtures must be demonstrably synthetic, minimized, labelled test-only, and reviewed before any future CC0 designation.

## Pull requests

Run `python3 scripts/check_docs.py`. Explain the authority owner, affected status/gate, licensing and provenance impact, and validation evidence. Use the pull-request checklist; maintainers must not treat a checked box as legal approval.
