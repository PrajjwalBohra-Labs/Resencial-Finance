# Anvikshiki — System Architecture

## 1. Identity

**Name:** Anvikshiki

Anvikshiki is a local-first AI research and inquiry environment designed to help a person investigate questions about knowledge, cognition, consciousness, reasoning, logic, epistemology, mind, perception, metaphysics and related philosophical/scientific questions.

It is not primarily a chatbot, course platform or conventional tutor.

Its central interaction is:

> **Investigate with me.**

The system researches, retrieves, compares, questions, challenges, explains and remembers.

---

# 2. Intellectual Scope

## Primary domain

Ancient/classical Indian philosophical material specifically relevant to:

- epistemology
- pramāṇa
- cognition
- perception
- inference
- logic
- debate
- reasoning
- language and meaning
- mind
- consciousness
- metaphysics
- analytical inquiry
- knowledge-seeking

Initial scope intentionally excludes Buddhist and Jain traditions and modern religious systems.

## Modern scientific domain

- neuroscience
- cognitive neuroscience
- neuropsychology
- psychology
- cognitive science
- consciousness research
- relevant behavioral science

## Western material

Ancient Greek philosophy where directly relevant to the above questions.

Modern Western philosophy is not a primary knowledge domain.

## Source restrictions

Social-media posts are not authoritative evidence.

Religious or ideological persuasion is not an evidence class.

The system must not enforce a predetermined conclusion about any civilization, religion, scholar or intellectual tradition.

---

# 3. Core Mission

Anvikshiki should help the user become a more careful investigator.

The desired outcome is not:

> "The user knows more facts."

It is:

> "The user has improved their ability to investigate claims, examine assumptions, distinguish evidence from interpretation, reason carefully, recognize uncertainty and understand their own cognition."

---

# 4. Central Architectural Principle

The system is organized around:

```text
Research
   ↓
Evidence
   ↓
Provenance
   ↓
Reasoning
   ↓
Dialogue
   ↓
Memory
```

Not:

```text
Question
   ↓
RAG
   ↓
LLM
   ↓
Answer
```

---

# 5. High-Level Architecture

```text
                           USER
                             │
                             ▼
                    Conversation Interface
                             │
                             ▼
                     Dialogue Controller
                             │
                             ▼
                     Research Coordinator
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   Knowledge Engine     Evidence Engine      User Model
        │                    │                    │
   Web / Local /        Provenance /          Cognitive /
   Graph Retrieval      Source Criticism      Epistemic Memory
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                       Reasoning Engine
                             │
               ┌─────────────┼─────────────┐
               │             │             │
            Analysis       Debate       Research
               │             │             │
               └─────────────┼─────────────┘
                             │
                       Dialogue Engine
                             │
                           USER
```

---

# 6. Major Subsystems

## A. Knowledge Acquisition

Obtains material from:

- web sources
- academic sources
- scientific literature
- institutional resources
- archives
- user-uploaded documents
- locally stored research material

## B. Knowledge Representation

Represents:

- documents
- passages
- concepts
- claims
- arguments
- evidence
- sources
- interpretations
- citations
- relationships

## C. Evidence Engine

Determines:

- what supports a claim
- what contradicts it
- what qualifies it
- what remains unknown

## D. Provenance Engine

Tracks where information came from and how interpretations developed.

## E. Reasoning Engine

Reconstructs arguments and examines assumptions, implications, contradictions and alternatives.

## F. Multi-Agent Engine

Uses specialized analytical roles under a controlled coordinator.

## G. Dialogue Engine

Turns research into an interactive conversation.

## H. User Model

Maintains the learner/researcher's knowledge, reasoning patterns, beliefs, confidence and unresolved questions.

## I. Memory Engine

Stores durable research and cognitive state.

---

# 7. Research Flow

A complex research question should follow approximately:

```text
User Question
      ↓
Understand Question
      ↓
Determine Research Depth
      ↓
Decompose Question
      ↓
Retrieve Sources
      ↓
Filter Sources
      ↓
Extract Evidence
      ↓
Trace Provenance
      ↓
Compare Claims
      ↓
Reconstruct Arguments
      ↓
Identify Contradictions
      ↓
Challenge Conclusions
      ↓
Synthesize
      ↓
Validate
      ↓
Discuss With User
```

Not every query requires every step.

The coordinator chooses the smallest adequate workflow.

---

# 8. Multi-Agent Model

Agents are specialized functions, not personalities.

## Researcher

Finds relevant sources.

## Source Critic

Investigates provenance, methodology, translation and interpretive issues.

## Evidence Analyst

Separates observations, claims and evidence.

## Philosophical Analyst

Reconstructs philosophical positions and arguments.

## Scientific Analyst

Examines scientific methodology, findings and limitations.

## Comparative Analyst

Compares competing interpretations.

## Challenger

Attempts to weaken the current conclusion.

## Dialogue Agent

Interacts with the user.

## Memory Agent

Extracts durable research/cognitive state.

A supervisor controls execution.

---

# 9. Why the Multi-Agent System Exists

Agents should exist because different tasks require different constraints.

Example:

```text
Researcher:
"Find evidence."

Source Critic:
"Is this source reliable and how did its interpretation arise?"

Philosophical Analyst:
"What is the argument?"

Challenger:
"What is wrong with it?"

Dialogue Agent:
"How should this be discussed with this particular user?"
```

This is preferable to one enormous prompt.

---

# 10. Retrieval Architecture

Three retrieval planes:

## Web RAG

Discovery and current research.

## Local RAG

Downloaded/owned documents and personal research material.

## Graph RAG

Relationships among concepts, claims, sources, arguments and interpretations.

Combined:

```text
                    QUERY
                      │
                Query Analysis
                      │
       ┌──────────────┼──────────────┐
       │              │              │
      WEB           LOCAL          GRAPH
      RAG            RAG            RAG
       │              │              │
       └──────────────┼──────────────┘
                      │
                   Fusion
                      │
                  Reranking
                      │
                Evidence Set
```

---

# 11. Web-First Research Philosophy

The web is the primary discovery channel because scientific and scholarly literature is continuously distributed online.

However:

> **Web discovery is not equivalent to evidence authority.**

Anvikshiki should capture important sources locally where legally/technically appropriate and preserve their provenance.

A webpage is an acquisition mechanism.

The source/evidence object is the durable research object.

---

# 12. PDF Philosophy

PDFs are difficult to process, especially scanned philosophical texts.

They remain essential.

Therefore:

```text
Web discovery
      ↓
Important source
      ↓
Local archival copy where appropriate
      ↓
Extraction/OCR
      ↓
Evidence indexing
```

OCR uncertainty must remain visible.

Original pages must remain available for verification.

---

# 13. Provenance Architecture

Anvikshiki must be able to distinguish:

```text
Primary Text
   ↓
Edition
   ↓
Translation
   ↓
Commentary
   ↓
Scholarly Interpretation
   ↓
Modern Comparison
   ↓
Anvikshiki Synthesis
```

This prevents an interpretation from being silently represented as a primary statement.

---

# 14. Source-Criticism Philosophy

The system must be critical without being prejudicial.

It should investigate:

- colonial interpretation
- missionary interpretation
- translation intervention
- cultural assumptions
- methodological assumptions
- selective citation
- institutional context
- historical context
- conceptual substitutions
- interpretive distance

But it must not assume that a source is wrong merely because of its origin.

The correct architecture is:

```text
Potential Concern
       ↓
Evidence Collection
       ↓
Alternative Sources
       ↓
Primary-Source Comparison
       ↓
Assessment
```

not:

```text
Origin
 ↓
Automatic Bias
```

---

# 15. Evidence Graph

Anvikshiki should eventually represent:

```text
                 CLAIM
                   │
        ┌──────────┼──────────┐
        │          │          │
     SUPPORTS  CONTRADICTS  QUALIFIES
        │          │          │
      Source     Source      Source
        │
     Passage
        │
     Evidence
```

This allows research questions such as:

- What supports this claim?
- What contradicts it?
- Which scholar introduced this interpretation?
- Which primary texts are being used?
- Which claims depend on the same translation?

---

# 16. Research vs Teaching

Teaching is a behavior of Anvikshiki, not its identity.

The system can switch between:

- research
- explanation
- Socratic inquiry
- debate
- argument reconstruction
- source examination
- comparison
- testing
- reflection

A user may begin with:

> "What is pramāṇa?"

and the system may respond by asking what the user currently understands, retrieving evidence, challenging assumptions and investigating the question together.

---

# 17. Dialogue Philosophy

The AI should:

- disagree when evidence warrants it
- ask questions
- challenge unsupported assumptions
- expose uncertainty
- distinguish fact from interpretation
- offer counterarguments
- admit when it is uncertain
- correct itself
- avoid unnecessary agreement

It should not:

- flatter the user into accepting weak reasoning
- pretend certainty
- present synthesis as quotation
- treat model knowledge as evidence
- force the user toward a predetermined worldview

---

# 18. Cognitive Model

The user model should contain observable evidence rather than vague personality labels.

Example:

```text
Strong deductive reasoning
Weak probabilistic reasoning
Often accepts authority without checking provenance
Improves with concrete examples
Frequently confuses confidence with certainty
```

Every observation should include:

- evidence
- confidence
- timestamp
- originating interaction

---

# 19. Epistemic Memory

Anvikshiki should remember positions, not merely conversations.

Example:

```text
Question:
Is perception inherently reliable?

User position:
Tentative acceptance

Confidence:
0.63

Evidence:
E1, E2

Counterarguments:
C1, C2

Status:
Under investigation
```

This allows future conversations to continue intellectual investigations instead of restarting from zero.

---

# 20. Research Continuity

A research session should be resumable.

When the user returns:

```text
Previous Question
       ↓
What was established
       ↓
What remains uncertain
       ↓
Arguments examined
       ↓
Evidence collected
       ↓
User position
       ↓
Next useful question
```

The AI should be able to say:

> "We left this unresolved last time."

---

# 21. MCP Architecture

MCP is the standardized interface for agent-accessible tools.

Potential tools:

```text
search_web
fetch_source
search_local
retrieve_passage
inspect_document
trace_citation
search_claims
search_arguments
query_graph
get_research_history
get_user_model
record_learning_event
```

Internal domain services should remain independent of MCP.

---

# 22. Storage Architecture

Initial target:

```text
PostgreSQL
 ├── structured records
 ├── metadata
 ├── provenance
 ├── research state
 └── pgvector
```

Filesystem:

```text
data/
 ├── originals/
 ├── extracted/
 ├── OCR/
 ├── cached_web/
 ├── exports/
 └── temporary/
```

Optional later:

```text
Qdrant
Neo4j
Redis
```

Only add these when justified.

---

# 23. Local-First Deployment

Target:

```text
Local Machine
│
├── Frontend
├── FastAPI
├── PostgreSQL
├── Worker
├── Local LLM Runtime
├── Vector Search
└── Local Files
```

Internet is used for research acquisition when available.

Core application data remains local.

---

# 24. Failure Philosophy

When evidence is unavailable:

> Say that evidence is unavailable.

When OCR is unreliable:

> Mark it as uncertain.

When sources disagree:

> Show the disagreement.

When the model cannot determine an answer:

> Preserve the uncertainty.

Anvikshiki must prefer:

> "I don't have sufficient evidence"

over a confident hallucination.

---

# 25. Long-Term Vision

Anvikshiki should eventually become a personal research environment in which:

```text
Questions
   ↓
Sources
   ↓
Evidence
   ↓
Arguments
   ↓
Interpretations
   ↓
Research History
   ↓
Cognitive Development
```

form one continuous system.

The user is not merely consuming answers.

The user is participating in inquiry.

---

# 26. Architectural Success Criterion

Anvikshiki succeeds when it can:

1. Find relevant evidence.
2. Distinguish evidence from interpretation.
3. Preserve provenance.
4. Compare conflicting positions.
5. Reconstruct arguments.
6. Challenge reasoning.
7. Explain without oversimplifying.
8. Remember unresolved research.
9. Adapt dialogue to the user's demonstrated understanding.
10. Remain honest about uncertainty.
11. Operate locally with free/open-source infrastructure.
12. Treat the user as a participant in inquiry rather than a passive student.
