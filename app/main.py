from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict

from app.upload import router as upload_router
from app.chatbot import chat

app = FastAPI(
    title="AI Document Search Backend",
    version="1.0.0"
)

app.include_router(upload_router)


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(
        ...,
        min_length=1,
        description="Enter a question about your uploaded documents."
    )

@app.get("/")
def home():

    return {
        "message": "AI Document Search Backend Running"
    }


@app.post("/chat")
def ask_question(request: ChatRequest):

    answer, sources = chat(request.question)

    formatted_sources = []

    seen = set()

    for source in sources:

        filename = source.get("filename", "Unknown File")
        page = source.get("page", "Unknown Page")

        key = (filename, page)

        if key not in seen:

            formatted_sources.append(
                {
                    "filename": filename,
                    "page": page
                }
            )

            seen.add(key)

    return {
        "question": request.question,
        "answer": answer,
        "sources": formatted_sources
    }