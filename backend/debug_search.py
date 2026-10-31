from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.rag import load_chunks

chunks = load_chunks()
texts = []
for chunk in chunks:
    texts.append(chunk["text"])

vectorizer = TfidfVectorizer(stop_words="english")
chunk_vectors = vectorizer.fit_transform(texts)
analyzer = vectorizer.build_analyzer()  # turns a sentence into the words TF-IDF actually uses

questions = [
    "What is the best pizza in Mumbai?",
    "Which mutual fund should I buy?",
    "How do I file my income tax return?",
    "What is the current repo rate?",
]

for question in questions:
    query_words = set(analyzer(question))
    scores = cosine_similarity(vectorizer.transform([question]), chunk_vectors)[0]
    best = scores.argmax()  # position of the highest score
    chunk_words = set(analyzer(texts[best]))

    print("\nQ:", question)
    print("  words used:  ", sorted(query_words))
    print("  best chunk:  ", chunks[best]["id"], "score", round(float(scores[best]), 3))
    print("  shared words:", sorted(query_words & chunk_words))