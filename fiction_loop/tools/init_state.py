"""One-time state initializer for fiction_loop (spec: pipeline_fixes F2).

Generates, from the single OPERATIONS table below:
  - fiction_loop/state/process_state.json     (24 operations, touch 0, seeded pools)
  - fiction_loop/cards/concept/op_*.json      (24 concept cards)
  - fiction_loop/core/operation_registry.md   (human-readable registry summary)

Content provenance: physical anchors and canonical problem structures were drafted
against the source text (Pólya, How to Solve It) and owner-approved 2026-07-02 via
fiction_loop/content_for_review.md. Touch schedules implement the spaced-repetition
map (concept_curriculum.md §7) under the owner's D9 difficulty scaling
(easy=2 touches, medium=3, hard=4, truncated where the book ends).
`prerequisite` is null pending the D5 authoring pass.

Idempotency: refuses to overwrite an already-initialized process_state.json or any
existing op_*.json card unless --force is passed.

Usage (from project root):
  python fiction_loop/tools/init_state.py [--force]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # fiction_loop/

# Canonical ordinary-life context enum (owner decision D4 — fixed pick-list,
# seeded from correspondence_map.md §5's domain column, normalized).
CONTEXT_ENUM = [
    "workplace",
    "professional",
    "family_domestic",
    "civic_institutional",
    "teaching_mentoring",
    "negotiation",
    "project_management",
    "creative",
    "argument_debate",
]

# Wrong-approach pools per introduction arc (concept_curriculum.md §4).
FAILURE_POOLS = {
    1: ["the executor", "the system builder", "the information gatherer"],
    2: ["the confident specialist", "the hypothesis tester"],
    3: ["the executor on complex condition", "the system builder on complex condition"],
    4: ["the confident specialist", "the force applier"],
    5: ["the information gatherer", "the perfectionist"],
    6: ["the confident specialist", "the variation-tester"],
    7: ["the heuristic-only solver", "the guild verifier"],
    8: ["the single-step auxiliary solver", "the planner without synthesis"],
}

# Prerequisite graph (owner decision D5, approved 2026-07-02 via content_for_review.md
# §6). Enforces the D1 chronological mastery ladder: an operation cannot receive its
# first touch until every prerequisite is clear (touch >= 2). Empty list = entry point.
# Two edges are source-direct (Pólya's own wording): look_at_unknown -> related_problem
# ("Look at the unknown! And try to think of a familiar problem having the same or a
# similar unknown") and use_related_problem -> auxiliary_elements ("Should you introduce
# some auxiliary element in order to make its use possible?").
PREREQS = {
    "op_identify_unknown": [],
    "op_what_is_missing": [],
    "op_separate_condition": ["op_identify_unknown"],
    "op_look_at_unknown": ["op_identify_unknown"],
    "op_use_all_data": ["op_separate_condition"],
    "op_check_result": ["op_identify_unknown"],
    "op_related_problem": ["op_look_at_unknown"],
    "op_use_related_problem": ["op_related_problem"],
    "op_looking_back": ["op_check_result"],
    "op_derive_differently": ["op_looking_back"],
    "op_analogy": ["op_related_problem"],
    "op_decompose_condition": ["op_separate_condition"],
    "op_auxiliary_elements": ["op_use_related_problem"],
    "op_use_result": ["op_looking_back"],
    "op_specialisation": ["op_analogy"],
    "op_auxiliary_problem": ["op_auxiliary_elements"],
    "op_generalisation": ["op_specialisation"],
    "op_working_backwards": ["op_auxiliary_problem"],
    "op_inventors_paradox": ["op_generalisation"],
    "op_reductio": ["op_working_backwards"],
    "op_variation_restatement": ["op_working_backwards"],
    "op_heuristic_vs_proof": ["op_variation_restatement"],
    "op_subconscious_work": ["op_variation_restatement"],
    "op_auxiliary_chains": ["op_auxiliary_problem", "op_working_backwards"],
}

# id, name, difficulty, arc_introduced, touch_schedule {touch: arc}, name_at_touch,
# preferred_context, physical_anchor, problem_structure, correct_approach
OPERATIONS = [
    {
        "id": "op_identify_unknown",
        "name": "Identify unknown / data / condition",
        "difficulty_rating": 2,
        "arc_introduced": 1,
        "touch_schedule": {"1": 1, "2": 2},
        "name_at_touch": 2,
        "preferred_context": "workplace",
        "physical_anchor": "Standing still at the entrance; naming aloud, to no one, what is wanted, what is given, what binds them — sometimes counted on three fingers.",
        "canonical_problem_structure": {
            "unknown": "Never stated; the room presents objects and a mechanism and lets the solver assume what is wanted.",
            "data": ["Fully visible, slightly too orderly — invites action before understanding."],
            "condition": "Explicit but easy to skip past.",
        },
        "canonical_correct_approach": "Stop at the entrance; name what is wanted, what is given, and what binds them — before touching anything.",
    },
    {
        "id": "op_what_is_missing",
        "name": "What is missing (absence over presence)",
        "difficulty_rating": 2,
        "arc_introduced": 1,
        "touch_schedule": {"1": 1, "2": 2},
        "name_at_touch": 1,
        "preferred_context": "family_domestic",
        "physical_anchor": "The gaze that moves to where things are not; a hand resting on an empty space.",
        "canonical_problem_structure": {
            "unknown": "An absence; the room is complete except for one thing that should be there and is not.",
            "data": ["An almost-complete set whose completeness invites cataloguing."],
            "condition": "Closure responds to the absence being named, not to the present things being arranged.",
        },
        "canonical_correct_approach": "Ask what should be here and is not; search the gaps, not the contents.",
    },
    {
        "id": "op_separate_condition",
        "name": "Separate the parts of the condition",
        "difficulty_rating": 3,
        "arc_introduced": 1,
        "touch_schedule": {"1": 1, "2": 2},
        "name_at_touch": 2,
        "preferred_context": "workplace",
        "physical_anchor": "Reading the condition clause by clause, a pause between clauses; covering part of it with a hand to see one part alone.",
        "canonical_problem_structure": {
            "unknown": "Clear.",
            "data": ["Clear."],
            "condition": "Compound — several clauses fused into what reads as one requirement; taken whole, it stalls.",
        },
        "canonical_correct_approach": "Split the condition into clauses; test each alone; find which one actually binds.",
    },
    {
        "id": "op_use_all_data",
        "name": "Did you use all the data?",
        "difficulty_rating": 3,
        "arc_introduced": 2,
        "touch_schedule": {"1": 2, "2": 3},
        "name_at_touch": 1,
        "preferred_context": "professional",
        "physical_anchor": "Returning to the room's edge after a partial solution; touching, one by one, what was never touched.",
        "canonical_problem_structure": {
            "unknown": "Clear.",
            "data": ["N elements, one of which the obvious path never needs — and the obvious path fails for exactly that reason."],
            "condition": "Satisfiable only when every given element plays a role.",
        },
        "canonical_correct_approach": "When the partial path stalls, inventory given-versus-used; bring in the untouched element.",
    },
    {
        "id": "op_check_result",
        "name": "Can you check the result?",
        "difficulty_rating": 3,
        "arc_introduced": 2,
        "touch_schedule": {"1": 2, "2": 3},
        "name_at_touch": 1,
        "preferred_context": "professional",
        "physical_anchor": "Standing at the gate after the solution, waiting; not assuming closure.",
        "canonical_problem_structure": {
            "unknown": "Clear, with a plausible solution easy to produce.",
            "data": ["Supports two candidates — one correct, one method-correct but wrong."],
            "condition": "Contains a built-in way to test a candidate against the original requirement.",
        },
        "canonical_correct_approach": "Do not stop at 'the method worked'; test the result against the condition itself.",
    },
    {
        "id": "op_derive_differently",
        "name": "Can you derive the result differently?",
        "difficulty_rating": 3,
        "arc_introduced": 3,
        "touch_schedule": {"1": 3, "2": 4},
        "name_at_touch": 1,
        "preferred_context": "creative",
        "physical_anchor": "Stillness after closure; not leaving; retracing the route with the eyes, backward.",
        "canonical_problem_structure": {
            "unknown": "Already found once, by a long route.",
            "data": ["Contains a shorter route, visible only in retrospect."],
            "condition": "Demands the result be reached or confirmed by a second, independent route.",
        },
        "canonical_correct_approach": "After solving, ask whether a cleaner derivation exists; find it.",
    },
    {
        "id": "op_look_at_unknown",
        "name": "Look at the unknown",
        "difficulty_rating": 4,
        "arc_introduced": 1,
        "touch_schedule": {"1": 1, "2": 2, "3": 3},
        "name_at_touch": 2,
        "preferred_context": "civic_institutional",
        "physical_anchor": "Standing at the entrance, eyes fixed on where the answer must appear — back half-turned to the data.",
        "canonical_problem_structure": {
            "unknown": "Of a recognizable category (a quantity, a place, a person) — naming the category activates memory.",
            "data": ["Abundant and seductive; starting from it leads into a maze."],
            "condition": "Links data to unknown only when read from the unknown's side.",
        },
        "canonical_correct_approach": "Stand with the unknown; ask what kind of thing is wanted and what has ever produced that kind of thing.",
    },
    {
        "id": "op_related_problem",
        "name": "Do you know a related problem?",
        "difficulty_rating": 4,
        "arc_introduced": 2,
        "touch_schedule": {"1": 2, "2": 3, "3": 4},
        "name_at_touch": 2,
        "preferred_context": "professional",
        "physical_anchor": "The unfocused gaze — not at the room, through it; stillness in the middle of an action.",
        "canonical_problem_structure": {
            "unknown": "The same kind as one the solver has met before.",
            "data": ["Dressed in a surface unlike any previous gate."],
            "condition": "Structurally identical to the ancestor problem's.",
        },
        "canonical_correct_approach": "Search memory for a problem with the same or similar unknown; the surface differs, the skeleton doesn't.",
    },
    {
        "id": "op_use_related_problem",
        "name": "Here is a problem related to yours and solved before",
        "difficulty_rating": 4,
        "arc_introduced": 2,
        "touch_schedule": {"1": 2, "2": 3, "3": 4},
        "name_at_touch": 1,
        "preferred_context": "teaching_mentoring",
        "physical_anchor": "Holding the remembered thing beside the present one — eyes moving between two points, comparing structure.",
        "canonical_problem_structure": {
            "unknown": "Reachable by adapting a known solution, not by re-deriving.",
            "data": ["Includes a bridge element that maps the old solution onto the new problem."],
            "condition": "Satisfied by the old method or result — but only after deliberate adaptation.",
        },
        "canonical_correct_approach": "Hold the recalled problem next to this one: use its result? its method? what must be added to make it usable?",
    },
    {
        "id": "op_analogy",
        "name": "Analogy — simpler analogous problem",
        "difficulty_rating": 4,
        "arc_introduced": 3,
        "touch_schedule": {"1": 3, "2": 4, "3": 5},
        "name_at_touch": 2,
        "preferred_context": "teaching_mentoring",
        "physical_anchor": "Sketching a smaller version — in dust, on a palm, on paper; eyes on the relations, not the contents.",
        "canonical_problem_structure": {
            "unknown": "Too complex to attack directly.",
            "data": ["Relations that survive simplification — a smaller problem with identical structure can be built."],
            "condition": "The simpler constructed problem shares the original's structural relations exactly.",
        },
        "canonical_correct_approach": "Construct the simplest problem with the same relations; solve it; carry the method back.",
    },
    {
        "id": "op_looking_back",
        "name": "Looking back / transfer",
        "difficulty_rating": 4,
        "arc_introduced": 2,
        "touch_schedule": {"1": 2, "2": 3, "3": 4},
        "name_at_touch": 2,
        "preferred_context": "professional",
        "physical_anchor": "Remaining after others leave; stillness that looks like confusion but is not; sometimes writing.",
        "canonical_problem_structure": {
            "unknown": "Not the gate's — the solver's own method is the unknown.",
            "data": ["The just-finished solution, still present and readable."],
            "condition": "Nothing forces staying; leaving costs nothing today and everything at the next gate.",
        },
        "canonical_correct_approach": "Stay; ask what was actually done; name where else it applies.",
    },
    {
        "id": "op_decompose_condition",
        "name": "Decompose condition / keep part drop part",
        "difficulty_rating": 5,
        "arc_introduced": 3,
        "touch_schedule": {"1": 3, "2": 4, "3": 5},
        "name_at_touch": 2,
        "preferred_context": "negotiation",
        "physical_anchor": "The gaze narrows; parts of the room deliberately ignored; a visible reduction of the attention field.",
        "canonical_problem_structure": {
            "unknown": "Unreachable under the full condition.",
            "data": ["Sufficient for a partial problem."],
            "condition": "Compound; the whole resists, but one part alone determines something solid.",
        },
        "canonical_correct_approach": "Keep one clause, drop the rest; solve what the partial condition determines; reintroduce the clauses one by one.",
    },
    {
        "id": "op_auxiliary_elements",
        "name": "Introduce auxiliary elements",
        "difficulty_rating": 5,
        "arc_introduced": 3,
        "touch_schedule": {"1": 3, "2": 4, "3": 5},
        "name_at_touch": 1,
        "preferred_context": "family_domestic",
        "physical_anchor": "Hands moving to the space between things — adding a mark, a line, an object that was not given.",
        "canonical_problem_structure": {
            "unknown": "Connected to the data only through something not given.",
            "data": ["Complete but disconnected — two shores, no bridge."],
            "condition": "Satisfiable only after the solver adds an element of their own.",
        },
        "canonical_correct_approach": "Add what was not given — the line, the mark, the sub-unknown that makes a known method applicable.",
    },
    {
        "id": "op_use_result",
        "name": "Can you use the result?",
        "difficulty_rating": 5,
        "arc_introduced": 4,
        "touch_schedule": {"1": 4, "2": 5, "3": 6},
        "name_at_touch": 1,
        "preferred_context": "professional",
        "physical_anchor": "Pausing at the exit; looking back in; not done yet.",
        "canonical_problem_structure": {
            "unknown": "Belongs to the next problem; this gate's result is a tool.",
            "data": ["A second chamber restates the first chamber's result in new clothes."],
            "condition": "The second chamber is unsolvable from scratch in the time available — and instant with the first chamber's result.",
        },
        "canonical_correct_approach": "Treat every result as an asset; ask what it now unlocks.",
    },
    {
        "id": "op_auxiliary_problem",
        "name": "Auxiliary problem",
        "difficulty_rating": 6,
        "arc_introduced": 4,
        "touch_schedule": {"1": 4, "2": 5, "3": 6, "4": 7},
        "name_at_touch": 2,
        "preferred_context": "project_management",
        "physical_anchor": "Stepping physically back from the work; beginning something that looks unrelated — deliberately, not in defeat.",
        "canonical_problem_structure": {
            "unknown": "No foothold; the forward path exhausted.",
            "data": ["Useless to the original problem directly, but sufficient for a different problem the solver could pose."],
            "condition": "The original yields only via the invented side-problem — and the detour visibly costs time and may fail.",
        },
        "canonical_correct_approach": "Deliberately pose a different problem as a stepping stone, knowing the risk; work it; return with what it yields.",
    },
    {
        "id": "op_generalisation",
        "name": "Generalisation",
        "difficulty_rating": 6,
        "arc_introduced": 5,
        "touch_schedule": {"1": 5, "2": 6, "3": 7, "4": 8},
        "name_at_touch": 1,
        "preferred_context": "professional",
        "physical_anchor": "Stepping back until the whole room is in view at once; asking a question about all gates rather than this one.",
        "canonical_problem_structure": {
            "unknown": "A specific instance whose specificity hides the structure.",
            "data": ["Peculiarities that look load-bearing and aren't."],
            "condition": "An instance of a general class with a reachable class solution.",
        },
        "canonical_correct_approach": "Ask what this is a case of; solve the class; step back down to the instance.",
    },
    {
        "id": "op_specialisation",
        "name": "Specialisation",
        "difficulty_rating": 5,
        "arc_introduced": 4,
        "touch_schedule": {"1": 4, "2": 5, "3": 6},
        "name_at_touch": 1,
        "preferred_context": "teaching_mentoring",
        "physical_anchor": "Crouching close to the smallest piece; the field of attention visibly contracted to one case.",
        "canonical_problem_structure": {
            "unknown": "General and sprawling; no purchase anywhere.",
            "data": ["Contains one simplest or extreme case that can actually be worked."],
            "condition": "Whatever holds must hold in the simplest case — which shows the pattern or kills the approach.",
        },
        "canonical_correct_approach": "Contract to the simplest case; solve it; use it as foothold or counterexample.",
    },
    {
        "id": "op_working_backwards",
        "name": "Working backwards / analysis",
        "difficulty_rating": 7,
        "arc_introduced": 5,
        "touch_schedule": {"1": 5, "2": 6, "3": 7, "4": 8},
        "name_at_touch": 2,
        "preferred_context": "civic_institutional",
        "physical_anchor": "The physical turn — standing with the back to the data, facing where the end must be.",
        "canonical_problem_structure": {
            "unknown": "Unreachable from the data side; every forward move dead-ends.",
            "data": ["Many forward paths, all divergent — from the goal side, one path is visible."],
            "condition": "A chain of dependencies legible only in reverse.",
        },
        "canonical_correct_approach": "Assume it solved; stand at the end; ask what must have been true immediately before, and step back until known ground.",
    },
    {
        "id": "op_variation_restatement",
        "name": "Variation of the problem / restatement",
        "difficulty_rating": 7,
        "arc_introduced": 6,
        "touch_schedule": {"1": 6, "2": 7, "3": 8, "4": 9},
        "name_at_touch": 2,
        "preferred_context": "civic_institutional",
        "physical_anchor": "The long stillness; the frown that is not frustration but suspicion; the problem restated aloud in different words.",
        "canonical_problem_structure": {
            "unknown": "As stated, the wrong unknown — the stated problem is solvable and solving it changes nothing.",
            "data": ["Contains a remainder the stated problem never touches."],
            "condition": "The true condition differs from the apparent one; closure responds only to the restated problem.",
        },
        "canonical_correct_approach": "Ask whether the stated problem is the real problem; restate until the condition matches what the gate actually requires.",
    },
    {
        "id": "op_inventors_paradox",
        "name": "Inventor's Paradox",
        "difficulty_rating": 7,
        "arc_introduced": 5,
        "touch_schedule": {"1": 5, "2": 6, "3": 7, "4": 8},
        "name_at_touch": 2,
        "preferred_context": "civic_institutional",
        "physical_anchor": "The widening — a step back, the gaze opening, the problem deliberately made larger before it is touched.",
        "canonical_problem_structure": {
            "unknown": "Specific, and harder because specific.",
            "data": ["Insufficient for the narrow question, exactly right for the broader one."],
            "condition": "The general problem's solution covers the specific case; the specific case alone offers no structure.",
        },
        "canonical_correct_approach": "Enlarge the problem on purpose; answer the bigger question; the specific answer falls out.",
    },
    {
        "id": "op_reductio",
        "name": "Reductio ad absurdum",
        "difficulty_rating": 7,
        "arc_introduced": 5,
        "touch_schedule": {"1": 5, "2": 6, "3": 7, "4": 8},
        "name_at_touch": 1,
        "preferred_context": "argument_debate",
        "physical_anchor": "Building the case for the thing known to be wrong — carefully, precisely; waiting for the break.",
        "canonical_problem_structure": {
            "unknown": "A certainty — something to prove impossible or necessary; no direct proof available.",
            "data": ["Consistent with the false assumption at first; the contradiction sits several honest steps deep."],
            "condition": "Assuming the opposite and following it faithfully must break against a given fact.",
        },
        "canonical_correct_approach": "Assume what you believe false; follow it precisely; the break is the proof.",
    },
    {
        "id": "op_heuristic_vs_proof",
        "name": "Heuristic reasoning vs proof distinction",
        "difficulty_rating": 8,
        "arc_introduced": 7,
        "touch_schedule": {"1": 7, "2": 8, "3": 9},
        "name_at_touch": 2,
        "preferred_context": "professional",
        "physical_anchor": "Movement with deliberateness that is not certainty; a running note kept of what is not yet checked.",
        "canonical_problem_structure": {
            "unknown": "Reachable by a plausible path that cannot yet be verified.",
            "data": ["Enough for a good guess now; enough for verification only separately, later."],
            "condition": "Acting on the guess is necessary (time), and verifying it is also necessary (what follows punishes unverified confidence).",
        },
        "canonical_correct_approach": "Commit to the provisional path while separately tracking what remains unverified; do both, confuse neither.",
    },
    {
        "id": "op_subconscious_work",
        "name": "Subconscious work",
        "difficulty_rating": 8,
        "arc_introduced": 7,
        "touch_schedule": {"1": 7, "2": 8, "3": 9},
        "name_at_touch": 1,
        "preferred_context": "creative",
        "physical_anchor": "Everything put down; the room left, or the wall sat against; the return — and the question present on return.",
        "canonical_problem_structure": {
            "unknown": "Will not yield to continued effort; every conscious approach exhausted.",
            "data": ["Fully absorbed already; nothing new to gather."],
            "condition": "The connection forms only after effort stops.",
        },
        "canonical_correct_approach": "Stop entirely; leave; return — the right question is present on return.",
    },
    {
        "id": "op_auxiliary_chains",
        "name": "Auxiliary problem chains",
        "difficulty_rating": 8,
        "arc_introduced": 8,
        "touch_schedule": {"1": 8, "2": 9},
        "name_at_touch": 1,
        "preferred_context": "project_management",
        "physical_anchor": "A sequence built visibly forward; then the turn, and the sequence traced backward with a finger before acting.",
        "canonical_problem_structure": {
            "unknown": "Separated from the data by several equivalent reformulations; no single reduction suffices.",
            "data": ["Supports the last problem in a chain, not the first."],
            "condition": "Each reduction must preserve equivalence, and closure requires walking the chain back (synthesis) after building it forward (analysis).",
        },
        "canonical_correct_approach": "Reduce problem to problem until one is solvable; then retrace the chain backward to deliver the original.",
    },
]


def build_card(op: dict) -> dict:
    touch_target = len(op["touch_schedule"])
    return {
        "id": op["id"],
        "name": op["name"],
        "source_text": "Pólya, How to Solve It (2nd ed.) — Part III, Short Dictionary of Heuristic",
        "difficulty_rating": op["difficulty_rating"],
        "arc_introduced": op["arc_introduced"],
        "current_touch": 0,
        "name_attached": False,
        "name_at_touch": op["name_at_touch"],
        "touch_schedule": op["touch_schedule"],
        "touch_target": touch_target,
        "prerequisite": PREREQS[op["id"]],
        "teaching_history": [],
        "failure_modes_shown": [],
        "failure_modes_not_yet_shown": list(FAILURE_POOLS[op["arc_introduced"]]),
        "contexts_demonstrated": [],
        "contexts_not_yet_demonstrated": list(CONTEXT_ENUM),
        "preferred_context": op["preferred_context"],
        "transferred_to_ordinary_life": False,
        "physical_anchor": op["physical_anchor"],
        "canonical_problem_structure": op["canonical_problem_structure"],
        "canonical_correct_approach": op["canonical_correct_approach"],
        "compressible_at_touch": touch_target,
    }


def build_process_state() -> dict:
    ops = {}
    for op in OPERATIONS:
        card = build_card(op)
        ops[op["id"]] = {
            k: card[k]
            for k in (
                "name", "difficulty_rating", "arc_introduced", "current_touch",
                "name_attached", "name_at_touch", "touch_schedule", "touch_target",
                "prerequisite", "teaching_history", "failure_modes_shown",
                "failure_modes_not_yet_shown", "contexts_demonstrated",
                "contexts_not_yet_demonstrated", "preferred_context",
                "transferred_to_ordinary_life", "compressible_at_touch",
            )
        }
    return {"context_enum": CONTEXT_ENUM, "operations": ops}


def build_registry_md() -> str:
    lines = [
        "# OPERATION REGISTRY",
        "",
        "Generated by `tools/init_state.py` — do not edit by hand; edit the OPERATIONS",
        "table in that script and re-run with --force. Canonical operation ids for all",
        "state files and cards. Touch schedules implement concept_curriculum.md §7",
        "under owner decision D9 (difficulty-scaled: easy=2, medium=3, hard=4 touches,",
        "truncated where the book ends). Arc 9 = Finale.",
        "",
        "| operation_id | Canonical name | Diff. | Arc in | Touch schedule (touch→arc) | Name at touch | Target | Prerequisite(s) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for op in OPERATIONS:
        sched = ", ".join(f"{t}→arc{a}" for t, a in op["touch_schedule"].items())
        prereq = ", ".join(f"`{p}`" for p in PREREQS[op["id"]]) or "—"
        lines.append(
            f"| `{op['id']}` | {op['name']} | {op['difficulty_rating']} | "
            f"{op['arc_introduced']} | {sched} | {op['name_at_touch']} | {len(op['touch_schedule'])} | {prereq} |"
        )
    total = sum(len(op["touch_schedule"]) for op in OPERATIONS)
    lines += [
        "",
        f"Total scheduled dedicated touch-events: **{total}** across {len(OPERATIONS)} operations.",
        "With D9 co-hosting (up to 2 in-gate piggybacks + 1 echo-carried touch per",
        "chapter) this packs into roughly 18–25 teaching chapters.",
        "",
        "Context enum (owner decision D4): " + ", ".join(f"`{c}`" for c in CONTEXT_ENUM) + ".",
        "",
        "Prerequisite graph: owner-approved 2026-07-02 (D5) — enforced by check CR3 and",
        "the scheduler's eligibility gate. A first touch may lag its map arc when its",
        "prerequisite has not yet reached touch 2; the deficit carries and gains",
        "priority as soon as the prerequisite clears (extractor.md STEP A/D).",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description="fiction_loop one-time state initializer")
    p.add_argument("--force", action="store_true", help="Overwrite existing initialized state")
    args = p.parse_args()

    process_state_path = ROOT / "state" / "process_state.json"
    concept_dir = ROOT / "cards" / "concept"
    registry_path = ROOT / "core" / "operation_registry.md"

    # Idempotency guard
    if not args.force:
        existing = json.loads(process_state_path.read_text(encoding="utf-8")) if process_state_path.exists() else {}
        ops = existing.get("operations", {})
        if ops and list(ops.keys()) != ["[operation_id]"]:
            print("process_state.json already initialized — use --force to overwrite.", file=sys.stderr)
            sys.exit(1)
        existing_cards = [f for f in concept_dir.glob("op_*.json")]
        if existing_cards:
            print(f"{len(existing_cards)} concept cards already exist — use --force to overwrite.", file=sys.stderr)
            sys.exit(1)

    process_state_path.write_text(
        json.dumps(build_process_state(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    for op in OPERATIONS:
        (concept_dir / f"{op['id']}.json").write_text(
            json.dumps(build_card(op), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    registry_path.write_text(build_registry_md(), encoding="utf-8")

    total = sum(len(op["touch_schedule"]) for op in OPERATIONS)
    print(f"OK: {len(OPERATIONS)} operations -> process_state.json, "
          f"{len(OPERATIONS)} concept cards, operation_registry.md "
          f"({total} scheduled touch-events).")


if __name__ == "__main__":
    main()
