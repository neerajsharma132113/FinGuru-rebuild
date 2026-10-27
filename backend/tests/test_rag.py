import pytest
from app.rag import split_into_chunks, load_chunks


def test_short_text_is_one_chunk():
    assert split_into_chunks("Hello\n\nWorld", 500) == ["Hello\n\nWorld"]


def test_long_text_is_split_between_paragraphs():
    text = ("a" * 200) + "\n\n" + ("b" * 200) + "\n\n" + ("c" * 200)
    chunks = split_into_chunks(text, 500)
    assert len(chunks) == 2
    assert chunks[1] == "c" * 200


def test_very_long_paragraph_is_kept_whole():
    chunks = split_into_chunks("x" * 800, 500)
    assert len(chunks) == 1
    assert len(chunks[0]) == 800


def test_empty_text_gives_no_chunks():
    assert split_into_chunks("", 500) == []
    assert split_into_chunks("\n\n  \n\n", 500) == []


def test_bad_max_chars():
    with pytest.raises(ValueError):
        split_into_chunks("hello", 0)


def test_load_chunks_reads_markdown_only(tmp_path):
    (tmp_path / "one.md").write_text("First note", encoding="utf-8")
    (tmp_path / "two.md").write_text("Second note", encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("Not a note", encoding="utf-8")

    chunks = load_chunks(str(tmp_path))
    assert len(chunks) == 2
    assert chunks[0]["id"] == "one.md#0"
    assert chunks[1]["source"] == "two.md"