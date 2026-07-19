from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DecisionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    objective: str = Field(min_length=3)
    observations: list[str] = Field(min_length=1)
    interpretation: str = Field(min_length=3)
    counterevidence: list[str] = Field(default_factory=list)
    invalidation_conditions: list[str] = Field(default_factory=list)
    action: str = Field(min_length=1)
    regime: str = Field(default="unspecified", max_length=80)


class DecisionRecord(DecisionCreate):
    id: str
    version: int
    created_at: datetime


class AuditRequest(BaseModel):
    question: str = Field(min_length=5)
    observations: list[str] = Field(default_factory=list)


class AuditResponse(BaseModel):
    verdict: Literal["continue", "modify", "withdraw", "insufficient_evidence"]
    rationale: str
    retrieved_memories: list[dict]
    changed_since_prior: list[str]
    next_test: str
    invalidation_conditions: list[str]

