"""Small, local hybrid memory proof of concept for the Day 19 bonus."""
from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi

from app.embeddings import Embedder


class HybridMemoryAgent:
    """Keep user-scoped memories in Qdrant and read user context from Feast."""

    COLLECTION = "personal_memories"
    FEATURES = [
        "user_profile_features:preferred_language",
        "user_profile_features:reading_speed_wpm",
        "user_profile_features:topic_affinity",
        "query_velocity_features:queries_last_hour",
    ]

    def __init__(self, client=None, feature_store=None, embedder=None):
        self.client = client or QdrantClient(":memory:")
        self.embedder = embedder or Embedder()
        if feature_store is None:
            repo = Path(__file__).resolve().parent.parent / "app" / "feast_repo"
            if (repo / "registry.db").exists():
                from feast import FeatureStore
                feature_store = FeatureStore(repo_path=str(repo))
        self.feature_store = feature_store
        if not self.client.collection_exists(self.COLLECTION):
            self.client.create_collection(
                collection_name=self.COLLECTION,
                vectors_config=models.VectorParams(
                    size=self.embedder.dim, distance=models.Distance.COSINE
                ),
            )

    @staticmethod
    def _chunks(text: str):
        """Keep paragraph boundaries; split long paragraphs at word boundaries."""
        for paragraph in re.split(r"\n\s*\n", text.strip()):
            words = paragraph.split()
            while words:
                chunk, length = [], 0
                while words and (length + len(words[0]) <= 600 or not chunk):
                    word = words.pop(0)
                    chunk.append(word)
                    length += len(word) + 1
                yield " ".join(chunk)

    def remember(self, text: str, user_id: str = "u_001") -> None:
        """Embed and upsert this user's new episodic memory."""
        if not user_id.strip() or not text.strip():
            raise ValueError("user_id and text must be non-empty")
        chunks = list(self._chunks(text))
        vectors = list(self.embedder.embed(chunks))
        self.client.upsert(
            collection_name=self.COLLECTION,
            points=[
                models.PointStruct(
                    id=str(uuid4()), vector=vector.tolist(),
                    payload={"user_id": user_id, "text": chunk},
                )
                for chunk, vector in zip(chunks, vectors)
            ],
        )

    def _user_memories(self, user_id: str):
        selector = models.Filter(must=[models.FieldCondition(
            key="user_id", match=models.MatchValue(value=user_id)
        )])
        points = []
        offset = None
        while True:
            page, offset = self.client.scroll(
                collection_name=self.COLLECTION, scroll_filter=selector,
                limit=100, offset=offset, with_payload=True,
            )
            points.extend(page)
            if offset is None:
                return selector, points

    def _profile(self, user_id: str) -> dict:
        if self.feature_store is None:
            return {}
        result = self.feature_store.get_online_features(
            features=self.FEATURES, entity_rows=[{"user_id": user_id}]
        ).to_dict()
        return {key: values[0] for key, values in result.items() if key != "user_id"}

    def recall(self, query: str, user_id: str = "u_001") -> str:
        """Fuse BM25 and vector ranks, then assemble grounded user context."""
        if not user_id.strip() or not query.strip():
            raise ValueError("user_id and query must be non-empty")
        selector, memories = self._user_memories(user_id)
        profile = self._profile(user_id)
        if not memories:
            return f"User: {user_id}\nProfile: {profile}\nTop memories: none"

        depth = min(20, len(memories))
        bm25 = BM25Okapi([p.payload["text"].lower().split() for p in memories])
        scores = bm25.get_scores(query.lower().split())
        lexical = [str(memories[i].id) for i in sorted(
            range(len(memories)), key=lambda i: -scores[i]
        )[:depth]]
        vector = next(self.embedder.embed([query])).tolist()
        semantic = [str(p.id) for p in self.client.query_points(
            collection_name=self.COLLECTION, query=vector,
            query_filter=selector, limit=depth,
        ).points]
        rrf = {}
        for ranking in (lexical, semantic):
            for rank, point_id in enumerate(ranking, start=1):
                rrf[point_id] = rrf.get(point_id, 0.0) + 1 / (60 + rank)
        by_id = {str(p.id): p.payload["text"] for p in memories}
        top = sorted(rrf, key=lambda point_id: -rrf[point_id])[:3]
        lines = [f"User: {user_id}", f"Profile: {profile}",
                 f"Memory IDs: {top}", "Top memories:"]
        lines.extend(f"- {by_id[point_id]}" for point_id in top)
        return "\n".join(lines)
