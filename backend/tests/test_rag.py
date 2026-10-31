import pytest
from app.rag import split_into_chunks, load_chunks, search_chunks
SAMPLE_CHUNKS = [
    {"id": "a.md#0", "source": "a.md", "text": "An emergency fund covers unexpected costs like medical bills."},
    {"id": "b.md#0", "source": "b.md", "text": "An EMI is a fixed monthly loan payment with interest and principal."},
    {"id": "c.md#0", "source": "c.md", "text": "The savings rate is the share of income left after spending."},
]


def test_search_finds_emergency_fund():
    results = search_chunks("what is an emergency fund", SAMPLE_CHUNKS)
    assert results[0]["source"] == "a.md"


def test_search_finds_loan_payment():
    results = search_chunks("monthly loan payment", SAMPLE_CHUNKS)
    assert results[0]["source"] == "b.md"


def test_search_returns_nothing_for_unrelated_question():
    assert search_chunks("best pizza in Mumbai", SAMPLE_CHUNKS) == []


def test_search_empty_question():
    assert search_chunks("   ", SAMPLE_CHUNKS) == []


def test_search_respects_top_k():
    results = search_chunks("loan payment fund savings income", SAMPLE_CHUNKS, top_k=1)
    assert len(results) == 1

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

def test_coverage_blocks_single_word_match():
    results = search_chunks("which mutual fund should I buy", SAMPLE_CHUNKS, min_score=0.0, min_coverage=0.5)
    assert results == []


def test_coverage_allows_full_match():
    results = search_chunks("emergency fund", SAMPLE_CHUNKS, min_coverage=0.5)
    assert results[0]["source"] == "a.md"


def test_default_coverage_does_not_filter():
    assert len(search_chunks("fund", SAMPLE_CHUNKS)) >= 1