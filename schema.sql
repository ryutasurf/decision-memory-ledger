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
  embedding VECTOR(1024) NOT NULL,
  supersedes UUID NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (lineage_id, version)
);

CREATE TABLE IF NOT EXISTS audit_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question STRING NOT NULL,
  retrieved_decision_ids UUID[] NOT NULL,
  verdict STRING NOT NULL,
  rationale STRING NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

SET use_declarative_schema_changer = 'unsafe_always';

CREATE VECTOR INDEX IF NOT EXISTS decisions_embedding_idx
ON decisions (embedding vector_cosine_ops);

SHOW TABLES;
SHOW INDEXES FROM decisions;
