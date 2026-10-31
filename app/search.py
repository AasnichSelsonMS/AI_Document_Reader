
import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Load embedding model only once
# --------------------------------------------------

print("Loading search embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Search embedding model loaded.")


# --------------------------------------------------
# 2. Connect to persistent ChromaDB
# --------------------------------------------------

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="documents"
)


# --------------------------------------------------
# 3. Search Documents
# --------------------------------------------------

def search_documents(query, top_k=3):
    """
    Performs semantic search using ChromaDB.

    Returns:
    - Document text
    - Filename
    - PDF page / PPT slide number
    - Distance score
    """

    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    print("\nGenerating query embedding...")

    # Generate normalized query embedding
    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).tolist()

    # Check database
    total_chunks = collection.count()

    if total_chunks == 0:
        print("No documents available in ChromaDB.")
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    # Avoid requesting more results than available
    result_count = min(top_k, total_chunks)

    print("Searching ChromaDB...")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=result_count,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    print(f"Retrieved {len(results['documents'][0])} results.")

    return results


# --------------------------------------------------
# 4. Display Search Results
# --------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("AI DOCUMENT SEARCH")
    print("=" * 60)

    while True:

        query = input("\nAsk a question (type exit to stop): ").strip()

        if query.lower() in ["exit", "quit"]:
            print("Search session ended.")
            break

        if not query:
            print("Please enter a valid question.")
            continue

        try:

            results = search_documents(query, top_k=3)

            documents = results["documents"][0]

            if not documents:
                print("No documents found.")
                continue

            print("\n" + "=" * 60)
            print("TOP MATCHING DOCUMENTS")
            print("=" * 60)

            for index, text in enumerate(documents):

                metadata = results["metadatas"][0][index]

                print(f"\nResult {index + 1}")
                print("-" * 50)

                print("Filename:", metadata.get("filename", "Unknown"))

                source_number = metadata.get("page")

                if source_number is not None:
                    print("Page / Slide:", source_number)

                print(
                    "Distance:",
                    results["distances"][0][index]
                )

                print("\nExtracted Text:")
                print(text)

                print("-" * 50)

        except Exception as error:
            print("Search error:", error)
