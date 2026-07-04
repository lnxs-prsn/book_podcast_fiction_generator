# HUMAN DECISIONS — fiction_loop

Everything in this file needs a call from you before the pipeline can be finished.
None of these are bugs an implementer can just fix — each one is a fork where both
directions are buildable, and picking one changes what the finished book feels like
or how the tool behaves. The bugs that *don't* need your input are already specified
in `specs/pipeline_fixes.spec.md` and can be applied without you.

For each decision: what the issue is, why it exists, why it's yours to make, what it
affects, and the two most likely options. Write your choice on the `DECISION:` line.
Recommendations are marked, but they're defaults, not pressure.

> **STATUS: ALL 8 DECISIONS RESOLVED — 2026-07-02.** Answers recorded on the
> `DECISION:` lines below, each with the implementable translation. The resulting
> work items live in `specs/pipeline_fixes.spec.md` (F5/F7/F8/F13 amended; F14–F17
> added). This file is now a record, not an open questionnaire.

---

## Quick glossary (30 seconds, then the rest of the file reads without detective work)

| Term | Meaning |
|---|---|
| **Operation** | One Pólya mental move (e.g. "working backwards", "what is missing"). There are 24. Each chapter formally teaches one. |
| **Touch** | One teaching pass on an operation. The curriculum re-teaches each operation several times, spaced apart — touch 1 (character suffers its absence), 1N (it gets named), 2 (character applies it unprompted), 3 (narrator uses it casually), 4 (combined with other operations). |
| **Anchor / mystery person** | The recurring observer character who watches gates and writes a notebook. Threads the book-length mystery. |
| **Gate** | The story's problem-container. A gate IS a problem (unknown, data, condition). |
| **Echo** | The ordinary-life scene where the same problem structure appears outside the gate. Never explained to the reader. |
| **Compression** | When an operation is "owned" the state files stop tracking it in detail, to keep the AI's context small over a long book. Currently triggers at touch 3. |
| **Pointer** | `next_chapter_pointer` in `master_state.json` — the machine-readable plan for the next chapter. The whole loop steers by it. |

---

## DECISION 1 — How do the later touches (3 and 4) happen?

**The issue.** The curriculum's spaced-repetition map schedules every operation for
touches 3 and 4 in later arcs. But the scheduling logic (Extractor's DECISION LOGIC)
can only ever schedule touch 1 and touch 2. Touches 3–4 are currently unreachable —
and since compression triggers at touch 3, compression never happens either, so the
state files grow forever.

**Analogy.** Language-learning flashcards. Touches 1–2 are dedicated study sessions
for a word. The question is what a "third review" means: does the word get **its own
study session again** (a chapter formally scheduled to feature it), or does it just
**start appearing naturally in the articles you read** (the narrator uses it casually
inside chapters that are formally about something else)?

**Why your call.** Both readings exist in your own design docs. The repetition map
reads like a schedule (dedicated). The style contract describes touch 3 as "narrator
uses naturally — part of the world's description" (ambient). An implementer can build
either; only you know which teaching rhythm you intended.

**Impact.** Dedicated = more chapters per operation, longer book, very explicit
reinforcement. Ambient = leaner book, but reinforcement quality depends on the Writer
doing it un-prompted, and compression must move to touch 2.

**Option A — Dedicated (schedule touches 3–4 as real chapters).**
Scheduling logic extends to `touch_due = current_touch + 1` up to 4. Compression stays
at touch 3. Deterministic, verifiable, matches the map literally. Cost: with 24
operations × up to 4 touches, the book plan implies a lot of chapters.

**Option B — Ambient (touches 3–4 happen inside other chapters).**
Scheduling stops at touch 2. The map's 3/4 columns become writer guidance: the
Assembler adds owned operations to the "use naturally, no re-explanation" list and the
Extractor records sightings when the prose actually uses them. Compression moves to
touch 2. Cost: reinforcement is softer and less guaranteed.

**Recommended:** B — it matches the style contract's description of what touch 3 *is*,
and it keeps the book from ballooning. A is safer pedagogically if you don't trust the
Writer to weave operations in unprompted.

**DECISION: HYBRID — chronological mastery ladder with dedicated reinforcement.**
The process is chronological and cumulative: step N+1 is not introduced until step N
is "clear" (experienced → named → applied once). Nothing is ever dropped — once clear,
an operation joins a cumulative "apply naturally" list included in every later chapter.
AND touches 3/4 still get dedicated scheduled chapters (owner chose this explicitly),
driven by the spaced-repetition map: curriculum §7 becomes the machine-readable
schedule (per operation, per arc, target touch), and the scheduler picks the operation
with the largest deficit between target and current touch, subject to the chronological
gate. Ambient use between dedicated touches is also recorded by the Extractor.
Compression stays at touch 3, after its dedicated chapter.

**REFINEMENT (owner, 2026-07-02) — co-hosted touches, to shrink the book without
dropping a single repetition:** scheduled touches remain map-driven and verified, but
a reinforcement touch no longer requires its own chapter. Up to **2 piggybacked
touch-events** may ride along in a chapter whose formal `operation_due` is something
else, carried by a character who already owns the operation — a returning solver, or
a **newcomer with off-page gate experience** (world-coherent: gates open globally;
thousands of solvers exist off-page; this also satisfies the ≥1-improvised-newcomer
rule while doing reinforcement work). The elegant form: the veteran first solver
applies owned operation Y competently (Y's scheduled touch, recorded) and then fails
the chapter's NEW operation X — which is exactly what the productive-failure structure
needs from its first solver anyway. No rule is broken: V2 limits *new* operations
only; owned operations are applied without re-explanation (the approved
character-action channel); "no technique succeeds first time" protects the reader's
first exposure, and piggybacks are by definition post-first-exposure. Guardrails: max
2 piggybacks per chapter (anti-parade), and the Extractor must verify each scheduled
piggyback actually appeared in prose before its touch is counted. Effect: ~96
touch-events pack into roughly 35–45 teaching chapters instead of 90+.

---

## DECISION 2 — What does Chapter 1 actually teach, and does the mystery person appear in it?

**The issue.** Two of your planning documents disagree about the very first chapter.
`living_document.md`'s NEXT CHAPTER TARGET plans four operations touched in chapter 1
(three as unnamed experience, one — "What is missing" — getting its name) **and** a
brief mystery-person appearance. But `master_state.json`'s pointer says one operation,
**no** mystery person, and consistency check V2 flags any chapter introducing more
than one new operation.

**Analogy.** Two departments printed different itineraries for the same trip, and the
tour guide (the Orchestrator) will follow whichever it reads first. Until you pick one
itinerary, chapter 1 is undefined behaviour.

**Why your call.** This is pure pedagogy. Pólya's phase-1 moves (name the unknown,
what's missing, separate the condition, look at the unknown) genuinely arrive as one
gestalt in the source — a single "understand before acting" cluster. Whether to honor
that cluster in one chapter or slice it into four chapters is a teaching-design taste
call. The mystery-person question is a pacing/tone call about page one of your book.

**Impact.** Chapter 1 sets the reader's contract for the whole book: how much is
taught per chapter, and whether the macro-mystery hook lands on page one or later.

**Option A — Cluster chapter (living doc wins).**
Chapter 1 formally teaches ONE operation ("What is missing" — it gets the 1N name at
the end), while the other three appear as unnamed background experience and are NOT
counted as touches in state. Mystery person appears briefly at the gate exterior.
Requires: rewording check V2 to count `operation_due` (the formal one), not every
operation brushed; pointer set to `anchor_appears: true`.

**Option B — Strict one-op chapters (state machine wins).**
Chapter 1 teaches only "What is missing"; the other three operations wait for their
own chapters. Mystery person held back until her scheduled cadence (Decision 3).
Requires: rewriting the living doc's NEXT CHAPTER TARGET. Cleaner bookkeeping, slower
arc 1, and the first gate scene may feel thin — a solver who never names the unknown
or separates the condition is hard to write believably.

**Recommended:** A — the productive-failure chapter structure (multiple solvers,
multiple wrong approaches) naturally exercises several phase-1 moves anyway; pretending
they're absent would fight the prose. And the mystery person on page one is your
strongest serialization hook.

**DECISION: Option A (cluster chapter) — resolved via the owner's directives, not a
direct pick.** The owner's rule: pacing directives come from Pólya's own teaching
guidance, and Pólya presents the understanding-phase questions as one inseparable
first move → chapter 1 shows the phase-1 moves as unnamed experience and formally
names only "What is missing." The mystery person appears (required by Decision 3:
she appears in every gate chapter). Concretely: `living_document.md`'s NEXT CHAPTER
TARGET stands as written; `master_state.json`'s pointer is corrected to match
(`operation_due: op_what_is_missing`, `touch_due: 1`, `anchor_appears: true`);
check V2 is reworded to count the formal `operation_due` only, not every operation
brushed in the prose. Owner's clarification also noted: master_state is a tracker
whose value begins after chapter 1 — but its `next_chapter_pointer` is the one field
that must be correct *before* chapter 1, because the Orchestrator steers by it.

---

## DECISION 3 — Mystery person cadence: how often, and how forced?

**The issue.** The design says the anchor should appear roughly every ≤5 chapters
(check C3 polices it), but the scheduling logic can never actually schedule her —
teaching chapters always win priority, so she'd never appear at all. The fix requires
picking actual numbers.

**Analogy.** A drumbeat under a song. Right now the drummer is in the building but
never gets a cue. You're choosing the tempo: how many bars between hits (brief
appearances inside normal chapters) and when the song stops for a drum solo (a
dedicated interlude chapter).

**Why your call.** Reader-pacing taste. Too frequent = the mystery feels nagging; too
rare = readers forget the thread exists between appearances (the curriculum itself
warns that 8+ chapter gaps risk reader forgetting).

**Impact.** Controls the rhythm of the book-length mystery and how much space
interludes take from teaching chapters.

**Option A — Tight weave: brief appearance every ~3 chapters, forced interlude at 5.**
The anchor is a constant background presence; interludes are rare because brief
appearances keep resetting the counter. Matches the current C3 check as written.

**Option B — Loose weave: brief appearance every ~5, forced interlude at 8.**
More subtle, more literary; the notebook entries feel like events when they come.
Requires relaxing C3's numbers to match.

**Recommended:** A for arcs 1–2 (readers need the pattern established), with the
option to loosen later — the numbers live in one place after the fix, so changing
tempo mid-book is a one-line edit.

**DECISION: Every gate chapter, minimal presence, varied form — and the travel
impossibility is a DELIBERATE CLUE.** Context from the owner: this is a multi-book
series; book 1 teaches the Pólya method; the mystery person is the bridge to book 2
(portals connecting to other worlds), so she must stay mysterious but present.
Resolution: she appears in every gate chapter, briefly, in relation to the gate — but
the *form* varies so it never becomes formula (seen directly / already gone, traces
left / mentioned by a bystander / a notebook page found). Because gates open in
different cities, her omnipresence is physically impossible for a normal person —
this impossibility is planted evidence about what she is, must be encoded in
`hidden_coherence` when it is authored, and must never be explained in book 1.
Consequence: check C3 inverts — it now flags a gate chapter where she is *absent*,
not one where she appears too often. Anchor interludes remain available as a chapter
type but are rare in book 1.

---

## DECISION 4 — Ordinary-life echo contexts: free text or a fixed list?

**The issue.** The system must avoid reusing the same echo context for the same
operation (two "stuck work project" echoes for the same operation = repetitive book).
But contexts are recorded as free-form phrases ("engineering project handover"), and
the dedupe check compares them by exact string match. "Project handover at work" and
"engineering handover" would be treated as different — the check silently misses
repeats.

**Analogy.** Labeling leftovers in a shared fridge with free-form sticky notes.
"Tuesday's stew" and "beef stew from Tue" are the same stew, but nobody comparing
labels can tell. Fixed containers with printed labels solve it — at the cost of only
having the containers you printed.

**Why your call.** Trading variety for reliability is a product/creative call. Also,
the fixed list *is* creative content — someone has to decide the canonical set of
life domains your book draws echoes from.

**Impact.** Repetitiveness of echo scenes across an 80+ chapter book — the exact
"reader feels the formula" failure this project is trying to avoid.

**Option A — Fixed pick-list.**
Define an enum of echo domains (seedable from correspondence_map §5's existing domain
column: workplace, family/domestic, civic/institutional, teaching/parenting,
negotiation, argument/debate, …). Extractor must classify each echo into one. Dedupe
becomes exact and reliable. Variety bounded by the list — but the list can grow
deliberately.

**Option B — Keep free text, accept fuzzy repeats.**
No schema change. The exact-match check stays as a weak tripwire, and the small
LLM checker pass gets one extra question ("is this context substantially the same as
any already used?"). Cheaper now; quietly leaky forever.

**Recommended:** A. The domain column already exists in correspondence_map §5, so the
list is nearly free — and this failure mode (formula visible to the reader) is the
project's stated enemy.

**DECISION: Option A — fixed pick-list.** Plus a new requirement the owner stated
emphatically: the gates' impact on ordinary life must be *perceivable to the reader*
across the book — when a past solver returns, their life has visibly progressed
(promotion, grades, resolved conflict) because the thinking process transferred.
Concretely: (a) echo contexts become a canonical enum seeded from correspondence_map
§5's domain column, and the Extractor classifies each echo into one — duplicate
detection becomes exact; (b) character cards gain a life-progression rule:
`ordinary_life_state` must move forward between appearances, and return-chapter
prompts must include the character's prior state so the Writer shows the progress.

---

## DECISION 5 — Operation prerequisites (check CR3): author the dependency graph or drop the check?

**The issue.** Check CR3 is supposed to block teaching a harder operation before its
prerequisite is learned. But no `prerequisite` field exists anywhere — the check
polices a rule nobody has written down. It currently returns an explicit SKIP forever.

**Analogy.** A university registrar programmed to block students from enrolling in
Calculus II before Calculus I — pointed at a course catalog where no course lists any
prerequisites. The registrar runs every day and blocks nothing.

**Why your call.** Deciding which of the 24 operations truly requires which others is
pedagogy — it's a claim about how Pólya's method is learned, and per your own sourcing
rule it should be authored against the source text, not guessed.

**Impact.** Safety net quality. Note: arcs already gate introduction order (an
operation can only be introduced in its scheduled arc), so most of the ordering
protection exists regardless. CR3 adds finer-grained protection (e.g. within-arc
ordering, touch-2 timing).

**Option A — Author the graph.**
Add `prerequisite` to the concept card schema, author it for all 24 operations from
the source text, CR3 becomes real. One-time content effort; permanent guardrail.

**Option B — Retire CR3, rely on arc ordering.**
Delete the check (explicitly, in the spec — not silently). The arc schedule remains
the only ordering guarantee, which is already fairly strong. Zero effort; slightly
weaker net.

**Recommended:** B now, A later if the loop ever mis-orders in practice. Don't author
24 pedagogical dependencies up front to feed a check that may never fire.

**DECISION: Option A — author the prerequisite graph.** Made cheap by Decision 1: since
the process is chronological, most operations' prerequisite IS the preceding step in
the chain. Add `prerequisite` to the concept card schema; author it for all 24
operations against the source text (per the sourcing rule in specs/README.md); CR3
becomes a real check.

---

## DECISION 6 — Multi-solver gates: does the state track everyone who enters, or only the focal character?

**The issue.** Your own chapter structure (world_rules §6) says every gate chapter
shows **multiple solvers** — first solver fails, second solver fails differently, the
right solver closes it. But the state model records exactly ONE character per gate
(`characters_entered` is hardcoded single-element, and only the focal character gets a
card). The failed solvers exist in prose and then vanish from the world's memory.
There's also a recorded-but-undecided orphan: `correct_approach` is written to every
event card and read by nothing.

**Analogy.** A guestbook that only lets the last guest sign. Fine if the other guests
are extras who never return — a continuity time bomb if a reader-favorite failed
solver from chapter 3 should be able to reappear in chapter 30.

**Why your call.** Story scope. Whether failed solvers are disposable extras or a
reusable cast is a decision about what kind of book this is — the tooling just follows.

**Impact.** Continuity depth and state-file size. Tracking everyone = richer returning
cast, more cards, more context per chapter. Tracking one = lean, but failed solvers
can never coherently return.

**Option A — Focal-only (formalize the current behaviour).**
Failed solvers are unnamed or lightly named extras; only the focal solver gets a card.
Document it as a rule so the Writer keeps extras deliberately thin. Also: drop the
unread `correct_approach` field. Lean and honest.

**Option B — Track all named entrants.**
`characters_entered` becomes a real list; any named solver gets at least a stub card;
the return-to-character logic may pick a past *failed* solver — which is a lovely
teaching beat (their touch 1 was suffering the absence; their return chapter is
touch 2). Keep `correct_approach` and wire it into return-chapter continuity.

**Recommended:** B, but scoped: stub cards only for solvers the prose *names*. The
"failed solver returns and finally gets it" arc is one of the strongest teaching
patterns available to this design, and Option A permanently forfeits it.

**DECISION: Option B — track all named entrants.**
**ADDENDUM (owner, 2026-07-04):** returning solvers are NOT focal by default — their
later touches usually ride as side-role secondary carriers; focal return is reserved
for name-due moments, fallback, or deliberate story fit, and never the same character
focally twice in a row. Rationale: the process is the main character; a recurring
focal human is a trope that distracts from it. (Implemented in extractor.md STEP B +
assembler cast rules.) With the owner's correction
formalized: every *gate* has a focal solver, but the *story* has no single protagonist
— it is an ensemble book, and this is now a stated design rule, not an accident.
`characters_entered` becomes a real list; any solver the prose names gets at least a
stub card; the return logic may select a past *failed* solver (their touch 1 was
suffering the operation's absence; their return is touch 2). `correct_approach` is
kept and wired into return-chapter continuity. Consequence accepted: the cast grows
~2–3 named people per chapter, so the dormancy/compression rules are load-bearing.

---

## DECISION 7 — New characters: LLM improvises them, or drawn from a curated pool?

**The issue.** Every `new_focal_character` chapter needs a fresh person (name,
occupation, city, situation). Today the Assembler invents them freely each time. Past
drift already forced a guardrail note ("African names only, no Arabic names") into the
living document — evidence that free invention wanders. Over 50+ characters, free
invention also risks near-duplicate names and occupation clustering.

**Analogy.** A casting director who improvises a new actor description every scene vs.
one who works from a pre-approved casting book. The improviser is more surprising —
and more likely to cast two near-identical leads without noticing.

**Why your call.** Variety-vs-control creative taste, plus cultural authenticity: a
curated name/city/occupation pool is something you can review once for authenticity;
per-chapter LLM invention you cannot.

**Impact.** Cast quality and authenticity across the whole book; whether naming rules
live as fragile prompt notes or as reviewed data.

**Option A — Curated pools + random draw (code, no LLM).**
You (or an assisted one-time pass you review) author pools: names by
region/gender, cities, ordinary occupations. Generator draws without replacement.
Deterministic, reviewable, duplicate-proof. Less serendipity; situation/backstory can
still be LLM-written around the drawn identity.

**Option B — LLM invention with a hard exclusion ledger.**
Keep free generation, but feed the Assembler the full used-name list plus the naming
rules from a dedicated file (not the LLM-rewritten living doc, where the rule can be
accidentally dropped). More variety; authenticity still per-chapter luck.

**Recommended:** A for identity (name/city/occupation), LLM for everything alive about
them (situation, voice, trouble). Identity is the part where drift is embarrassing and
review is cheap.

**DECISION: BOTH — and the "curated pool" is the accumulated cast itself.** Early
arcs: everyone is LLM-improvised. Later arcs: returning solvers and failers (from the
population built up under Decision 6) are mixed in — with a hard rule: **every gate
chapter contains at least one fully improvised newcomer**, so the world keeps
producing strangers and never feels like a closed cast. Safety net kept from the
original issue: naming rules move out of the fragile LLM-rewritten living document
into a stable `core/character_naming.md` (rules + used-name ledger) that the Assembler
reads every chapter — this is the durable fix for the drift that once forced the
"no Arabic names" note.

---

## DECISION 8 — Run the loop agent-driven first, or implement the deterministic code first?

**The issue.** The `specs/` directory defines which pipeline parts should become plain
Python (state math, checks, prompt assembly) instead of LLM agents interpreting
markdown. None of it is implemented. You can fix the specs and run the loop
agent-driven now, or build the code layer first.

**Analogy.** Flying the route manually with a good checklist vs. installing the
autopilot before the first flight. Manual gets you airborne this week and tells you
whether the destination is even right; autopilot makes every later flight cheaper and
prevents fat-finger errors — but delays finding out whether the book is any good.

**Why your call.** Resource allocation. Both paths converge (the code was always the
plan); the question is what you want first — evidence about the *fiction*, or
reliability of the *machine*.

**Impact.** Time-to-first-chapter vs. per-chapter cost and state-corruption risk.
Agent-driven runs burn tokens on mechanical steps and occasionally mis-add a number;
code doesn't. But no amount of code tells you whether chapter 1 lands.

**Option A — Agent-driven first.**
Apply the spec fixes to the markdown agents, initialize state, generate chapters 1–3,
judge the prose against your 1.docx bar. Implement the code layer only after the
creative design survives contact with reality. Accept some manual state-checking
after each chapter.

**Option B — Code first.**
Implement `deterministic_pipeline.spec.md` + the assembler template as Python, then
generate. First chapter arrives later, but every chapter after is cheaper and the
state math is trustworthy from day one.

**Recommended:** A. The riskiest unknown in this project is not the plumbing — it's
whether process fiction of this specific design reads well. Find that out on three
chapters before investing in automation. (Chapters written during the manual phase
remain valid; state files carry over.)

**DECISION: BOTH — no ordering preference.** The owner sees no decision here since AI
implements either way. Execution order (an implementation detail, not a decision):
agent specs are fixed first, then the deterministic code layer is implemented from
those fixed specs — the code must implement what the corrected specs say, so this
order avoids implementing the wrong thing twice.

---

## DECISION 9 — Book length: compression levers (added 2026-07-02)

**The issue.** Even with co-hosted touches (D1 refinement), the map implied ~35–45
teaching chapters. Owner target: **20–30 chapters total**, keeping every rule.

**DECISION: ALL FOUR LEVERS ADOPTED.**

1. **Echo scenes carry touches.** The mandatory ordinary-life echo may carry one
   scheduled reinforcement touch for a *different* cleared operation — already
   sanctioned by the style contract's own touch-2 definition ("a gate of different
   type or ordinary life problem"), and it doubles as the D4 life-progression proof.
   One scene, three jobs: echo, progression, touch.
2. **Difficulty-scaled touch counts.** Per Pólya's own guidance (repetition need
   scales with difficulty) and the curriculum's difficulty scale ("easy ops are
   half-known from daily life"): easy ops (difficulty 2–3) target 2 touches, medium
   (4–5) target 3, hard (6–8) keep 4. Touch-events drop ~96 → ~75. Applied as edits
   to the map's columns when the registry is authored (F2) — the owner's earlier
   note stands: the lever is the map's columns, not the machinery.
3. **Phase clusters.** Generalizes the chapter-1 gestalt ruling: when one solving
   sequence genuinely chains sibling operations in process order ("look at the
   unknown → related problem → use its method"), the Extractor may verify one touch
   per sibling exercised. One scene, several touches — legitimate because the
   process itself chains them, never a parade.
4. **Structural chapters absorb stragglers.** Arc transitions and interludes may
   carry *ambient reinforcement only* (never new operations); the mystery person's
   notebook entries already do this for free. This amends `chapter_type_contract.md`:
   `process_updates` for those types changes from strictly null to
   reinforcement-only-optional.

**Guardrails (anti-formula, per D4's "at all cost"):** hard cap of 4 verified
touch-events per chapter (1 formal + up to 2 in-gate piggybacks + 1 echo-carried);
every scheduled touch must be verified in prose by the Extractor or it returns to the
deficit pool — never forced, never silently counted. If touches can't be placed
naturally, the book runs slightly longer rather than reading like a checklist.

**Resulting projection:** ~75 touch-events ÷ ~4 per chapter ≈ 19–22 teaching chapters
+ ~4–6 structural chapters → **~23–28 total.**

---

## NOT DECISIONS — content only you can provide

These aren't forks with options; they're blanks only a human should fill (per the
sourcing rule in `specs/README.md`, checked against the Pólya text, and reviewed by
you because they're the pedagogical core):

1. **Story identity** — `story_title`, `genre`, `source_material` in
   `master_state.json`. Two-minute job, currently `"[ ]"`.
2. **The mystery person's secret** — `hidden_coherence` in `mystery_anchor.json`
   (who she really is, what she knows, what her notebook is building toward). The
   whole macro-mystery steers by this and it is currently `"[ ]"`. Never enters any
   prompt — but the planning layer can't plant coherent evidence without it.
3. **Physical anchors, per operation** — the bodily gesture that embodies each of the
   24 operations (the sitting down, hands flat on the desk, …). Partial source
   already exists in style_contract §1 Rule 2. Needs authoring + your review.
4. **The two missing echo rows + label alignment** in correspondence_map §5
   (decision already recorded in field_registry.md: split the merged rows; needs the
   source text open while writing).
5. **Canonical problem structures** — per-operation unknown/data/condition templates
   (proposed as `canonical_problem_structure` in assembler_template.spec.md Fix 2).
   Can be drafted for you, needs your review before it goes live.

---

*Once the DECISION lines are filled in, everything above collapses into ordinary
implementation work — no further judgment calls are hiding behind any of them.*
