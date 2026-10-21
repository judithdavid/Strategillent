from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass(frozen=True)
class EvidenceValidationResult:
    valid: bool
    supplied_evidence_count: int
    citation_count: int
    valid_citation_count: int
    invalid_evidence_ids: list[str]
    uncited_claim_paths: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "supplied_evidence_count": self.supplied_evidence_count,
            "citation_count": self.citation_count,
            "valid_citation_count": self.valid_citation_count,
            "invalid_evidence_ids": self.invalid_evidence_ids,
            "uncited_claim_paths": self.uncited_claim_paths,
        }


def _to_plain_data(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: _to_plain_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain_data(item) for item in value]
    return value


def validate_evidence_references(
    output: Any,
    allowed_evidence_ids: set[str] | frozenset[str] | list[str] | tuple[str, ...],
    *,
    claim_fields: tuple[str, ...] = (
        "description",
        "reasoning",
        "rationale",
        "claim_supported",
        "expected_benefits",
        "expected_outcomes",
    ),
) -> EvidenceValidationResult:
    """
    Validate citation IDs and identify claim-like fields without citations.

    This checks reference integrity, not whether a source truly proves a claim.
    Human review or a separate semantic evaluation is needed to assess support.
    """
    data = _to_plain_data(output)
    allowed = {str(item) for item in allowed_evidence_ids}
    invalid_ids: set[str] = set()
    citation_count = 0
    valid_citation_count = 0
    uncited_paths: list[str] = []

    def walk(node: Any, path: str = "$") -> None:
        nonlocal citation_count, valid_citation_count

        if isinstance(node, dict):
            citations = node.get("citations")

            # A citation is valid only if its evidence ID exists in the context.
            if isinstance(citations, list):
                for index, citation in enumerate(citations):
                    if not isinstance(citation, dict):
                        invalid_ids.add(f"<malformed citation at {path}.citations[{index}]>")
                        citation_count += 1
                        continue

                    evidence_id = citation.get("evidence_id")
                    citation_count += 1

                    if evidence_id is None or str(evidence_id) not in allowed:
                        invalid_ids.add(
                            str(evidence_id)
                            if evidence_id is not None
                            else f"<missing evidence_id at {path}.citations[{index}]>"
                        )
                    else:
                        valid_citation_count += 1

            has_valid_local_citation = (
                isinstance(citations, list)
                and any(
                    isinstance(item, dict)
                    and item.get("evidence_id") is not None
                    and str(item["evidence_id"]) in allowed
                    for item in citations
                )
            )

            for key, value in node.items():
                child_path = f"{path}.{key}"

                # Flag substantive text claims without a valid citation on the
                # same object. This is a review signal, not a truth judgement.
                if (
                    key in claim_fields
                    and isinstance(value, str)
                    and value.strip()
                    and not has_valid_local_citation
                ):
                    uncited_paths.append(child_path)

                if isinstance(value, (dict, list)):
                    walk(value, child_path)

        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f"{path}[{index}]")

    walk(data)

    return EvidenceValidationResult(
        valid=not invalid_ids,
        supplied_evidence_count=len(allowed),
        citation_count=citation_count,
        valid_citation_count=valid_citation_count,
        invalid_evidence_ids=sorted(invalid_ids),
        uncited_claim_paths=sorted(set(uncited_paths)),
    )


def require_valid_evidence_references(
    output: Any,
    allowed_evidence_ids: set[str] | frozenset[str] | list[str] | tuple[str, ...],
) -> EvidenceValidationResult:
    """Raise when any generated citation points outside the supplied context."""
    result = validate_evidence_references(output, allowed_evidence_ids)

    if not result.valid:
        raise ValueError(
            "Generated output contains unsupported evidence references: "
            + ", ".join(result.invalid_evidence_ids)
        )

    return result