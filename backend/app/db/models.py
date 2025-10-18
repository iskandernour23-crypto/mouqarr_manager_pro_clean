from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, LargeBinary, String, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    tool_name = Column(String(64), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role": self.role,
            "content": self.content,
            "tool_name": self.tool_name,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat(),
        }


class AIEmbedding(Base):
    __tablename__ = "ai_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(128), nullable=False, index=True)
    chunk = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=False)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def embedding_to_list(self) -> Optional[list[float]]:
        try:
            return json.loads(self.embedding.decode("utf-8"))
        except Exception:
            return None

    @staticmethod
    def from_values(
        doc_id: str,
        chunk: str,
        vector: list[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "AIEmbedding":
        payload = json.dumps(vector).encode("utf-8")
        meta_str = json.dumps(metadata or {})
        record = AIEmbedding(
            doc_id=doc_id,
            chunk=chunk,
            embedding=payload,
            metadata=meta_str,
        )
        return record
