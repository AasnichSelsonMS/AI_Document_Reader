
from sentence_transformers import SentenceTransformer
import numpy as np

# --------------------------------------------------
# 1. Load embedding model only once
# --------------------------------------------------

print("Loading SentenceTransformer model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded successfully.")


# --------------------------------------------------
# 2. Generate embeddings
# --------------------------------------------------

def generate_embeddings(chunks, batch_size=32):
    """
    Generate embeddings for document chunks.

    Preserves:
    - filename
    - page (PDF page or PPT slide)
    - text
    - embedding
    """

    if not chunks:
        print("No chunks available for embedding.")
        return []

    print("\nGenerating embeddings...\n")

    texts = [chunk["text"] for chunk in chunks]

    # Generate embeddings in batches
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embedded_chunks = []

    for chunk, embedding in zip(chunks, embeddings):

        embedded_chunks.append({
            "filename": chunk["filename"],
            "page": chunk.get("page"),
            "text": chunk["text"],
            "embedding": embedding.tolist()
        })

    print("\nEmbedding generation completed.")
    print(f"Total embedded chunks: {len(embedded_chunks)}")
    print(f"Embedding dimensions: {len(embeddings[0])}")

    return embedded_chunks


# --------------------------------------------------
# 3. Single document embedding
# --------------------------------------------------

def generate_single_embeddings(chunks):
    """
    Generate embeddings for a single uploaded document.

    Uses the same embedding pipeline as multiple documents.
    """

    return generate_embeddings(chunks)


# --------------------------------------------------
# 4. Test embeddings.py
# --------------------------------------------------

if __name__ == "__main__":

    from chunker import chunk_documents
    from pdf_reader import read_all_documents

    print("\nReading documents...")

    documents = read_all_documents("data/pdfs")

    print(f"Documents/pages/slides extracted: {len(documents)}")

    print("\nCreating chunks...")

    chunks = chunk_documents(documents)

    print(f"Total chunks: {len(chunks)}")

    embedded_chunks = generate_embeddings(chunks)

    if embedded_chunks:

        sample = embedded_chunks[0]

        print("\n" + "=" * 60)
        print("EMBEDDING TEST SUCCESSFUL")
        print("=" * 60)

        print("\nFilename:")
        print(sample["filename"])

        print("\nPage / Slide:")
        print(sample["page"])

        print("\nText:")
        print(sample["text"][:300])

        print("\nEmbedding dimensions:")
        print(len(sample["embedding"]))

        print("\nFirst 10 embedding values:")
        print(sample["embedding"][:10])

    else:
        print("No embeddings were generated.")
