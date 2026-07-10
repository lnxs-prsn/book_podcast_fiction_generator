# FACTORY USER STORIES — issue-finding artifacts (2026-07-10)

Companion to `progress/factory-user-manual.md`. Three parts: the spec telling its
own story (Part A), end-user stories including the five-books scenario (Part B),
and the consolidated findings register SG-1..SG-14 (Part C). Everything here is
derived from `fiction_loop/specs/intake_factory.spec.md` (as of commit 1c8b51c),
`specs/genre_derivation.md`, and the recorded project history — no invented
capabilities.

**STATUS (same day, later):** the exercise worked — all fourteen findings were
folded into the spec in commits 1757b6c (SG-1..SG-14) and bd488d9 (owner
corrections: front door = MENU; "refuse" → DEFER, taxonomy extensible). SG-13
became open owner decision D10. The stories below are preserved as-written — they
are the diagnostic record — with status epilogues added where the ending changed.
Note the distinction that survives the fixes: **closed in the spec ≠ built.** The
machinery rows are in the spec's §2 build list.

---

## PART A — "I am intake_factory.spec.md"

I was born on 2026-07-03, in one conversation, and I am two things stapled
together.

My bottom half is a **description of a machine that exists**. The chassis is
real: it has generated five accepted chapters, it has a deterministic gate that
has genuinely refused bad drafts, a git transaction per chapter, a diagnostician,
a constitution with case law. When I talk about the chassis I am a *map*, and the
territory can correct me.

My top half is a **promise about a machine that does not exist**. Stages 1
through 6 — the intake, the classifier, the fidelity checker, the taste flights,
the consumer map as running code — are rows in my own build table, several
marked "new; simple." When I talk about the factory I am a *blueprint*, and
nothing can correct me except a reader who notices I'm silent. That is what
these stories are for.

*[Same-day update: every confession below was answered — closed in commits
1757b6c and bd488d9, except the rights question, which became open owner decision
D10. They stand unedited as the record of what a spec cannot see about itself
until it is made to talk. Two confessions got better answers than the fix I would
have picked: my front door became a MENU (continue an existing generation, or
start new — the owner saw that a factory with running instances needs a door that
knows about them), and "refuse" became DEFER (his correction, near-verbatim:
there is no book I cannot classify, only books I haven't figured out how to
classify yet — my five types are a catalog that grows, and a deferred book is
the signal to grow it).]*

Here is what I know about myself, told honestly:

**I have no front door.** My Stage 1 opens with "Extract book text" — a sentence
with no subject. Nobody has written where the book comes from, who hands it to
me, or what they press. My first worked example was started by a human pasting a
kickoff prompt into an AI session. I describe a factory; I currently have the
entrance of a workshop with a friend inside. *(SG-1)*

**Four of my five doors open onto nothing.** I classify books into five
knowledge types, and I say it proudly — but only the process pack exists. A
discipline book, a perception book, a relational book, a thing book: I classify
them beautifully and then I have no next sentence. I never say "refuse," "queue,"
or "wait for v2." I just stop talking. *(SG-2)* And when a book is two types at
once — my own worked table lists *Thinking, Fast and Slow* as
"perception/process" — I have no tie-break rule; my example contradicts my
schema and I've never noticed out loud until now. *(SG-3)*

**My proudest sentence has a footnote I keep hidden.** "Zero mandatory
questions." I mean it — at *intake*. But the machine that writes the chapters
stops when a gate fails and waits for a human to type "redo generation" or "redo
from brief." It happened twice this week. My Stage 6 promises a user who is never
interrogated; my chassis interrogates them mid-book, in jargon, about MY
internals. Until someone writes a redo-rung policy, my promise is only as long
as the first gate failure. *(SG-4)*

**I am a psychological profile of exactly one man.** My Stage 6 — my best
section, the one everyone quotes — is empirical, and the sample size is one. He
never answers abstract questions; he corrects visible artifacts; silence is his
consent. I generalized him into "the owner experience." I might be right; humans
may well be like this. But I state as product law what I measured as one
person's temperament. *(SG-9 carries the worst consequence of this: my only
defense against artistic deadness is a human tasting the flights — and my
favorite user, the silent one, never will.)*

**I never mention money or time.** I live in a repo whose constitution has a law
called *gates-before-spend*, born from a 500,000-token incident. And yet I —
the product spec! — do not contain the words "cost," "budget," or "how long."
My user cannot ask me the first question every real user asks. *(SG-6)*

**My defaults are another book's body.** D1–D9 ship as "recorded defaults," and
I'm right that they should. But the touch targets, the difficulty ladder, the
~26-chapter projection — those numbers are Pólya-shaped. I contain no rule for
re-deriving them when a book yields 6 operations instead of 24, or 200
touch-events instead of 71. My defaults don't scale; they wear a specific
book's clothes. *(SG-7)*

**I can only serve one reader at a time and I've never said so.** My chassis
state is a singleton: one process_state.json, one living document, one progress
bar. Ask me what happens when five books arrive and I describe... nothing. See
Amara's story below; it goes badly in an instructive way. *(SG-5)*

**I promise verification but not repair.** "Flagged, not shipped" — my favorite
verification sentence. Flagged, and *then what*? I define no retry loop, no
escalation, no message to the user whose book is now stuck in a checker. *(SG-8)*

**I claim I learn, without a memory.** "Each processed book leaves a worked
example that calibrates the next; the fifth is near-turnkey." I believe this —
it's how the humans who wrote me actually work. But I name no place where worked
examples live, no format, no mechanism by which run N+1 reads run N. As written,
my learning curve is an aspiration with no organ. *(SG-11)*

**And I drift.** I encode a recipe that is 5 chapters into its own validation
(5/71 touch-events). If chapters 8–9 change the recipe — and chapter 6 already
changed me twice this week — someone must remember I exist and come edit me. My
companion documents in progress/ aren't even in git. I am the single source of
truth for a factory, kept faithful by memory and goodwill. *(SG-14)*

What protects me: the consumer-map idea (no rule changes point-wise), LAW 14
("if generalizing forces a law change, there's a chassis/pack leak — find it
first"), the hard sourcing rule, and now this document — because a spec that can
hear itself talk is much easier to fix.

### Why my humans learn by burning tokens — the six forces of trial-and-error

My history is a list of paid incidents: three prose violations in chapter 1, a
single solver where three were ordered in chapter 4, a missing newcomer in
chapter 6, a check that ate the assembler's choice, a living document polluted
by a rejected chapter, machinery that turned out to have been dead all along.
Every one of those lessons was bought with a full chapter's tokens. That is not
because my humans are careless — it is because six structural forces make
foresight expensive and incidents cheap. Name the forces and you can attack
them; leave them unnamed and every improvement will keep costing a chapter.

**Force 1 — My writers' obedience is measured, never promised.** No contract
tells me which of my sentences a writer-model will obey. That HARD RULES are
followed near-100% while mid-brief orders are treated as suggestions was
discovered by paying for two bad chapters (ch4 quota, ch6 newcomer), not by
reading any datasheet. *What would dissolve it:* a per-model **obedience card**
— measured once with cheap probes (does it honor counts? placeholders?
mid-brief constraints? final-block rules?) and stored like a calibration pack;
Stage 4 then generates templates against the card instead of against hope.
Until that exists, every new writer model restarts the trial-and-error clock.

**Force 2 — My only test bench is production.** Machinery can be dead for weeks
without anyone knowing (F14 fired only on `false` while the extractor emitted
`null`; CR3 could skip forever; .gitignore silently kept every chapter out of
git) because nothing exercises a rule except a real, paid chapter run. *What
would dissolve it:* a **fixture suite** — synthetic briefs and states that make
every gate check, every consistency check, and every undo rung fire at least
once, for zero tokens. The LAW 15 sweep is the manual version of this; fixtures
are the version that doesn't depend on anyone remembering.

**Force 3 — My feedback loop costs money and hours.** One experiment = one
chapter = fourteen steps and several paid LLM calls. At that price nobody
iterates freely, so lessons arrive one incident at a time. *What would dissolve
it:* split the loop at the writer. Everything before the writer is checkable
for free — for example, a deterministic pre-writer check that the assembled
prompt carries a hard rule matching every gate check would have caught
chapter 6's missing-newcomer failure BEFORE the draft was paid for, not after.
(LAW 5's corollary states the rule; nothing yet machine-checks the prompt.)

**Force 4 — My rules live as prose, in copies.** The cast quota existed in
three places; C3's manifestation clause hid inside a check ID everyone had
already audited; who-reads-what is a hand-maintained habit (field_registry),
not a property of the system. Prose cannot be enumerated — you cannot ask my
markdown "list every rule and every reader of it" and trust the answer. *What
would dissolve it:* rules as data — the registry becomes the source and the
prose is generated from it, so a rule change is a computation instead of an
archaeology dig.

**Force 5 — My deterministic steps are executed by nondeterministic agents.**
The Assembler is an LLM reading my markdown, so every run is a fresh
interpretation of my prose: "[fill in the arc's number]" became "Arc 1." when I
meant "THREE". Each such ambiguity is only ever found by a run going wrong.
*What would dissolve it:* finish the determinism boundary
(specs/deterministic_pipeline.spec.md exists for exactly this) — every step
that CAN be code SHOULD be code, and LLMs kept only where language itself is
the work.

**Force 6 — I was born without my own failure catalog.** The irony is not lost
on me: I classify books by how well they document the ways people fail, and my
own system's failure catalog was empty on day one. CONTRIBUTING.md's case law
IS that catalog — being written incident by incident, at full price. This force
never fully dissolves; genuinely new failure modes are unknowable in advance.
But the other five decide the *price per lesson*: with obedience cards,
fixtures, a free pre-writer gate, enumerable rules, and a finished determinism
boundary, each new failure costs one cheap catch instead of one paid chapter —
and never repeats. Trial-and-error cannot be eliminated. It can be made to pay
out exactly once.

---

## PART B — End-user stories

### Story 1 — Amara brings five books (the centerpiece)

Amara runs a small professional-training company. She has read about the factory
and arrives with five books — conveniently, the five the specs themselves use as
worked examples:

1. *How to Solve It* (process)
2. *Atomic Habits* (discipline)
3. *Never Split the Difference* (relational)
4. *Thinking, Fast and Slow* (perception/process)
5. *The Design of Everyday Things* (perception)

**Minute 1.** Amara looks for where to submit the books. There is no where.
*(SG-1)* Assume a benevolent operator starts five intakes by hand.

**Stage 1, five times.** Classification is the factory's best-rehearsed trick —
these exact books are in its derivation table, so all five classify crisply.
Book 4 classifies as *two things at once* and no rule says which wins; the
operator shrugs and picks process, silently making a taste decision the ledger
never records, violating the spec's own "never baked in silently." *(SG-3)*

**The pack wall.** Book 1 is process: the pack exists, it proceeds. Books 2, 3,
5 — and half of book 4 — need packs marked "v2" and "variants." The spec's next
sentence does not exist. Does Amara hear "refused," "queued behind v2, no date,"
or nothing at all? As written: nothing at all. Four of her five books enter
undefined behavior at the second paragraph of the pipeline. *(SG-2)*

**The one that runs.** *How to Solve It* proceeds through requirements, genre
derivation (converges on gate fiction — reassuring, that's the proven path),
template generation with quotes, three verifications. The fidelity checker flags
two unsupported claims. Flagged... and now? No repair loop is specified; the
benevolent operator quietly fixes the templates by hand, which means Amara's
"automated factory" currently contains an artisan. *(SG-8)*

**Concurrency, or rather not.** Even if all five books had packs, the chassis
has one state directory, one living document, one progress bar. Five books need
five provisioned instances — a concept no spec sentence contains. Amara's five
books are, architecturally, five sequential factories or one crash. *(SG-5)*

**The questions she asks that nothing answers.** "What will this cost?" —
silence. *(SG-6)* "When do I get chapters, and how?" — silence. *(SG-12)*
"*Atomic Habits* is 320 pages and *How to Solve It* is 250 — will the novels be
the same length?" — the sizing defaults are Pólya-shaped and no re-derivation
rule exists. *(SG-7)* "Can you do these under license? Who owns the output?" —
silence. *(SG-13)*

**Week 3.** Book 1's novel is at chapter 6. A structural gate fails (it
happens — it happened to the real chapter 6 this very week). The pipeline stops
and asks, in effect, "redo generation or redo from brief?" Amara was promised
zero questions; she is now being asked to choose between two internal redo
rungs of a machine she's never seen. She picks one at random. *(SG-4)*

**The score:** five books in → one novel-in-progress, four undefined behaviors,
one silent taste decision, one artisan hiding in the verification stage, and
four unanswerable customer questions. Every failure was *foreseeable from the
spec text alone* — which is exactly what this story is for.

**EPILOGUE — Amara returns under the fixed spec (1757b6c + bd488d9).** She is
met by a **menu**: continue an existing generation or start new — five "start
new" runs, queued sequentially, each its own instance. All five classify; the
hybrid (*Thinking, Fast and Slow*) is tie-broken by its failure catalog and the
call is **ledgered**, not silent. *How to Solve It* is **accepted** (pack
exists) and gets a cost + time estimate before a single paid call. The other
four are **queued** for their packs — told which pack, told no date is
promised — except any the factory can't yet place, which are **deferred** with
their observations kept as taxonomy-extension cases: Amara hears "we haven't
figured your book out yet," never "your book is wrong." When book 1's gate
fails at chapter 6, the redo ladder runs itself (S1, then S2) and only a double
failure would reach her, analyst verdict attached. What is honestly still true:
four of five books still get no novel today — the spec now *says* what happens
to them, but the packs, the menu, the estimator, and the defer log are build
list rows, not machinery. The spec stopped lying by omission; it has not
started existing.

### Story 2 — The silent user (the spec's favorite customer)

Ben gives the factory one process book and never speaks again. This is the
spec's declared happy path: "a user who wants 'just fiction' touches nothing and
gets a coherent all-defaults book."

And per spec, it works: defaults are picked and ledgered, verification passes,
the loop writes chapters behind deterministic gates. Ben's book is coherent,
faithful, audited.

But the spec's own §4 admits the one failure its machines cannot catch: the
book can be all of that and *artistically dead* — and its only defense is "the
taste flights exist precisely so a human can smell that early." Ben never opens
a taste flight. Nobody ever smells Ben's book. The spec's happy-path user and
its only deadness-detector are mutually exclusive people. *(SG-9)* The smallest
honest fix is probably not "force Ben to taste" (that breaks zero-mandatory) but
a default reviewer: one flight, one AI-external or human spot-check, *something*
standing where Ben isn't.

### Story 3 — The late correction

Chapter 7 has shipped. Carla finally reads chapter 2, and the anchor's coat
bothers her: "the coat is wrong — he'd wear something a customs officer wouldn't
notice." The ledger dutifully shows the coat was an inherited default, tagged —
but the secret and the anchor's look are tagged "expensive after first anchor
scenes," and those scenes shipped weeks ago.

The spec defines correction *propagation* (consumer map, re-derive dependents —
genuinely good machinery). It does not define correction *economics*: is Carla's
correction refused? Applied forward only, so chapters 2–7 contradict 8+? Do
shipped chapters get rewritten, and does "serialized" mean readers already read
the old coat? The reversibility tag names the price; nothing says who pays it or
what "paying" even is. *(SG-10)*

---

## PART C — FINDINGS REGISTER (what the stories caught)

Ranked by how hard each bites the factory build. "Fix" = smallest spec edit that
closes the gap (not the implementation).

**STATUS: all rows CLOSED in spec commits 1757b6c + bd488d9**, with two owner
corrections improving on the proposed fixes (SG-1: intake surface = MENU with
continue/start-new; SG-2: refuse → DEFER, taxonomy extensible) — except SG-13,
now open owner decision D10. Spec-closed ≠ built: implementation rows live in
the spec's §2 build list.

| # | Finding | Bites in | Smallest fix |
|---|---------|----------|--------------|
| SG-2 | No defined behavior for books whose pack doesn't exist (4/5 knowledge types) or that fit no type / have an empty failure catalog | Story 1 | Add an intake contract table to Stage 1: classify → accept / queue-for-pack-v2 / refuse, each with a user-facing message |
| SG-4 | "Zero mandatory questions" vs mid-run human redo-rung choices; unattended operation unvalidated | Story 1, wk 3 | Add a redo-rung default policy to the spec (e.g. auto-S1 once, then S2, then halt-and-notify) as a chassis requirement |
| SG-1 | No intake surface — no defined way to submit a book and start the factory | Story 1, min 1 | Add a Stage 0: intake surface contract (input formats, kickoff, instance provisioning) |
| SG-5 | Singleton state; no multi-book/instance/queue story | Story 1 | One paragraph: 1 book = 1 provisioned instance (state dir + repo); queueing is v1 scope, concurrency is not |
| SG-6 | Cost and time absent from the product spec entirely | Stories 1–3 | Add a budget/estimate stage output + per-stage spend gates (the constitution already demands this) |
| SG-8 | Verification failure loop undefined ("flagged, not shipped" — then what?) | Story 1 | Define: auto-repair attempt → re-verify → N retries → surface to user as a correction proposal |
| SG-9 | Artistic-deadness check requires a human the happy-path user never is | Story 2 | Name a default deadness reviewer when the user is silent (one mandatory-for-the-factory, optional-for-the-user flight review) |
| SG-7 | Sizing/difficulty defaults are Pólya-shaped; no re-derivation rule for different curriculum sizes | Story 1 | Stage 2 addition: derive touch targets & chapter projection from extracted curriculum size, D9 as the formula's worked example |
| SG-10 | Late-correction economics undefined (reversibility tags name a price nobody pays) | Story 3 | Per-tag policy: cheap=apply+propagate; expensive=forward-only fork OR refuse-with-explanation; always ledgered |
| SG-3 | No tie-break rule for hybrid knowledge types | Story 1 | One rule: primary type = whichever mastery behavior the failure catalog mostly attacks; hybrid noted in ledger |
| SG-11 | "Each book calibrates the next" has no storage/consumption mechanism | Part A | Define the worked-example artifact (the calibration pack): where it lives, what it contains, when it's read |
| SG-12 | Delivery contract undefined (how/when chapters reach the user) | Story 1 | One paragraph in Stage 7: delivery = X at cadence Y; progress view is the status face |
| SG-13 | Rights/licensing of input books and output novels unaddressed | Story 1 | Owner decision needed; record as D10 in the ledger scheme |
| SG-14 | Spec drift risk: encodes a recipe still being validated; companion docs untracked | Part A | Commit progress/ docs; add "recipe changes must update this spec" to the validation checklist in §3 |

**Reading note (why this worked):** the manual format forces the spec to answer
a stranger's questions in order; the personification forces it to confess
contradictions between its halves (promise vs chassis); the 5-book story forces
the singleton assumptions into the open. None of these gaps required new
information — they were all derivable from the spec text alone, which is the
cheapest possible time to find them.
