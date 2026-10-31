
# 🤖 AI Document Search Assistant

An AI-powered PDF Document Search Assistant built using Retrieval-Augmented Generation (RAG). Upload PDF documents and ask questions in natural language to receive context-aware answers with source page citations.

## 🚀 Features

- PDF document upload
- Automatic text extraction using PyMuPDF
- Intelligent text chunking
- Semantic search using SentenceTransformers
- Vector storage using ChromaDB
- AI-powered answers using Google Gemini
- Source document and page citations
- Interactive Streamlit interface
- FastAPI backend

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| FastAPI | Backend API |
| Streamlit | User interface |
| PyMuPDF | PDF text extraction |
| SentenceTransformers | Text embeddings |
| ChromaDB | Vector database |
| Google Gemini | Answer generation |
| LangChain Text Splitters | Text chunking |

## 🏗️ Architecture

PDF Upload
    ↓
Text Extraction
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
ChromaDB Storage
    ↓
User Query
    ↓
Semantic Search
    ↓
Google Gemini
    ↓
Answer with Page Citations

## 📁 Project Structure

AI_Document_Search/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── upload.py
│   ├── pdf_reader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── search.py
│   └── chatbot.py
│
├── data/
│   └── pdfs/
│
├── chroma_db/
│
├── frontend.py
├── test_gemini.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md

## ⚙️ Installation

### 1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL

cd AI_Document_Search

### 2. Create a virtual environment

python -m venv venv

### 3. Activate the environment

Windows:

venv\Scripts\activate

### 4. Install dependencies

pip install -r requirements.txt

### 5. Configure Gemini API

Create a `.env` file in the project root.

Add:

GEMINI_API_KEY=your_gemini_api_key

### 6. Start FastAPI

uvicorn app.main:app --reload

Backend API:

http://127.0.0.1:8000

API Documentation:

http://127.0.0.1:8000/docs

### 7. Start Streamlit

Open another terminal:

streamlit run frontend.py

## 🔍 How It Works

1. Upload a PDF through the Streamlit interface.
2. FastAPI receives the document.
3. PyMuPDF extracts page-wise text.
4. Text is divided into smaller chunks.
5. SentenceTransformers generates embeddings.
6. ChromaDB stores the embeddings and metadata.
7. User questions are converted into embeddings.
8. Relevant chunks are retrieved using semantic search.
9. Gemini generates an answer using retrieved context.
10. The application displays the answer with source citations.

## 🔮 Future Improvements

- OCR support for scanned PDFs
- Multiple PDF uploads
- Document deletion
- Improved retrieval and reranking
- Conversation memory
- User authentication
- Cloud deployment

## 🔐 Security

Never upload your `.env` file or API keys to GitHub.

## 👨‍💻 Author

AI Document Search Assistant Project
