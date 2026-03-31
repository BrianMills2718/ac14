"""Tests for persisted external retrieval artifacts."""

from __future__ import annotations

from pathlib import Path

from ac14.retrieval import (
    RepoRetrievalQuery,
    RetrievedRepoMatch,
    RetrievedWebDocument,
    WebRetrievalQuery,
    build_external_retrieval_artifact,
)


def test_build_external_retrieval_artifact_persists_reviewable_context(
    tmp_path: Path,
) -> None:
    """External retrieval artifact should persist reviewable web and repo context."""

    artifact = build_external_retrieval_artifact(
        output_dir=tmp_path / "retrieval",
        web_queries=[
            WebRetrievalQuery(query="context management for coding agents", top_k=2),
        ],
        repo_queries=[
            RepoRetrievalQuery(query="packet compiler", repos=["example/ac14"], limit=3),
        ],
        web_retriever=lambda _query: [
            RetrievedWebDocument(
                query="context management for coding agents",
                provider="fixture",
                url="https://example.com/context",
                title="Context Note",
                publisher="Example",
                snippet="context snippet",
                preview="context preview",
            ),
        ],
        repo_retriever=lambda _query: [
            RetrievedRepoMatch(
                query="packet compiler",
                repository="example/ac14",
                path="ac14/packets.py",
                url="https://github.com/example/ac14/blob/main/ac14/packets.py",
            ),
        ],
    )

    assert len(artifact.web_documents) == 1
    assert len(artifact.repo_matches) == 1
    assert (tmp_path / "retrieval" / "external_retrieval_artifact.json").exists()
