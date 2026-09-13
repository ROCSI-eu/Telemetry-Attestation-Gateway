# Contributing

This repository contains governance documentation plus disposable sandbox artifacts that comply with the [exploration boundary](docs/delivery-plan.md#exploration-boundary). Other implementation contributions are not authorized. Follow the authority and status rules in the [documentation guide](docs/README.md), and do not present proposed or sandbox behavior as implemented product capability.

Sandbox contributions must use demonstrably synthetic data, remain inside the documented isolation boundary, and carry **`EXPERIMENTAL`**, **`SYNTHETIC_ONLY`**, and **`NOT VALIDATION OR PRODUCTION AUTHORIZATION`**. If a format cannot embed the markings, include the adjacent path-and-digest manifest required by the delivery plan; human-visible renderings must still display them. A sandbox contribution is not a supported prototype, external-validation or promotion evidence, an MVP component, or pilot/production work.

Executable synthetic research belongs in the lightweight [experimental research workspace](experiments/README.md). Use its short experiment record and template rather than creating new milestone or governance paperwork for each disposable technical spike.

## Developer Certificate of Origin

Every contribution must be certified under Developer Certificate of Origin 1.1 with a `Signed-off-by` trailer. The sign-off certifies the contributor's right to submit the work under the applicable project license; it is not a copyright assignment.

Create a signed-off commit with:

```sh
git commit -s
```

The trailer must use a real name and reachable email, for example `Signed-off-by: Example Contributor <contributor@example.org>`. To repair the latest local commit, run `git commit --amend --signoff`; repair older unpublished commits with an interactive rebase. Coordinate with maintainers rather than rewriting shared history.

By making a contribution to this project, I certify that:

> (a) The contribution was created in whole or in part by me and I
> have the right to submit it under the open source license
> indicated in the file; or
>
> (b) The contribution is based upon previous work that, to the best
> of my knowledge, is covered under an appropriate open source
> license and I have the right under that license to submit that work
> with modifications, whether created in whole or in part by me,
> under the same open source license (unless I am permitted to submit
> under a different license), as indicated in the file; or
>
> (c) The contribution was provided directly to me by some other
> person who certified (a), (b) or (c) and I have not modified it.
>
> (d) I understand and agree that this project and the contribution
> are public and that a record of the contribution (including all
> personal information I submit with it, including my sign-off) is
> maintained indefinitely and may be redistributed consistent with
> this project or the open source license(s) involved.

That is the official DCO 1.1 certification text, also published at [developercertificate.org](https://developercertificate.org/).

## Licensing and provenance

Contributions are provided under the license effective for the destination file or path. See [`LICENSING.md`](LICENSING.md); currently the root MIT `LICENSE` remains effective and the layered model is only Proposed. The project requires no contributor copyright assignment and has no CLA requirement. A CLA could be introduced only by a separately reviewed future decision.

Identify third-party material, its source, version, license, notices, and modifications in the pull request. Contributors are responsible for having permission to submit it. Do not assume project terms override upstream obligations.

Never commit secrets, credentials, private keys, proof witnesses, private telemetry, customer or participant data, production identifiers, re-identifying combinations, or other confidential, personal, export-controlled, or restricted material. Fixtures must be demonstrably synthetic, minimized, labelled test-only, and reviewed before any future CC0 designation.

## Pull requests

Run `python3 scripts/check_docs.py`. Explain the authority owner, affected status/gate, licensing and provenance impact, and validation evidence. Use the pull-request checklist; maintainers must not treat a checked box as legal approval.
