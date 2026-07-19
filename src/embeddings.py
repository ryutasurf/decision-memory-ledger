import hashlib
import json
import math
import os

import boto3

VECTOR_DIMENSIONS = 1024


def _normalize(values: list[float]) -> list[float]:
    length = math.sqrt(sum(value * value for value in values)) or 1.0
    return [value / length for value in values]


def _local_embedding(text: str) -> list[float]:
    """Deterministic local fallback for tests; production uses Bedrock."""
    values = [0.0] * VECTOR_DIMENSIONS
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % VECTOR_DIMENSIONS
        values[index] += 1.0 if digest[4] % 2 == 0 else -1.0
    return _normalize(values)


def embed(text: str) -> list[float]:
    model_id = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
    try:
        client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": text, "dimensions": VECTOR_DIMENSIONS, "normalize": True}),
        )
        payload = json.loads(response["body"].read())
        return payload["embedding"]
    except Exception:
        if os.getenv("ALLOW_LOCAL_EMBEDDINGS", "false").lower() == "true":
            return _local_embedding(text)
        raise

