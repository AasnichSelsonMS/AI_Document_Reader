
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.pdf_reader import read_all_documents


def create_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )


def chunk_documents(documents):
    text_splitter = create_text_splitter()
    chunks = []

    for document in documents:
        filename = document["filename"]
        text = document["text"]
        page = document["page"]

        split_text = text_splitter.split_text(text)

        print(
            f"\nChunking: {filename} | "
            f"Page/Slide: {page} | "
            f"Chunks: {len(split_text)}"
        )

        for chunk in split_text:
            chunks.append({
                "filename": filename,
                "page": page,
                "text": chunk
            })

    return chunks


def chunk_single_document(pages):
    return chunk_documents(pages)


if __name__ == "__main__":

    print("\nReading documents...\n")

    documents = read_all_documents("data/pdfs")

    print(f"Successfully read {len(documents)} pages/slides")

    print("\nCreating chunks...\n")

    chunks = chunk_documents(documents)

    print("\n" + "=" * 60)
    print(f"TOTAL CHUNKS CREATED: {len(chunks)}")
    print("=" * 60)

    for index, chunk in enumerate(chunks[:5], start=1):
        print(f"\nChunk {index}")
        print(f"Source: {chunk['filename']}")
        print(f"Page/Slide: {chunk['page']}")
        print(chunk["text"])
