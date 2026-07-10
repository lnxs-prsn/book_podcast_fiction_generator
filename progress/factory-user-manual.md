# THE INTAKE FACTORY — USER MANUAL (derived from the specs, 2026-07-10)

**What this document is.** A user manual for the factory described in
`fiction_loop/specs/intake_factory.spec.md` + `specs/genre_derivation.md`, written
AS IF the product existed, using ONLY what the specs define. Its purpose is
diagnostic: everywhere a real manual would have to answer a user question and the
spec is silent, there is a **⚠ SPEC GAP (SG-n)** marker. The numbered gaps are
consolidated in `progress/factory-user-stories.md` §FINDINGS.

**STATUS (same day, later):** all gaps below were closed in the spec (commits
1757b6c + bd488d9; SG-13 → open owner decision D10; SG-1's fix became a MENU,
SG-2's "refuse" became DEFER). This manual is preserved as the diagnostic record
of the pre-fix spec — do not use it as current documentation.

---

## 1. What this product does

You give the factory a **knowledge book** — a book that teaches something (a
method, a concept system, a skill of judgment, a way of dealing with people, a
practice that compounds). You get back a **serialized teaching novel**: fiction in
which characters experience the book's material — including failing the way the
book says people fail — so that you absorb the knowledge by living it, not by
being told it.

You do not fill in templates. You are never interviewed. You may correct anything
you see, in plain words, at any time — or touch nothing and receive a coherent
all-defaults book.

## 2. Quick start

> ⚠ **SPEC GAP (SG-1).** This is where a manual says "go to X, upload your book,
> press Y." The spec has no intake surface at all. Stage 1 begins "Extract book
> text" — the sentence where a user actually hands over a book and starts the
> machine is written nowhere. (The worked example was started by a human typing a
> kickoff prompt from RUN.md into an AI session — not a product surface.)

Accepted formats: PDF and EPUB (format adapters exist).
⚠ **SPEC GAP (SG-1b):** scanned/image PDFs, DRM, non-English books — undefined.

## 3. What happens to your book (the six stages, in user terms)

1. **Reading & classification.** The factory reads your book and decides what
   *mastery* of it looks like: executing moves under pressure (**process**),
   seeing a concept everywhere (**thing**), discriminating what others can't
   (**perception**), running a process on other minds (**relational**), or
   compounding practice over time (**discipline**). It also extracts your book's
   own catalog of how people get it wrong — this drives the whole story design.

   > ⚠ **SPEC GAP (SG-2).** Only the *process* pedagogy pack exists (v1). If your
   > book classifies as any of the other four types, the spec defines no behavior:
   > refuse? queue for v2? force-fit into the process pack? Nothing is written.
   > ⚠ **SPEC GAP (SG-2b).** No behavior for a book that fits *no* type (a novel,
   > a cookbook, a reference work) or whose failure catalog comes up empty — even
   > though the spec calls the failure catalog the strictest filter of all.
   > ⚠ **SPEC GAP (SG-3).** No tie-break rule for hybrid books. The specs' own
   > worked table classifies *Thinking, Fast and Slow* as "perception/process."

2. **Requirements.** A near-invariant list of seven demands any teaching fiction
   must satisfy (playable without expertise, guaranteed solvability, externalized
   thinking, ensemble variety, adjacency to ordinary life, real stakes, a serial
   mystery) is instantiated and weighted for your book's type.

3. **World invention.** Candidate genres are stress-tested against those
   requirements; most die (there is a recorded kill-table). What survives is a
   structure, not a costume — then the factory invents the one thing no genre
   catalog supplies: the **externalization mechanism** that makes thinking
   visible on the page. This is the taste-bearing step; it is where your
   corrections matter most (see §4).

4. **Template generation.** The full document set your book's story-machine runs
   on is drafted — every domain claim carrying a supporting quote located in your
   book. Templates are generated to satisfy hard-won craft rules (constraints go
   in the channel writer-models actually obey; every automated check has a
   matching rule that *prevents* what it detects).

5. **Verification (automated — you don't read piles).** Three checks: every
   claim re-traced to a quote (**fidelity**), a different AI model hunting
   contradictions (**logic**), and an IS-not-LIKE audit that every story element
   is your book's mechanic with the same failure mode (**correspondence**).
   Anything unsupported is flagged, not shipped.

   > ⚠ **SPEC GAP (SG-8).** Flagged — then what? The spec defines no repair loop,
   > no retry limit, no escalation path, and no message to you.

6. **Your decisions — without questions.** See §4.

7. **The book gets written**, chapter by chapter, by the existing story engine,
   with deterministic quality gates before any chapter becomes canon.

## 4. Your role (all optional)

- **Decisions ledger.** Every taste decision the factory took for you is logged
  with its rationale and a reversibility tag (title: cheap anytime; genre skin:
  expensive after ~5 chapters; the story's secret: expensive after it first
  shows on page). "AI proposed and I let it stand" is always visible.
- **Taste flights.** Where options genuinely diverge, you get *tasteable
  samples* — half a page under option A vs option B — never a paragraph
  describing options. You choose by pointing.
- **Free-text corrections, anytime.** "The coat is wrong." "More menace."
  Silence = consent. Corrections propagate: the factory knows every consumer of
  every rule and re-derives them — never a point-fix.

  > ⚠ **SPEC GAP (SG-10).** The tags say late corrections are "expensive" but the
  > spec never says what happens when you make one anyway after chapters exist:
  > refused? chapters rewritten? a fork? a price?

## 5. Receiving your book

A live progress view answers "where are we / how much left" (chapters done,
curriculum progress bar, estimated chapters remaining, current step).

> ⚠ **SPEC GAP (SG-12).** How chapters actually reach you (files? feed? email?),
> at what cadence, and what "done" looks like — undefined.
> ⚠ **SPEC GAP (SG-6).** What it costs and how long it takes — the spec never
> mentions money or time, in a project whose own constitution has a
> "gates-before-spend" law.

## 6. When something goes wrong

The engine has a deterministic diagnostician (receipt-based, zero-token) and a
staged redo ladder (redo the draft / redo from the brief / undo state / undo the
chapter).

> ⚠ **SPEC GAP (SG-4).** Today a failed quality gate stops the pipeline and waits
> for a *human* to choose a redo rung. The spec promises "zero mandatory
> questions" but defines no policy for choosing rungs automatically — so an
> unattended user's book can simply stop. (Unattended operation is explicitly
> not yet validated; the transaction-integrity work is open.)

## 7. Honest limits (the spec says this itself)

A coherent, source-faithful, fully audited book can still be **artistically
dead**. The taste flights exist precisely so a human can smell that early. The
factory's defaults carry real authorial weight; the ledger keeps that honest.

> ⚠ **SPEC GAP (SG-9).** The smelling is optional. A "just fiction" user who
> never opens a taste flight has *nobody* checking for artistic deadness — the
> one failure the spec admits its machines can't catch.

## 8. FAQ

**Q: Can I give it several books at once?**
⚠ **SPEC GAP (SG-5).** Undefined. The engine's state is a singleton (one book's
cards, one living document, one progress file); nothing describes provisioning a
second instance, a queue, or five books arriving together. See the 5-book story.

**Q: My book is short / enormous — how big will the novel be?**
⚠ **SPEC GAP (SG-7).** The sizing defaults (touch targets, ~20–30 chapters) are
inherited from the first worked example's book and ship as recorded defaults; no
rule says how to re-derive them for a curriculum of a different size.

**Q: Does the factory get better as it processes more books?**
The spec says yes — "each processed book leaves a worked example that calibrates
the next; the fifth is near-turnkey."
⚠ **SPEC GAP (SG-11).** Where worked examples are stored, in what form, and how
a later run consumes them — undefined.

**Q: Who owns the result / can I feed it any copyrighted book?**
⚠ **SPEC GAP (SG-13).** Not addressed anywhere in the specs.
