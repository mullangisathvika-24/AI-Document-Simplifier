# AI Document Simplifier 📄

A production-grade Streamlit web app that uses Google's Gemini AI to simplify PDF documents by generating summaries and key points.

## Features ✨

### Core Functionality
- **PDF Upload**: Clean drag-and-drop interface for PDF files
- **Text Extraction**: Powered by PyMuPDF for reliable text extraction
- **AI Summarization**: 3-sentence summaries in simple English
- **Key Points**: 5 bolded bullet points highlighting main ideas
- **Modern UI**: Clean, responsive interface with tabs and spinners

### Production-Grade Enhancements
- ✅ **Session State Management**: Results persist across interactions
- ✅ **Smart Caching**: API results cached for 1 hour (prevents redundant calls)
- ✅ **Robust Error Handling**: User-friendly messages for all error scenarios
- ✅ **Input Validation**: Comprehensive checks before processing
- ✅ **Resource Management**: 10-page limit to prevent timeouts
- ✅ **UX Polish**: Loading spinners, success balloons, and disabled buttons
- ✅ **File Hash Tracking**: Detects duplicate uploads automatically

## Installation 🚀

### Option 1: Using requirements.txt (Recommended)

```bash
pip install -r requirements.txt
```

### Option 2: Manual Installation

```bash
pip install streamlit==1.31.0
pip install PyMuPDF==1.23.26
pip install fitz==0.0.1.dev2
pip install google-generativeai==0.3.2
```

### Verify Installation

```bash
python test_app.py
```

This will run automated tests to ensure everything is set up correctly.

## Setup 🔧

1. **Get a Gemini API Key**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Create a new API key
   - Copy the key (you'll need it in the app)

2. **Run the Application**
   ```bash
   streamlit run app.py
   ```

3. **Access the App**
   - The app will automatically open in your browser
   - If not, navigate to: http://localhost:8501

## Usage 📖

1. **Enter API Key**: Paste your Gemini API key in the sidebar
2. **Upload PDF**: Click "Browse files" and select a PDF document
3. **Process**: Click the "Process Document" button
4. **View Results**: 
   - Switch between Summary, Key Points, and Full Text tabs
   - Results are generated in real-time with AI
   - 🎉 Balloons appear when processing completes!

## Production Features 🛡️

### Session State Persistence
- Results remain visible even after UI interactions
- Upload different files without losing previous results
- Cached results displayed automatically

### Smart Caching
- API calls cached for 1 hour to save time and costs
- Duplicate file detection prevents reprocessing
- Manual cache clear option in sidebar

### Error Handling
The app gracefully handles:
- ❌ Invalid or missing API keys
- ❌ Corrupted or invalid PDFs
- ❌ Empty PDFs or image-only PDFs
- ❌ Network connectivity issues
- ❌ API quota/rate limit errors
- ❌ PDFs too large or with too many pages

### Resource Management
- **Page Limit**: Processes first 10 pages automatically
- **Text Limit**: Maximum ~1MB of extracted text
- **Warning System**: Alerts users about large documents
- **Timeout Protection**: Prevents long-running API calls

### UX Enhancements
- 🎯 Disabled buttons when inputs are missing
- ⏳ Loading spinners with estimated time
- 🎉 Success balloons on completion
- 📊 Real-time file size and page count display
- 💡 Helpful tooltips and guidance messages

## Limitations ⚠️

- PDF files must contain extractable text (not scanned images)
- Maximum document size: 10 pages or ~1MB of text
- Requires internet connection for AI processing
- API key must be valid and have available quota

## Testing 🧪

Run the automated test suite:

```bash
python test_app.py
```

This validates:
- ✅ All required libraries are installed
- ✅ App structure and critical functions exist
- ✅ PDF processing works correctly
- ✅ Error handling is implemented
- ✅ Requirements file is complete

## Deployment 🚀

### Quick Start (Local)
```bash
streamlit run app.py
```

### Production Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment options including:
- Streamlit Cloud
- Docker containers
- Heroku
- Google Cloud Run
- Production hardening tips

## Project Structure 📁

```
.
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── test_app.py            # Automated test suite
├── README.md              # This file
└── DEPLOYMENT.md          # Deployment guide
```

## Technical Details 🛠️

### Libraries Used:
- **Streamlit**: Web framework for the UI
- **PyMuPDF (fitz)**: PDF text extraction
- **google-generativeai**: Gemini AI integration

### Key Functions:
- `extract_text_from_pdf()`: Extracts text from uploaded PDFs
- `get_summary()`: Generates 3-sentence summary using Gemini
- `get_key_points()`: Extracts 5 key bullet points using Gemini

## Troubleshooting 🔍

**"Error reading PDF"**
- Ensure the PDF is not corrupted
- Try a different PDF file
- Check that the PDF contains text (not just images)

**"Error generating summary/key points"**
- Verify your API key is correct
- Check your internet connection
- Ensure you have API quota available

**"PDF is too large"**
- Try splitting the PDF into smaller sections
- Remove unnecessary pages
- Use a PDF compressor

## Security Note 🔒

- API keys are entered via password field (hidden text)
- Keys are not stored permanently
- Consider using environment variables for production deployments

## License

MIT License - Feel free to use and modify as needed!
