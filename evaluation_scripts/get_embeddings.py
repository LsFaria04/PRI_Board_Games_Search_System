import io
import sys
import json
from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2', device="cuda")

def get_embedding(text):
    return model.encode(text, convert_to_tensor=False).tolist()

def chunk_text(text, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def aggregate_fields(document):
    """
    Aggregate description + smaller text fields into one string.
    """
    parts = []
    parts.append(document.get("description", ""))
    parts.append(document.get("name", "") or "")
    parts.extend(document.get("alt_names", []) or [])
    parts.extend(document.get("publishers", []) or [])
    parts.extend(document.get("designers", []) or [])
    parts.extend(document.get("categories", []) or [])
    parts.extend(document.get("mechanics", []) or [])
    parts.extend(document.get("families", []) or [])
    return " ".join([p for p in parts if p])

if __name__ == "__main__":
    data = json.load(sys.stdin)

    for document in data:
        # Aggregate all text fields
        combined_text = aggregate_fields(document)

        # Chunk the aggregated text
        chunks = chunk_text(combined_text)

        # Embed each chunk
        document["combined_vectors"] = [get_embedding(chunk) for chunk in chunks]

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    json.dump(data, sys.stdout, indent=4, ensure_ascii=False)
