from __future__ import annotations

import hashlib
import math
from typing import List, Sequence, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import AIEmbedding


async def _ensure_seed_data(session: AsyncSession) -> None:
    count = (await session.execute(select(AIEmbedding))).scalars().first()
    if count:
        return
    seed_documents = [
        (
            "readme_policy",
            "يصف هذا المستند سياسات السكن، يجب إشعار المقيمين بأي صيانة مجدولة قبل 48 ساعة.",
        ),
        (
            "schema_overview",
            "Residents(id, name, phone, unit, start_date) مرتبطون بالمدفوعات Payments(resident_id, month, amount, status).",
        ),
    ]
    for doc_id, chunk in seed_documents:
        embedding = _mock_embed(chunk)
        record = AIEmbedding.from_values(doc_id=doc_id, chunk=chunk, vector=embedding, metadata={"source": doc_id})
        session.add(record)
    await session.flush()


def _mock_embed(text: str) -> List[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [byte / 255.0 for byte in digest[:64]]


def _cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def search_context(session: AsyncSession, query: str, limit: int = 4) -> List[Tuple[str, float]]:
    await _ensure_seed_data(session)
    query_vec = _mock_embed(query)
    rows = (await session.execute(select(AIEmbedding))).scalars().all()
    scored: List[Tuple[str, float]] = []
    for row in rows:
        vector = row.embedding_to_list()
        if not vector:
            continue
        score = _cosine_similarity(query_vec, vector)
        scored.append((f"{row.doc_id}:{row.chunk}", score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


async def gather_context_chunks(session: AsyncSession, query: str, limit: int = 4) -> str:
    matches = await search_context(session, query=query, limit=limit)
    return "\n".join(chunk for chunk, _ in matches)
