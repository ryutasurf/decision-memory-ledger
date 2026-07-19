import json
import os
import uuid
from contextlib import contextmanager

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row

from .embeddings import VECTOR_DIMENSIONS


@contextmanager
def connection():
    database_url = os.environ["DATABASE_URL"]
    connection_args = conninfo_to_dict(database_url)
    # CockroachDB's copied connection string can reference a certificate file
    # on the developer's computer. Lambda does not have that file, so use its
    # trusted system certificate store while retaining full TLS verification.
    connection_args["sslrootcert"] = "system"
    connection_args.setdefault("sslmode", "verify-full")
    with psycopg.connect(**connection_args, row_factory=dict_row) as conn:
        yield conn


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def init_schema() -> None:
    statements = [
        f"""
        CREATE TABLE IF NOT EXISTS decisions (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          lineage_id UUID NOT NULL,
          version INT8 NOT NULL,
          title STRING NOT NULL,
          objective STRING NOT NULL,
          observations JSONB NOT NULL,
          interpretation STRING NOT NULL,
          counterevidence JSONB NOT NULL,
          invalidation_conditions JSONB NOT NULL,
          action STRING NOT NULL,
          regime STRING NOT NULL,
          memory_text STRING NOT NULL,
          embedding VECTOR({VECTOR_DIMENSIONS}) NOT NULL,
          supersedes UUID NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          UNIQUE (lineage_id, version)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS audit_events (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          question STRING NOT NULL,
          retrieved_decision_ids UUID[] NOT NULL,
          verdict STRING NOT NULL,
          rationale STRING NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """,
        "CREATE VECTOR INDEX IF NOT EXISTS decisions_embedding_idx ON decisions (embedding vector_cosine_ops)",
    ]
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SET use_declarative_schema_changer = 'unsafe_always'")
            for statement in statements:
                cur.execute(statement)
        conn.commit()


def create_decision(payload: dict, embedding: list[float], supersedes: str | None = None) -> dict:
    memory_text = "\n".join([
        payload["title"], payload["objective"], *payload["observations"],
        payload["interpretation"], *payload["counterevidence"],
        *payload["invalidation_conditions"], payload["action"], payload["regime"],
    ])
    with connection() as conn:
        with conn.cursor() as cur:
            if supersedes:
                cur.execute("SELECT lineage_id, version FROM decisions WHERE id = %s", (supersedes,))
                prior = cur.fetchone()
                if not prior:
                    raise KeyError("superseded decision not found")
                lineage_id, version = prior["lineage_id"], prior["version"] + 1
            else:
                lineage_id, version = uuid.uuid4(), 1
            cur.execute(
                """
                INSERT INTO decisions (
                  lineage_id, version, title, objective, observations, interpretation,
                  counterevidence, invalidation_conditions, action, regime, memory_text,
                  embedding, supersedes
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::VECTOR,%s)
                RETURNING id, lineage_id, version, title, objective, observations,
                  interpretation, counterevidence, invalidation_conditions, action,
                  regime, supersedes, created_at
                """,
                (
                    lineage_id, version, payload["title"], payload["objective"],
                    json.dumps(payload["observations"]), payload["interpretation"],
                    json.dumps(payload["counterevidence"]),
                    json.dumps(payload["invalidation_conditions"]), payload["action"],
                    payload["regime"], memory_text, vector_literal(embedding), supersedes,
                ),
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def search_memories(embedding: list[float], limit: int = 5) -> list[dict]:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, lineage_id, version, title, objective, observations,
                  interpretation, counterevidence, invalidation_conditions, action,
                  regime, created_at, 1 - (embedding <=> %s::VECTOR) AS similarity
                FROM decisions
                ORDER BY embedding <=> %s::VECTOR
                LIMIT %s
                """,
                (vector_literal(embedding), vector_literal(embedding), limit),
            )
            return [dict(row) for row in cur.fetchall()]


def record_audit(question: str, memories: list[dict], verdict: str, rationale: str) -> None:
    ids = [memory["id"] for memory in memories]
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO audit_events
                   (question, retrieved_decision_ids, verdict, rationale)
                   VALUES (%s, %s, %s, %s)""",
                (question, ids, verdict, rationale),
            )
        conn.commit()
