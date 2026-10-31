
from app.pdf_reader import read_single_document

file_path = input("Enter PDF/PPT/PPTX file path: ")

try:
    document = read_single_document(file_path)

    print("\nFilename:", document["filename"])
    print("\nExtracted text:\n")
    print(document["text"][:3000])

except Exception as error:
    print("\nERROR:", error)
