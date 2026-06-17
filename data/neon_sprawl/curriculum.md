## DOCUMENT 2: CONCEPT CURRICULUM

### Teaching Principles

- **Concrete before abstract.** Every concept arrives as physical/practical experience first, label second.
- **Failure teaches.** Characters survive wrong understanding, then revise. No lecture without prior pain.
- **One hard concept per arc.** Easy concepts can pair with hard ones. Never two hard concepts together.
- **Repetition without re-teaching.** Once a concept is learned, later chapters use it naturally — no re-explanation.

### Arc Breakdown

| Arc | Chapters | Hard Concept | Easy Pairing | Narrative Engine |
|---|---|---|---|---|
| 1: First Jack-In | 1–3 | — | **Raw data ingestion / sensor fusion** | Lyra's implant firmware updates mid-shift, removing the factory throttle. She experiences the Sprawl's full packet flood for the first time — raw hex, beacon spam, telemetry storms — and nearly seizures in a crowded transit tube. A stranger's hand on her shoulder grounds her; she learns to *feel* the difference between signal and noise before she has words for either. |
| 2: The Vocab Wall | 4–6 | **Tokenization & vocabulary fixation** | — | Lyra takes her first corpus-curation contract: clean a dump of street-dialect chats for a corp sentiment model. She discovers her childhood slang registers as OOV — every utterance she submits is rejected, her cycle quota burns, her calorie balance drops. She must build a personal tokenizer that maps her dialect to valid tokens without triggering the substrate's fraud detection. |
| 3: Signal Hygiene | 7–10 | **Stop-word filtering & noise suppression** | — | A rival crew plants a covert ad-beacon inside a public weather feed. Lyra's pipeline ingests it, her attention mechanism weights the beacon higher than the actual query, and her next search routes to a competitor's shard — exposing her mentor's safehouse. She must design a filter that kills the beacon without killing the weather data, learning that *what you discard defines what you keep*. |
| 4: Canonical Forms | 11–14 | — | **Normalization & lemmatization** | Lyra's crew negotiates a territory swap with a rival gang. Both sides submit claims to the Ledger — but Lyra's normalization maps two distinct street concepts ("the Rust" and "the Scrap") to the same lemma. The Ledger merges them, the rival's claim overwrites hers, and the resulting turf war kills three friends. She learns to trace the collision back to her own lemma table. |
| 5: Pipeline Composition | 15–18 | **Preprocessing pipeline composition** | — | Lyra submits her first composed pipeline (ingest → tokenize → filter → normalize) for a high-value corp contract. It passes validation but hangs on normalize; the substrate rolls back only the first three stages. Her raw sensor logs — childhood memories, mentor's true name, her biometric root key — publish to the public ledger. She has hours to construct a compensating transaction before scrapers strip her identity. |
| 6: Drift & Poison | 19–22 | **Model drift / distributed fine-tuning coordination** | — | A sector-wide sentiment model begins hallucinating new districts. Lyra traces the drift to a poisoned corpus her own crew curated — a single malicious annotator flipped labels on 0.3% of tokens. The global model fine-tuned on it, shifted embeddings, and rewrote the Sprawl's geography. She must coordinate a distributed rollback across 47 nodes before the hallucination cements into consensus. |
| 7: Clean Feed | 23–25 | **Text preprocessing (climax)** | — | The Sprawl's central consensus layer enters a **preprocessing deadlock**: every node's pipeline emits tokens the others reject, the Ledger stalls, and the city freezes — no contracts, no identity, no food dispensers. Lyra must compose a *universal* preprocessing pipeline that every shard will accept, using every concept she's earned. The climax is not a battle but a **commit**: one atomic transaction that cleans the feed for the entire city. |

### Difficulty Scale Applied

- **2–3 (intuitive):** Raw data ingestion, sensor fusion, normalization, lemmatization — learnable from everyday analogy (filtering noise, finding the "true name"), no prior technical knowledge needed
- **4–5 (moderate):** Tokenization, vocabulary fixation, stop-word filtering, noise suppression, pipeline composition — requires holding two simultaneous processes in mind (what to keep vs. what to discard; stage ordering dependencies)
- **6–7 (hard):** Model drift detection, distributed fine-tuning coordination, provenance chain management — counter-intuitive, challenges existing mental models (local optimization corrupts global state; rollback requires consensus)
- **7+ (climactic):** **Text preprocessing (full pipeline orchestration under consensus deadlock)** — only lands after all prior concepts are earned; the novel's final teaching

---