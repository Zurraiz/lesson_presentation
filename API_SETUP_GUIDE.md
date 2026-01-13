# API Keys Setup Guide

## 🔑 Step 1: Get Your Gemini API Key

1. **Visit Google AI Studio**:
   - Go to: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey

2. **Create API Key**:
   - Click "Create API Key"
   - Select your Google Cloud project (or create a new one)
   - Copy the generated API key

3. **Add to .env file**:
   ```
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   ```

## 🖼️ Step 2: Get Google Custom Search API (for Images)

### Part A: Get API Key

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/apis/credentials

2. **Enable Custom Search API**:
   - Go to: https://console.cloud.google.com/apis/library
   - Search for "Custom Search API"
   - Click "Enable"

3. **Create Credentials**:
   - Go back to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" → "API Key"
   - Copy the API key

### Part B: Create Search Engine ID

1. **Go to Programmable Search Engine**:
   - Visit: https://programmablesearchengine.google.com/

2. **Create New Search Engine**:
   - Click "Add" or "Create a new search engine"
   - **Search engine name**: "Lesson Planner Images"
   - **What to search**: Select "Search the entire web"
   - **Image search**: Turn ON
   - **SafeSearch**: Turn ON (recommended for educational content)

3. **Get Search Engine ID**:
   - After creation, go to "Control Panel"
   - Find "Search engine ID" (looks like: `0123456789abcdef0:abcdefghij`)
   - Copy this ID

4. **Add to .env file**:
   ```
   GOOGLE_SEARCH_API_KEY=AIzaSy...your_search_api_key
   GOOGLE_SEARCH_ENGINE_ID=0123456789abcdef0:abcdefghij
   ```

## 📝 Step 3: Create Your .env File

Create a file named `.env` in your project root directory:

```bash
# In: c:/Users/PMLS/Documents/Workspace for experiments/.env

# Google Gemini API Key (REQUIRED for AI content generation)
GEMINI_API_KEY=AIzaSy...your_gemini_key_here

# Google Custom Search API (OPTIONAL - for real images)
# If not set, placeholder images will be used
GOOGLE_SEARCH_API_KEY=AIzaSy...your_search_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

## 🔄 Step 4: Restart the Server

After adding your API keys:

1. Stop the Django server (Ctrl+C in terminal)
2. Restart it: `python manage.py runserver`
3. The new environment variables will be loaded

## ✅ Verification

### Test Gemini API:
```python
# In Python shell
import os
from dotenv import load_dotenv
load_dotenv()

print("Gemini Key:", "✓ Set" if os.getenv("GEMINI_API_KEY") else "✗ Missing")
print("Search Key:", "✓ Set" if os.getenv("GOOGLE_SEARCH_API_KEY") else "✗ Missing")
print("Search ID:", "✓ Set" if os.getenv("GOOGLE_SEARCH_ENGINE_ID") else "✗ Missing")
```

## 💡 How Images Work

### With Google Search API (Recommended):
1. AI generates image queries like "photosynthesis diagram for kids"
2. Backend calls Google Custom Search API
3. Real, relevant images are inserted into the PowerPoint

### Without API Keys (Fallback):
1. AI still generates image queries
2. Backend uses placeholder images from picsum.photos
3. Presentation still works, but with generic placeholder images

## 💰 Pricing Notes

### Gemini API:
- **Free tier**: 60 requests per minute
- **Cost**: Free for most educational use cases
- Docs: https://ai.google.dev/pricing

### Google Custom Search API:
- **Free tier**: 100 queries per day
- **Paid**: $5 per 1000 queries after free tier
- Docs: https://developers.google.com/custom-search/v1/overview

## 🚨 Troubleshooting

### "GEMINI_API_KEY not set" warning:
- Make sure `.env` file is in the project root
- Check that `python-dotenv` is installed: `pip install python-dotenv`
- Restart the Django server

### "Google Search API credentials not configured":
- This is just a warning - the system will use placeholder images
- To fix: Add both `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID` to `.env`

### API quota exceeded:
- Gemini: Wait 1 minute or upgrade to paid tier
- Search: Wait until next day or enable billing in Google Cloud
