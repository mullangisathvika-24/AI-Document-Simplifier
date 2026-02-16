"""
AI Document Simplifier - Modern Glass Morphism UI
Beautiful gradient design with glassmorphism effects
"""

import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
from typing import Optional, Tuple
import hashlib
import os

# Page configuration
st.set_page_config(
    page_title="AI Document Simplifier",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'key_points' not in st.session_state:
    st.session_state.key_points = None
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'processed_file_hash' not in st.session_state:
    st.session_state.processed_file_hash = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('GEMINI_API_KEY', '')

# Modern Glass Morphism CSS with Gradient Background
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
    
    /* Main Background with Animated Gradient */
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
    
    /* Glass Morphism Card Effect */
    .main .block-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Typography */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    h1, h2, h3 {
        color: white !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h1 {
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }
    
    p, label, .stMarkdown {
        color: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Sidebar Glass Effect */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Modern Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton>button:active {
        transform: translateY(0px);
    }
    
    /* File Uploader Styling */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 2px dashed rgba(255, 255, 255, 0.3);
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(255, 255, 255, 0.5);
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: white !important;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    
    /* Info Boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        padding: 1rem 1.5rem;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Tabs Styling */
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
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
    }
    
    /* Text Area */
    .stTextArea>div>div>textarea {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        color: white;
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
    }
    
    /* Success/Warning Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
        border-left: 4px solid #10b981;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%);
        border-left: 4px solid #f59e0b;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border-left: 4px solid #ef4444;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.2) 100%);
        border-left: 4px solid #3b82f6;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
        border-right-color: #764ba2 !important;
    }
    
    /* Columns */
    [data-testid="column"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        backdrop-filter: blur(5px);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Pulse Animation for Processing */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .processing {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Floating Animation for Upload Area */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    [data-testid="stFileUploader"] {
        animation: float 3s ease-in-out infinite;
    }
    </style>
""", unsafe_allow_html=True)

# [Rest of the Python code remains the same - only UI styling changed]
# Include all the functions from the previous version here...

def extract_text_from_pdf(pdf_file, max_pages: int = 10) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """Extract text from PDF"""
    pdf_document = None
    try:
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = pdf_document.page_count
        
        if total_pages > max_pages:
            st.warning(f"⚠️ PDF has {total_pages} pages. Processing only the first {max_pages} pages.")
        
        text = ""
        pages_to_process = min(total_pages, max_pages)
        
        for page_num in range(pages_to_process):
            try:
                page = pdf_document[page_num]
                text += page.get_text() + "\n"
            except Exception as page_error:
                st.warning(f"⚠️ Could not read page {page_num + 1}")
                continue
        
        pdf_document.close()
        
        if not text.strip():
            return None, "PDF appears empty or contains only images.", total_pages
        if len(text) > 1_000_000:
            return None, "Text too large. Please use a smaller document.", total_pages
        
        return text, None, total_pages
        
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}", 0
    finally:
        if pdf_document:
            try:
                pdf_document.close()
            except:
                pass

@st.cache_data(show_spinner=False, ttl=3600)
def get_summary(text: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    """Generate summary using Gemini AI"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Please provide a 3-sentence summary in simple English:\n\n{text[:15000]}"
        response = model.generate_content(prompt)
        return response.text if response and response.text else None, None if response and response.text else "Empty response"
    except Exception as e:
        if "api key" in str(e).lower():
            return None, "Invalid API key"
        elif "quota" in str(e).lower():
            return None, "API quota exceeded"
        return None, f"Error: {str(e)}"

@st.cache_data(show_spinner=False, ttl=3600)
def get_key_points(text: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    """Generate key points using Gemini AI"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Provide exactly 5 key points as bolded bullets (**text**):\n\n{text[:15000]}"
        response = model.generate_content(prompt)
        return response.text if response and response.text else None, None if response and response.text else "Empty response"
    except Exception as e:
        if "api key" in str(e).lower():
            return None, "Invalid API key"
        elif "quota" in str(e).lower():
            return None, "API quota exceeded"
        return None, f"Error: {str(e)}"

def get_file_hash(uploaded_file) -> str:
    """Generate file hash"""
    try:
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        return hashlib.sha256(file_bytes).hexdigest()
    except:
        return None

def main():
    """Main application"""
    
    # Header with custom styling
    st.markdown('<h1>📄 AI Document Simplifier</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.2rem; margin-top: -1rem; opacity: 0.9;">Transform complex PDFs into simple summaries with the power of AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        env_api_key = os.getenv('GEMINI_API_KEY', '')
        if env_api_key:
            st.success("✅ API Key loaded from environment")
            api_key = env_api_key
        else:
            api_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.api_key,
                type="password",
                placeholder="Enter your API key...",
                help="Get your key from https://makersuite.google.com/app/apikey"
            )
            st.session_state.api_key = api_key
        
        st.markdown("---")
        st.markdown("### 📊 Processing Limits")
        st.info("• Max pages: 10\n• Max text: ~1MB\n• Format: Text PDFs only")
        
        st.markdown("---")
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.session_state.clear()
            st.success("Cache cleared!")
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📤 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            label_visibility="collapsed"
        )
        
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
    
    # Processing
    if process_button:
        if not uploaded_file or not api_key:
            st.error("❌ Missing required inputs!")
            return
        
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
                st.error(f"❌ {error}")
            else:
                st.session_state.summary = summary
                st.info(summary)
        
        with tab2:
            with st.spinner("🤖 Extracting key points..."):
                key_points, error = get_key_points(text, api_key)
            if error:
                st.error(f"❌ {error}")
            else:
                st.session_state.key_points = key_points
                st.success(key_points)
        
        with tab3:
            st.text_area("Extracted Text", text, height=400, label_visibility="collapsed")
        
        if st.session_state.summary and st.session_state.key_points:
            st.balloons()

if __name__ == "__main__":
    main()
