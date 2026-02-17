"""
AI Document Simplifier - Streamlit Web App
Extracts text from PDFs and generates AI-powered summaries and key points.
"""

import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import hashlib
from typing import Optional, Tuple

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Document Simplifier",
    page_icon="📄",
    layout="wide",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main { padding: 2rem; }
.stButton > button {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
    padding: 0.5rem;
    border-radius: 5px;
}
.stButton > button:hover { background-color: #45a049; }
.stButton > button:disabled { background-color: #aaa; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────────
for _key, _default in {
    "summary": None,
    "key_points": None,
    "extracted_text": None,
    "processed_file_hash": None,
    "processing_complete": False,
}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default

# ── Constants ──────────────────────────────────────────────────────────────────
MAX_PAGES   = 20
MAX_FILE_MB = 5
MAX_CHARS   = 15000    # characters sent to Gemini per request
MODEL_NAME  = "gemini-1.5-flash"   # replaces deprecated gemini-pro


# ── PDF extraction ─────────────────────────────────────────────────────────────
def extract_text_from_pdf(
    pdf_file,
    max_pages: int = MAX_PAGES,
) -> Tuple[Optional[str], Optional[str], int]:
    """
    Extract text from an uploaded PDF using PyMuPDF.
    Returns: (text, error_message, total_pages)
    """
    pdf_document = None
    try:
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = pdf_document.page_count

        if total_pages > max_pages:
            st.warning(
                f"PDF has {total_pages} pages. "
                f"Processing only the first {max_pages} pages."
            )

        pages_to_process = min(total_pages, max_pages)
        text_parts = []

        for page_num in range(pages_to_process):
            try:
                page_text = pdf_document[page_num].get_text()
                text_parts.append(page_text)
            except Exception as page_err:
                st.warning(f"Skipped page {page_num + 1}: {page_err}")

        text = "\n".join(text_parts)

        if not text.strip():
            return (
                None,
                "The PDF appears to be empty or image-only. "
                "Please upload a PDF with selectable text.",
                total_pages,
            )

        if len(text) > 1_000_000:
            return (
                None,
                "Extracted text is too large. Please upload a shorter document.",
                total_pages,
            )

        return text, None, total_pages

    except fitz.FileDataError:
        return None, "File is corrupted or not a valid PDF.", 0
    except MemoryError:
        return None, "PDF is too large to load into memory.", 0
    except Exception as e:
        return None, f"Unexpected error reading PDF: {e}", 0
    finally:
        if pdf_document is not None:
            try:
                pdf_document.close()
            except Exception:
                pass


# ── Gemini helpers ─────────────────────────────────────────────────────────────
def _call_gemini(prompt: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    """Low-level Gemini call. Returns (response_text, error_message)."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # Safely extract text — response.text raises ValueError if blocked
        try:
            result_text = response.text
        except ValueError:
            return None, "Response blocked by Gemini safety filters. Try a different document."

        if not result_text or not result_text.strip():
            return None, "Gemini returned an empty response. Please try again."

        return result_text, None

    except Exception as e:
        msg = str(e).lower()
        if any(k in msg for k in ("api key", "api_key", "authentication", "invalid", "401")):
            return None, "Invalid API key. Please check your Gemini API key."
        if any(k in msg for k in ("quota", "rate limit", "429", "resource exhausted")):
            return None, "API quota or rate limit reached. Please wait and try again."
        if any(k in msg for k in ("network", "connection", "timeout")):
            return None, "Network error. Please check your internet connection."
        return None, f"Gemini error: {e}"


@st.cache_data(show_spinner=False, ttl=3600)
def get_summary(text: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    """Generate a plain-English summary (cached 1 hour)."""
    truncated = text[:MAX_CHARS]
    prompt = (
        "Please provide a clear 3-sentence summary of the following text in simple English. "
        "Avoid technical jargon so anyone can understand it.\n\n"
        "Text:\n" + truncated
    )
    return _call_gemini(prompt, api_key)


@st.cache_data(show_spinner=False, ttl=3600)
def get_key_points(text: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract 5 key bullet points (cached 1 hour)."""
    truncated = text[:MAX_CHARS]
    prompt = (
        "Please list exactly 5 key points from the following text. "
        "Format each as a markdown bullet starting with '- **Point:**' "
        "and keep each point concise and clear.\n\n"
        "Text:\n" + truncated
    )
    return _call_gemini(prompt, api_key)


# ── Utility ────────────────────────────────────────────────────────────────────
def get_file_hash(uploaded_file) -> Optional[str]:
    """SHA-256 hash of uploaded file for change detection."""
    try:
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        return hashlib.sha256(file_bytes).hexdigest()
    except Exception:
        return None


# ── Main app ───────────────────────────────────────────────────────────────────
def main():
    st.title("AI Document Simplifier")
    st.markdown("Upload a PDF and let AI generate a plain-English summary and key points.")

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get a free key at https://aistudio.google.com/app/apikey",
            key="api_key_input",
        )

        st.markdown("---")
        st.markdown("### Processing Limits")
        st.info(
            f"- **Max pages:** {MAX_PAGES}\n"
            f"- **Max file size:** {MAX_FILE_MB} MB\n"
            "- **Format:** Text-based PDFs only"
        )

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            f"Uses **PyMuPDF** for extraction and **Google Gemini** (`{MODEL_NAME}`) for AI. "
            "Results are cached for 1 hour."
        )

        st.markdown("---")
        st.markdown("### Tips")
        st.markdown(
            "- Scanned/image PDFs won't work — use text-selectable PDFs\n"
            "- Get your free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)"
        )

        st.markdown("---")
        if st.button("Clear Cache & Reset", help="Clear all cached results and start fresh"):
            st.cache_data.clear()
            st.session_state.clear()
            st.rerun()

    # ── Upload + Process row ───────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader(
            f"Choose a PDF file (max {MAX_FILE_MB} MB)",
            type=["pdf"],
            help=f"Text-based PDF up to {MAX_FILE_MB} MB and {MAX_PAGES} pages",
            key="pdf_uploader",
        )

        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > MAX_FILE_MB:
                st.error(
                    f"File is {file_size_mb:.2f} MB — exceeds the {MAX_FILE_MB} MB limit. "
                    "Please upload a smaller PDF."
                )
                uploaded_file = None
            else:
                st.success(f"**{uploaded_file.name}**")
                st.caption(f"Size: {file_size_mb:.2f} MB")

    with col2:
        st.subheader("Process")
        ready = bool(uploaded_file and api_key)
        process_button = st.button(
            "Process Document",
            type="primary",
            disabled=not ready,
        )
        if not uploaded_file:
            st.warning("Upload a PDF file to continue.")
        elif not api_key:
            st.warning("Enter your Gemini API key in the sidebar.")
        else:
            st.info("Ready — click **Process Document**.")

    # ── Processing ─────────────────────────────────────────────────────────────
    if process_button:
        if not uploaded_file:
            st.error("No file uploaded.")
            return
        if not api_key or not api_key.strip():
            st.error("No API key provided.")
            return
        if uploaded_file.size > MAX_FILE_MB * 1024 * 1024:
            st.error(f"File exceeds {MAX_FILE_MB} MB limit.")
            return

        current_hash = get_file_hash(uploaded_file)

        # Step 1: Extract
        with st.spinner("Reading PDF..."):
            text, extract_error, total_pages = extract_text_from_pdf(
                uploaded_file, max_pages=MAX_PAGES
            )

        if extract_error:
            st.error(f"{extract_error}")
            return

        st.session_state.extracted_text = text
        st.session_state.processed_file_hash = current_hash

        pages_processed = min(total_pages, MAX_PAGES)
        st.success(
            f"Extracted **{len(text):,}** characters from "
            f"**{pages_processed}** page(s) of `{uploaded_file.name}`"
        )
        if total_pages > MAX_PAGES:
            st.info(f"Only the first {MAX_PAGES} of {total_pages} pages were processed.")

        # Step 2: AI tabs
        tab1, tab2, tab3 = st.tabs(["Summary", "Key Points", "Full Text"])

        with tab1:
            with st.spinner("Generating summary..."):
                summary, sum_err = get_summary(text, api_key.strip())
            if sum_err:
                st.error(sum_err)
                st.session_state.summary = None
            else:
                st.session_state.summary = summary
                st.markdown("### Summary")
                st.write(summary)

        with tab2:
            with st.spinner("Extracting key points..."):
                key_points, kp_err = get_key_points(text, api_key.strip())
            if kp_err:
                st.error(kp_err)
                st.session_state.key_points = None
            else:
                st.session_state.key_points = key_points
                st.markdown("### Key Points")
                st.markdown(key_points)

        with tab3:
            st.text_area(
                label="Full Extracted Text",
                value=text,
                height=400,
                help="Complete text extracted from the PDF",
                label_visibility="visible",
            )

        if st.session_state.summary and st.session_state.key_points:
            st.session_state.processing_complete = True
            st.balloons()
            st.success("Done! Your document has been simplified.")

    # ── Cached results ─────────────────────────────────────────────────────────
    elif any([
        st.session_state.summary,
        st.session_state.key_points,
        st.session_state.extracted_text,
    ]):
        st.info("Showing previously processed results. Upload a new file to refresh.")

        tab1, tab2, tab3 = st.tabs(["Summary", "Key Points", "Full Text"])

        with tab1:
            if st.session_state.summary:
                st.markdown("### Summary")
                st.write(st.session_state.summary)
            else:
                st.warning("No summary yet. Process a document first.")

        with tab2:
            if st.session_state.key_points:
                st.markdown("### Key Points")
                st.markdown(st.session_state.key_points)
            else:
                st.warning("No key points yet. Process a document first.")

        with tab3:
            if st.session_state.extracted_text:
                st.text_area(
                    label="Full Extracted Text",
                    value=st.session_state.extracted_text,
                    height=400,
                    help="Complete text extracted from the PDF",
                    label_visibility="visible",
                )
            else:
                st.warning("No text yet. Upload and process a PDF first.")
if __name__ == "__main__":
    main()