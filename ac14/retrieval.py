"""Persisted external retrieval artifacts for discovery and planning."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any
from typing import Literal

from pydantic import BaseModel, Field


ProviderName = Literal["brave", "searxng", "tavily", "exa"]


def _default_web_providers() -> list[ProviderName]:
    """Return the default provider order for web retrieval."""

    return ["brave", "searxng"]


class WebRetrievalQuery(BaseModel):
    """Query spec for external documentation retrieval."""

    query: str = Field(description="Search query for external documentation retrieval.")
    top_k: int = Field(default=3, ge=1, le=10, description="Maximum documents to retain.")
    providers: list[ProviderName] = Field(
        default_factory=_default_web_providers,
        description="Open-web providers to use when configured.",
    )
    domains_allow: list[str] = Field(
        default_factory=list,
        description="Optional allow-list of domains for the query.",
    )
    domains_deny: list[str] = Field(
        default_factory=list,
        description="Optional deny-list of domains for the query.",
    )


class RepoRetrievalQuery(BaseModel):
    """Query spec for external repository search."""

    query: str = Field(description="Repository code-search query.")
    repos: list[str] = Field(
        default_factory=list,
        description="Optional GitHub repositories to scope the query to.",
    )
    limit: int = Field(default=5, ge=1, le=20, description="Maximum repository matches to retain.")


class RetrievedWebDocument(BaseModel):
    """Compact retrieved external documentation record."""

    query: str = Field(description="Query that produced this document.")
    provider: str = Field(description="Provider used for the search result.")
    url: str = Field(description="Final source URL.")
    title: str | None = Field(default=None, description="Document title.")
    publisher: str | None = Field(default=None, description="Best-effort publisher.")
    snippet: str | None = Field(default=None, description="Search-result snippet.")
    preview: str = Field(description="Compact extracted preview for planning context.")


class RetrievedRepoMatch(BaseModel):
    """Compact retrieved GitHub repository code-search match."""

    query: str = Field(description="Query that produced this code-search match.")
    repository: str = Field(description="Repository name or owner/name slug.")
    path: str = Field(description="Matched file path.")
    url: str | None = Field(default=None, description="GitHub URL when available.")


class ExternalRetrievalArtifact(BaseModel):
    """Persisted external retrieval artifact for reviewable planning context."""

    web_queries: list[WebRetrievalQuery] = Field(description="Executed web retrieval queries.")
    repo_queries: list[RepoRetrievalQuery] = Field(description="Executed repository search queries.")
    web_documents: list[RetrievedWebDocument] = Field(
        description="Retrieved external documentation summaries.",
    )
    repo_matches: list[RetrievedRepoMatch] = Field(
        description="Retrieved repository search matches.",
    )
    concerns: list[str] = Field(description="Retrieval concerns and gaps.")


def build_external_retrieval_artifact(
    output_dir: Path | str,
    *,
    web_queries: Sequence[WebRetrievalQuery] | None = None,
    repo_queries: Sequence[RepoRetrievalQuery] | None = None,
    web_retriever: Callable[[WebRetrievalQuery], list[RetrievedWebDocument]] | None = None,
    repo_retriever: Callable[[RepoRetrievalQuery], list[RetrievedRepoMatch]] | None = None,
) -> ExternalRetrievalArtifact:
    """Build and persist a reviewable external retrieval artifact."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    resolved_web_queries = list(web_queries or [])
    resolved_repo_queries = list(repo_queries or [])
    resolved_web_retriever = web_retriever or _default_web_retriever
    resolved_repo_retriever = repo_retriever or _default_repo_retriever

    web_documents: list[RetrievedWebDocument] = []
    repo_matches: list[RetrievedRepoMatch] = []
    concerns: list[str] = []

    for web_query in resolved_web_queries:
        docs = resolved_web_retriever(web_query)
        web_documents.extend(docs)
        if not docs:
            concerns.append(f"web query {web_query.query!r} returned no documents")

    for repo_query in resolved_repo_queries:
        matches = resolved_repo_retriever(repo_query)
        repo_matches.extend(matches)
        if not matches:
            concerns.append(f"repo query {repo_query.query!r} returned no matches")

    if not resolved_web_queries and not resolved_repo_queries:
        concerns.append("no external retrieval queries were requested")

    artifact = ExternalRetrievalArtifact(
        web_queries=resolved_web_queries,
        repo_queries=resolved_repo_queries,
        web_documents=web_documents,
        repo_matches=repo_matches,
        concerns=concerns,
    )
    (destination / "external_retrieval_artifact.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def _default_web_retriever(query: WebRetrievalQuery) -> list[RetrievedWebDocument]:
    """Retrieve external web documents using the shared open-web client."""

    fixture_path = os.environ.get("AC14_WEB_RETRIEVAL_FIXTURE")
    if fixture_path:
        fixture_payload = json.loads(Path(fixture_path).read_text())
        return [
            RetrievedWebDocument.model_validate(document)
            for document in fixture_payload.get(query.query, [])
        ]

    from open_web_retrieval import OpenWebRetrievalClient, SearchQuery

    client = OpenWebRetrievalClient(
        brave_api_key=os.environ.get("BRAVE_API_KEY"),
        exa_api_key=os.environ.get("EXA_API_KEY"),
        searxng_base_url=os.environ.get("SEARXNG_BASE_URL"),
        tavily_api_key=os.environ.get("TAVILY_API_KEY"),
        cache_dir=os.environ.get("AC14_OPEN_WEB_CACHE_DIR"),
    )
    try:
        batch = client.retrieve(
            SearchQuery(
                query=query.query,
                providers=tuple(query.providers),
                top_k=query.top_k,
                domains_allow=tuple(query.domains_allow),
                domains_deny=tuple(query.domains_deny),
            ),
            trace_id=f"ac14/retrieval/{_slug(query.query)}",
            task="ac14_external_retrieval",
        )
    finally:
        client.close()

    return [
        RetrievedWebDocument(
            query=query.query,
            provider=record.search_hit.provider,
            url=record.search_hit.url,
            title=(record.extracted_document.title if record.extracted_document else record.search_hit.title),
            publisher=(
                record.extracted_document.publisher_guess
                if record.extracted_document
                else record.search_hit.publisher
            ),
            snippet=record.search_hit.snippet,
            preview=_preview_text(record),
        )
        for record in batch.records
    ]


def _default_repo_retriever(query: RepoRetrievalQuery) -> list[RetrievedRepoMatch]:
    """Retrieve GitHub repository search matches using the local gh CLI."""

    fixture_path = os.environ.get("AC14_REPO_RETRIEVAL_FIXTURE")
    if fixture_path:
        fixture_payload = json.loads(Path(fixture_path).read_text())
        return [
            RetrievedRepoMatch.model_validate(match)
            for match in fixture_payload.get(query.query, [])
        ]

    gh_bin = os.environ.get("AC14_GH_BIN", "gh")
    command = [
        gh_bin,
        "search",
        "code",
        query.query,
        "--json",
        "path,repository,url",
        "--limit",
        str(query.limit),
    ]
    for repo in query.repos:
        command.extend(["--repo", repo])
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    return [
        RetrievedRepoMatch(
            query=query.query,
            repository=_repository_name(entry.get("repository")),
            path=str(entry.get("path", "")),
            url=entry.get("url"),
        )
        for entry in payload
    ]


def _repository_name(repository_payload: Any) -> str:
    """Return a compact repository name from gh JSON payloads."""

    if isinstance(repository_payload, str):
        return repository_payload
    if isinstance(repository_payload, dict):
        for key in ("nameWithOwner", "fullName", "name"):
            value = repository_payload.get(key)
            if isinstance(value, str):
                return value
    return "unknown"


def _preview_text(record: Any) -> str:
    """Build a compact preview from a retrieved open-web record."""

    if getattr(record, "extracted_document", None) is not None:
        text = record.extracted_document.text
    else:
        text = record.search_hit.snippet or ""
    stripped = " ".join(text.split())
    return stripped if len(stripped) <= 280 else stripped[:277] + "..."


def _slug(value: str) -> str:
    """Create a compact slug for trace identifiers."""

    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    return cleaned[:48] or "query"
