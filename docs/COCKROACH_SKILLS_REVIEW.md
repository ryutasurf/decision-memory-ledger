# CockroachDB Agent Skills review log

The project uses the official CockroachDB Codex plugin and its upstream Agent Skills as an engineering review layer. Before the final submission, record the actual Skill names and resulting changes here.

Required review passes:

- Schema design: UUID keys, version uniqueness, JSONB use, transaction boundaries.
- Vector search: vector dimensions, index syntax, distance operator, query plan.
- Security: least-privilege SQL user, secret handling, read-only MCP access.
- Operations: retry behavior, observability, backup and failure handling.

## Review evidence

To be completed after the CockroachDB Cloud cluster and official plugin are connected. Do not claim a review that has not been run.

