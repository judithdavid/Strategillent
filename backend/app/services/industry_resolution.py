"""Data-driven industry alias resolution for Strategillent."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]

REGISTRY_PATH = (
    PROJECT_ROOT / "data" / "seed" / "industry_registry.json"
)

with REGISTRY_PATH.open("r", encoding="utf-8") as file:
    INDUSTRY_REGISTRY = json.load(file)

@dataclass(frozen=True)
class Industry:
    id: str
    canonical_name: str
    aliases: tuple[str, ...]
    parent_id: str | None = None


def _key(value: str) -> str:
    """Normalize whitespace, punctuation separators, and case for lookup."""
    value = (value or "").strip().casefold()
    value = value.replace("&", " and ")
    value = re.sub(r"[-_/]+", " ", value)
    value = re.sub(r"[^\w\s]", "", value)
    return re.sub(r"\s+", " ", value).strip()


@lru_cache(maxsize=1)
def load_industries() -> tuple[Industry, ...]:
    data: dict[str, Any] = json.loads(
        REGISTRY_PATH.read_text(encoding="utf-8")
    )

    result = []
    for item in data.get("industries", []):
        result.append(
            Industry(
                id=str(item["id"]),
                canonical_name=str(item["canonical_name"]),
                aliases=tuple(
                    str(alias) for alias in item.get("aliases", [])
                ),
                parent_id=item.get("parent_id"),
            )
        )

    return tuple(result)


@lru_cache(maxsize=1)
def _lookup() -> dict[str, Industry]:
    lookup: dict[str, Industry] = {}
    for industry in load_industries():
        for name in (industry.id, industry.canonical_name, *industry.aliases):
            key = _key(name)
            previous = lookup.get(key)
            if previous and previous.id != industry.id:
                raise ValueError(
                    f"Industry alias {name!r} is ambiguous between "
                    f"{previous.id!r} and {industry.id!r}. Fix industry_registry.json."
                )
            lookup[key] = industry
    return lookup


def resolve_industry(value: str, *, allow_unknown: bool = False) -> Industry | None:
    """Resolve a name or alias to a canonical industry.

    Unknown labels raise ValueError by default. When allow_unknown=True, a stable
    slug and the supplied display label are returned without adding it to the
    registry; callers should not confuse this with a verified taxonomy mapping.
    """
    label = (value or "").strip()
    if not label:
        raise ValueError("Industry is required.")
    industry = _lookup().get(_key(label))
    if industry:
        return industry
    if not allow_unknown:
        raise ValueError(
            f"Unknown industry {label!r}. Add it or its alias to industry_registry.json."
        )
    slug = re.sub(r"[^a-z0-9]+", "_", label.casefold()).strip("_") or "unknown"
    return Industry(id=slug, canonical_name=label, aliases=())


def resolve_industry_ids(values: list[str] | tuple[str, ...]) -> list[str]:
    """Resolve several industry labels to unique canonical IDs."""
    ids: list[str] = []
    for value in values:
        resolved = resolve_industry(value)
        assert resolved is not None
        if resolved.id not in ids:
            ids.append(resolved.id)
    return ids


def industry_filter_names(value: str) -> list[str]:
    """Names accepted by legacy Qdrant payloads that store display strings."""
    resolved = resolve_industry(value)
    assert resolved is not None
    return list(dict.fromkeys([
        resolved.canonical_name,
        resolved.id,
        *resolved.aliases,
        "*",
    ]))
