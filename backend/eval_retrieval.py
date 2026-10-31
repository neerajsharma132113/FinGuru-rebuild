from app.rag import load_chunks, search_chunks

# (question, file that should answer it, or None if the notes cannot answer it)
TESTS = [
    ("What is an EMI?", "emi.md"),
    ("How is an EMI split between interest and principal?", "emi.md"),
    ("Does a longer loan tenure cost more interest?", "emi.md"),
    ("Why does paying extra early save more interest?", "emi.md"),
    ("What is an emergency fund?", "emergency-fund.md"),
    ("How many months of expenses should I keep aside?", "emergency-fund.md"),
    ("Where should I keep my emergency money?", "emergency-fund.md"),
    ("What target does FinGuru use for emergency savings?", "emergency-fund.md"),
    ("What is the savings rate?", "savings-and-debt.md"),
    ("How do I calculate my savings rate?", "savings-and-debt.md"),
    ("What share of income should go to loan EMIs?", "savings-and-debt.md"),
    ("Why does FinGuru warn at 40 percent?", "savings-and-debt.md"),
    # paraphrased: almost no words in common with the notes
    ("I want to put money aside for a rainy day", "emergency-fund.md"),
    ("How much of my salary can go to repayments?", "savings-and-debt.md"),
    # the notes cannot answer these
    ("Which mutual fund should I buy?", None),
    ("What is the best pizza in Mumbai?", None),
    ("How do I file my income tax return?", None),
    ("What is the current repo rate?", None),
]

chunks = load_chunks()


def run(min_score):
    answerable = 0
    top1 = 0
    top3 = 0
    unanswerable = 0
    refused = 0
    misses = []

    for question, expected in TESTS:
        results = search_chunks(question, chunks, top_k=3, min_score=min_score)
        sources = []
        for result in results:
            sources.append(result["source"])

        if expected is None:
            unanswerable += 1
            if len(sources) == 0:
                refused += 1
            else:
                misses.append("SHOULD BE EMPTY: " + question + " -> " + sources[0])
        else:
            answerable += 1
            if len(sources) > 0 and sources[0] == expected:
                top1 += 1
            else:
                found = sources[0] if len(sources) > 0 else "nothing"
                misses.append("WRONG: " + question + " -> " + found + " (wanted " + expected + ")")
            if expected in sources:
                top3 += 1

    print(
        "min_score", min_score,
        "| top-1 correct:", str(top1) + "/" + str(answerable),
        "| in top-3:", str(top3) + "/" + str(answerable),
        "| correctly empty:", str(refused) + "/" + str(unanswerable),
    )
    return misses


for score in [0.05, 0.1, 0.15, 0.2, 0.3]:
    all_misses = run(score)
    if score == 0.1:
        misses_at_default = all_misses

print("\nMisses at min_score 0.1:")
for line in misses_at_default:
    print(" ", line)