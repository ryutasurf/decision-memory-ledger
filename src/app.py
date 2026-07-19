from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from mangum import Mangum

from .agent import audit
from .db import create_decision, init_schema, record_audit, search_memories
from .embeddings import embed
from .models import AuditRequest, AuditResponse, DecisionCreate

app = FastAPI(title="Decision Memory Ledger", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
def home():
    return (Path(__file__).parent.parent / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "ok", "memory": "CockroachDB", "agent": "AWS Bedrock"}


@app.post("/schema/init")
def schema_init():
    init_schema()
    return {"status": "initialized"}


@app.post("/decisions")
def decisions(payload: DecisionCreate, supersedes: str | None = None):
    data = payload.model_dump()
    text = "\n".join([payload.title, payload.objective, *payload.observations, payload.interpretation, payload.action])
    try:
        return create_decision(data, embed(text), supersedes=supersedes)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/audit", response_model=AuditResponse)
def run_audit(payload: AuditRequest):
    query = "\n".join([payload.question, *payload.observations])
    memories = search_memories(embed(query))
    result = audit(payload.question, payload.observations, memories)
    record_audit(payload.question, memories, result["verdict"], result["rationale"])
    return {**result, "retrieved_memories": memories}


handler = Mangum(app)

