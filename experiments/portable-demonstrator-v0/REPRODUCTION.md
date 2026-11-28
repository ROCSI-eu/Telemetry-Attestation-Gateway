# Portable Demonstrator — assembly and acceptance / asamblare și acceptanță

EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Non-cryptographic UX prototype — no proof generated or verified.
Experimental / Synthetic evidence / Unreviewed / Synthetic data / Local-only / No external assurance claim.

## RO

Sursele sunt fixate la main `4f9c2f2b746f938bd589062b0bf947d98e7166fc`, PR #222; asamblatorul verifică 33 de blob-uri canonice. Nu redistribuie binare de la terți, CRS, granturi, profile private sau dovezi autentice. [README.md](README.md) este inclus nemodificat în distribuția deterministă. Folosește Python 3.14.4 Linux x86_64, bibliotecă standard, executorul local izolat existent, fără provisioning. În mediul deja autorizat, cu namespace de rețea/IPC privat, fără GUI/hardware, sursa exactă a repository-ului read-only la /source, acest director read-only la /design, /tmp privat, directoare distincte deținute de operator (0700) și limite de resurse, execută:

1. Asamblare, /release gol și singurul rezultat writable: `python3 -I -B /design/assemble_demo.py /source /release`.
2. Verifică independent manifestul SHA256SUMS: digest așteptat `9c1cf5e48aac136ce3e625c9827b497252d5325d21f611deb852f487286489bc`, toate cele 38 de intrări și setul exact de 39 de fișiere. Digestul nu este o semnătură.
3. Cu /release read-only, /output gol și writable, execută `python3 -I -B /release/demo.py --release-sha256 9c1cf5e48aac136ce3e625c9827b497252d5325d21f611deb852f487286489bc --output /output`.
4. Pentru QA, folosește un alt /output gol și writable, /source, /design, /release read-only: `python3 -I -B /design/test_portable.py`. Testul reasamblează în tmpfs, compară cele două ieșiri cu digesturile sintetice fixate și exercită șase controale negative. Nu necesită montarea dovezilor private.
5. Opțional, cu /archive gol și writable și /release read-only: `python3 -I -B /design/archive_demo.py`. Arhiva este locală, nu publicată.

Oprește la orice abatere, fără retry automat; retrage numai runtime-ul propriu. Rezultatele locale inițiale (28.11.2026): 33/33 pini, 39/39 fișiere identice în două asamblări, 2/2 rezultate identice, 3/3 teste de artefacte, 6/6 controale negative, reproducere arhivă și cleanup PASS. Testarea este pe un singur host, nu acceptanță multiplatformă. Fără promovare, QGC/GTK 02 HOLD, Gate A/B/D OPEN.

## EN

Sources are pinned to main `4f9c2f2b746f938bd589062b0bf947d98e7166fc`, PR #222; assembly checks 33 canonical blobs. No vendor binaries, CRS, grants, private profiles or authentic proofs are redistributed. [README.md](README.md) is included unchanged in the deterministic package. Use Python 3.14.4 Linux x86_64, standard library, existing authorized local isolated executor, no provisioning. Use independent network/IPC namespaces, no GUI/hardware, exact repository source read-only at /source, this directory read-only at /design, private /tmp, separate owner-private directories (0700), bounded resources:

1. Assemble with empty /release as the only writable output: `python3 -I -B /design/assemble_demo.py /source /release`.
2. Independently check SHA256SUMS: expected digest `9c1cf5e48aac136ce3e625c9827b497252d5325d21f611deb852f487286489bc`, all 38 entries and exact 39-file set. Digest is not a signature.
3. With /release read-only, empty writable /output, run `python3 -I -B /release/demo.py --release-sha256 9c1cf5e48aac136ce3e625c9827b497252d5325d21f611deb852f487286489bc --output /output`.
4. For QA, use another empty writable /output, read-only /source, /design, /release: `python3 -I -B /design/test_portable.py`. It reassembles in tmpfs, compares both outputs to pinned synthetic digests and exercises six negative controls. No private evidence mount required.
5. Optionally, with empty writable /archive and read-only /release: `python3 -I -B /design/archive_demo.py`. Archive is local, not published.

Stop on mismatch, no automatic retry; clean only owned runtime. Initial local results (2026-11-28): 33/33 pins, 39/39 identical files from two assemblies, 2/2 identical outputs, 3/3 artifact tests, 6/6 negative controls, archive reproducibility and cleanup PASS. Single-host testing only, not cross-platform acceptance. No promotion, QGC/GTK 02 HOLD, Gate A/B/D OPEN.
