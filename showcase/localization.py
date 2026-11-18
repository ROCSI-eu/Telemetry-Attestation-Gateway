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
        "Validitatea dovezii nu garantează corectitudinea telemetriei. O observație sintetică nu demonstrează acoperirea unui interval sau a unui zbor, siguranța ori conformitatea contractuală, de plată sau reglementară. Înregistrarea sursă nu a fost validată de clienți sau comercial.",
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
    "A–B–C / 01": "A–B–C / 01",
    "OBS / 02": "OBS / 02",
    "ROUTE / SYN": "TRASEU / SINT",
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
    "A cryptographically valid proof does not establish telemetry truth, trusted sensors or time, whole-flight coverage, safety or legal compliance. This public page shows recorded synthetic outcomes: the browser neither generates nor verifies a proof.":
        "O dovadă criptografică validă nu confirmă corectitudinea telemetriei, încrederea în senzori ori timp, acoperirea întregului zbor, siguranța sau conformitatea legală. Pagina publică afișează rezultate sintetice înregistrate: browserul nu generează și nu verifică dovezi.",
    # TAG-MISSION-CONTROL-EVIDENCE-01: static bilingual evidence checkpoint.
    "SITL and offline proof: distinct evidence":
        "SITL și dovada offline: rezultate distincte",
    "Local ArduPilot Copter 4.7.1 SITL (TAG #86): PASS for isolated, receive-only MAVLink2 intake of two GLOBAL_POSITION_INT observations and TAG normalization. This does not establish telemetry truth.":
        "ArduPilot Copter 4.7.1 SITL local (TAG #86): PASS pentru recepția izolată, exclusiv pasivă, a două observații MAVLink2 GLOBAL_POSITION_INT și normalizarea TAG. Aceasta nu atestă corectitudinea telemetriei.",
    "Independent synthetic ZK checkpoint (14 November 2026): historical Qube evidence records proof generation and offline verifier VALID with the pinned verification key. This proof was separate from the SITL observations.":
        "Checkpoint ZK sintetic independent (14 noiembrie 2026): dovezile istorice Qube consemnează generarea unei dovezi și rezultatul VALID al verificatorului offline cu cheia de verificare fixată. Dovada este separată de observațiile SITL.",
    "Combined SITL → 600 cm/s predicate → ZK: NO-GO / not demonstrated end to end. The speed predicate produced different outcomes across isolated SITL sessions; no SITL-derived ZK proof was generated or verified.":
        "Flux combinat SITL → predicat 600 cm/s → ZK: NO-GO / nedemonstrat integral. Predicatul de viteză a dat rezultate diferite între sesiuni SITL izolate; nicio dovadă ZK derivată din SITL nu a fost generată sau verificată.",
    # TAG-TECH-ANIMATION-01: static labels; the shared script translates controls.
    "01 / NOIR": "01 / NOIR",
    "02 / BARRETENBERG": "02 / BARRETENBERG",
    "03 / OFFLINE": "03 / OFFLINE",
    "CONCEPTUAL ANIMATION / NOT A PROOF RUN": "ANIMAȚIE CONCEPTUALĂ / FĂRĂ GENERAREA DOVEZII",
    "Replay explanation": "Reia explicația",
    "Pause illustration": "Oprește animația",
    "Three illustrative stages, not measured computation or a live verifier.":
        "Trei etape ilustrative, fără calcul măsurat sau verificator live.",
    "Conceptual illustration · no proving or verification in this browser":
        "Ilustrație conceptuală · fără generare sau verificare în browser",
    # Preserve machine-readable evidence codes and experimental markings.
    "EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION":
        "EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION",
    "speed_cm_s ≤ maximum_speed_cm_s": "speed_cm_s ≤ maximum_speed_cm_s",
    "NOT_LOADED": "NEÎNCĂRCAT",
    "NOT_OBSERVED": "NEOBSERVAT",
    "NOT_EVALUATED": "NEEVALUAT",
    "NOT_PERFORMED": "NEEFECTUAT",
    "NOT_MADE": "NEADOPTATĂ",
    "NONE": "NICIUNA",
    "A0_SYNTHETIC": "A0_SYNTHETIC",
}

RO_ARIA = {
    "Scope and limitations of synthetic evidence": "Domeniul și limitele dovezilor sintetice",
    "Independent evidence status": "Starea independentă a dovezilor",
    "Conceptual pipeline": "Flux conceptual",
    "Page sections": "Secțiunile paginii",
    "Conceptual evidence path, not executed in the browser": "Secvență conceptuală a dovezilor, neexecutată în browser",
    "Experimental proof flow, executed offline": "Flux experimental al dovezii, executat offline",
    "Tool documentation and TAG implementation": "Documentația instrumentelor și implementarea TAG",
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
        "description": "Descoperă verificarea condițiilor despre telemetrie cu divulgare minimă. Demonstrație experimentală cu scenarii sintetice și rezultate precalculate.",
        "image_alt": "Centru de comandă și control TAG: dronă ilustrativă pe traseul sintetic A–B–C, fără telemetrie live.",
    },
    "en": {
        "title": "TAG — Privacy-Preserving Telemetry Attestation | ROCSI",
        "description": "Explore telemetry condition verification with limited disclosure. Experimental showcase with synthetic scenarios and precomputed results.",
        "image_alt": "TAG Mission Control: illustrative drone on a synthetic A–B–C route, with no live telemetry.",
    },
}

def social_metadata(html: str, language: str) -> str:
    if language not in SHARE:
        raise ValueError("unsupported social locale")
    meta = SHARE[language]
    url = ORIGIN + ("/ro/" if language == "ro" else "/en/")
    image_url = ORIGIN + ("/og/ro.png" if language == "ro" else "/og/en.png")
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
    switch = (
        '<nav class="language-switch" aria-label="Limbă / Language">'
        f'<a href="/ro/" hreflang="ro" lang="ro" aria-current="{"page" if language=="ro" else "false"}">RO</a>'
        f'<a href="/en/" hreflang="en" lang="en" aria-current="{"page" if language=="en" else "false"}">EN</a>'
        "</nav>"
    )
    anchor = '<div class="pill" id="console-mode">'
    if html.count(anchor) != 1:
        raise ValueError("locale switch anchor missing")
    html = html.replace(anchor, switch + "\n    " + anchor, 1)
    css = '''
    .pill{white-space:normal;max-width:100%;overflow-wrap:anywhere}
    .language-switch{display:inline-flex;gap:5px;border:1px solid #596567;border-radius:0;padding:4px;align-self:start}
    .language-switch a{min-width:36px;text-align:center;text-decoration:none;color:#e4e1d8;font-size:.78rem;font-weight:750;padding:5px 8px;border-radius:0}
    .language-switch a[aria-current="page"]{background:#d9bd8a;color:#151918}
    .language-switch a:focus-visible{outline:3px solid #f1d4a2;outline-offset:2px}
'''
    if html.count("</style>") != 1:
        raise ValueError("style marker invalid")
    html = html.replace("</style>", css + "  </style>", 1)
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
