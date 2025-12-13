from app.core.embeddings import EMBEDDING_DIM, embed_text


def test_embed_text_returns_list_of_floats() -> None:
    text = "Sample quotation text."
    embedding = embed_text(text)

    assert isinstance(embedding, list), "Embedding should be a list."
    assert len(embedding) == EMBEDDING_DIM, "Embedding has unexpected dimension."
    assert all(
        isinstance(value, float) for value in embedding
    ), "All embedding values must be floats."


def test_embed_text_is_deterministic_for_same_text() -> None:
    text = " Hello   world  "
    embedding_1 = embed_text(text)
    embedding_2 = embed_text(text)

    assert embedding_1 == embedding_2, "Embeddings must be deterministic."


def test_embed_text_normalizes_whitespace() -> None:
    base = "Multi Agent RAG quotation"
    embedding_1 = embed_text(base)
    embedding_2 = embed_text("  Multi   Agent   RAG   quotation  ")

    assert embedding_1 == embedding_2, "Whitespace normalization should not change embedding."


def test_embed_text_differs_for_different_texts() -> None:
    embedding_a = embed_text("First quotation text.")
    embedding_b = embed_text("Second quotation text.")

    assert embedding_a != embedding_b, "Different texts should produce different embeddings."
