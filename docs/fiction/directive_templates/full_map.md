# [Domain] ↔ [Genre] Full Map

<!-- INSTRUCTION: This document requires 5 translation tables + a time scaling table + 1 prose example.
Every table must have a column explaining WHY the mapping holds mechanically.
Weak mappings — shared name only, no shared mechanics — are not permitted.
If a mapping requires an asterisk or caveat, the mapping is probably wrong; find a better one. -->

## Core Infrastructure

<!-- Map the genre's fundamental physical/structural elements to system design infrastructure.
Minimum 5 rows. The third column must explain the mechanical overlap, not just rename things. -->

| System design | [Genre] equivalent | Mechanics that must survive translation |
|---|---|---|
| Distributed node | | |
| Network topology | | |
| Volatile memory (RAM) | | |
| Persistent storage | | |
| Cache hierarchy | | |
| [add rows as needed] | | |

## Progression Stages as System States

<!-- Map each progression stage from world_laws.md to a system state.
The "Why this mapping holds" column must explain mechanics, not just the metaphor.
Every stage from world_laws.md must appear here. -->

| Progression stage | System state | Why this mapping holds |
|---|---|---|
| [Stage 1 from world_laws] | | |
| [Stage 2] | | |
| [Stage 3] | | |
| [Stage 4] | | |
| [Stage 5] | | |

## Actions and Operations

<!-- Map the genre's active events (combat, rituals, crafting, negotiation, etc.) to system operations.
Include rate limiting, failure modes, and retry semantics where they apply. -->

| [Genre] action | System equivalent | Mechanics |
|---|---|---|
| | | |
| | | |
| | | |
| | | |

## Resources

<!-- Map the genre's consumable or tradable resources to system resources.
"Properties that must match" column: only list properties that are mechanically identical in both domains.
Do not list properties that merely sound similar. -->

| Resource | System analogy | Properties that must match |
|---|---|---|
| | | |
| | | |
| | | |
| | | |

## Failure Modes

<!-- This is the most important table. Failure is what makes both systems narratively interesting.
"Why they're the same" must show identical causal structure — not just similar names. -->

| [Genre] failure | System failure | Why they're the same |
|---|---|---|
| | | |
| | | |
| | | |
| | | |

## Time Scaling

<!-- System design problems resolve in minutes or hours. Fiction spans months or years.
The concepts map 1:1; the clock does not. Define a consistent conversion rate or pacing breaks.
List at least 6 operations ordered from fastest to slowest, with their fiction-time equivalent. -->

| System design operation | [Genre] equivalent time |
|---|---|
| [fastest — e.g., cache miss] | [e.g., one breath, one glance] |
| [e.g., API call round-trip] | [e.g., one exchange in a scene] |
| [e.g., circuit breaker trip] | [e.g., seconds — a desperate reflex] |
| [e.g., schema migration] | [e.g., days sealed away] |
| [e.g., consensus protocol change] | [e.g., months of focused work] |
| [slowest — e.g., full re-architecture] | [e.g., years, a generation] |

## Prose Example

<!-- Write one before/after example for a mid-novel concept.
"Before" = conventional genre prose — reads naturally in the genre, no technical grounding.
"After" = same moment rewritten so the system design mechanic is dramatized, not described.
The "After" version must demonstrate a real mechanic, not just rename things with technical vocabulary. -->

### [Genre] prose

[Conventional version. A reader of this genre would find this unremarkable.]

### System-designed version

[Same scene, rewritten. The technical mechanic is embedded in the action and consequence —
not stated, not explained, but enacted. A reader learns the concept by watching it fail or succeed.]
