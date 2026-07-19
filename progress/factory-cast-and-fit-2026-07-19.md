# THE FACTORY AS A COMPANY — CAST & FIT (interaction personification, 2026-07-19)

The companion angle to `factory-spec-personification-2026-07-19.md`. That one was
**individual** — one entity introspecting. This one is **interaction**: cast the
factory as a company with a staff, then run the five CAST & FIT questions across
how they fit together. Method: `innovations/situation-personification/kit/CAST-AND-FIT.md`.
The lens *finds* fit problems; the mechanics remain the judge — every finding below
is checked against the code/docs I've read.

---

## The company

**Sankofa Fiction Works** — a firm that takes a knowledge book at the front door
and ships a serialized teaching novel out the back. Its org chart (Stages 0–7) is
fully drawn. Payroll is another matter.

## The staff (cast + temperament)

**Front office (Stages 0–2) — the intake wing.**
- **The Receptionist** (Stage 0: menu, instancing, budget). *Does not exist.* The
  job description is written; the chair is empty. Right now a human leans through
  the doorway and starts a job by hand.
- **The Classifier** (Stage 1: knowledge-type rubric, accept/queue/defer). Empty
  chair. Supposed to greet a book, name its type, and route it.
- **The Estimator** (Stage 2: requirements + sizing). Empty chair.

**Design wing (Stages 3–4).**
- **The Architect** (Stage 3: genre derivation + mechanism invention). Has a
  complete *manual* (`genre_derivation.md`, 5 worked books) but no code and no
  desk — a brilliant consultant who's written the textbook and never been hired.
  Temperament: taste-bearing, needs the owner's eye.
- **The Draftsman** (Stage 4: generates the whole pack — curriculum, world rules,
  correspondence map, cards). The single most important empty chair. When someone
  says "build the factory," they mostly mean *hire this person.*

**Quality wing (Stage 5) — three inspectors, all empty chairs.**
- **The Fidelity Inspector** (every domain claim → a located quote).
- **The Logic Inspector** (a different model cross-reads for contradictions).
- **The Correspondence Auditor** (IS-not-LIKE; every story element traces to a
  book mechanic).

**Client wing (Stage 6).**
- **The Account Manager** (propose-and-correct, taste flights, decisions ledger,
  consumer map). Exists only as a *human habit*, not code. Temperament: never
  interviews the client; shows samples and reads corrections.

**The floor (Stage 7) — the one wing that's actually staffed and working.**
- **The Orchestrator** — floor manager. Recently *had his job narrowed* (T-011:
  Orchestrator-only, no governance reading) after he was caught improvising from
  company strategy. Now runs the line and nothing else.
- **The Fetcher, the Assembler, the Writer, the two Consistency Checkers, the
  Extractor, the Updater** — the line crew. Real, working.
- **The Structural Gate** — the incorruptible inspector who reads only the
  paperwork (`update_brief.json`), never the prose. Refuses to pass work that
  doesn't tally. Receipt-guarded: nobody downstream moves without his stamp.
- **The Analyst / progress.py** — the company doctor and the front-desk status
  board (built deliberately as the future customer-facing face).
- **The Regression Suite** — a brand-new junior QA who tests the tools on a bench
  instead of in production. Just hired (T-016).
- **The Archivist** (calibration organ — "each book teaches the next"). Has a job
  title and a filing format and *no filing room* — `calibration/` doesn't exist.

---

## The five questions

### Q1 — Does anyone duplicate another's job? (redundancy)

**One job is currently held by four people at four maturity levels:** "make sure a
change re-verifies everything downstream of it." The **field_registry RULE-CHANGE
AUDIT** does it as a manual habit; **LAW 17** does it as a constitutional rule; the
**Regression Suite** does a slice of it automatically; and the **Stage-6 consumer
map** is supposed to do it as running code. That's not bloat *yet* — it's one role
maturing across four layers — but it's a warning: the factory must **collapse these
into one consumer-map organ**, not staff four people who each half-remember the same
duty. *(Mechanics check: all four are real and named in field_registry / CONTRIBUTING
/ intake_factory §6; they genuinely overlap in intent.)*

Smaller overlap: the **hard sourcing rule** (Stage 4, prevention) and the **Fidelity
Inspector** (Stage 5, detection) guard the same property — "every claim traces to a
quote." That's belt-and-suspenders by design (LAW 6), not redundancy. Keep both.

### Q2 — Is any chair empty? (a job nobody is doing)

**The company has an eight-role org chart and roughly one wing staffed.** Receptionist,
Classifier, Estimator, Draftsman, three Inspectors, Account-Manager-as-code, Archivist
— **all empty chairs.** Everyone upstream of the running loop is a job description
pinned to a vacant desk. And one *scheduled* role on the working floor has never once
clocked in: the **anchor_interlude** shift (that chapter type has never fired). *(Mechanics
check: build list = 14+ rows, built = 0; `calibration/` absent; anchor_interlude never
run — all confirmed.)*

### Q3 — Does any new hire need a babysitter? (bad fit / hidden coupling)

**The sharpest finding, and it's the same bad hire made three times.** The Structural
Gate, and the Assembler (twice), were each let keep a **private copy of pack content**
instead of reading the posted rulebook: the Gate hoarded `QUOTA_BY_ARC`; the Assembler
hoarded the anchor's description and the mirror content. A worker who keeps his own copy
of a rule needs a minder to keep that copy in sync with the real one — and **the minder
is the human who runs sync passes** (I *was* that minder twice this week: the arc-2 fix
and today's spec-sync). The lens is emphatic here: *don't institutionalize the
babysitter.* Re-onboard the three workers to **read the count/description/mirror from the
pack** (curriculum, world_rules §5), and the minder's job disappears. This is literally
the §0 chassis/pack leak list, seen as a hiring pattern rather than a debt list — which
is why fixing one value (arc-2 = 2) didn't fix the *fit*: the Gate still hoards. *(Mechanics
check: QUOTA_BY_ARC still a hardcoded dict; assembler.md still carries anchor ×8 and mirror
×7; confirmed this session.)*

Second, smaller: **Stage-4 rule 5** (the "one quantity, one owning table" rule I added
today) is a new policy hire that currently needs the human to enforce it — no fixture
fires when a generated curriculum self-contradicts. Per LAW 16, it should arrive *with*
its own check, or it's a hire who can't work unsupervised.

### Q4 — Is anyone overloaded? (offload the station, don't blame the worker)

**The most overloaded worker in the building is the human.** Because seven chairs are
empty, the owner is *personally* standing in as Receptionist, Classifier, Estimator, all
three Inspectors, and Account Manager — the spec's own phrase was "the automated factory
currently contains an artisan." Every empty chair in Q2 is unpaid overtime the human is
silently working. The offload isn't "work harder" — it's *hire the chairs.*

On the line, the **Assembler** is the overloaded worker: he does mechanical assembly **and**
improvises new characters **and** serves as a filing cabinet for pack content. The specs
already plan his relief — `assembler_template.spec.md` splits off the mechanical half to
code; the leak fixes pull out the filing-cabinet half. Good instinct already on record.
*(Mechanics check: assembler.md spans mechanical steps + generative new-character section +
hardcoded content — confirmed.)*

### Q5 — Who is actually malfunctioning vs. who is getting blamed?

**We just lived the textbook case.** When the arc-2 chapter failed, the **Structural Gate**
threw the alarm and *looked* like the culprit — you nearly signed a waiver to override him.
But the Gate was doing his job perfectly. The real malfunction was two floors away: the
**Curriculum** contradicted itself (two tables, two counts) and three workers hoarded
private copies of the wrong one. Loud failure (the Gate) ≠ root cause (the Curriculum +
the hoarding). Blaming or overriding the Gate would have punished the one honest worker and
left the actual fault in place. *(Mechanics check: DECISION 10 — the gate was correct, the
curriculum self-contradicted; confirmed.)*

The same pattern is written into the constitution as standing wisdom: when prose is bad,
the **Writer** gets blamed, but usually the **brief induced it** — "check the assembled
prompt before blaming the Writer model." The loud worker and the guilty worker are rarely
the same person.

---

## What the interaction angle shows that the individual angle didn't

The individual personification concluded: *design closed, build didn't* — the bottleneck
is construction, not insight. The company view sharpens that into three actionable shapes:

1. **The firm has one working wing and a human covering seven empty chairs.** "Are we ready
   for the factory?" reframes as "which chair do we hire first?" — and the honest answer is
   the human is the overloaded station, so the highest-value hire is whichever chair removes
   the most of *his* silent overtime. (The Draftsman is the biggest, but the intake wing —
   Receptionist/Classifier — is what makes the front door real.)
2. **The three chassis/pack leaks are ONE hiring mistake made three times**, not three
   unrelated debts — and the human is the standing babysitter. The move is to re-onboard
   those workers to read from the pack, which also *retires the minder* (the sync-pass
   burden). Start with the Gate (`QUOTA_BY_ARC`), since he already proved he'll fail honest
   work when his copy drifts.
3. **Protect the honest inspectors from blame.** The Gate took the heat this week for the
   Curriculum's fault. As the factory automates, the loud-failure-≠-root-cause gap widens;
   the Analyst exists precisely to point past the loud worker to the guilty one, and should
   be the first thing consulted on every failure, never the worker who threw the alarm.

*Per the lens: this is a per-decision cast, not a standing character-map to maintain. The
findings located the problems; the mechanics (checked inline) are the judge.*
