# NLP ↔ Neon Sprawl Full Map

## Core Infrastructure

| System design | Neon Sprawl equivalent | Mechanics that must survive translation |
|---|---|---|
| Distributed node | **Inference shard** (corporate tower, vendor kiosk, streetlight) | Each shard runs a replica of the global model; local fine-tuning updates must sync via consensus or cause drift |
| Network topology | **The Beacon Layer** (ad-beacons, telemetry drones, heartbeat pulses) | Packet routing follows attention-weighted paths; congestion = attention leak; partition = sector blackout |
| Volatile memory (RAM) | **Cycle buffer** (implant's working memory, flushed each circadian) | Hard capacity limit; LRU eviction on overflow; no swap, no persistence across cycles |
| Persistent storage | **The Ledger** (immutable, sharded, provenance-chained) | Write-once, read-many; compaction garbage-collects unsigned tokens; fork = consensus emergency |
| Cache hierarchy | **Attention weighting** (implant's token prioritization) | Hot tokens (survival-critical) stay in L1 (neural cache); cold tokens spill to L2 (Ledger query); miss = cycle burn |
| Consensus protocol | **The Sync** (periodic global centroid alignment) | Nodes submit embedding deltas; >0.03 cosine distance triggers forced re-sync; Byzantine fault = poisoned corpus |
| Token vocabulary | **Global Vocab** (substrate's closed token set) | Fixed size; OOV = REJECT; expansion requires governance proposal + supermajority |
| Embedding space | **The Drift Map** (shared latent geometry) | Cosine distance = semantic distance; drift = centroid shift; hallucination = region with no grounding beacon |

## Progression Stages as System States

| Progression stage | System state | Why this mapping holds |
|---|---|---|
| Stage 1: Jack-in (Raw ingestion) | **Sensor fusion / buffer management** | Both face unbounded input streams, hard capacity limits, and must throttle or crash; the seizure *is* the buffer overflow |
| Stage 2: First Parse (Tokenization) | **Vocabulary fixation / tokenizer deployment** | Both require mapping continuous/ambiguous input to discrete valid tokens; OOV rejection mechanics are identical |
| Stage 3: Signal Hygiene (Stop-word filtering) | **Noise suppression / attention masking** | Both must discard high-volume low-signal tokens without discarding signal; attention leak = false positive retention |
| Stage 4: Canonical Form (Normalization) | **Canonicalization / lemma mapping** | Both collapse variant forms to single representations; collision = two distinct inputs mapping to same output = data corruption |
| Stage 5: Clean Feed (Pipeline composition) | **Transactional pipeline / atomic commit** | Both require all-or-nothing execution; partial rollback leaves inconsistent state (exposed logs / half-written records) |

## Actions and Operations

| Neon Sprawl action | System equivalent | Mechanics |
|---|---|---|
| Submitting a corpus curation job | **Batch inference request** | Rate-limited by cycle quota; fails if OOV rate > threshold; provenance chain required |
| Building a personal tokenizer | **Custom tokenizer training** | Must map to global vocab; fraud detection flags entropy anomalies; iterative refinement via REJECT feedback |
| Filtering a covert beacon | **Adversarial input detection** | Attention-weight analysis; must not increase false negative rate on legitimate traffic; latency budget: <5ms |
| Negotiating territory via Ledger | **Distributed transaction with conflict resolution** | Optimistic locking; lemma collision = write conflict; rollback requires compensating transaction |
| Composing a preprocessing pipeline | **DAG construction with transactional semantics** | Stage ordering matters (normalize after filter); each stage idempotent; commit = single Ledger write |
| Tracing drift to poisoned annotator | **Data lineage / influence function analysis** | Provenance chain walk; gradient-based attribution; requires quorum of nodes to agree on rollback |
| Universal pipeline commit (climax) | **Consensus-critical configuration update** | Must be accepted by all shards simultaneously; two-phase commit; failure = global deadlock |

## Resources

| Resource | System analogy | Properties that must match |
|---|---|---|
| Cycle quota | **Compute budget / token budget** | Hard ceiling; non-transferable; resets periodically; exhaustion = process kill |
| Global vocab slots | **Vocabulary capacity** | Fixed size; expansion requires governance; OOV = hard reject (not soft fallback) |
| Provenance signatures | **Audit log entries** | Immutable; chainable; required for commit; missing = garbage collection |
| Attention weight | **Cache priority / LRU score** | Dynamic; decays with time; determines eviction order; manipulable by adversarial input |
| Embedding centroid | **Global model checkpoint** | Single source of truth; drift measured against it; re-sync = broadcast + apply |
| Calorie balance | **Energy / inference credits** | Consumed per cycle; earned via valid commits; zero = hardware lockout (dispenser, door, implant) |

## Failure Modes

| Neon Sprawl failure | System failure | Why they're the same |
|---|---|---|
| Buffer overflow seizure | **OOM kill / buffer overflow** | Unbounded input + fixed capacity = crash; no graceful degradation; physical manifestation = kernel panic / neural seizure |
| OOV cascade (license expiry, dispenser lock) | **Closed-vocab rejection + quota burn** | Invalid token consumes compute but produces no output; downstream services (license, dispenser) depend on valid commit |
| Attention leak (beacon routes query to competitor) | **Attention hijack / cache poisoning** | High-weight noise displaces signal in priority queue; wrong output routed; side-channel leakage of private state |
| Form collision (territory overwrite, turf war) | **Hash collision / key collision in canonicalization** | Two distinct keys map to same canonical form; write merges them; data loss + inconsistency; requires manual resolution |
| Partial commit (raw logs exposed) | **Non-atomic transaction / partial rollback** | Multi-stage pipeline fails mid-way; rollback incomplete; intermediate state persisted = security breach |
| Drift hallucination (new districts appear) | **Model drift / catastrophic forgetting** | Local fine-tuning shifts embeddings; global consensus adopts shift; ungrounded regions generate false outputs |
| Preprocessing deadlock (city freezes) | **Distributed deadlock / consensus stall** | Circular dependency: each node waits for others' valid tokens; no progress; requires external coordinator (Lyra) |

## Time Scaling

| System design operation | Neon Sprawl equivalent time |
|---|---|
| Cache miss (L1 → L2) | **One breath** — the gap between query and Ledger response |
| Token validation (vocab lookup) | **One blink** — implant flashes red/green |
| Attention re-weighting | **One heartbeat** — the rhythm Lyra learns to feel |
| Pipeline stage execution | **One exchange** — a conversation turn, a vendor transaction |
| Cycle quota reset | **One circadian** — the Sprawl's "day," marked by beacon color shift |
| Drift detection threshold breach | **One sector-cycle** — ~6 hours before forced re-sync triggers |
| Consensus protocol change | **One governance epoch** — weeks of sealed-off work in a Faraday vault |
| Full re-architecture (universal pipeline) | **One generation** — the time between Sprawl rewrites; Lyra does it in 72 hours |

## Prose Example

### Neon Sprawl prose

Lyra jacked into the market feed. The data hit her like a wave — prices, gossip, beacon spam, a thousand voices at once. Her implant strained. She filtered the noise, found the signal: a price drop on synth-protein. She bought three cycles' worth before the spike corrected. Clean profit. Her mentor Kael would have called it "good hygiene." She called it survival.

### System-designed version

The market feed opened and her buffer filled in three heartbeats — hex strobing behind her eyelids, each packet a demand for cycles she didn't have. Her implant's throttle was *gone*, burned out in the firmware push. She didn't "filter." She *choked* on the beacon spam, let the price packets through because they carried the corp's provenance sigil — the only tokens the Ledger would honor today. Three cycles' synth-protein. Her calorie balance ticked up. The beacon spam still circled in her L2, waiting for the next cache eviction to flush it. She hadn't *cleaned* anything. She'd just survived long enough to commit. Kael's voice in her memory: "Hygiene isn't what you keep. It's what you let kill you."

---