import pytest

from app.services.industry_resolution import resolve_industry, resolve_industry_ids


@pytest.mark.parametrize("name", ["FinTech", "Fintech", "fintech", "Banking", "BFS"])
def test_fintech_aliases_resolve_to_same_id(name):
    assert resolve_industry(name).id == "fintech"


@pytest.mark.parametrize(
    "name",
    ["EdTech", "EduTech", "Education Technology", "Educational Technology"],
)
def test_edtech_aliases_resolve_to_same_id(name):
    assert resolve_industry(name).id == "edtech"


@pytest.mark.parametrize(
    "name",
    ["Retail", "Retail & Consumer Goods", "Commerce"],
)
def test_retail_aliases_resolve_to_same_id(name):
    assert resolve_industry(name).id == "retail"


def test_multiple_industries_resolve_without_duplicates():
    assert resolve_industry_ids(["Retail", "Commerce", "Cloud Computing"]) == [
        "retail", "cloud_computing"
    ]


def test_unknown_industry_requires_explicit_allow_unknown():
    with pytest.raises(ValueError):
        resolve_industry("Marine Robotics")

    result = resolve_industry("Marine Robotics", allow_unknown=True)
    assert result.id == "marine_robotics"
    assert result.canonical_name == "Marine Robotics"
