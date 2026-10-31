import streamlit as st
import requests
from pathlib import Path

# ---------------------------------------
# Configuration
# ---------------------------------------

API_URL = "http://127.0.0.1:8000"

FILE_TYPES = ["pdf", "ppt", "pptx"]

MIME_TYPES = {
    ".pdf": "application/pdf",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
}

# ---------------------------------------
# Page Configuration
# ---------------------------------------

st.set_page_config(
    page_title="AI Document Search Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------
# Session State
# ---------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------
# Sidebar - Document Upload
# ---------------------------------------

with st.sidebar:

    st.title("📄 Upload Documents")

    st.caption("Supported formats: PDF, PPT and PPTX")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=FILE_TYPES,
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        st.info(f"Selected: {uploaded_file.name}")

    if st.button("📤 Upload Document", use_container_width=True):

        if uploaded_file is None:
            st.warning("Please choose a document.")

        else:
            extension = Path(uploaded_file.name).suffix.lower()
            mime_type = MIME_TYPES.get(extension)

            if mime_type is None:
                st.error("Unsupported document format.")

            else:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        mime_type
                    )
                }

                try:
                    with st.spinner(
                        "Uploading and indexing document..."
                    ):

                        response = requests.post(
                            f"{API_URL}/upload",
                            files=files,
                            timeout=300
                        )

                    if response.status_code == 200:

                        result = response.json()

                        if result.get("status") == "success":

                            st.success(
                                "✅ Document uploaded successfully!"
                            )

                            st.info(
                                f"""
**Filename:** {result['filename']}

**File Type:** {result['file_type']}

**Pages / Slides Processed:** {result['pages_processed']}

**Chunks Added:** {result['chunks_added']}

**Total Chunks in Database:** {result['total_chunks']}
"""
                            )

                        else:
                            st.warning(
                                result.get(
                                    "message",
                                    "Document upload was not completed."
                                )
                            )

                    else:
                        try:
                            error_detail = response.json().get(
                                "detail",
                                "Unknown upload error."
                            )
                        except ValueError:
                            error_detail = response.text

                        st.error(
                            f"❌ Upload failed ({response.status_code}): "
                            f"{error_detail}"
                        )

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Cannot connect to the backend. "
                        "Please start FastAPI first."
                    )

                except requests.exceptions.Timeout:
                    st.error(
                        "Upload timed out. Try a smaller document."
                    )

                except requests.exceptions.RequestException as error:
                    st.error(f"Upload error: {error}")

    st.divider()

    # ---------------------------------------
    # Clear Chat
    # ---------------------------------------

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ---------------------------------------
# Main Page
# ---------------------------------------

st.title("🤖 AI Document Search Assistant")

st.caption(
    "Upload PDF, PPT or PPTX documents and ask questions "
    "using AI-powered document search."
)

# ---------------------------------------
# Display Chat History
# ---------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            sources = message.get("sources", [])

            if sources:

                with st.expander("📚 Source Documents"):

                    for source in sources:

                        filename = source.get(
                            "filename",
                            "Unknown document"
                        )

                        location = source.get("page")

                        extension = Path(filename).suffix.lower()

                        location_type = (
                            "Slide" if extension in [".ppt", ".pptx"]
                            else "Page"
                        )

                        if location is not None:
                            st.write(
                                f"📄 {filename} "
                                f"({location_type} {location})"
                            )
                        else:
                            st.write(f"📄 {filename}")


# ---------------------------------------
# Chat Input
# ---------------------------------------

question = st.chat_input(
    "Ask a question about your uploaded documents..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        try:

            with st.spinner("🤖 AI is thinking..."):

                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": question
                    },
                    timeout=180
                )

            if response.status_code == 200:

                result = response.json()

                answer = result.get(
                    "answer",
                    "No answer received from the AI."
                )

                sources = result.get("sources", [])

                st.markdown(answer)

                if sources:

                    with st.expander("📚 Source Documents"):

                        for source in sources:

                            filename = source.get(
                                "filename",
                                "Unknown document"
                            )

                            location = source.get("page")

                            extension = Path(filename).suffix.lower()

                            location_type = (
                                "Slide" if extension in [".ppt", ".pptx"]
                                else "Page"
                            )

                            if location is not None:
                                st.write(
                                    f"📄 {filename} "
                                    f"({location_type} {location})"
                                )
                            else:
                                st.write(f"📄 {filename}")

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    }
                )

            else:
                st.error(
                    f"Backend error ({response.status_code}): "
                    f"{response.text}"
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the backend. "
                "Please start FastAPI."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The AI response timed out. Please try again."
            )

        except requests.exceptions.RequestException as error:
            st.error(f"Request failed: {error}")
