import json
import os

import boto3


SYSTEM = """You are a decision-memory auditor. Use retrieved prior decisions as evidence,
not authority. Separate current observations from interpretations. Detect what changed,
surface counterevidence, prefer reversible tests, and state explicit invalidation conditions.
Return strict JSON with keys: verdict, rationale, changed_since_prior, next_test,
invalidation_conditions. verdict must be continue, modify, withdraw, or insufficient_evidence."""


def _fallback(question: str, observations: list[str], memories: list[dict]) -> dict:
    if not observations:
        verdict = "insufficient_evidence"
    elif any("zero" in item.lower() or "0" == item.strip() for item in observations):
        verdict = "modify"
    else:
        verdict = "insufficient_evidence"
    return {
        "verdict": verdict,
        "rationale": "Local deterministic mode: prior decisions were retrieved, but a production judgment requires Bedrock.",
        "changed_since_prior": ["Current observations must be compared with the retrieved record."],
        "next_test": "Run the smallest reversible test that can distinguish the leading explanations.",
        "invalidation_conditions": ["New evidence contradicts the current interpretation."],
    }


def audit(question: str, observations: list[str], memories: list[dict]) -> dict:
    compact_memories = [
        {key: memory[key] for key in ("id", "title", "objective", "interpretation", "action", "regime", "similarity")}
        for memory in memories
    ]
    prompt = json.dumps({"question": question, "observations": observations, "prior_decisions": compact_memories}, default=str)
    try:
        client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        response = client.converse(
            modelId=os.getenv("BEDROCK_CHAT_MODEL_ID", "amazon.nova-lite-v1:0"),
            system=[{"text": SYSTEM}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.1, "maxTokens": 1200},
        )
        text = response["output"]["message"]["content"][0]["text"]
        start, end = text.find("{"), text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        if os.getenv("ALLOW_LOCAL_EMBEDDINGS", "false").lower() == "true":
            return _fallback(question, observations, memories)
        raise

