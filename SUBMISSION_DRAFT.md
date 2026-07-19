# Devpost submission draft

## Project name

Decision Memory Ledger

## Tagline

An agent that remembers why decisions changed—not just what users said.

## Inspiration

Most AI memory stores facts, preferences, or conversation summaries. That is not enough for consequential judgment. A useful memory must preserve the objective, evidence available at the time, interpretation, counterevidence, action, and conditions that would reverse the decision.

After previously extracting an inspectable decision method from seven years of timestamped market records, I wanted to test the next question: can an agent retain that method across time without collapsing old conclusions into timeless truth?

## What it does

Decision Memory Ledger commits every decision as a versioned causal record in CockroachDB. Amazon Bedrock creates an embedding, and CockroachDB Distributed Vector Indexing retrieves semantically similar past decisions when a new case arrives. A Bedrock-powered agent compares current observations with retrieved history, explains what changed, and returns one of four outcomes: continue, modify, withdraw, or insufficient evidence.

The agent also records which memories it used. Through CockroachDB Managed MCP, an operator can independently inspect the schema, vector index, decision lineage, and audit trail. Memory is therefore persistent, semantic, transactional, and externally auditable.

## How we built it

- FastAPI and Mangum on AWS Lambda
- Amazon Bedrock Titan Text Embeddings V2
- Amazon Nova on Bedrock for structured audits
- CockroachDB as the transactional system of record
- CockroachDB Distributed Vector Indexing for semantic memory retrieval
- CockroachDB Managed MCP for inspectable operator access
- Official CockroachDB Agent Skills for schema, vector, security, and operations review
- AWS SAM for reproducible deployment

## Challenges

The central problem was preventing memory from becoming authority. A past decision may be coherent and still be wrong under a new regime. The retrieval layer therefore supplies evidence, while the audit layer must surface counterevidence, identify changes, and state explicit invalidation conditions.

The second challenge was making memory use inspectable. The system records retrieved decision IDs for every audit and exposes the database through read-only Managed MCP, allowing an external agent to verify what the application actually remembered.

## Accomplishments

- Stored complete decision causality rather than chat summaries.
- Added explicit version lineage and supersession.
- Used transactional data and vectors in the same distributed database.
- Made every agent recommendation traceable to retrieved memory IDs.
- Separated identity and private biography from the reusable decision method.

## What we learned

The most useful long-term agent memory may not be a larger biography. It may be a disciplined record of which evidence mattered, what contradicted it, and what caused a human to change course.

## What's next

The next step is fidelity evaluation: give the original and memory-enabled agents the same unseen cases, measure differences in decision structure, and test whether the memory improves consistency without creating automation bias.

## Prior-work disclosure

The conceptual framing and decision-audit method build on the previously published Judgment Portability Layer. The CockroachDB schema, distributed vector memory, AWS agent, UI, APIs, audit ledger, and deployment in this submission were newly created during the hackathon period.

