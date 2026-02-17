"""
AI Document Simplifier - Modern Glass Morphism UI
Complete Fixed Version with gemini-2.0-flash
"""

import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
from typing import Optional, Tuple
import hashlib
import os

st.set_page_config(
    page_title="AI Document Simplifier",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'key_points' not in st.session_state:
    st.session_state.key_points = None
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('GEMINI_API_KEY', '')

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .main .block-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    * { font-family: 'Poppins', sans-serif; }
    h1, h2, h3 { color: white !important; font-weight: 700 !important; }
    h1 {
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    p, label, .stMarkdown { color: rgba(255, 255, 255, 0.95) !important; }
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6);
    }
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        border: 2px dashed rgba(255, 255, 255, 0.3);
        padding: 2rem;
    }
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: white !important;
        padding: 0.75rem;
    }
    .stAlert {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        padding: 1rem 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.5rem;
        border-radius: 50px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 50px;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
        padding: 0.5rem 1.5rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
    }
    [data-testid="column"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        backdrop-filter: blur(5px);
    }
    </style>
""", unsafe_allow_html=True)


def extract_text_from_pdf(pdf_file, max_pages: int = 10) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    pdf_document = None
    try:
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = pdf_document.page_count
        if total_pages > max_pages:
            st.warning(f"Processing only first {max_pages} of {total_pages} pages.")
        text = ""
        for page_num in range(min(total_pages, max_pages)):
            try:
                text += pdf_document[page_num].get_text() + "\n"
            except:
                continue
        if pdf_document:
            pdf_document.close()
        if not text.strip():
            return None, "PDF appears empty or contains only images.", total_pages
        if len(text) > 1_000_000:
            return None, "Text too large.", total_pages
        return text, None, total_pages
    except Exception as e:
        if pdf_document:
            try:
                pdf_document.close()
            except:
                pass
        return None, f"Error reading PDF: {str(e)}", 0


@st.cache_data(show_spinner=False, ttl=3600)
def get_summary(text: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"3-sentence summary in simple English:\n\n{text[:15000]}")
        return (response.text, None) if response and response.text else (None, "Empty response")
    except Exception as e:
        err = str(e).lower()
        if "api key" in err or "invalid" in err:
            return None, "Invalid API key"
        elif "quota" in err:
            return None, "API quota exceeded"
        return None, f"Error: {str(e)}"


@st.cache_data(show_spinner=False, ttl=3600)
def get_key_points(text: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"5 key points as bolded bullets:\n\n{text[:15000]}")
        return (response.text, None) if response and response.text else (None, "Empty response")
    except Exception as e:
        err = str(e).lower()
        if "api key" in err or "invalid" in err:
            return None, "Invalid API key"
        elif "quota" in err:
            return None, "API quota exceeded"
        return None, f"Error: {str(e)}"


def main():
    st.markdown('<h1>📄 AI Document Simplifier</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.2rem; margin-top: -1rem; opacity: 0.9;">Transform complex PDFs into simple summaries with the power of AI</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        env_api_key = os.getenv('GEMINI_API_KEY', '')
        if env_api_key:
            st.success("✅ API Key loaded!")
            api_key = env_api_key
        else:
            api_key = st.text_input("Gemini API Key", value=st.session_state.api_key, type="password", placeholder="Enter your API key...")
            st.session_state.api_key = api_key
        st.markdown("---")
        st.info("• Max pages: 10\n• Max text: ~1MB\n• Format: Text PDFs only")
        st.markdown("---")
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.session_state.clear()
            st.rerun()

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("### 📤 Upload Document")
        uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            st.info(f"📊 Size: {uploaded_file.size / 1024:.2f} KB")

    with col2:
        st.markdown("### 🚀 Process")
        process_button = st.button("🎯 Process Document", disabled=not uploaded_file or not api_key, use_container_width=True)
        if not uploaded_file:
            st.warning("⚠️ Upload a PDF first")
        elif not api_key:
            st.warning("⚠️ Enter API key in sidebar")

    if process_button:
        with st.spinner("📖 Reading PDF..."):
            text, error, total_pages = extract_text_from_pdf(uploaded_file)
        if error:
            st.error(f"❌ {error}")
            return
        st.session_state.extracted_text = text
        st.success(f"✅ Extracted {len(text):,} characters from {min(total_pages, 10)} pages")

        tab1, tab2, tab3 = st.tabs(["📝 Summary", "🔑 Key Points", "📄 Full Text"])
        with tab1:
            with st.spinner("🤖 Generating summary..."):
                summary, error = get_summary(text, api_key)
            if error:
                st.error(error)
            else:
                st.session_state.summary = summary
                st.info(summary)
        with tab2:
            with st.spinner("🤖 Extracting key points..."):
                key_points, error = get_key_points(text, api_key)
            if error:
                st.error(error)
            else:
                st.session_state.key_points = key_points
                st.success(key_points)
        with tab3:
            st.text_area("", text, height=400, label_visibility="collapsed")

        if st.session_state.summary and st.session_state.key_points:
            st.balloons()

    elif st.session_state.summary or st.session_state.key_points:
        st.info("ℹ️ Showing previously processed results.")
        tab1, tab2, tab3 = st.tabs(["📝 Summary", "🔑 Key Points", "📄 Full Text"])
        with tab1:
            if st.session_state.summary:
                st.info(st.session_state.summary)
        with tab2:
            if st.session_state.key_points:
                st.success(st.session_state.key_points)
        with tab3:
            if st.session_state.extracted_text:
                st.text_area("", st.session_state.extracted_text, height=400, label_visibility="collapsed")


if __name__ == "__main__":
    main()