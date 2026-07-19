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
    model_id = os.getenv("BEDROCK_EMBED_MODEL_ID", "cohere.embed-multilingual-v3")
    try:
        client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        if model_id.startswith("cohere.embed"):
            request = {
                "texts": [text],
                "input_type": "search_document",
                "embedding_types": ["float"],
            }
        else:
            request = {
                "inputText": text,
                "dimensions": VECTOR_DIMENSIONS,
                "normalize": True,
            }
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request),
        )
        payload = json.loads(response["body"].read())
        if model_id.startswith("cohere.embed"):
            embeddings = payload["embeddings"]
            if isinstance(embeddings, dict):
                return embeddings["float"][0]
            return embeddings[0]
        return payload["embedding"]
    except Exception:
        if os.getenv("ALLOW_LOCAL_EMBEDDINGS", "false").lower() == "true":
            return _local_embedding(text)
        raise
