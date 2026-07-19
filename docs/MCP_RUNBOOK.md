# CockroachDB Managed MCP runbook

The Managed MCP Server is the second runtime-facing CockroachDB tool in the project. It gives a Codex operator read-only, audited access to the same persistent memory used by the Lambda agent.

## Verified live setup

Verified on July 19, 2026 with the CockroachDB Cloud Managed MCP server and Codex CLI 0.144.6. OAuth authentication succeeded in read-only mode. The MCP tools listed `defaultdb`, retrieved the `decisions` and `audit_events` schemas, and confirmed the 1,024-dimensional `embedding` column and cosine vector index without modifying data.

## Connect

1. Open the CockroachDB Cloud cluster.
2. Open the MCP configuration provided by the Cloud Console.
3. Configure the client with the generated endpoint and credentials.
4. Keep the connection read-only for judging and demonstration.

Do not commit MCP credentials or database connection strings.

## Demonstration queries

Ask the operator agent to:

1. Inspect the `decisions` and `audit_events` schemas.
2. Confirm that the vector index `decisions_embedding_idx` exists.
3. List decision versions sharing one `lineage_id`.
4. Show which decision IDs were retrieved for the latest audit.
5. Confirm that the Lambda application's recommendation is traceable to stored memories.

This proves that the memory layer is inspectable outside the application and that access is audit logged rather than hidden behind a custom proxy.
