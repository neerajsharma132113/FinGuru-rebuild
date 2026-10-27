from app.rag import load_chunks, search_chunks

chunks = load_chunks()

questions = [
    "What is an EMI?",
    "How much emergency fund should I keep?",
    "Does a longer loan tenure cost more interest?",
    "What is a good EMI share of income?",
    "Which mutual fund should I buy?",
]

for question in questions:
    print("\nQ:", question)
    results = search_chunks(question, chunks)
    if len(results) == 0:
        print("   no relevant source found")
    for result in results:
        print("  ", result["id"], "score", result["score"])