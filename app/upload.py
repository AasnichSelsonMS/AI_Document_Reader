
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from app.pdf_reader import read_single_document
from app.chunker import chunk_single_document
from app.embeddings import generate_single_embeddings
from app.vector_store import store_embeddings

router = APIRouter()

# --------------------------------------------------
# Upload configuration
# --------------------------------------------------

UPLOAD_FOLDER = Path("data/pdfs")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {".pdf", ".ppt", ".pptx"}

PDF_SIGNATURE = b"%PDF-"
PPT_SIGNATURE = bytes.fromhex("D0 CF 11 E0 A1 B1 1A E1")
PPTX_SIGNATURE = b"PK\x03\x04"


# --------------------------------------------------
# Document Upload Endpoint
# --------------------------------------------------

@router.post("/upload")
def upload_document(file: UploadFile = File(...)):

    file_path = None
    file_saved = False

    try:
        # 1. Validate filename
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided."
            )

        # Prevent directory traversal
        filename = Path(file.filename.replace("\\", "/")).name

        if not filename.strip():
            raise HTTPException(
                status_code=400,
                detail="Invalid filename."
            )

        # 2. Validate file extension
        extension = Path(filename).suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, PPT, and PPTX files are supported."
            )

        # 3. Validate file signature
        file.file.seek(0)
        file_header = file.file.read(8)
        file.file.seek(0)

        if extension == ".pdf":
            valid_file = file_header.startswith(PDF_SIGNATURE)

        elif extension == ".ppt":
            valid_file = file_header == PPT_SIGNATURE

        else:  # .pptx
            valid_file = file_header.startswith(PPTX_SIGNATURE)

        if not valid_file:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format or file extension mismatch."
            )

        # 4. Check duplicate filename
        file_path = UPLOAD_FOLDER / filename

        if file_path.exists():
            raise HTTPException(
                status_code=409,
                detail="A file with this name already exists."
            )

        # 5. Save uploaded document
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_saved = True

        print(f"\nDocument saved: {filename}")

        # 6. Extract PDF pages or presentation slides
        pages = read_single_document(str(file_path))

        if not pages:
            raise HTTPException(
                status_code=422,
                detail="No readable text found in the document."
            )

        print(f"Pages/slides extracted: {len(pages)}")

        # 7. Generate text chunks
        chunks = chunk_single_document(pages)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="Unable to generate text chunks."
            )

        print(f"Chunks generated: {len(chunks)}")

        # 8. Generate embeddings
        embedded_chunks = generate_single_embeddings(chunks)

        if not embedded_chunks:
            raise HTTPException(
                status_code=500,
                detail="Embedding generation failed."
            )

        print(f"Embeddings generated: {len(embedded_chunks)}")

        # 9. Store embeddings in ChromaDB
        total_chunks = store_embeddings(embedded_chunks)

        print(f"Document indexed successfully: {filename}")

        # 10. Return success response
        return {
            "status": "success",
            "message": "Document uploaded and indexed successfully.",
            "filename": filename,
            "file_type": extension.replace(".", "").upper(),
            "pages_processed": len(pages),
            "chunks_added": len(embedded_chunks),
            "total_chunks": total_chunks
        }

    except HTTPException:
        # Delete only the file saved during this upload
        if file_saved and file_path and file_path.exists():
            file_path.unlink()

        raise

    except Exception as error:
        if file_saved and file_path and file_path.exists():
            file_path.unlink()

        print(f"Document processing error: {error}")

        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the document: {str(error)}"
        )

    finally:
        file.file.close()
