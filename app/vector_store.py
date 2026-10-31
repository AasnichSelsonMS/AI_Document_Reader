
import chromadb
import uuid

# --------------------------------------------------
# 1. Initialize Persistent ChromaDB
# --------------------------------------------------

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)


# --------------------------------------------------
# 2. Store Embeddings
# --------------------------------------------------

def store_embeddings(embedded_chunks, batch_size=100):
    """
    Stores document chunks and embeddings in ChromaDB.

    Preserves:
    - filename
    - page / slide number
    - extracted text
    - embedding vector
    """

    if not embedded_chunks:
        print("No embeddings available to store.")
        return collection.count()

    print("\nStoring embeddings in ChromaDB...\n")

    total_chunks = len(embedded_chunks)

    for start in range(0, total_chunks, batch_size):

        batch = embedded_chunks[start:start + batch_size]

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for chunk in batch:

            embedding = chunk["embedding"]

            # Support both NumPy arrays and Python lists
            if hasattr(embedding, "tolist"):
                embedding = embedding.tolist()

            ids.append(str(uuid.uuid4()))

            documents.append(chunk["text"])

            embeddings.append(embedding)

            metadata = {
                "filename": chunk["filename"]
            }

            # ChromaDB metadata cannot contain None values
            if chunk.get("page") is not None:
                metadata["page"] = int(chunk["page"])

            metadatas.append(metadata)

        # Store an entire batch
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        completed = min(start + len(batch), total_chunks)

        print(
            f"Stored {completed}/{total_chunks} chunks"
        )

    total_stored = collection.count()

    print("\n" + "=" * 50)
    print("CHROMADB STORAGE SUCCESSFUL")
    print("=" * 50)

    print(f"New chunks stored: {total_chunks}")
    print(f"Total chunks in database: {total_stored}")

    return total_stored


# --------------------------------------------------
# 3. Get Collection
# --------------------------------------------------

def get_collection():
    """
    Returns the persistent ChromaDB collection.
    """

    return collection


# --------------------------------------------------
# 4. Get Collection Statistics
# --------------------------------------------------

def get_collection_stats():

    return {
        "collection_name": collection.name,
        "total_chunks": collection.count()
    }


# --------------------------------------------------
# 5. Test Vector Store
# --------------------------------------------------

if __name__ == "__main__":

    print("\nChromaDB Vector Store")
    print("=" * 50)

    stats = get_collection_stats()

    print("Collection:", stats["collection_name"])
    print("Total chunks:", stats["total_chunks"])

    print("\nVector store ready.")
