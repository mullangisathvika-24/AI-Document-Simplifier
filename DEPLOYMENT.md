# Production Deployment Guide 🚀

## Pre-Deployment Checklist ✅

### 1. Environment Setup
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from requirements.txt
- [ ] Gemini API key obtained and tested

### 2. Testing Checklist

#### Basic Functionality Tests
- [ ] App starts without errors (`streamlit run app.py`)
- [ ] UI renders correctly in browser
- [ ] File uploader accepts PDF files only
- [ ] API key input field works (password masked)

#### Error Handling Tests
- [ ] Upload empty/blank API key → Shows error message
- [ ] Upload without PDF → Shows warning message
- [ ] Upload corrupted PDF → Shows user-friendly error
- [ ] Upload PDF with only images → Shows appropriate error
- [ ] Upload PDF > 10 pages → Shows warning, processes first 10 pages
- [ ] Enter invalid API key → Shows clear authentication error
- [ ] Exceed API quota → Shows rate limit message
- [ ] Disconnect internet during processing → Shows network error

#### Session State Tests
- [ ] Process document → Results appear
- [ ] Interact with sidebar → Results persist
- [ ] Switch tabs → Content remains visible
- [ ] Upload new file → Old results replaced
- [ ] Process same file twice → Uses cached results (faster)

#### Performance Tests
- [ ] Process 1-page PDF → Completes in <30 seconds
- [ ] Process 10-page PDF → Completes in <60 seconds
- [ ] Cache hit → Response near-instant
- [ ] Clear cache → All data removed
- [ ] Multiple rapid clicks → No crashes

### 3. Security Checklist
- [ ] API key input uses `type="password"`
- [ ] API key not logged or exposed in UI
- [ ] File uploads properly validated (PDF only)
- [ ] No sensitive data stored permanently
- [ ] Error messages don't expose internal details

### 4. UX/Polish Checklist
- [ ] Loading spinners appear during processing
- [ ] Success balloons appear after completion
- [ ] Warning messages show for large PDFs
- [ ] Progress indicated during each step
- [ ] Buttons disabled when inputs missing
- [ ] Clear cache button works correctly

## Deployment Options

### Option 1: Streamlit Cloud (Recommended for Demo)

1. **Push to GitHub**
   ```bash
   git init
   git add app.py requirements.txt README.md
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to App Settings → Secrets
   - Add (optional, for default API key):
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```

### Option 2: Local Production Server

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run with production settings
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Option 3: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t ai-document-simplifier .
docker run -p 8501:8501 ai-document-simplifier
```

### Option 4: Cloud Platforms

#### Heroku
1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

#### Google Cloud Run
```bash
gcloud run deploy ai-doc-simplifier \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Production Hardening

### 1. Environment Variables
Instead of sidebar input, use environment variables for API key:

```python
import os
api_key = os.getenv('GEMINI_API_KEY', '')
```

### 2. Rate Limiting
Add user-level rate limiting:

```python
from streamlit_extras.app_timer import timer

MAX_REQUESTS_PER_HOUR = 10
```

### 3. Monitoring
Add analytics and error tracking:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 4. Content Security
Add file size validation:

```python
MAX_FILE_SIZE_MB = 10
if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
    st.error(f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB")
```

## Troubleshooting

### Issue: "Invalid API Key"
**Solution**: Verify API key at https://makersuite.google.com/app/apikey

### Issue: Slow Processing
**Solution**: 
- Reduce max_pages limit
- Check internet connection
- Verify API quota

### Issue: Cache Not Working
**Solution**: 
- Clear browser cache
- Click "Clear Cache" button
- Restart Streamlit server

### Issue: PDF Not Reading
**Solution**:
- Ensure PDF has extractable text (not scanned image)
- Try opening PDF in Adobe Reader first
- Check file isn't password-protected

## Performance Optimization

### Recommended Settings
```python
# In config.toml (create .streamlit/config.toml)
[server]
maxUploadSize = 10
enableXsrfProtection = true
enableCORS = false

[browser]
gatherUsageStats = false

[runner]
magicEnabled = false
```

### Caching Strategy
- Summary/Key Points: 1 hour TTL
- File hash: Prevents duplicate processing
- Clear cache: Manual control for users

## Monitoring & Maintenance

### Key Metrics to Track
- Average processing time
- Error rate by type
- Cache hit rate
- API usage/cost
- User engagement (files processed per session)

### Regular Maintenance
- [ ] Weekly: Review error logs
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Review API costs
- [ ] As needed: Clear old cache data

## Support & Documentation

### User Documentation
Include in app or separate guide:
1. How to get Gemini API key
2. Supported PDF formats
3. Processing limits
4. Privacy policy (data not stored)

### Developer Documentation
- Code comments are inline
- Function docstrings included
- README.md covers basics
- This guide covers deployment

## Cost Estimation

### Gemini API Pricing (as of Jan 2025)
- Free tier: 60 requests/minute
- Paid tier: $0.00025 per 1K characters

### Example Usage
- 10-page PDF ≈ 15,000 characters
- Cost per document: ~$0.004
- 1000 documents/month: ~$4

### Streamlit Cloud
- Free tier: 1 app, community sharing
- Team tier: $250/month (unlimited apps)

## License & Legal

- Ensure compliance with PDF sources
- Gemini API terms of service
- User privacy considerations
- Content moderation if public-facing

## Next Steps

1. ✅ Complete all testing checklist items
2. ✅ Choose deployment option
3. ✅ Set up monitoring
4. ✅ Document for end users
5. ✅ Launch and gather feedback!
