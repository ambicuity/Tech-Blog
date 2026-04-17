from __future__ import annotations

import hashlib
import math
import re
from typing import Iterable


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _stable_index(token: str, dims: int) -> tuple[int, float]:
    raw = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    value = int.from_bytes(raw, "big", signed=False)
    idx = value % dims
    sign = -1.0 if (value >> 1) & 1 else 1.0
    return idx, sign


def embed_text(text: str, dims: int = 512) -> list[float]:
    """
    Lightweight deterministic text embedding using hashed unigram+bigram features.
    Produces L2-normalized vector for cosine comparisons without external deps.
    """
    vec = [0.0] * dims
    tokens = _tokenize(text)
    if not tokens:
        return vec

    features: list[str] = []
    features.extend(tokens)
    for i in range(len(tokens) - 1):
        features.append(tokens[i] + "_" + tokens[i + 1])

    for feat in features:
        idx, sign = _stable_index(feat, dims)
        vec[idx] += sign

    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return vec
    return [round(v / norm, 6) for v in vec]


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    a_list = list(a)
    b_list = list(b)
    if not a_list or not b_list or len(a_list) != len(b_list):
        return 0.0
    dot = sum(x * y for x, y in zip(a_list, b_list))
    na = math.sqrt(sum(x * x for x in a_list))
    nb = math.sqrt(sum(y * y for y in b_list))
    if na == 0 or nb == 0:
        return 0.0
    return round(dot / (na * nb), 6)
