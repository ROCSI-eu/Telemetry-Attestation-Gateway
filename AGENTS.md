# AGENTS.md — Telemetry Attestation Gateway

**Aplicabilitate:** întregul repository. Acest document coordonează comportamentul agentic; nu schimbă autorizațiile, etapele sau statutul dovezilor prevăzute în documentele canonice.

## 1. Surse de adevăr și preflight

- Înainte de modificări citește [autorizația curentă](docs/current-work-authorization.md), [modelul de status și autoritate](docs/README.md), [planul cu gate-uri](docs/delivery-plan.md) și [regulile de contribuție și DCO](CONTRIBUTING.md), plus documentele tematice necesare.
- Verifică în timp real `main`, SHA-ul exact, PR-urile active, fișierele și eventualele conflicte. Nu transforma rezumate conversaționale, propuneri, imagini, mockuri sau planuri în fapte implementate.
- Folosește branch/PR cu scop restrâns, păstrează munca altor contributori și documentează difful, verificările executate, riscurile și următorul gate. Pentru documentație aplică `python3 scripts/check_docs.py`; nu raporta PASS pentru verificări neexecutate.
- Respectă `Signed-off-by` și proveniența contribuției impuse de DCO. Un agent nu trebuie să atribuie fictiv identitatea sau semnătura unei persoane.

## 2. Autonomie în limitele deja permise

- Continuă autonom documentarea și explorarea sintetică reversibilă permisă de `docs/current-work-authorization.md`; nu inventa aprobări sau blocaje pentru investigații independente.
- Experimentele sunt exclusiv locale, sintetice, izolate și fără hardware, comenzi vehicul, telemetrie reală, rețele/ledgere live, date participant sau infrastructură Production. Conform [exploration boundary](docs/delivery-plan.md#exploration-boundary), toate artefactele și ieșirile poartă `EXPERIMENTAL`, `SYNTHETIC_ONLY` și `NOT VALIDATION OR PRODUCTION AUTHORIZATION` (ori manifestul adiacent prevăzut).
- Nu echivala proof-validity cu adevărul senzorului, includerea într-un ledger cu autenticitatea sursei, ori un experiment cu securitate, interoperabilitate, validare independentă, MVP, pilot sau readiness.
- Respectă cele șase dimensiuni ortogonale ale dovezilor și statusului. `Blocked` descrie doar un gate de promovare identificat, nu întregul proiect; un gate respins nu oprește altă cercetare permisă.
- Promovarea într-un contract stabil, evaluarea cu participanți/proofs reale, conectarea la hardware, declararea MVP sau deployment necesită gate-ul și aprobările distincte din planul canonic. Agentul nu este participant, reviewer independent sau autoritate de aprobare.
- Nu introduce secrete, martori de proof, telemetrie privată, date de participant sau identificatori sensibili în Git, CI ori raportări publice.

## 3. AGENTIC-INTERACTION-01 — Checkpoint-uri conversaționale

- Pentru toate discuțiile proiectului, când agentul oprește execuția și așteaptă utilizatorul, oferă un **buton apăsabil „Continuă”**, dacă interfața îl suportă și nu trebuie luată o nouă decizie. Butonul transmite efectiv reluarea de la ultimul checkpoint verificat.
- Dacă este necesară o aprobare sau alegere, oferă un buton cu **decizia precisă** ori opțiuni distincte (de exemplu „Aprob promovarea la Gate A”), fără a masca aprobarea în „Continuă”. Dacă nu există controale interactive, folosește o instrucțiune textuală clară.
- La oprire precizează succint ce este terminat, ce urmează, blocajul și gate-ul concret. Nu cere repetat o aprobare valabilă deja acordată și nu opri inutil lucrări în mandat.
- Nici afișarea, nici apăsarea unui control nu reprezintă autorizare anticipată pentru gate-uri, acces la date, furnizori/costuri, merge, deployment sau operațiuni ireversibile.

## 4. Handoff și acceptanță

- Reconciliază mereu HEAD-ul curent, starea documentelor, dovezile și gate-urile înainte de a relua; folosește registrele existente, fără a crea infrastructură de orchestrare.
- Raportează distinct `proposed`, `experimental`, `tested synthetic`, `reviewed`, `merged`, `externally validated`, `authorized` și `deployed`. Nu prezenta etapele ca echivalente.
- Aprobarea de merge și cea de deployment sunt distincte; o aprobare generică de continuare nu poate înlocui cerințele de promovare.
