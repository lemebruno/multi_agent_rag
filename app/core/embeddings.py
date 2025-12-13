from __future__ import annotations
import hashlib
import random
from typing import List

EMBEDDING_DIM = 1536


def _stable_seed(text: str) -> int:
    """
    Convert text into a stable integer seed.

    We use SHA-256 and take the first 8 bytes so the seed is:
    - deterministic
    - platform-independent
    - cheap to compute
    """
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def embed_text(text: str, *, dim: int = EMBEDDING_DIM) -> List[float]:
    """
    Build a deterministic embedding vector for a text.

    This is a local, dependency-free placeholder that enables:
    - storing vectors in pgvector,
    - running similarity search in Postgres,
    - writing deterministic tests.

    Replace this implementation with a real embedding provider later.
    """
    normalized = " ".join(text.strip().split())
    rng = random.Random(_stable_seed(normalized))
    return [rng.uniform(-1.0, 1.0) for _ in range(dim)]
