from app.retrieval.chunking import chunk_text


def test_chunk_text_empty_input():
    assert chunk_text("") == []


def test_chunk_text_preserves_content_and_overlaps():
    text = ("Strategillent semantic retrieval must preserve source metadata. " * 80)
    chunks = chunk_text(text, chunk_size=500, overlap=80)
    assert len(chunks) > 1
    assert all(chunks)
    # A repeated phrase across the boundary is expected due to overlap.
    assert any(chunks[i][-80:] in chunks[i + 1] for i in range(len(chunks) - 1))


def test_chunk_text_validates_parameters():
    import pytest
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=10)
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=300, overlap=300)
