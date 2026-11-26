"""Static Romanian localization, sharing metadata and exact display copy only.

No operator functionality, user language profiling, or external API calls.
The same JavaScript is emitted in both locales; CSP hashes remain identical.
"""
from __future__ import annotations

from html import escape
from html.parser import HTMLParser
import re

ORIGIN = "https://tag.rocsi.eu"

# Exact visible text from the public *post-sanitization* page.
# Do not translate immutable typed evidence enums or experiment boundary labels.
RO_TEXT = {
    "TAG — Privacy-Preserving Telemetry Attestation | ROCSI":
        "TAG — Verificarea telemetriei cu divulgare minimă | ROCSI",
    "ROCSI / Telemetry Attestation Gateway":
        "ROCSI / Telemetry Attestation Gateway",
    "Mission Control": "Centru de comandă și control",
    "TAG explores how specific telemetry conditions could be verified without sharing all underlying data. This experimental public page only displays synthetic animations, mock scenarios and a recorded offline verification outcome; no live vehicle connection, control, proof generation or browser verification occurs.":
        "TAG explorează verificarea unor condiții privind telemetria fără divulgarea tuturor datelor. Această pagină experimentală prezintă doar animații sintetice, scenarii simulate și un rezultat offline înregistrat; nu conectează sau controlează vehicule și nu generează ori verifică dovezi în browser.",
    "THE CONCEPT IN BRIEF": "CONCEPTUL, PE SCURT",
    "Verify a condition without revealing all the telemetry": "Verifică o condiție fără să divulgi toată telemetria",
    "TAG investigates cryptographic verification of selected telemetry conditions with limited disclosure. Instead of providing a full mission record, a system could provide a proof about a specific condition, subject to trusted inputs and appropriate validation.":
        "TAG investighează verificarea criptografică a unor condiții privind telemetria, cu divulgare limitată. În loc să transmită întregul istoric al unei misiuni, un sistem ar putea furniza o dovadă despre o condiție precisă, cu condiția utilizării unor date de intrare de încredere și a unei validări adecvate.",
    "Illustrative example:": "Exemplu ilustrativ:",
    "A speed value satisfies a predefined limit without revealing the exact private value. This page does not test a real measurement or attest an actual mission.":
        "O valoare a vitezei respectă o limită prestabilită fără divulgarea valorii private exacte. Această pagină nu testează măsurători reale și nu atestă o misiune efectivă.",
    "Explore the synthetic route": "Explorează traseul sintetic",
    "Inspect recorded scenarios": "Examinează scenariile înregistrate",
    "See the separate offline verifier result": "Vezi rezultatul separat al verificatorului offline",
    "Potential applications, not validated deployments": "Aplicații potențiale, nu implementări validate",
    "Telemetry audits": "Auditul telemetriei",
    "An operator could present evidence about a predefined condition without exposing the complete underlying dataset. No audit acceptance is established by this showcase.":
        "Un operator ar putea prezenta dovezi privind o condiție prestabilită fără să expună întregul set de date. Această demonstrație nu stabilește acceptarea în cadrul unui audit.",
    "Autonomous platforms": "Platforme autonome",
    "Future integrations could be investigated for aerial, ground or maritime vehicles. This page does not connect to or control any vehicle.":
        "Ar putea fi investigate integrări viitoare cu vehicule aeriene, terestre sau navale. Pagina nu se conectează la vehicule și nu le controlează.",
    "Existing workflows": "Fluxuri existente",
    "CLI tools and possible future connectors could support integration with other systems. The public site exposes no execution endpoint.":
        "Instrumentele CLI și posibilii conectori viitori ar putea permite integrarea cu alte sisteme. Site-ul public nu expune niciun punct de execuție.",
    "Full experimental scope and limitations": "Domeniul complet și limitele experimentale",
    "PUBLIC SHOWCASE · PRECOMPUTED ONLY":
        "DEMONSTRAȚIE PUBLICĂ · DOAR REZULTATE PRECALCULATE",
    "What the recorded result can show": "Ce poate demonstra rezultatul înregistrat",
    "A separately executed offline verifier recorded a cryptographic VALID or INVALID outcome for one synthetic proof. The browser only displays a minimized, unauthenticated JSON replay; it does not verify or authenticate the proof. The orchestration scenarios below are mocks, not proof checks.":
        "Un verificator independent, executat offline, a înregistrat un rezultat criptografic VALID sau INVALID pentru o dovadă sintetică. Browserul afișează doar o reluare JSON minimizată și neautentificată; nu verifică și nu autentifică dovada. Scenariile de mai jos sunt simulări, nu verificări de dovezi.",
    "What it does not establish": "Ce nu poate demonstra",
    "Telemetry truth, source integrity, trustworthy time, interval or flight coverage, safety, compliance, policy/freshness/revocation/replay acceptance, publication, customer demand or a relying-party decision. Assurance remains A0_SYNTHETIC.":
        "Nu confirmă corectitudinea telemetriei, integritatea sursei, timpul de încredere, acoperirea intervalului ori a zborului, siguranța, conformitatea, acceptarea politicilor, prospețimea, revocarea, protecția contra reluării, publicarea, cererea clienților sau decizia beneficiarului. Nivelul de asigurare rămâne A0_SYNTHETIC.",
    "Mission Control · synthetic visualization": "Centru de comandă și control · vizualizare sintetică",
    "Observation only, never vehicle control": "Doar observație, niciodată controlul vehiculului",
    "A predefined 2.5D vehicle and route illustrate the concept. Motion is not telemetry, a measured trajectory, a live mission, proof generation, or verification progress.":
        "Un vehicul 2.5D și un traseu prestabilit ilustrează conceptul. Animația nu reprezintă telemetrie, traiectorie măsurată, misiune reală, generare de dovezi ori progresul verificării.",
    "Pause illustration": "Oprește animația",
    "Illustrative scene": "Scenă ilustrativă",
    "Observation pass · A–B–C": "Trecere de observație · A–B–C",
    "Hold at waypoint · A–B": "Oprire la punctul B · A–B",
    "Return route · A–B–A": "Traseu de întoarcere · A–B–A",
    "Replay illustration": "Reia ilustrația de la început",
    "Resume illustration": "Continuă animația",
    "Ready · prerecorded illustration only": "Pregătit · doar ilustrație preînregistrată",
    "Illustrative synthetic observation route and 2.5D vehicle":
        "Traseu sintetic ilustrativ și vehicul 2.5D",
    "Abstract non-geographic waypoints and an animated synthetic vehicle. No physical coordinates, real telemetry, or verified flight path.":
        "Puncte abstracte, fără localizare geografică, și un vehicul sintetic animat. Nu sunt prezentate coordonate reale, telemetrie reală sau trasee de zbor verificate.",
    "SYNTHETIC ROUTE · NOT GEOGRAPHIC": "TRASEU SINTETIC · FĂRĂ REFERINȚĂ GEOGRAFICĂ",
    "ILLUSTRATION ONLY · NO LIVE STREAM": "DOAR ILUSTRAȚIE · FĂRĂ FLUX LIVE",
    "No live backend · independent of illustration": "Fără backend live · independent de animație",
    "Execution deliberately disabled": "Execuție dezactivată intenționat",
    "Execution": "Execuție",
    "DISABLED · static showcase only": "DEZACTIVAT · doar demonstrație statică",
    "Proof generation": "Generarea dovezii",
    "Cryptographic verification": "Verificare criptografică",
    "These fields never represent running computation on this public site. The mock scenario panel and independently recorded offline-verifier result below remain separate from the illustration.":
        "Aceste câmpuri nu indică niciodată operațiuni în execuție pe site-ul public. Scenariile simulate și rezultatul verificatorului offline, înregistrat separat mai jos, sunt independente de animație.",
    "EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION. No MAVLink commands, navigation control, mission edits, or source assurance. Animation never changes evidence status.":
        "EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION. Fără comenzi MAVLink, controlul navigației, modificarea misiunilor sau garanții privind sursa. Animația nu modifică niciodată starea dovezilor.",
    "Scenario replay": "Reluarea scenariilor",
    "/ orchestration mock": "/ simulare a orchestrării",
    "Synthetic test case": "Scenariu sintetic de test",
    "Loading deterministic evidence…": "Se încarcă dovezile deterministe…",
    "Show result": "Afișează rezultatul",
    "Conceptual flow only: synthetic telemetry → normalization → proof → independent verification → optional publication. The stages below replay mocks; they are not live progress.":
        "Flux exclusiv conceptual: telemetrie sintetică → normalizare → dovadă → verificare independentă → publicare opțională. Etapele de mai jos redau simulări, nu progres în timp real.",
    "01 · Normalize": "01 · Normalizare",
    "Source state": "Starea sursei",
    "02 · Prove": "02 · Dovadă",
    "Generation state": "Starea generării",
    "03 · Verify": "03 · Verificare",
    "Crypto state": "Starea criptografică",
    "04 · Publish": "04 · Publicare",
    "Optional mock": "Simulare opțională",
    "Public policy predicate": "Condiție din politica publică",
    "The private normalized speed is never displayed. This preview does not expose a public limit for each recorded case.":
        "Viteza normalizată privată nu este afișată. Această demonstrație nu expune o limită publică pentru fiecare caz înregistrat.",
    "Recorded cryptographic dimension": "Rezultat criptografic înregistrat",
    "Recorded mock orchestration result, not independently verified proof evidence.":
        "Rezultat al unei orchestrări simulate, nu dovadă verificată independent.",
    "What this does — and does not — demonstrate": "Ce demonstrează și ce nu demonstrează",
    "This preview demonstrates how separate typed outcomes can be presented. Its source data comes from deterministic tests that mock proof generation and verification. It does not demonstrate a newly generated genuine proof, telemetry truth, trustworthy source/time, whole-flight coverage, safety, compliance, customer demand or production readiness.":
        "Demonstrația arată cum pot fi prezentate rezultate distincte, tipizate. Datele provin din teste deterministe care simulează generarea și verificarea dovezilor. Nu demonstrează generarea unei noi dovezi autentice, corectitudinea telemetriei, încrederea în sursă sau timp, acoperirea integrală a zborului, siguranța, conformitatea, cererea clienților ori pregătirea pentru producție.",
    "Recorded typed outcomes": "Rezultate tipizate înregistrate",
    "Source normalization": "Normalizarea sursei",
    "Source trust": "Încrederea în sursă",
    "Claim eligibility": "Eligibilitatea afirmației",
    "Verification input": "Intrarea verificării",
    "Assurance": "Nivel de asigurare",
    "Optional publication mock": "Simulare de publicare opțională",
    "State": "Stare",
    "Attempts": "Încercări",
    "Reconciled": "Reconciliat",
    "Trust boundaries": "Limite de încredere",
    "Business decision": "Decizie de afaceri",
    "MAVLink command path": "Canal de comenzi MAVLink",
    "Restricted disclosure": "Divulgarea datelor restricționate",
    "Verification is not a relying party's decision. Publication is not cryptographic verification. A0_SYNTHETIC does not establish real-world telemetry assurance.":
        "Verificarea nu este decizia beneficiarului. Publicarea nu înseamnă verificare criptografică. A0_SYNTHETIC nu oferă asigurări privind telemetria din lumea reală.",
    "Separate evidence type · no live prover": "Tip distinct de dovadă · fără generator live",
    "Precomputed genuine synthetic proof verification": "Verificare precalculată a unei dovezi sintetice autentice",
    "This is a recorded result from the independent local Noir/Barretenberg verifier, not an orchestration mock. Verification happened offline before export, not in this browser. A static JSON replay is not an authenticated proof or an independently verifiable receipt. No proof, witness, key, raw telemetry, or private observation is supplied to the page.":
        "Acesta este rezultatul înregistrat al verificatorului local independent Noir/Barretenberg, nu o simulare a orchestrării. Verificarea s-a efectuat offline, înainte de export, nu în browser. Reluarea unui fișier JSON static nu reprezintă o dovadă autentificată sau o confirmare verificabilă independent. Pagina nu primește dovezi, martori, chei, telemetrie brută sau observații private.",
    "This frozen result was created before publication. Reloading this static file never runs a prover, verifies a proof or refreshes an offline computation.":
        "Acest rezultat fix a fost creat înainte de publicare. Reîncărcarea fișierului static nu generează și nu verifică o dovadă și nu reexecută procesarea offline.",
    "Reload recorded result": "Reîncarcă rezultatul înregistrat",
    "Loading minimized offline verification replay…": "Se încarcă rezultatul minimizat al verificării offline…",
    "Recorded offline cryptographic outcome": "Rezultat criptografic offline înregistrat",
    "Evidence kind: PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION. Proof generation was not observed by this verifier.":
        "Tip de dovadă: PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION. Generarea dovezii nu a fost observată de acest verificator.",
    "Input reconstruction": "Reconstrucția intrării",
    "Recorded proof rejection reason": "Motivul înregistrat al respingerii dovezii",
    "Independent dimensions": "Dimensiuni independente",
    "Policy": "Politică",
    "Freshness": "Actualitate",
    "Revocation": "Revocare",
    "Replay": "Protecție contra reluării",
    "Publication": "Publicare",
    "Relying-party decision": "Decizia beneficiarului",
    "Browser cryptographic verification": "Verificare criptografică în browser",
    "Proof validity is not telemetry truth. One synthetic observation does not establish interval coverage, flight/safety, contractual, payment or regulatory compliance. The source record has no customer or commercial validation.":
        "Validitatea dovezii nu garantează corectitudinea telemetriei. O observație sintetică nu demonstrează acoperirea unui interval sau a unui zbor, siguranța ori respectarea cerințelor contractuale, de plată sau de reglementare. Înregistrarea originală nu a fost validată de clienți și nici în condiții comerciale.",
    "Public static technology showcase. Experimental synthetic-only, precomputed results. No visitor execution, vehicle connection, telemetry upload, analytics, tracking, external fonts or proof jobs. The browser does not independently verify proofs.":
        "Demonstrație tehnologică publică, statică. Rezultate experimentale, exclusiv sintetice și precalculate. Fără execuții inițiate de vizitatori, conectare la vehicule, încărcare de telemetrie, analiză de trafic, urmărire, fonturi externe sau sarcini de generare a dovezilor. Browserul nu verifică independent dovezile.",
    # Public-only TAG visual narrative; immutable typed evidence remains untranslated.
    "TAG": "TAG",
    "Page sections": "Secțiunile paginii",
    "The Principle": "Principiul",
    "Mission Observability": "Observabilitatea misiunii",
    "Technical Evidence": "Dovezi tehnice",
    "01 / THE PRINCIPLE": "01 / PRINCIPIUL",
    "02 / OBSERVATIONAL RESEARCH": "02 / CERCETARE OBSERVAȚIONALĂ",
    "03 / POTENTIAL APPLICATIONS": "03 / APLICAȚII POTENȚIALE",
    "04 / EVIDENCE BOUNDARIES": "04 / LIMITELE DOVEZILOR",
    "05 / EXPERIMENTAL BOUNDARY": "05 / LIMITE EXPERIMENTALE",
    "EXPERIMENTAL / SYNTHETIC-ONLY RESEARCH": "CERCETARE EXPERIMENTALĂ / DATE SINTETICE",
    "Verify the condition. Keep the rest private.": "Verifică o condiție. Păstrează restul privat.",
    "Explore the illustration": "Explorează ilustrația",
    "Review technical evidence": "Examinează dovezile tehnice",
    "TAG / SYNTHETIC OBSERVATION": "TAG / OBSERVAȚIE SINTETICĂ",
    "A0 / SYNTHETIC · OBSERVATION ONLY": "A0 / SINTETIC · DOAR OBSERVAȚIE",
    "TAG explores verification without disclosing all telemetry. This public scene is synthetic and its separate verifier result was recorded offline; the browser neither connects to vehicles nor verifies proofs.":
        "TAG explorează verificarea fără divulgarea întregii telemetrii. Scena publică este sintetică, iar rezultatul verificatorului separat a fost înregistrat offline; browserul nu se conectează la vehicule și nu verifică dovezi.",
    "Explore the scene": "Explorează scena",
    "Review the evidence": "Examinează dovezile",
    "01 / CLAIM": "01 / CONDIȚIE",
    "02 / PROOF": "02 / DOVADĂ",
    "03 / CHECK": "03 / VERIFICARE",
    "04 / DECISION": "04 / DECIZIE",
    "Predefined condition": "Condiție prestabilită",
    "Synthetic research artifact": "Artefact de cercetare sintetică",
    "Recorded offline result": "Rezultat înregistrat offline",
    "Not made on this page": "Nu este luată aici",
    "TAG / EXPERIMENT": "TAG / EXPERIMENT",
    "A0 / SYNTHETIC": "A0 / SINTETIC",
    "The orchestration is simulated. The separate verifier outcome was recorded offline; the browser displays both without independently checking proofs.":
        "Orchestrarea este simulată. Rezultatul separat al verificatorului a fost înregistrat offline; browserul le afișează pe ambele fără să verifice independent dovezile.",
    "Research": "Cercetare",
    "Limitations": "Limitări",
    "A": "A", "B": "B", "C": "C", "—": "—",
    # TAG-TECH-EXPLAIN-01: display-only public explanation (not a proof runner).
    "EXPERIMENTAL PROOF TOOLCHAIN": "INSTRUMENTE EXPERIMENTALE PENTRU DOVEZI",
    "How Noir and Barretenberg are used in TAG": "Cum sunt folosite Noir și Barretenberg în TAG",
    "The synthetic bounded-speed experiment uses a pinned research toolchain: Noir/Nargo 1.0.0-beta.26 and Barretenberg bb 5.2.0. This is not a production technology selection.":
        "Experimentul sintetic privind limita de viteză utilizează versiuni fixate ale instrumentelor de cercetare: Noir/Nargo 1.0.0-beta.26 și Barretenberg bb 5.2.0. Acestea nu reprezintă o alegere tehnologică pentru producție.",
    "01 / DEFINE": "01 / DEFINIRE",
    "02 / PROVE": "02 / GENERARE",
    "03 / VERIFY": "03 / VERIFICARE",
    "Noir": "Noir",
    "Barretenberg": "Barretenberg",
    "Offline verifier": "Verificator offline",
    "Noir expresses a constraint comparing a private speed value with a public limit; Nargo compiles the circuit.":
        "Noir exprimă o constrângere care compară viteza privată cu o limită publică; Nargo compilează circuitul.",
    "With the private witness, the pinned bb backend generates a zero-knowledge proof of the constrained statement.":
        "Folosind martorul privat, backendul bb cu versiune fixată generează o dovadă zero-knowledge pentru condiția definită.",
    "A separately invoked verifier reconstructs public inputs from canonical CBOR and checks the proof with the expected verification key, without the private speed.":
        "Un verificator invocat separat reconstruiește intrările publice din CBOR canonic și verifică dovada cu cheia de verificare așteptată, fără acces la viteza privată.",
    "Noir documentation": "Documentație Noir",
    "Barretenberg documentation": "Documentație Barretenberg",
    "TAG experimental implementation": "Implementarea experimentală TAG",
    "Integrated SITL-to-ZKP CI evidence": "Dovada CI pentru fluxul SITL–ZKP integrat",
    "A cryptographically valid proof does not establish telemetry truth, trusted sensors or time, whole-flight coverage, safety or legal compliance. This public page shows recorded synthetic outcomes: the browser neither generates nor verifies a proof.":
        "O dovadă criptografică validă nu confirmă corectitudinea telemetriei, încrederea în senzori ori timp, acoperirea întregului zbor, siguranța sau conformitatea legală. Pagina publică afișează rezultate sintetice înregistrate: browserul nu generează și nu verifică dovezi.",
    # TAG-MISSION-CONTROL-EVIDENCE-01: static bilingual evidence checkpoint.
    "SITL to ZKP: an integrated synthetic result":
        "SITL → ZKP: rezultat sintetic integrat",
    "Local ArduPilot Copter 4.7.1 SITL (TAG #86): PASS for isolated, receive-only MAVLink2 intake of two GLOBAL_POSITION_INT observations and TAG normalization. This does not establish telemetry truth.":
        "ArduPilot Copter 4.7.1 SITL local (TAG #86): PASS pentru recepția izolată, exclusiv pasivă, a două observații MAVLink2 GLOBAL_POSITION_INT și normalizarea TAG. Aceasta nu atestă corectitudinea telemetriei.",
    "Independent synthetic ZK checkpoint (14 November 2026): historical Qube evidence records proof generation and offline verifier VALID with the pinned verification key. This proof was separate from the SITL observations.":
        "Checkpoint ZK sintetic independent (14 noiembrie 2026): dovezile istorice Qube consemnează generarea unei dovezi și rezultatul VALID al verificatorului offline cu cheia de verificare fixată. Dovada este separată de observațiile SITL.",
    "Integrated ArduPilot Copter 4.7.1 SITL → MAVLink2 → TAG normalization → 600 cm/s predicate → Noir/Barretenberg proof → separate verifier: PASS on 22 November 2026 (GitHub Actions #44995909866). Two synthetic observations; proof GENERATED; both checks VALID. Source UNSIGNED; no commands, publication or operational validation.":
        "Flux integrat ArduPilot Copter 4.7.1 SITL → MAVLink2 → normalizare TAG → condiție 600 cm/s → dovadă Noir/Barretenberg → verificator separat: PASS pe 22 noiembrie 2026 (GitHub Actions #44995909866). Două observații sintetice; dovadă GENERATED; ambele verificări VALID. Sursa UNSIGNED; fără comenzi, publicare sau validare operațională.",
    # TAG-TECH-ANIMATION-01: static labels; the shared script translates controls.
    "CONCEPTUAL ANIMATION / NOT A PROOF RUN": "ANIMAȚIE CONCEPTUALĂ / FĂRĂ GENERAREA DOVEZII",
    "Replay explanation": "Reia explicația",
    "Pause illustration": "Oprește animația",
    "Three illustrative stages, not measured computation or a live verifier.":
        "Trei etape ilustrative, fără calcul măsurat sau verificator live.",
    "Conceptual illustration · no proving or verification in this browser":
        "Ilustrație conceptuală · fără generare sau verificare în browser",
    "No MAVLink commands, navigation control, mission edits, or source assurance are provided by this static site.": "Fără comenzi MAVLink, controlul navigației, modificarea misiunilor sau garanții privind sursa pe acest site static.",
    # TAG-EDITORIAL-01: bilingual visitor-facing four-chapter narrative.
    "Illustrative mission": "Misiune ilustrativă",
    "Three synthetic routes": "Trei trasee sintetice",
    "Source": "Sursă",
    "Synthetic only": "Doar date sintetice",
    "Proof on this page": "Dovadă pe această pagină",
    "Not generated": "Nu este generată",
    "Verification on this page": "Verificare pe această pagină",
    "Not performed": "Nu este efectuată",
    "Choose a route to explore a predefined animation. Neither the route nor the vehicle represents measured telemetry.": "Alege un traseu pentru a explora o animație prestabilită. Nici traseul, nici vehiculul nu reprezintă telemetrie măsurată.",
    "Illustration only. The animation is not a real mission or a verification result.": "Doar ilustrație. Animația nu reprezintă o misiune reală sau rezultatul unei verificări.",
    "Experimental research into verifying telemetry conditions with limited disclosure. Public demonstrations use synthetic data and previously recorded results. This site does not control vehicles, verify cryptographic proofs or represent a production-validated solution.": "Cercetare experimentală privind verificarea unor condiții asupra telemetriei cu divulgare limitată. Demonstrațiile publice folosesc date sintetice și rezultate înregistrate anterior. Site-ul nu controlează vehicule, nu verifică dovezi criptografice și nu reprezintă o soluție validată pentru producție.",

    "The Concept": "Conceptul",
    "How It Works": "Cum funcționează",
    "Applications": "Aplicații",
    "The Research": "Cercetarea",
    "EXPERIMENTAL RESEARCH · DATA PRIVACY": "CERCETARE EXPERIMENTALĂ · CONFIDENȚIALITATEA DATELOR",
    "What if a system could prove a condition was met without revealing the data behind it? TAG explores this idea for telemetry through controlled experiments using synthetic data.": "Ce-ar fi dacă un sistem ar putea demonstra respectarea unei condiții fără să dezvăluie datele din spatele ei? TAG explorează această idee pentru telemetrie, prin experimente controlate cu date sintetice.",
    "Explore the concept": "Descoperă conceptul",
    "See the demonstration": "Explorează demonstrația",
    "Research journal": "Jurnalul cercetării",
    "Research": "Cercetare",
    "TAG researches cryptographic checks of telemetry conditions without revealing private data. Discover the experiments, findings and their limits in the research journal.": "TAG cercetează verificarea criptografică a condițiilor din telemetrie, fără divulgarea datelor private. Descoperă experimentele, rezultatele și limitele în jurnal.",
    "01 / THE CONCEPT": "01 / CONCEPTUL",
    "THE CONCEPT": "CONCEPTUL",
    "Less data exposed. A condition that can be verified.": "Mai puține date expuse. O condiție verificabilă.",
    "Verifying a rule can require sharing detailed information. TAG investigates a different approach: proving that one defined condition is satisfied while keeping the underlying value private.": "Verificarea unei reguli poate necesita transmiterea unor informații detaliate. TAG cercetează o altă abordare: demonstrarea îndeplinirii unei condiții precise, păstrând privată valoarea de la care s-a pornit.",
    "A simple example:": "Un exemplu simplu:",
    "A vehicle must stay within a speed limit. A cryptographic proof could establish that a private speed value meets the public limit without disclosing the exact speed.": "Un vehicul trebuie să respecte o limită de viteză. O dovadă criptografică ar putea confirma că valoarea privată respectă limita publică, fără să divulge viteza exactă.",
    "A valid proof does not, by itself, establish whether the original measurement was trustworthy.": "O dovadă validă nu confirmă, în sine, că măsurătoarea originală provine dintr-o sursă de încredere.",
    "02 / HOW IT WORKS": "02 / CUM FUNCȚIONEAZĂ",
    "From a private observation to a verifiable proof.": "De la o observație privată la o dovadă verificabilă.",
    "Explore a synthetic mission and see how a precise rule could be checked without exposing the private observation.": "Explorează o misiune sintetică și vezi cum ar putea fi verificată o regulă precisă fără expunerea observației private.",
    "THE PROOF IN THREE STEPS": "DOVADA ÎN TREI ETAPE",
    "From private data to a verifiable result": "De la informație privată la rezultat verificabil",
    "TAG studies how a defined condition can be checked without disclosing the underlying private value.":
        "TAG cercetează cum poate fi verificată o condiție fără divulgarea valorii private folosite la evaluare.",
    "01 / CONDITION": "01 / CONDIȚIE",
    "02 / PROOF": "02 / DOVADĂ",
    "03 / CHECK": "03 / VERIFICARE",
    "Define the rule": "Definirea condiției",
    "Compare a private speed value with a public limit.": "Compararea unei valori private a vitezei cu o limită publică.",
    "Generate the proof": "Generarea dovezii",
    "Use specialized cryptographic tools to prove the condition without disclosing the private value.": "Instrumentele criptografice specializate demonstrează condiția fără divulgarea valorii private.",
    "Verify independently": "Verificare independentă",
    "A verifier checks the proof using public inputs, without receiving the private speed.": "Un verificator examinează dovada folosind datele publice, fără să primească viteza privată.",
    "This animation explains the concept. Proof generation and offline verification were performed separately, outside the browser.": "Animația explică ideea. Generarea și verificarea experimentală au fost realizate separat, în afara browserului.",
    "Where could this capability matter?": "Unde ar putea conta această capacitate?",
    "Selective verification may help when a result needs to be demonstrated but sharing the entire dataset is undesirable.": "Verificarea selectivă ar putea fi utilă când trebuie demonstrat un rezultat, dar divulgarea integrală a datelor este nedorită.",
    "Audit and verification": "Audit și verificare",
    "An organization could demonstrate that an agreed condition was met without handing over its complete underlying dataset.":
        "O organizație ar putea demonstra că a respectat o condiție convenită fără să transmită întregul set de date folosit la evaluare.",
    "Autonomous systems": "Sisteme autonome",
    "A UAS or autonomous vehicle could report that a defined operational threshold was met without sharing its full telemetry record.":
        "Un UAS sau un vehicul autonom ar putea confirma respectarea unui prag operațional definit fără să transmită întreaga telemetrie.",
    "Information exchange": "Schimb de informații",
    "Two organizations could exchange the verifiable outcome of an agreed check while keeping private inputs at their source.":
        "Două organizații ar putea transmite rezultatul verificabil al unui control convenit, păstrând datele private la sursă.",
    "Logistics and transport": "Logistică și transport",
    "A temperature-sensitive shipment could support a check against an agreed limit without disclosing its entire sensor history.":
        "Pentru un transport de produse sensibile la temperatură, s-ar putea verifica respectarea unei limite convenite fără divulgarea întregului istoric al senzorilor.",
    "Industrial monitoring": "Monitorizare industrială",
    "An operator could demonstrate that a technical threshold was respected without exposing all measurements from its equipment.":
        "Un operator ar putea demonstra respectarea unui prag tehnic fără să expună toate măsurătorile echipamentelor.",
    "Collaborative research": "Cercetare colaborativă",
    "Research teams could verify agreed properties of sensitive datasets without exchanging the raw records between them.":
        "Echipele de cercetare ar putea verifica proprietăți convenite ale unor seturi de date sensibile fără să-și transmită reciproc înregistrările brute.",
    "These are possible applications, not validated operational deployments.": "Acestea sunt aplicații posibile, nu implementări operaționale validate.",
    "04 / THE RESEARCH": "04 / CERCETAREA",
    "What have we demonstrated so far?": "Ce-am demonstrat până acum?",
    "From the TAG research journal": "Din jurnalul de cercetare TAG",
    "What we tested in the lab, what we learned and what still needs to be demonstrated.": "Ce-am testat în laborator, ce-am învățat și ce mai trebuie demonstrat.",
    "TAG is experimental research. The independent results below are useful starting points, not a complete demonstration in a real-world system.": "TAG este cercetare experimentală. Rezultatele independente de mai jos sunt puncte de plecare, nu o demonstrație completă într-un sistem real.",
    "01 / CRYPTOGRAPHY": "01 / CRIPTOGRAFIE",
    "02 / SIMULATION": "02 / SIMULARE",
    "03 / OPEN QUESTION": "03 / ÎNTREBARE DESCHISĂ",
    "Synthetic proof": "Dovadă sintetică",
    "A separate experiment recorded generation of a proof and its acceptance by an offline verifier using the expected verification key.": "Un experiment separat a consemnat generarea unei dovezi și acceptarea sa de către un verificator offline, folosind cheia de verificare așteptată.",
    "Simulator observations": "Observații din simulator",
    "An isolated ArduPilot SITL session received and normalized two synthetic observations through a receive-only interface.": "O sesiune izolată ArduPilot SITL a recepționat și normalizat două observații sintetice printr-o interfață exclusiv pasivă.",
    "End-to-end integration": "Integrarea completă",
    "The full path from SITL observations to an independently verified cryptographic proof has not yet been demonstrated.": "Fluxul complet de la observații SITL la o dovadă criptografică verificată independent nu a fost încă demonstrat.",
    "Next: integrate the stages, evaluate trust in the data source, and test the method's limits in controlled conditions.": "Mai departe: integrarea etapelor, evaluarea încrederii în sursa datelor și testarea limitelor metodei în condiții controlate.",
    "Inside the experiments": "Experimentele, în detaliu",
    "The journal above records accepted findings. Open a topic below for the method, the recorded evidence or what still needs testing.": "Jurnalul de mai sus prezintă rezultatele acceptate. Alege o temă pentru metodă, dovezile înregistrate sau întrebările care rămân deschise.",
    "Research notes and evidence are published together from the TAG repository.": "Notele de cercetare și dovezile sunt publicate împreună din repository-ul TAG.",
    "How the proof works": "Cum funcționează dovada",
    "The rule, the proof and independent verification": "Condiția, dovada și verificarea independentă",
    "Define the condition": "Definim condiția",
    "Noir describes a comparison between a private speed value and a public limit.": "Noir definește condiția prin compararea unei valori private a vitezei cu o limită publică.",
    "Create the proof": "Generăm dovada",
    "Barretenberg uses the private witness to generate a proof of that condition.": "Barretenberg folosește martorul privat pentru a genera dovada condiției.",
    "Verify independently": "Verificăm independent",
    "An offline verifier checks the proof with the expected verification key, without receiving the private speed.": "Un verificator offline folosește cheia de verificare așteptată pentru a valida dovada, fără să primească valoarea privată a vitezei.",
    "Tool versions, full method and source documentation": "Versiuni, metodă completă și documentație",
    "Recorded laboratory evidence": "Rezultate înregistrate în laborator",
    "Separate offline verification from simulated orchestration": "Verificarea offline este distinctă de simularea orchestrării",
    "INDEPENDENT OFFLINE EXPERIMENT": "EXPERIMENT OFFLINE INDEPENDENT",
    "The recorded verifier result is from a separate experiment with synthetic data. No cryptographic verification happens on this page.": "Rezultatul verificatorului provine dintr-un experiment separat, cu date sintetice. Pagina nu efectuează verificări criptografice.",
    "DETERMINISTIC SCENARIOS": "SCENARII DETERMINISTE",
    "recorded cases": "cazuri înregistrate",
    "These cases exercise orchestration, input changes and publication states. They do not constitute independently verified cryptographic proofs.": "Aceste cazuri testează orchestrarea, modificarea intrărilor și stările de publicare. Ele nu reprezintă dovezi criptografice verificate independent.",
    "A separate isolated GitHub Actions run has now generated and independently verified a synthetic SITL-derived ZKP. The cases below remain static mock replays, not live proof execution in the browser.": "O execuție izolată GitHub Actions a generat și a verificat independent o dovadă ZKP sintetică pornind de la observații SITL. Cazurile de mai jos sunt în continuare simulări statice, nu generări live de dovezi în browser.",
    "Explore recorded scenarios and the full offline result": "Consultă scenariile și rezultatul offline complet",
    "The scenario controls replay static fixtures; their progress and publication indicators are not live operations.": "Controalele redau date statice; indicatorii de progres și publicare nu reprezintă operațiuni live.",
    "Limits and next validation steps": "Limite și validări necesare",
    "What a successful cryptographic check cannot establish": "Ce nu poate confirma singură verificarea criptografică",
    "Source and time": "Sursa și timpul",
    "A valid proof alone does not establish who produced a measurement or whether its time is trustworthy.": "O dovadă validă nu stabilește singură originea măsurării sau încrederea în timpul asociat.",
    "Coverage and integration": "Acoperire și integrare",
    "One bounded two-observation SITL-to-ZKP run passed; whole-mission coverage, source authentication and trusted time remain unproven.": "Un test SITL–ZKP limitat la două observații a trecut; acoperirea întregii misiuni, autentificarea sursei și timpul de încredere rămân nedemonstrate.",
    "Operational use": "Utilizare operațională",
    "Safety, policy acceptance, customer decisions and production readiness require separate validation.": "Siguranța, acceptarea politicilor, deciziile beneficiarului și pregătirea pentru producție necesită validări separate.",
    "Full experimental boundaries and assurance fields": "Toate limitele experimentale și câmpurile de asigurare",
    "Explore the technical research": "Explorează cercetarea tehnică",
    "Detailed methods, recorded scenarios and limitations are available below for readers who want to go deeper.": "Metodele detaliate, scenariile înregistrate și limitele sunt disponibile mai jos pentru cititorii care vor să aprofundeze.",
    "Methods and tools": "Metode și instrumente",
    "Laboratory scenarios and recorded outcomes": "Scenarii de laborator și rezultate înregistrate",
    "These scenarios replay deterministic mocks, not cryptographic verification in the browser. The separately recorded offline-verifier outcome is labeled independently.": "Aceste scenarii redau simulări deterministe, nu verificări criptografice în browser. Rezultatul separat al verificatorului offline este etichetat independent.",
    "Limitations and assumptions": "Limite și ipoteze",
    # TAG-CONCEPT-CLARITY-01: visitor-facing, hypothetical, no real measurement.
    "VEHICLE SPEED · HYPOTHETICAL EXAMPLE": "VITEZA UNUI VEHICUL · EXEMPLU IPOTETIC",
    "THE IDEA, AT A GLANCE": "IDEEA, DINTR-O PRIVIRE",
    "01 / PRIVATE VALUE": "01 / VALOARE PRIVATĂ",
    "Speed: hidden": "Viteză: ascunsă",
    "The exact reading stays private.": "Valoarea exactă rămâne privată.",
    "02 / PUBLIC RULE": "02 / REGULĂ PUBLICĂ",
    "Speed ≤ speed limit": "Viteză ≤ limita admisă",
    "The condition is known to everyone.": "Condiția este cunoscută tuturor.",
    "03 / VERIFIABLE ANSWER": "03 / RĂSPUNS VERIFICABIL",
    "Within the limit: YES": "Respectă limita: DA",
    "A proof could confirm this without revealing the speed.":
        "O dovadă ar putea confirma răspunsul fără divulgarea vitezei.",
    "MISSION PATTERNS · SELECT A ROUTE": "MODELE DE MISIUNE · ALEGE UN TRASEU",
    "MISSION ROUTE · THREE PATTERNS": "TRASEU DE MISIUNE · TREI MODELE",
    "Mission scenario · selected route": "Scenariu de misiune · traseu selectat",
    # TAG-PRESENTATION-POLISH-01: visitor-facing copy, not immutable evidence labels.
    "PRIVACY-PRESERVING TELEMETRY": "TELEMETRIE CU PROTECȚIA DATELOR",
    "RESEARCH · DATA PRIVACY": "CERCETARE · CONFIDENȚIALITATEA DATELOR",
    "SYNTHETIC ROUTE": "TRASEU SINTETIC",
    "What if systems could demonstrate a condition without revealing the data behind it? TAG investigates this direction for telemetry through cryptographic research.": "Cum ar fi dacă un sistem ar putea demonstra respectarea unei condiții fără să dezvăluie datele din spatele ei? TAG cercetează această direcție pentru telemetrie prin metode criptografice.",
    "SELECTIVE VERIFICATION": "VERIFICARE SELECTIVĂ",
    "PROOF WORKFLOW": "PROCESUL DOVEZII",
    "From a private condition to an independently verifiable result.": "De la o condiție privată la un rezultat verificabil independent.",
    "Rule defined · proof prepared · result checked": "Condiție definită · dovadă pregătită · rezultat verificat",
    "THE IDEA": "PRINCIPIUL",
    "From observation to evidence": "De la observație la dovadă",
    "Three routes help explore how a private observation, a public condition and a verifiable result relate to one another.": "Trei trasee exemplifică legătura dintre o observație privată, o condiție publică și un rezultat verificabil.",
    "Private observation": "Observație privată",
    "Defined condition": "Condiție definită",
    "Verifiable result": "Rezultat verificabil",
    "01": "01",
    "02": "02",
    "03": "03",
    "TAG brings together research on privacy-preserving proofs and controlled observations from a vehicle simulator.": "TAG reunește cercetarea dovezilor care protejează datele și observațiile controlate dintr-un simulator de vehicule.",
    "TAG · Telemetry Attestation Gateway. Exploring verifiable conditions, selective disclosure and privacy-preserving telemetry.": "TAG · Telemetry Attestation Gateway. Cercetare despre condiții verificabile, divulgare selectivă și protecția datelor din telemetrie.",
    # Public navigation-only links to the parent ROCSI initiative and its booking page.
    "Romanian Cyber Space Initiative": "Inițiativa Română pentru Spațiul Cibernetic",
    "Start a conversation": "Programează o conversație",
    "TAG is a research initiative of the Romanian Cyber Space Initiative.": "TAG este o inițiativă de cercetare a Inițiativei Române pentru Spațiul Cibernetic.",
    "Discover more of ROCSI's open research and explore collaboration opportunities.": "Descoperă cercetările deschise ROCSI și oportunitățile de colaborare.",
    "Explore ROCSI": "Descoperă ROCSI",
    # TAG-SPEED-EXPLAIN-01: visitor-first speed example; exact evidence codes unchanged.
    "Can a vehicle prove it respects a speed limit without revealing its speed?": "Poate un vehicul demonstra respectarea unei limite fără să dezvăluie viteza?",
    "TAG researches how a cryptographic proof could confirm that a private speed value meets a public limit, while keeping the exact value confidential.": "TAG cercetează cum o dovadă criptografică ar putea confirma că o valoare privată a vitezei respectă o limită publică, fără divulgarea valorii exacte.",
    "A VEHICLE IN MOTION": "UN VEHICUL ÎN MIȘCARE",
    "Three routes, one question about speed": "Trei trasee, aceeași întrebare despre viteză",
    "Explore how the vehicle moves between A, B and C. The research question is whether a speed measurement meets a defined limit while its precise value stays private.": "Explorează deplasarea vehiculului între punctele A, B și C. Întrebarea cercetată este dacă viteza respectă o limită stabilită, păstrând valoarea exactă privată.",
    "Choose a route": "Alege traseul",
    "Travel from A to C · A–B–C": "Deplasare de la A la C · A–B–C",
    "Stop at B · A–B": "Oprire la B · A–B",
    "Return to A · A–B–A": "Întoarcere la A · A–B–A",
    "Explore the routes": "Explorează traseele",
    "THE SPEED-LIMIT EXAMPLE": "EXEMPLUL LIMITEI DE VITEZĂ",
    "What could a proof confirm?": "Ce ar putea confirma o dovadă?",
    "Imagine the vehicle has measured its speed. The aim is to check a rule without making the exact reading public.": "Imaginează-ți că vehiculul a măsurat viteza. Scopul este verificarea unei reguli fără publicarea valorii exacte.",
    "Private information": "Informația privată",
    "The exact speed value": "Valoarea exactă a vitezei",
    "Public rule": "Regula publică",
    "The maximum permitted speed": "Limita maximă admisă",
    "Verifiable claim": "Afirmația verificabilă",
    "The private value is within the public limit": "Viteza privată respectă limita publică",
    "A zero-knowledge proof could support that claim without revealing the exact speed.": "O dovadă criptografică de tip ZKP ar putea confirma respectarea regulii fără să dezvăluie viteza exactă.",
    "02 / THE ARCHITECTURE": "02 / ARHITECTURA",
    "From a UAS measurement to a verifiable result.": "De la măsurarea UAS la un rezultat verificabil.",
    "A proposed architecture linking an uncrewed aircraft, a TAG cryptographic gateway and command-and-control.": "O arhitectură propusă care conectează o aeronavă fără pilot, un gateway criptografic TAG și centrul de comandă și control.",
    "Proposed UAS to TAG to command-and-control information flow": "Flux informațional propus între UAS, TAG și centrul de comandă și control",
    "ARCHITECTURE UNDER RESEARCH": "ARHITECTURĂ ÎN CERCETARE",
    "UAS": "UAS",
    "Collects a private measurement": "Colectează o măsurare privată",
    "Protected channel": "Canal protejat",
    "TAG / ZKP": "TAG / ZKP",
    "Would prepare a verifiable proof": "Ar pregăti o dovadă verificabilă",
    "Verifiable result": "Rezultat verificabil",
    "C2": "C2",
    "Would check the defined condition": "Ar verifica respectarea condiției",
    "Secure communication protects the channel; a ZKP supports verification. The combined UAS–TAG–C2 flow remains a research objective.": "Comunicația securizată protejează canalul, iar dovada ZKP permite verificarea. Integrarea UAS–TAG–C2 rămâne un obiectiv de cercetare.",
    # Preserve machine-readable evidence codes and experimental markings.
    # The banner is visitor-facing; evidence JSON and local CLI retain immutable codes.
    "EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION":
        "EXPERIMENTAL · EXCLUSIV DATE SINTETICE · NIVEL DE ASIGURARE A0 · NU REPREZINTĂ VALIDARE SAU AUTORIZARE PENTRU PRODUCȚIE",
    "speed_cm_s ≤ maximum_speed_cm_s": "speed_cm_s ≤ maximum_speed_cm_s",
    "NOT_LOADED": "NEÎNCĂRCAT",
    "NOT_OBSERVED": "NEOBSERVAT",
    "NOT_EVALUATED": "NEEVALUAT",
    "NOT_PERFORMED": "NEEFECTUAT",
    "NOT_MADE": "NEADOPTATĂ",
    "NONE": "NICIUNA",
    "A0_SYNTHETIC": "A0_SYNTHETIC",
}

RO_TEXT.update({'The Demonstration': 'Demonstrația',
 'Results': 'Rezultate',
 'THE DEMONSTRATION': 'DEMONSTRAȚIA',
 'Telemetry → cryptographic proof → verification': 'Telemetrie → dovadă criptografică → verificare',
 'The conceptual flow shows how a condition can be checked without revealing the data behind it.': 'Fluxul conceptual arată cum poate fi verificată o condiție fără a dezvălui datele din spatele ei.',
 '01 / TELEMETRY': '01 / TELEMETRIE',
 'Receive observations': 'Recepționăm observații',
 'A simulator produces synthetic observations. The exact value need not be shown to the verifier.': 'Simulatorul produce observații '
                                                                                                    'sintetice. Valoarea exactă nu trebuie '
                                                                                                    'dezvăluită verificatorului.',
 '02 / CRYPTOGRAPHIC PROOF': '02 / DOVADĂ CRIPTOGRAFICĂ',
 'Generate a proof': 'Generăm dovada',
 'A zero-knowledge proof supports a defined condition using the private input.': 'O dovadă cu divulgare zero permite verificarea condiției '
                                                                                 'folosind valoarea privată.',
 '03 / VERIFICATION': '03 / VERIFICARE',
 'Check independently': 'Verificăm independent',
 'A verifier checks the proof without needing the private measurement.': 'Un verificator controlează dovada fără să primească măsurătoarea '
                                                                         'privată.',
 'DOCUMENTED EXPERIMENTAL RESULTS': 'REZULTATE EXPERIMENTALE DOCUMENTATE',
 'Three steps confirmed in synthetic laboratory tests': 'Trei etape confirmate prin teste sintetice de laborator',
 'Synthetic telemetry received': 'Telemetrie sintetică recepționată',
 'Simulator observations reached the experimental processing flow.': 'Observațiile simulatorului au ajuns în fluxul experimental de '
                                                                     'procesare.',
 'ZKP generated': 'Dovadă ZKP generată',
 'A cryptographic proof was generated for the bounded synthetic test.': 'Am generat o dovadă criptografică pentru testul sintetic cu '
                                                                        'limită prestabilită.',
 'Independent verification passed': 'Verificare independentă reușită',
 'A separate verifier successfully checked the synthetic proof offline.': 'Un verificator separat a confirmat dovada sintetică în testul offline.',
 'Research progress.': 'Progresul cercetării.',
 'In a synthetic experiment, we checked the signing key and signature, applied session-local replay protection and independently verified a zero-knowledge proof bound to the observation. Separate tests with a mock proof verifier rejected replay after restart using retained local state. Restoring old state defeats this protection. Separate synthetic tests with a mock proof verifier checked reception freshness using an authenticated time reference from a simulated authority separate from the telemetry source. This does not establish physical capture time or a real trusted-time service. The signing key is a publicly known test key; real vehicle identity remains unproven.': 'Într-un experiment sintetic, am verificat autorizarea cheii și semnătura, am aplicat protecția împotriva reutilizării observațiilor în aceeași sesiune și am verificat independent o dovadă zero-knowledge legată de observație. În teste separate, cu un verificator de dovezi simulat, am respins reutilizarea după repornire folosind starea locală păstrată. Restaurarea unei stări mai vechi anulează această protecție. În teste sintetice separate, cu un verificator de dovezi simulat, am verificat prospețimea recepției folosind o referință temporală autentificată de o autoritate simulată, separată de sursa telemetriei. Nu am demonstrat momentul fizic al observației sau existența unui serviciu real de timp de încredere. Cheia de semnare este una de test, cunoscută public; identitatea unui vehicul real rămâne nedemonstrată.',
 'Experimental and synthetic only.': 'Exclusiv experimental și sintetic.',
 'Research scope.': 'Domeniul cercetării.',
 'Our isolated laboratory tests use synthetic data, not authentic flight telemetry. A valid cryptographic proof does not, by itself, authenticate the telemetry source, timestamp or the full mission. The published illustrations and JSON records are not independently authenticated by this site.': 'În testele izolate de laborator folosim date sintetice, nu telemetrie de zbor autentică. O dovadă criptografică validă nu autentifică, prin ea însăși, sursa telemetriei, marcajul temporal sau întreaga misiune. Ilustrațiile și înregistrările JSON publicate nu sunt autentificate independent de acest site.',
 'Technical documentation and research evidence on GitHub': 'Documentația tehnică și dovezile cercetării pe GitHub',
 'EXPERIMENTAL · SYNTHETIC ONLY · NOT VALIDATION OR PRODUCTION AUTHORIZATION. TAG is a ROCSI research project.': 'EXPERIMENTAL · DOAR DATE '
                                                                                                                 'SINTETICE · NU '
                                                                                                                 'REPREZINTĂ VALIDARE SAU '
                                                                                                                 'AUTORIZARE PENTRU '
                                                                                                                 'PRODUCȚIE. TAG este un '
                                                                                                                 'proiect de cercetare '
                                                                                                                 'ROCSI.'})

RO_ARIA = {
    "Scope and limitations of synthetic evidence": "Domeniul și limitele dovezilor sintetice",
    "Independent evidence status": "Starea independentă a dovezilor",
    "Conceptual pipeline": "Flux conceptual",
    "Page sections": "Secțiunile paginii",
    "Conceptual evidence path, not executed in the browser": "Secvență conceptuală a dovezilor, neexecutată în browser",
    "Experimental proof flow, executed offline": "Flux experimental al dovezii, executat offline",
    "Tool documentation and TAG implementation": "Documentația instrumentelor și implementarea TAG",
    "Technical research panels": "Panouri de cercetare tehnică",
    "Published research version": "Versiunea publicată a cercetării",
    "Three stages of the offline proof experiment": "Trei etape ale experimentului de dovadă offline",
    "Three stages of the conceptual verification flow": "Cele trei etape ale verificării conceptuale",

    "Speed-limit verification example": "Exemplu de verificare a unei limite de viteză",
}

SCENARIO_RO = {
    "altered_public_input": "Date publice modificate",
    "below_limit_local_publication": "Publicare locală sub limită",
    "equality_publication_disabled": "Publicare dezactivată la egalitate",
    "malformed_source": "Sursă invalidă",
    "over_limit": "Depășirea limitei",
    "publication_definitive_failure": "Eșec definitiv la publicare",
    "publication_timeout_retry_reconciliation": "Timeout, reîncercare și reconciliere",
    "publication_unavailable": "Publicare indisponibilă",
    "tampered_proof": "Dovadă modificată",
    "unsupported_public_version": "Versiune publică neacceptată",
}

class _Translator(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output: list[str] = []
        self.block: str | None = None
        self.seen: set[str] = set()
        self.unknown: set[str] = set()

    def handle_starttag(self, tag, attrs):
        value = self.get_starttag_text()
        if tag == "html":
            value = value.replace('lang="en"', 'lang="ro"')
        if tag == "a":
            # Exactly the two approved, static parent-site navigation destinations.
            value = value.replace('href="https://rocsi.eu/en/contact"', 'href="https://rocsi.eu/ro/contact"')
            value = value.replace('href="https://rocsi.eu/en"', 'href="https://rocsi.eu/ro"')
            value = value.replace('href="/en/research/"', 'href="/ro/research/"')
        for en, ro in RO_ARIA.items():
            value = value.replace(f'aria-label="{en}"', f'aria-label="{ro}"')
        self.output.append(value)
        if tag in {"script", "style"}:
            self.block = tag

    def handle_startendtag(self, tag, attrs):
        self.output.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.output.append(f"</{tag}>")
        if tag == self.block:
            self.block = None

    def handle_data(self, text):
        if self.block or not text.strip():
            self.output.append(text)
            return
        start = len(text) - len(text.lstrip())
        end = len(text) - len(text.rstrip())
        core = text[start:len(text)-end if end else len(text)]
        value = RO_TEXT.get(core)
        if value is None:
            self.unknown.add(core)
            value = core
        else:
            self.seen.add(core)
        self.output.append(text[:start] + value + (text[len(text)-end:] if end else ""))

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")

    def handle_comment(self, text):
        self.output.append(f"<!--{text}-->")

    def handle_decl(self, decl):
        self.output.append(f"<!{decl}>")

def romanian_html(english: str) -> str:
    parser = _Translator()
    parser.feed(english)
    parser.close()
    if parser.unknown:
        raise ValueError("untranslated public HTML: " + repr(sorted(parser.unknown)))
    result = "".join(parser.output)
    if '<html lang="ro">' not in result:
        raise ValueError("Romanian page language missing")
    return result

# This block is identical for RO and EN. Only localized display messages change.
LOCALE_JS = r'''
const isRomanian = document.documentElement.lang === "ro";
const copy = isRomanian ? {
  pause: "Oprește animația",
  resume: "Reia animația",
  reduce: "Ilustrație statică · mișcare redusă",
  unavailable: "Fișierul scenariilor precalculate nu este disponibil. Verificați activele statice de pe același domeniu; nu există serviciu de rezervă.",
  precomputedLoading: "Se încarcă rezultatul offline precalculat; browserul nu verifică dovezi.",
  precomputedFailure: "Rezultatul offline nu este disponibil sau este incompatibil. Scenariile simulate rămân distincte; nu se presupune verificarea criptografică.",
  precomputedSuccess: "Rezultatul verificatorului offline a fost încărcat. Verificare în browser: NOT_PERFORMED."
} : {
  pause: "Pause illustration", resume: "Resume illustration",
  reduce: "Illustration stationary · reduced motion",
  unavailable: "Precomputed scenario file unavailable. Check the same-origin static assets; no live fallback exists.",
  precomputedLoading: "Loading precomputed offline result; no verification is performed in this browser.",
  precomputedFailure: "Authentic replay unavailable or incompatible. Mock orchestration remains separate; no cryptographic verification is implied.",
  precomputedSuccess: "Precomputed offline verifier result loaded. Browser verification: NOT_PERFORMED."
};
const scenarioNamesRo = %SCENARIO_NAMES_RO%;
const localizedStatus = {
  NOT_RECORDED:"NEÎNREGISTRAT", NOT_LOADED:"NEÎNCĂRCAT",
  NOT_OBSERVED:"NEOBSERVAT", NOT_EVALUATED:"NEEVALUAT",
  NOT_PERFORMED:"NEEFECTUAT", NOT_ATTEMPTED:"NEÎNCERCAT",
  NOT_CHECKED:"NEVERIFICAT", NOT_MADE:"NEADOPTATĂ",
  NOT_SATISFIED:"NEÎNDEPLINIT", SATISFIED:"ÎNDEPLINIT",
  ACCEPTED:"ACCEPTAT", REJECTED:"RESPINS", UNSIGNED:"NESEMNAT",
  NORMALIZED:"NORMALIZAT", GENERATED:"GENERAT",
  NONE:"NICIUNA",
  YES:"DA", NO:"NU", RECORDED:"ÎNREGISTRAT",
  final:"FINALIZAT", failed:"EȘUAT"
};
'''

def inject_locale_js(english: str) -> str:
    import json
    block = LOCALE_JS.replace(
        "%SCENARIO_NAMES_RO%", json.dumps(SCENARIO_RO, ensure_ascii=False, sort_keys=True)
    )
    anchor = 'const $ = id => document.getElementById(id);'
    if english.count(anchor) != 1:
        raise ValueError("unexpected script initialization shape")
    english = english.replace(anchor, anchor + "\n" + block, 1)
    old = 'const label = key => key.replaceAll("_"," ").toLowerCase().replace(/^./,x=>x.toUpperCase());'
    new = 'const label = key => isRomanian ? (scenarioNamesRo[key] || key) : key.replaceAll("_"," ").toLowerCase().replace(/^./,x=>x.toUpperCase());'
    if english.count(old) != 1:
        raise ValueError("unexpected scenario display label code")
    english = english.replace(old, new)
    old = 'const safe = (v) => typeof v === "string" || typeof v === "number" ? String(v) : "NOT_RECORDED";'
    new = 'const safe = (v) => { const raw = typeof v === "string" || typeof v === "number" ? String(v) : "NOT_RECORDED"; return isRomanian ? (localizedStatus[raw] || raw) : raw; };'
    if english.count(old) != 1:
        raise ValueError("unexpected typed value rendering")
    english = english.replace(old, new)
    pairs = {
        '$(\"error\").textContent=\"Precomputed scenario file unavailable. Check the same-origin static assets; no live fallback exists.\";':
            '$(\"error\").textContent=copy.unavailable;',
        '$(\"authentic-error\").textContent=\"Loading precomputed offline result; no verification is performed in this browser.\";':
            '$(\"authentic-error\").textContent=copy.precomputedLoading;',
        '$(\"authentic-error\").textContent=\"Authentic replay unavailable or incompatible. Mock orchestration remains separate; no cryptographic verification is implied.\";':
            '$(\"authentic-error\").textContent=copy.precomputedFailure;',
        '$(\"authentic-error\").textContent=\"Precomputed offline verifier result loaded. Browser verification: NOT_PERFORMED.\";':
            '$(\"authentic-error\").textContent=copy.precomputedSuccess;',
    }
    for old, new in pairs.items():
        if english.count(old) != 1:
            raise ValueError("unexpected public message code: " + old[:55])
        english = english.replace(old, new)
    return english

SHARE = {
    "ro": {
        "title": "TAG — Verificarea telemetriei cu divulgare minimă | ROCSI",
        "description": "Descoperă cum observațiile SITL sintetice duc la o dovadă criptografică și verificare independentă, fără expunerea valorilor private.",
        "image_alt": "TAG: dronă ilustrativă pe traseul sintetic A–B–C.",
    },
    "en": {
        "title": "TAG — Privacy-Preserving Telemetry Attestation | ROCSI",
        "description": "Explore how synthetic SITL observations lead to a cryptographic proof and independent verification, without exposing private values.",
        "image_alt": "TAG: illustrative drone on a synthetic A–B–C route.",
    },
}

# Native, keyboard-operable locale disclosure; ordinary links preserve CSP.
LANGUAGE_DROPDOWN_CSS = """
.locale-dropdown{position:relative;display:block;flex:none;z-index:5;align-self:center;font-size:.8rem}
.locale-dropdown summary{cursor:pointer;list-style:none;border:1px solid #596567;color:#e4e1d8;padding:8px 11px;min-width:58px;text-align:center;font-weight:750;white-space:nowrap}
.locale-dropdown summary::-webkit-details-marker{display:none}
.locale-dropdown summary::after{content:" ▾";color:#eacb91}
.locale-dropdown summary:focus-visible,.locale-dropdown a:focus-visible{outline:2px solid #f1d4a2;outline-offset:2px}
.locale-options{position:absolute;right:0;top:calc(100% + 4px);min-width:116px;background:#142326;border:1px solid #596567;padding:4px;box-shadow:0 6px 20px #0007}
.locale-options a{display:block;color:#e4e1d8;padding:8px 10px;text-decoration:none;white-space:nowrap}
.locale-options a[aria-current=page]{background:#d9bd8a;color:#151918}
.locale-options a:hover{background:#30464b;color:#fff}
@media(max-width:750px){.r-lang .locale-options{position:static;margin-top:4px}}
"""


def language_dropdown(language: str, suffix: str, css_class: str) -> str:
    """Static selector for the same route in each supported locale."""
    label = "Alege limba" if language == "ro" else "Choose language"
    links = "".join(
        f'<a href="/{lang}{escape(suffix, quote=True)}" hreflang="{lang}" lang="{lang}"'
        f' aria-current="{"page" if lang == language else "false"}">{name}</a>'
        for lang, name in (("ro", "Română"), ("en", "English"))
    )
    return (f'<details class="{css_class} locale-dropdown"><summary aria-label="{label} · {language.upper()}">'
            f'{language.upper()}</summary><div class="locale-options">{links}</div></details>')


def social_metadata(html: str, language: str) -> str:
    if language not in SHARE:
        raise ValueError("unsupported social locale")
    meta = SHARE[language]
    url = ORIGIN + ("/ro/" if language == "ro" else "/en/")
    image_url = ORIGIN + ("/og/ro.png" if language == "ro" else "/og/en.png") + "?v=20261121"
    oglocale = "ro_RO" if language == "ro" else "en_US"
    altlocale = "en_US" if language == "ro" else "ro_RO"
    def attr(s: str) -> str:
        return escape(s, quote=True)
    additions = f'''
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="ro" href="{ORIGIN}/ro/">
  <link rel="alternate" hreflang="en" href="{ORIGIN}/en/">
  <link rel="alternate" hreflang="x-default" href="{ORIGIN}/ro/">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="alternate icon" type="image/x-icon" href="/assets/favicon.ico">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <meta name="description" content="{attr(meta['description'])}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="ROCSI · Telemetry Attestation Gateway">
  <meta property="og:locale" content="{oglocale}">
  <meta property="og:locale:alternate" content="{altlocale}">
  <meta property="og:title" content="{attr(meta['title'])}">
  <meta property="og:description" content="{attr(meta['description'])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image_url}">
  <meta property="og:image:secure_url" content="{image_url}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{attr(meta['image_alt'])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{attr(meta['title'])}">
  <meta name="twitter:description" content="{attr(meta['description'])}">
  <meta name="twitter:image" content="{image_url}">
  <meta name="twitter:image:alt" content="{attr(meta['image_alt'])}">
'''
    # Keep the existing document title translated by romanian_html().
    if html.count("</head>") != 1:
        raise ValueError("head marker invalid")
    html = html.replace("</head>", additions + "</head>", 1)
    switch = language_dropdown(language, "/", "language-switch")
    anchor = '<div class="pill" id="console-mode">'
    if html.count(anchor) != 1:
        raise ValueError("locale switch anchor missing")
    html = html.replace(anchor, switch + "\n    " + anchor, 1)
    css = '''
    .pill{white-space:normal;max-width:100%;overflow-wrap:anywhere}
'''
    if html.count("</style>") != 1:
        raise ValueError("style marker invalid")
    html = html.replace("</style>", css + LANGUAGE_DROPDOWN_CSS + "  </style>", 1)
    return html

def localize_404(language: str) -> str:
    if language == "ro":
        return '''<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>TAG — 404 · Pagina nu a fost găsită</title>
</head>
<body>
  <main>
    <h1>404 · Pagina nu a fost găsită</h1>
    <p>Acest demonstrator static experimental nu are pagini sau servicii live la această adresă.</p>
    <p>EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION</p>
    <p><a href="/ro/">Înapoi la Centrul de comandă și control</a> · <a href="/en/">English</a></p>
  </main>
</body>
</html>
'''
    if language == "en":
        return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>TAG Mission Control — 404 · Not found</title>
</head>
<body>
  <main>
    <h1>404 · Page not found</h1>
    <p>This experimental static showcase has no page or live service at this path.</p>
    <p>EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION</p>
    <p><a href="/en/">Return to Mission Control</a> · <a href="/ro/">Română</a></p>
  </main>
</body>
</html>
'''
    raise ValueError("unsupported locale")
