
import os
from dotenv import load_dotenv
from google import genai

from app.search import search_documents


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )


# --------------------------------------------------
# 2. Initialize Gemma client
# --------------------------------------------------

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemma-4-26b-a4b-it"

TOP_K = 5


# --------------------------------------------------
# 3. AI Document Chatbot
# --------------------------------------------------

def chat(question):

    question = question.strip()

    if not question:
        return (
            "Please enter a valid question.",
            []
        )

    try:

        # ------------------------------------------
        # A. Retrieve relevant document chunks
        # ------------------------------------------

        print("\nSearching uploaded documents...")

        results = search_documents(
            query=question,
            top_k=TOP_K
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        if not documents:
            return (
                "I couldn't find the answer in the uploaded documents.",
                []
            )

        # ------------------------------------------
        # B. Build document context
        # ------------------------------------------

        context_parts = []
        sources = []

        for index, document in enumerate(documents):

            metadata = metadatas[index] or {}

            filename = metadata.get(
                "filename",
                "Unknown File"
            )

            page = metadata.get("page")

            extension = os.path.splitext(filename)[1].lower()

            if extension in [".ppt", ".pptx"]:
                location = (
                    f"Slide {page}"
                    if page is not None
                    else "Unknown slide"
                )
            else:
                location = (
                    f"Page {page}"
                    if page is not None
                    else "Unknown page"
                )

            source_label = f"Source {index + 1}"

            context_parts.append(
                f"""
[{source_label}]
Filename: {filename}
Location: {location}

Content:
{document}
"""
            )

            source = {
                "filename": filename,
                "page": page,
                "distance": distances[index]
            }

            sources.append(source)

        context = "\n\n".join(context_parts)

        # ------------------------------------------
        # C. Construct AI prompt
        # ------------------------------------------

        prompt = f"""
You are an AI Document Search Assistant.

Your task is to answer the user's question using
ONLY the information available in the provided
document context.

IMPORTANT INSTRUCTIONS:

1. Do not invent information.
2. Do not use outside knowledge.
3. Answer clearly and directly.
4. Organize the answer using headings or bullet
   points when useful.
5. When using information from a source, cite it
   using its source label, for example [Source 1].
6. Use the source labels exactly as provided.
7. If the answer is not available in the context,
   reply exactly:

"I couldn't find the answer in the uploaded documents."

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

        # ------------------------------------------
        # D. Generate AI response
        # ------------------------------------------

        print("\nGenerating answer using Gemma...")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = (response.text or "").strip()

        if not answer:
            answer = (
                "The AI could not generate an answer. "
                "Please try asking another question."
            )

        print("\nAnswer generated successfully.")

        return answer, sources

    except Exception as error:

        print("\nChatbot Error:", error)

        return (
            "The AI service is temporarily unavailable. "
            "Please try again later.",
            []
        )


# --------------------------------------------------
# 4. Run Chatbot Independently
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 65)
    print("          AI DOCUMENT SEARCH ASSISTANT")
    print("=" * 65)

    print("Model:", MODEL_NAME)

    while True:

        question = input(
            "\nAsk a question (type 'exit' to quit): "
        ).strip()

        if question.lower() in ["exit", "quit"]:
            print("\nChat session ended.")
            break

        if not question:
            print("Please enter a question.")
            continue

        answer, sources = chat(question)

        print("\n" + "=" * 65)
        print("AI ANSWER")
        print("=" * 65)

        print(answer)

        print("\n" + "-" * 65)
        print("DOCUMENT SOURCES")
        print("-" * 65)

        if sources:

            printed = set()

            for source in sources:

                filename = source["filename"]
                page = source["page"]

                extension = os.path.splitext(filename)[1].lower()

                if extension in [".ppt", ".pptx"]:
                    location = f"Slide {page}"
                else:
                    location = f"Page {page}"

                key = (filename, page)

                if key not in printed:

                    print(f"File: {filename}")
                    print(f"Location: {location}")
                    print()

                    printed.add(key)

        else:
            print("No document sources available.")

        print("=" * 65)
