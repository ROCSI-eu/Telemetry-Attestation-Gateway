# SOURCE-PHYSICAL-COVERAGE-BOUNDARY-01 — constatare analitică sintetică

**25 noiembrie 2026 · FINAL/PASS exclusiv pentru analiza locală delimitată**  
**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Rezultat:** **pozitiv**, în sensul existenței unui contraexemplu *ipotetic și sintetic* de indistinguibilitate a două istorii fizice prin dovezile disponibile verificatorului. **Negativ** pentru inferența „dovada ZKP validă implică acoperire fizică completă”. Rezultatul nu este o constatare empirică despre un vehicul, o sursă sau o observație reală.

## 1. Scop, baseline și autorizare

- Repository canonic: `ROCSI-eu/Telemetry-Attestation-Gateway`, `main` citit la `0fe2424cb22be5f867b62cfd8a3f7f0d73c5902c`; PR [#190](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/pull/190) **MERGED**.
- Reguli consultate pe `main`: [AGENTS.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/AGENTS.md), [docs/README.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/docs/README.md), [docs/current-work-authorization.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/docs/current-work-authorization.md), [docs/delivery-plan.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/docs/delivery-plan.md), [experiments/README.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/experiments/README.md), [CONTRIBUTING.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/CONTRIBUTING.md), [docs/security-and-privacy.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/docs/security-and-privacy.md), [docs/data-and-proof-model.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/docs/data-and-proof-model.md) și [docs/claim-envelope.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/main/docs/claim-envelope.md).
- Scop autorizat: numai cercetare sintetică, locală, reversibilă, citire și documentare. **Nu** au fost efectuate: proving, provisioning, generare de telemetrie, execuție nouă a testelor, invocare CI, scriere GitHub, deployment, publicare, promovare, intervenție în SOURCE-INTERVAL-ZKP-01 sau TAG #88.
- Checkpointuri **reutilizate, nu reexecutate**: circuit Noir SHA-256 `098c49802636cd3b2407868e091144b25dbaa3e79baa26eeb5e0688104a4f814`; E2E autentic cu trei cadre sintetice, 98 intrări publice, verificare independentă PASS; commit atomic o singură dată, controale de dovadă/VK/intrări/replay respinse; adaptor 43/43 teste locale PASS; CI #45601799248 SUCCESS conform checkpointului furnizat; Production FINAL/PASS și 14 constatări RO/EN conform baseline-ului furnizat. Nu sunt certificări efectuate în acest mandat.

## 2. Ipoteză

Există două istorii fizice ipotetice distincte `H0 != H1` care induc exact aceeași secvență de trei observații recepționate și autentificate și, astfel, **aceleași date de verificare**. Prin urmare, validitatea criptografică a dovezii agregate pentru observațiile furnizate nu poate stabili singură exhaustivitatea observațiilor fizice ale intervalului.

## 3. Model minim și metodă (analiză, fără experiment criptografic)

Fie `C = (c1, c2, c3)` cele **trei cadre sintetice admise** în dovada canonică și `R = (r1, r2, r3)` cele **trei recepții cu MAC de test**. Politica locală fixează un interval de recepție de 300 ms, cu centre nominale de intrare `start + 50`, `start + 150`, `start + 250 ms`, toleranță `±10 ms`; cerința este exact o observație primară recepționată pentru fiecare slot și ordine strict crescătoare a valorilor semnate de boot. Acestea sunt **momente de recepție simulate**, nu momente fizice atestate.

Definim două lumi **exclusiv ipotetice**; nu se atribuie valori de telemetrie fizică:

| | Istoria `H0` | Istoria `H1` |
|---|---|---|
| Succesiune fizică postulată | `p1 → p2 → p3` | `p1 → p* → p2 → p3` |
| Observație intermediară | niciuna suplimentară în model | `p*` are loc între `p1` și `p2`, dar nu ajunge în fluxul semnat/recepționat |
| Date care ajung la verificator | `c1, c2, c3` | **aceleași** `c1, c2, c3` |
| Recepții autentificate | `r1, r2, r3` | **aceleași** `r1, r2, r3` |
| Alte efecte vizibile, inclusiv secvență/counter | niciunul | **niciunul prin ipoteza explicită**: `p*` este omis înainte de orice schimbare observabilă de protocol sau de registru |

Această alegere minimală nu presupune că un pachet semnat suplimentar a fost transmis și pierdut fără urmă. Dacă o implementare ar autentifica independent un contor exhaustiv al tuturor observațiilor create, o asemenea diferență **ar putea** deveni observabilă. Tocmai o astfel de legătură verificabilă cu toate observațiile fizice lipsește din modelul prezent.

Funcția de observație a verificatorului, `V`, primește doar cadrele/capturile admise, recepțiile și starea/verificarea aferentă. Prin construcție:

`V(H0) = V(H1) = (C, R, digests(C), public_inputs(C), proof_for_C, pinned_VK, policy, watermark_context)`.

Mai exact, [circuitul Noir](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/0fe2424cb22be5f867b62cfd8a3f7f0d73c5902c/experiments/source-proof-binding-v0/interval-zkp-v0/src/main.nr) verifică digestul BLAKE2s al **fiecăruia dintre cele trei cadre furnizate** și limita fixă de viteză, nu numărul tuturor evenimentelor fizice. [Adaptorul criptografic](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/0fe2424cb22be5f867b62cfd8a3f7f0d73c5902c/experiments/source-proof-binding-v0/aggregate_crypto.py) reconstruiește `3 × 32 + 2 = 98` câmpuri publice: 96 octeți de digest, limita `500` cm/s și versiunea `2`. [Controlul de interval](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/0fe2424cb22be5f867b62cfd8a3f7f0d73c5902c/experiments/source-proof-binding-v0/interval_coverage.py) verifică cele trei sloturi de **recepție**. [Referința temporală](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/0fe2424cb22be5f867b62cfd8a3f7f0d73c5902c/experiments/source-proof-binding-v0/trusted_time.py) atestă simulat recepția, nu captarea fizică.

Nu s-a generat nicio nouă dovadă. `proof_for_C` reprezintă **artefactul verificat în checkpointul anterior**, nereținut în acest raport; nu se afirmă că două noi execuții randomizate de proving ar produce exact aceiași octeți de dovadă. Afirmația este mai restrânsă: **același transcript de verificare deja acceptat este compatibil cu ambele lumi ipotetice**, pentru că niciuna dintre intrările lui nu depinde de `p*`.

## 4. Rezultat logic și controale proporționale

- **PASS — construcția sintetică:** `H0 != H1` prin prezența lui `p*`, dar toate dovezile disponibile verificatorului sunt identice prin definiția canalului de observație. Distincția fizică nu este identificabilă din acestea.
- **PASS — verificarea de domeniu statică:** sursele canonice arată că numărul de cadre din circuit este fix la trei, că intrările publice sunt cele 98 definite și că timpul atestat este de recepție simulată. Niciuna dintre aceste condiții nu include un angajament față de universul complet al observațiilor fizice.
- **Controale existente, reutilizate:** circuitul și E2E autentic au verificare pozitivă pentru cele trei cadre; proba absentă/modificată, VK greșită, secvența autentificată diferită și replay au fost respinse în experimentul precedent, fără avansarea stării în cazurile indicate. Aceste controale demonstrează legătura cu **intrările furnizate**, nu detectarea unui `p*` nevăzut.
- **Nu s-au rulat teste noi:** comparația este o demonstrație de indistinguibilitate la nivelul informațiilor observabile; re-proving-ul ar reevalua aceeași propoziție despre aceleași trei cadre și nu ar putea crea dovezi despre `p*`.

## 5. Informația lipsă și separarea garanțiilor

1. **Autenticitate criptografică — acoperită strict pentru intrările din experiment.** Semnăturile/recepțiile sintetice, digesturile și dovada validă leagă cele trei cadre furnizate de predicatul testat. Nu garantează că nu mai există evenimente sau măsurători în afara lor.
2. **Acoperire fizică — NEDEMONSTRATĂ.** Lipsește un mecanism independent și autentificat care să declare și să lege verificabil de interval **ce observații fizice ar fi trebuit generate, care au fost efectiv generate, câte au fost pierdute/omise și care este semantica exactă a acoperirii**. Trei sloturi de recepție complete nu certifică o istorie fizică exhaustivă. Chiar și un contor exhaustiv de mesaje ar acoperi doar mesajele din domeniul controlat, nu fenomene nesesizate de senzor.
3. **Origine de încredere — NEDEMONSTRATĂ pentru dispozitive reale.** Semnăturile sunt generate cu chei de test, fără înrolare probată a unei surse fizice, protecție de chei, lanț de proveniență al senzorului sau atestarea traseului dinaintea semnării.
4. **Timp independent — NEDEMONSTRAT pentru captare fizică.** MAC-ul de test asupra momentului de ingress și ceasul decizional simulat nu stabilesc o cronologie fizică independentă, sincronizată și rezistentă la manipulare pentru `p1`, `p*`, `p2`, `p3`.

**Concluzie:** integritatea și ordinea recepțiilor pot fi verificate în modelul sintetic, dar nu permit inferența că fiecare observație fizică posibilă a fost recepționată sau că nu s-a întâmplat nimic între cadre. Diferența este o **limită a evidenței**, nu dovada unei vulnerabilități în algoritmul criptografic.

## 6. Limite, reproducibilitate și proveniență

- Acesta este un **contraexemplu analitic sintetic, condițional**, nu o observare empirică a unui `p*`, nu o simulare fizică, nu o măsurătoare, nu un nou proof artifact și nu o verificare nouă a lui `bb`.
- Istoriile folosesc exclusiv simboluri artificiale `p1,p*,p2,p3`; niciun timp fizic, conținut al observației, dispozitiv real, cheie sau eveniment adevărat nu este inventat ori atribuit.
- Procedură de reproducere fără execuție: (a) fixează exact `C` și `R` din contractul canonic; (b) adaugă doar `p*` în istoria abstractă, fără să îl proiectezi în intrările recepționate; (c) reconstruiește expresia funcției `V` din cele trei fișiere de implementare; (d) constată că valorile domeniului funcției `V` nu depind de `p*`; (e) compară condițional aceleași rezultate ale verificatorului. Niciun secret sau artefact efemer E2E nu este necesar.
- Proveniența criptografică: [qa-aggregate-crypto-e2e-20261125.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/0fe2424cb22be5f867b62cfd8a3f7f0d73c5902c/experiments/source-proof-binding-v0/qa-aggregate-crypto-e2e-20261125.md), real proof 14.656 octeți raportat acolo, 98 inputuri și VK SHA-256 `942b463decd9b1f6ab58369b0ab16f8412cf769d0e8cf137e4ea5862ef644fba`, toate **evidență anterioară**, nu reexecutată. Dovezile negative/fixture anterioare: [qa-evidence-20261124.md](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/blob/0fe2424cb22be5f867b62cfd8a3f7f0d73c5902c/experiments/source-proof-binding-v0/qa-evidence-20261124.md).
- Nu demonstrează adevăr senzorial, origine reală, acoperire fizică continuă, captare cronologică independentă, validare a produsului, siguranță, conformitate, performanță, disponibilitate ori autorizare de producție.
- **Cleanup:** nu s-a creat runtime de experiment, martor, dovadă, captură, socket, proces sau cheie; niciun cleanup de infrastructură nu este necesar. Singurul rezultat nou este acest fișier de documentare locală. Checkpointurile de cleanup PASS ale E2E anterior sunt doar reutilizate.

## 7. Profilul celor șase dimensiuni independente

| Dimensiune | Încadrare efectivă a acestui nou raport local |
|---|---|
| Artifact implementation state | `Experimental` |
| Evidence source | `Synthetic evidence` — analiză sintetică plus referințe la dovezi sintetice anterioare |
| Review independence | `Unreviewed` — revizia/acceptarea reală a maintainerului **nu a avut loc** în acest mandat; numai după ea se poate consemna `Maintainer-reviewed` conform profilului canonic |
| Data class | `Synthetic data` |
| Permitted environment | `Local-only` |
| External claim level | `No external assurance claim` |

`FINAL/PASS` în antet înseamnă numai că **analiza locală delimitată a fost încheiată și documentată**; nu conferă statut `Maintainer-reviewed`, acceptare publică, promovare a dovezii ori autorizare de produs.

## 8. Cel mai mic pas următor, separat de constatarea locală

1. **Pas recomandat, încă neexecutat:** maintainerul examinează contraexemplul și, dacă îl acceptă, păstrează explicit în formularea claim-ului distincția **„trei recepții autentificate care satisfac predicatul”**, nu **„acoperire fizică completă”**. Nu este necesară o schimbare de circuit pentru a consemna această limită epistemică.
2. **Propunere de integrare GitHub, numai după autorizare distinctă:** un PR concentrat care anexează constatarea la documentația/evidența existentă `experiments/source-proof-binding-v0/qa-aggregate-crypto-e2e-20261125.md` (sau la un fișier de experiment dedicat cross-linkat), cu diff/review/documentation check și gate-ul existent proporționale. Nu modifica SOURCE-INTERVAL-ZKP-01, TAG #88, runtime, circuit sau workflow.
3. **Propunere de publicare RO/EN, numai după acceptarea ca public-safe și aprobare de merge:** în același PR focalizat, dacă se decide publicarea, se adaugă a 15-a constatare bilingvă în `showcase/research_journal.json`, cu rezultat, învățătură, limitare și cale la evidența integrată, plus testele statice/focalizate aplicabile. Nu se realizează publicarea în acest mandat. Merge-ul autorizat în `main` declanșează automat Cloudflare Pages Production și trebuie tratat ca decizie distinctă, urmată de verificarea efectivă a paginilor RO/EN conform `AGENTS.md`.

**Checkpoint de predare:** analiza locală `SOURCE-PHYSICAL-COVERAGE-BOUNDARY-01` este completă; **PENDING**, separat: revizie/acceptare maintainer, orice GitHub write, integrare, publicare RO/EN ori promovare. Nu există niciun motiv tehnic de a relua proving-ul PASS pentru această întrebare.
