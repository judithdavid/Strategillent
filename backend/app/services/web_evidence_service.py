
from datetime import date
from hashlib import sha256
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models import Evidence, ResearchSource
from app.services.web_research_service import search_web


def _external_id_for_url(url: str) -> str:
    """Create a stable identifier for a URL."""
    digest = sha256(url.strip().lower().encode("utf-8")).hexdigest()[:40]
    return f"WEB-{digest}"


def _parse_publication_date(value) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def search_and_store_web_evidence(
    db: Session,
    query: str,
    industry: str,
    domain: str,
    max_results: int = 5,
) -> dict:
    """
    Search the web and persist results as traceable evidence records.

    Search results are source material, not independently verified facts.
    """
    query = query.strip()
    industry = industry.strip()
    domain = domain.strip()

    if not industry:
        raise ValueError("Industry cannot be empty.")
    if not domain:
        raise ValueError("Domain cannot be empty.")

    results = search_web(query, max_results=max_results)

    created = 0
    updated = 0
    skipped = 0

    try:
        for item in results:
            url = item["url"].strip()
            title = item["title"].strip()
            content = item["content"].strip()

            if not content:
                skipped += 1
                continue

            external_id = _external_id_for_url(url)
            source_name = urlparse(url).netloc.lower()

            source = (
                db.query(ResearchSource)
                .filter(ResearchSource.url == url)
                .first()
            )

            if source is None:
                source = ResearchSource(
                    source_name=source_name or "Web source",
                    source_type="web_search",
                    url=url,
                    publication_date=_parse_publication_date(
                        item.get("published_date")
                    ),
                )
                db.add(source)
                db.flush()

            evidence = (
                db.query(Evidence)
                .filter(Evidence.external_id == external_id)
                .first()
            )

            if evidence is None:
                evidence = Evidence(
                    external_id=external_id,
                    domain=domain,
                    title=title,
                    research_source_id=source.id,
                    publication_date=_parse_publication_date(
                        item.get("published_date")
                    ),
                    url=url,
                    claim=content[:5000],
                    evidence_text=content,
                    strategic_implication=(
                        "External search result. Assess its credibility, "
                        "relevance, and implications against the organisation "
                        "context before using it in a recommendation."
                    ),
                    confidence=1,
                    relevance=1,
                    tags=["web_search", "unverified"],
                    industries=[industry],
                )
                db.add(evidence)
                created += 1
            else:
                # Refresh source content while preserving the existing record.
                evidence.title = title
                evidence.domain = domain
                evidence.research_source_id = source.id
                evidence.url = url
                evidence.claim = content[:5000]
                evidence.evidence_text = content
                evidence.strategic_implication = (
                    "External search result. Assess its credibility, "
                    "relevance, and implications against the organisation "
                    "context before using it in a recommendation."
                )
                evidence.tags = list(
                    dict.fromkeys([*(evidence.tags or []), "web_search", "unverified"])
                )
                evidence.industries = list(
                    dict.fromkeys([*(evidence.industries or []), industry])
                )
                updated += 1

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "query": query,
        "industry": industry,
        "domain": domain,
        "results_found": len(results),
        "created": created,
        "updated": updated,
        "skipped": skipped,
    }
