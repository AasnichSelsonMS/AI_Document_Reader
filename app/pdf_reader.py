
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pymupdf
from pptx import Presentation


def read_pdf(file_path):
    pages = []

    try:
        with pymupdf.open(file_path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                if text:
                    pages.append({
                        "filename": os.path.basename(file_path),
                        "page": page_number,
                        "text": text
                    })

    except Exception as error:
        raise ValueError(f"PDF extraction failed: {error}")

    return pages


def read_pptx(file_path):
    pages = []

    try:
        presentation = Presentation(file_path)

        for slide_number, slide in enumerate(
            presentation.slides, start=1
        ):
            slide_text = []

            for shape in slide.shapes:

                if shape.has_text_frame:
                    text = shape.text.strip()

                    if text:
                        slide_text.append(text)

                if shape.has_table:
                    for row in shape.table.rows:
                        row_text = [
                            cell.text.strip()
                            for cell in row.cells
                            if cell.text.strip()
                        ]

                        if row_text:
                            slide_text.append(" | ".join(row_text))

            if slide_text:
                pages.append({
                    "filename": os.path.basename(file_path),
                    "page": slide_number,
                    "text": "\n".join(slide_text)
                })

    except Exception as error:
        raise ValueError(f"PPTX extraction failed: {error}")

    return pages



def convert_ppt_to_pptx(file_path, output_folder):

    # Locate LibreOffice
    soffice = (
        shutil.which("soffice.exe")
        or shutil.which("soffice")
        or r"C:\Program Files\LibreOffice\program\soffice.exe"
    )

    # Verify executable exists
    if not Path(soffice).is_file():
        raise ValueError(
            f"LibreOffice executable not found: {soffice}"
        )

    file_path = str(Path(file_path).resolve())
    output_folder = str(Path(output_folder).resolve())

    if not Path(file_path).is_file():
        raise ValueError(f"PPT file not found: {file_path}")

    try:
        result = subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "pptx",
                "--outdir",
                output_folder,
                file_path
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        converted_path = (
            Path(output_folder) /
            (Path(file_path).stem + ".pptx")
        )

        if result.returncode != 0:
            raise ValueError(
                f"LibreOffice conversion failed: "
                f"{result.stderr or result.stdout}"
            )

        if not converted_path.exists():
            raise ValueError(
                "PPT conversion failed. "
                f"LibreOffice output: {result.stdout} "
                f"{result.stderr}"
            )

        print("PPT converted successfully to PPTX.")

        return str(converted_path)

    except subprocess.TimeoutExpired:
        raise ValueError("PPT conversion timed out.")

    except OSError as error:
        raise ValueError(
            f"Could not start LibreOffice: {error}"
        )


def read_single_document(file_path):
    file_path = str(file_path)
    extension = Path(file_path).suffix.lower()

    print(f"\nReading: {os.path.basename(file_path)}")

    if extension == ".pdf":
        pages = read_pdf(file_path)

    elif extension == ".pptx":
        pages = read_pptx(file_path)

    elif extension == ".ppt":
        with tempfile.TemporaryDirectory() as temp_folder:
            converted_file = convert_ppt_to_pptx(
                file_path, temp_folder
            )
            pages = read_pptx(converted_file)

            # Restore the original filename in source metadata
            for page in pages:
                page["filename"] = os.path.basename(file_path)

    else:
        raise ValueError(f"Unsupported format: {extension}")

    if not pages:
        raise ValueError(
            f"No readable text found in {os.path.basename(file_path)}"
        )

    print(f"Extracted sections: {len(pages)}")

    return pages


def read_single_pdf(file_path):
    # Backward-compatible function name
    return read_single_document(file_path)


def read_all_documents(folder_path="data/pdfs"):
    documents = []

    supported_extensions = {".pdf", ".pptx", ".ppt"}
    folder = Path(folder_path)

    if not folder.exists():
        return documents

    for file_path in folder.iterdir():
        if (
            file_path.is_file()
            and file_path.suffix.lower() in supported_extensions
        ):
            try:
                documents.extend(read_single_document(file_path))

            except Exception as error:
                print(f"Could not read {file_path.name}: {error}")

    return documents


def read_all_pdfs(folder_path="data/pdfs"):
    # Backward-compatible function name
    return read_all_documents(folder_path)
