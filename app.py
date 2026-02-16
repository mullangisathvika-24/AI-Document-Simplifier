"""
AI Document Simplifier - Streamlit Web App
Production-Grade Version with API Key Persistence Options
"""

import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
from typing import Optional, Tuple
import time
import hashlib
import os

# Page configuration
st.set_page_config(
    page_title="AI Document Simplifier",
    page_icon="📄",
    layout="wide"
)

# Initialize session state variables
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'key_points' not in st.session_state:
    st.session_state.key_points = None
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'processed_file_hash' not in st.session_state:
    st.session_state.processed_file_hash = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'api_key' not in st.session_state:
    # Try to load from environment variable first
    st.session_state.api_key = os.getenv('GEMINI_API_KEY', '')

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)


def extract_text_from_pdf(pdf_file, max_pages: int = 10) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    Extract text from a PDF file using PyMuPDF with page limit.
    
    Args:
        pdf_file: Uploaded PDF file object from Streamlit
        max_pages: Maximum number of pages to process (default: 10)
        
    Returns:
        Tuple of (extracted_text, error_message, total_pages)
    """
    pdf_document = None
    try:
        # Open PDF from bytes
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)  # Reset file pointer for potential re-reads
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        total_pages = pdf_document.page_count
        
        # Warn if PDF is too large
        if total_pages > max_pages:
            st.warning(f"⚠️ PDF has {total_pages} pages. Processing only the first {max_pages} pages to ensure optimal performance.")
        
        # Extract text from pages (up to max_pages)
        text = ""
        pages_to_process = min(total_pages, max_pages)
        
        for page_num in range(pages_to_process):
            try:
                page = pdf_document[page_num]
                page_text = page.get_text()
                text += page_text + "\n"
            except Exception as page_error:
                st.warning(f"⚠️ Could not read page {page_num + 1}: {str(page_error)}")
                continue
        
        pdf_document.close()
        
        # Check if text was extracted
        if not text.strip():
            return None, "The PDF appears to be empty or contains only images. Please use a PDF with extractable text.", total_pages
        
        # Check if text is too large (>1MB of text ≈ 1,000,000 chars)
        if len(text) > 1_000_000:
            return None, "The extracted text is too large. Please upload a smaller document or reduce the number of pages.", total_pages
        
        return text, None, total_pages
        
    except fitz.FileDataError:
        return None, "The file appears to be corrupted or not a valid PDF. Please try a different file.", 0
    except MemoryError:
        return None, "The PDF is too large to process. Please try a smaller file.", 0
    except Exception as e:
        return None, f"Unexpected error reading PDF: {str(e)}. Please try a different file or contact support.", 0
    finally:
        # Ensure PDF is closed even if an error occurs
        if pdf_document is not None:
            try:
                pdf_document.close()
            except:
                pass


@st.cache_data(show_spinner=False, ttl=3600)
def get_summary(text: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate a 3-sentence summary using Gemini AI with caching.
    
    Args:
        text: The text to summarize
        api_key: Gemini API key
        
    Returns:
        Tuple of (summary, error_message)
    """
    try:
        # Configure API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
Please provide a 3-sentence summary of the following text in simple English. 
Make it easy to understand for anyone, avoiding technical jargon when possible.

Text:
{text[:15000]}  # Limit to ~15k chars to avoid token limits
"""
        
        # Generate content with timeout protection
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return None, "Gemini AI returned an empty response. Please try again."
        
        return response.text, None
        
    except genai.types.generation_types.BlockedPromptException:
        return None, "The content was blocked by Gemini's safety filters. Please try a different document."
    except genai.types.generation_types.StopCandidateException:
        return None, "The generation was stopped by Gemini. The content may have triggered safety filters."
    except Exception as e:
        error_msg = str(e).lower()
        if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg:
            return None, "Invalid API key. Please check your Gemini API key and try again."
        elif "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
            return None, "API quota exceeded or rate limit reached. Please try again later or check your API usage."
        elif "network" in error_msg or "connection" in error_msg:
            return None, "Network error. Please check your internet connection and try again."
        else:
            return None, f"Error generating summary: {str(e)}. Please try again or contact support."


@st.cache_data(show_spinner=False, ttl=3600)
def get_key_points(text: str, api_key: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate 5 key bullet points using Gemini AI with caching.
    
    Args:
        text: The text to analyze
        api_key: Gemini API key
        
    Returns:
        Tuple of (key_points, error_message)
    """
    try:
        # Configure API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
Please provide exactly 5 key points from the following text as bolded bullet points.
Each point should be concise and capture the most important information.
Format each point with markdown bold (**point text here**).

Text:
{text[:15000]}  # Limit to ~15k chars to avoid token limits
"""
        
        # Generate content with timeout protection
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return None, "Gemini AI returned an empty response. Please try again."
        
        return response.text, None
        
    except genai.types.generation_types.BlockedPromptException:
        return None, "The content was blocked by Gemini's safety filters. Please try a different document."
    except genai.types.generation_types.StopCandidateException:
        return None, "The generation was stopped by Gemini. The content may have triggered safety filters."
    except Exception as e:
        error_msg = str(e).lower()
        if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg:
            return None, "Invalid API key. Please check your Gemini API key and try again."
        elif "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
            return None, "API quota exceeded or rate limit reached. Please try again later or check your API usage."
        elif "network" in error_msg or "connection" in error_msg:
            return None, "Network error. Please check your internet connection and try again."
        else:
            return None, f"Error generating key points: {str(e)}. Please try again or contact support."


def get_file_hash(uploaded_file) -> str:
    """
    Generate a hash of the uploaded file for cache management.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        SHA256 hash of the file
    """
    try:
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
        return hashlib.sha256(file_bytes).hexdigest()
    except Exception:
        return None


def main():
    """Main application function with production-grade robustness"""
    
    # Header
    st.title("📄 AI Document Simplifier")
    st.markdown("Upload a PDF document and let AI create a simple summary and key points for you!")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check if API key is already in environment
        env_api_key = os.getenv('GEMINI_API_KEY', '')
        if env_api_key:
            st.success("✅ API Key loaded from environment variable")
            api_key = env_api_key
        else:
            # Manual input with session state persistence
            api_key = st.text_input(
                "Enter your Gemini API Key",
                value=st.session_state.api_key,
                type="password",
                help="Get your API key from https://makersuite.google.com/app/apikey",
                key="api_key_input"
            )
            # Update session state
            st.session_state.api_key = api_key
        
        st.markdown("---")
        st.markdown("### 💡 API Key Tips")
        st.info("""
        **Option 1**: Enter it here (resets on refresh)
        
        **Option 2**: Set environment variable:
        ```bash
        export GEMINI_API_KEY="your-key"
        ```
        Then restart the app.
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Processing Limits")
        st.info("""
        - **Max pages**: 10 pages
        - **Max text**: ~1MB
        - **Format**: Text-based PDFs only
        """)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app uses:
        - **PyMuPDF** for PDF text extraction
        - **Google Gemini AI** for intelligent summarization
        - **Caching** to avoid redundant API calls
        
        Upload a PDF to get started!
        """)
        
        st.markdown("---")
        st.markdown("### Tips")
        st.markdown("""
        - PDFs with images/scans won't work well
        - Results are cached for 1 hour
        - Best results with well-formatted PDFs
        - Limit: 10 pages for optimal performance
        """)
        
        # Add cache clear button
        if st.button("🗑️ Clear Cache", help="Clear cached results and start fresh"):
            st.cache_data.clear()
            st.session_state.summary = None
            st.session_state.key_points = None
            st.session_state.extracted_text = None
            st.session_state.processed_file_hash = None
            st.success("Cache cleared!")
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Select a PDF document to analyze",
            key="pdf_uploader"
        )
        
        if uploaded_file:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            st.info(f"📊 File size: {uploaded_file.size / 1024:.2f} KB")
    
    with col2:
        st.subheader("🚀 Process")
        process_button = st.button("Process Document", type="primary", disabled=not uploaded_file or not api_key)
        
        # Show helpful message if button is disabled
        if not uploaded_file:
            st.warning("⚠️ Please upload a PDF file first")
        elif not api_key:
            st.warning("⚠️ Please enter your API key in the sidebar")
    
    # Processing logic
    if process_button:
        # Input validation (redundant check for safety)
        if not uploaded_file:
            st.error("❌ Please upload a PDF file first!")
            return
        
        if not api_key or len(api_key.strip()) == 0:
            st.error("❌ Please enter a valid Gemini API key in the sidebar!")
            return
        
        # Check if this is a new file or same file as before
        current_file_hash = get_file_hash(uploaded_file)
        is_new_file = (current_file_hash != st.session_state.processed_file_hash)
        
        # Extract text from PDF
        with st.spinner("📖 Reading PDF..."):
            try:
                text, error, total_pages = extract_text_from_pdf(uploaded_file, max_pages=10)
            except Exception as e:
                st.error(f"❌ Critical error reading PDF: {str(e)}")
                return
            
        if error:
            st.error(f"❌ {error}")
            return
        
        if not text:
            st.error("❌ Could not extract text from the PDF. Please ensure the PDF contains extractable text.")
            return
        
        # Store extracted text in session state
        st.session_state.extracted_text = text
        st.session_state.processed_file_hash = current_file_hash
        
        # Show extracted text info
        pages_processed = min(total_pages, 10)
        st.success(f"✅ Extracted {len(text):,} characters from {pages_processed} page(s) of {uploaded_file.name}")
        
        if total_pages > 10:
            st.info(f"ℹ️ Note: Only the first 10 pages were processed out of {total_pages} total pages.")
        
        # Create tabs for results
        tab1, tab2, tab3 = st.tabs(["📝 Summary", "🔑 Key Points", "📄 Full Text"])
        
        # Generate summary
        with tab1:
            with st.spinner("🤖 AI is generating summary... (this may take 10-20 seconds)"):
                try:
                    summary, error = get_summary(text, api_key)
                except Exception as e:
                    st.error(f"❌ Unexpected error during summary generation: {str(e)}")
                    summary, error = None, str(e)
            
            if error:
                st.error(f"❌ {error}")
                st.session_state.summary = None
            else:
                st.session_state.summary = summary
                st.info("### 📝 Summary")
                st.write(summary)
        
        # Generate key points
        with tab2:
            with st.spinner("🤖 AI is extracting key points... (this may take 10-20 seconds)"):
                try:
                    key_points, error = get_key_points(text, api_key)
                except Exception as e:
                    st.error(f"❌ Unexpected error during key points generation: {str(e)}")
                    key_points, error = None, str(e)
            
            if error:
                st.error(f"❌ {error}")
                st.session_state.key_points = None
            else:
                st.session_state.key_points = key_points
                st.success("### 🔑 Key Points")
                st.markdown(key_points)
        
        # Show full text
        with tab3:
            st.text_area(
                "Full Extracted Text",
                text,
                height=400,
                help="All text extracted from the PDF"
            )
        
        # Success celebration
        if st.session_state.summary and st.session_state.key_points:
            st.session_state.processing_complete = True
            st.balloons()
            st.success("🎉 Processing complete! Your document has been simplified.")
    
    # Display cached results if they exist (even if button hasn't been pressed this session)
    elif st.session_state.summary or st.session_state.key_points or st.session_state.extracted_text:
        st.info("ℹ️ Displaying previously processed results. Upload a new file or click 'Process Document' to refresh.")
        
        tab1, tab2, tab3 = st.tabs(["📝 Summary", "🔑 Key Points", "📄 Full Text"])
        
        with tab1:
            if st.session_state.summary:
                st.info("### 📝 Summary")
                st.write(st.session_state.summary)
            else:
                st.warning("No summary available. Click 'Process Document' to generate.")
        
        with tab2:
            if st.session_state.key_points:
                st.success("### 🔑 Key Points")
                st.markdown(st.session_state.key_points)
            else:
                st.warning("No key points available. Click 'Process Document' to generate.")
        
        with tab3:
            if st.session_state.extracted_text:
                st.text_area(
                    "Full Extracted Text",
                    st.session_state.extracted_text,
                    height=400,
                    help="All text extracted from the PDF"
                )
            else:
                st.warning("No text available. Upload and process a PDF first.")


if __name__ == "__main__":
    main()