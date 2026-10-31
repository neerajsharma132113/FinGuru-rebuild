import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
BACKEND_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_FOLDER = os.path.join(BACKEND_FOLDER, "knowledge")


def split_into_chunks(text, max_chars=500):
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")

    # Paragraphs are separated by a blank line
    paragraphs = []
    for part in text.split("\n\n"):
        if part.strip() != "":
            paragraphs.append(part.strip())

    chunks = []
    current = ""

    for paragraph in paragraphs:
        if current == "":
            current = paragraph
        elif len(current) + len(paragraph) + 2 <= max_chars:
            current = current + "\n\n" + paragraph
        else:
            chunks.append(current)
            current = paragraph

    if current != "":
        chunks.append(current)

    return chunks


def load_chunks(folder=KNOWLEDGE_FOLDER, max_chars=500):
    chunks = []

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".md"):
            continue

        with open(os.path.join(folder, filename), encoding="utf-8") as file:
            text = file.read()

        pieces = split_into_chunks(text, max_chars)
        for number, piece in enumerate(pieces):
            chunks.append({
                "id": filename + "#" + str(number),
                "source": filename,
                "text": piece,
            })

    return chunks

def search_chunks(question, chunks, top_k=3, min_score=0.1, min_coverage=0.0):
    if question.strip() == "" or len(chunks) == 0:
        return []

    texts = []
    for chunk in chunks:
        texts.append(chunk["text"])

    vectorizer = TfidfVectorizer(stop_words="english")
    chunk_vectors = vectorizer.fit_transform(texts)
    question_vector = vectorizer.transform([question])
    scores = cosine_similarity(question_vector, chunk_vectors)[0]

    analyzer = vectorizer.build_analyzer()
    question_words = set(analyzer(question))

    ranked = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)

    results = []
    for i in ranked[:top_k]:
        chunk_words = set(analyzer(chunks[i]["text"]))
        if len(question_words) > 0:
            coverage = len(question_words & chunk_words) / len(question_words)
        else:
            coverage = 0.0

        if scores[i] >= min_score and coverage >= min_coverage:
            results.append({
                "id": chunks[i]["id"],
                "source": chunks[i]["source"],
                "text": chunks[i]["text"],
                "score": round(float(scores[i]), 3),
                "coverage": round(coverage, 2),
            })
    return results