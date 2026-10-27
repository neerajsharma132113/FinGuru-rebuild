import os

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