import sys
from app.rag import load_chunks, search_chunks
from retrieval_tests import TUNING, HELD_OUT

chunks = load_chunks()


def evaluate(name, tests, min_coverage):
    answerable = 0
    found = 0
    unanswerable = 0
    refused = 0

    for question, expected in tests:
        results = search_chunks(question, chunks, top_k=3, min_score=0.1, min_coverage=min_coverage)
        if expected is None:
            unanswerable += 1
            if len(results) == 0:
                refused += 1
        else:
            answerable += 1
            if len(results) > 0 and results[0]["source"] == expected:
                found += 1

    print(
        name, "| min_coverage", min_coverage,
        "| answered correctly:", str(found) + "/" + str(answerable),
        "| correctly empty:", str(refused) + "/" + str(unanswerable),
    )


if len(sys.argv) == 1:
    # No argument: try several values on the tuning questions
    for coverage in [0.0, 0.4, 0.5, 0.6, 0.75]:
        evaluate("tuning", TUNING, coverage)
else:
    # With an argument: the final check on the held-out questions
    chosen = float(sys.argv[1])
    evaluate("tuning", TUNING, chosen)
    evaluate("held-out", HELD_OUT, chosen)